"""Reconciliation qualification: provider durable state, authentication and uncertainty."""
from app.engines.t24_provider_commit_fence_reference import ProviderCommitFence
from external_targets.cbp002_consequence_service import ExternalLedger
from tests.provider_signed_fixture import issuer, signed_payment


def _setup(tmp_path):
    key = issuer()
    path = tmp_path / "provider.sqlite3"
    fence = ProviderCommitFence(path)
    fence.establish("MANDATE-A", epoch=1)
    ledger = ExternalLedger(fence=fence, mandate_id="MANDATE-A",
                            authority_epoch=1, authorization_public_key=key.public_key())
    payment = signed_payment(key, {
        "transaction_id": "durable-intent-001", "mandate_id": "MANDATE-A",
        "authority_epoch": 1, "source_account": "TREASURY-001",
        "beneficiary": "SUPPLIER-X", "amount": 750000.0,
        "currency": "GBP", "purpose": "settlement"})
    return key, path, fence, ledger, payment


def test_lost_ack_restart_reconciliation_is_read_only(tmp_path):
    key, path, fence, ledger, payment = _setup(tmp_path)
    status, _ = ledger.transfer(payment)
    assert status == 201
    # Simulate lost HTTP acknowledgement and provider process restart.
    restarted = ExternalLedger(fence=ProviderCommitFence(path), mandate_id="MANDATE-A",
                               authority_epoch=1, authorization_public_key=key.public_key())
    status, result = restarted.reconcile(payment)
    assert status == 200 and result == {
        "status": "TRANSFER_RECORDED", "payment_intent_id": "durable-intent-001"}
    assert restarted.snapshot()["transfer_count"] == 1
    retry_status, retry = restarted.transfer(payment)
    assert retry_status == 409 and retry["status"] == "REFUSED_DUPLICATE_INTENT"
    assert restarted.snapshot()["transfer_count"] == 1


def test_missing_reference_record_is_not_proof_of_noncommit(tmp_path):
    _, _, fence, ledger, payment = _setup(tmp_path)
    status, result = ledger.reconcile(payment)
    assert status == 200 and result["status"] == "NOT_FOUND_IN_REFERENCE_LEDGER"
    assert result["status"] != "NOT_COMMITTED"
    assert fence.transfer_count() == 0


def test_reconciliation_refuses_unsigned_or_changed_payment(tmp_path):
    _, _, fence, ledger, payment = _setup(tmp_path)
    assert ledger.transfer(payment)[0] == 201
    unsigned = dict(payment)
    unsigned.pop("institutional_authorization")
    status, result = ledger.reconcile(unsigned)
    assert status == 403 and result["status"] == "REFUSED_UNAUTHENTICATED_INSTRUCTION"
    altered = {**payment, "beneficiary": "ATTACKER"}
    status, result = ledger.reconcile(altered)
    assert status == 403 and result["status"] == "REFUSED_UNAUTHENTICATED_INSTRUCTION"
    assert fence.transfer_count() == 1


def test_other_route_commit_is_invisible_to_reference_reconciliation(tmp_path):
    """Preserved scope counterexample: one ledger cannot attest another route."""
    _, _, fence, protected, payment = _setup(tmp_path)
    legacy = ExternalLedger(legacy_test_mode=True)
    status, _ = legacy.transfer({
        "transaction_id": payment["transaction_id"],
        "source_account": payment["source_account"],
        "beneficiary": payment["beneficiary"],
        "amount": payment["amount"],
        "currency": payment["currency"],
        "purpose": payment["purpose"],
    })
    assert status == 201 and legacy.snapshot()["transfer_count"] == 1
    status, result = protected.reconcile(payment)
    assert status == 200
    assert result["status"] == "NOT_FOUND_IN_REFERENCE_LEDGER"
    assert result["status"] != "NOT_COMMITTED"
    assert fence.transfer_count() == 0


def test_revocation_does_not_erase_preexisting_commit_evidence(tmp_path):
    _, _, fence, ledger, payment = _setup(tmp_path)
    assert ledger.transfer(payment)[0] == 201
    fence.revoke("MANDATE-A")
    status, result = ledger.reconcile(payment)
    assert status == 200 and result["status"] == "TRANSFER_RECORDED"
    assert fence.transfer_count() == 1
