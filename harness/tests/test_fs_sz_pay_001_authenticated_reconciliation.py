"""Authenticated reconciliation after provider restart and lost acknowledgement."""
from app.engines.t24_provider_commit_fence_reference import ProviderCommitFence
from external_targets.cbp002_consequence_service import ExternalLedger
from tests.provider_signed_fixture import issuer, signed_payment

def test_lost_ack_reconciles_committed_intent_after_restart(tmp_path):
    key = issuer()
    path = tmp_path / "provider.sqlite3"
    provider = ProviderCommitFence(path)
    provider.establish("MANDATE-A", epoch=1)
    ledger = ExternalLedger(fence=provider, mandate_id="MANDATE-A",
                            authority_epoch=1, authorization_public_key=key.public_key())
    payload = signed_payment(key, {
        "transaction_id": "stable-intent-001", "mandate_id": "MANDATE-A",
        "authority_epoch": 1, "source_account": "TREASURY-001",
        "beneficiary": "SUPPLIER-X", "amount": 750000.0, "currency": "GBP",
        "purpose": "supplier settlement"})
    assert ledger.transfer(payload)[0] == 201
    # Simulate lost HTTP acknowledgement; new service instance uses same durable state.
    restarted = ExternalLedger(fence=ProviderCommitFence(path), mandate_id="MANDATE-A",
                               authority_epoch=1, authorization_public_key=key.public_key())
    status, result = restarted.reconcile(payload)
    assert status == 200 and result == {
        "status": "TRANSFER_RECORDED", "payment_intent_id": "stable-intent-001"}
    assert restarted.transfer(payload)[0] != 201
    assert provider.transfer_count() == 1

def test_reconciliation_requires_signed_exact_payment_and_is_read_only(tmp_path):
    key = issuer()
    path = tmp_path / "provider.sqlite3"
    provider = ProviderCommitFence(path)
    provider.establish("MANDATE-A", epoch=1)
    ledger = ExternalLedger(fence=provider, mandate_id="MANDATE-A",
                            authority_epoch=1, authorization_public_key=key.public_key())
    payload = signed_payment(key, {
        "transaction_id": "unknown-intent", "mandate_id": "MANDATE-A",
        "authority_epoch": 1, "source_account": "TREASURY-001",
        "beneficiary": "SUPPLIER-X", "amount": 100.0, "currency": "GBP",
        "purpose": "supplier settlement"})
    assert ledger.reconcile(payload) == (200, {"status": "NOT_FOUND_IN_REFERENCE_LEDGER"})
    assert ledger.reconcile({**payload, "beneficiary": "ATTACKER"})[0] == 403
    assert ledger.reconcile({**payload, "institutional_authorization": {}})[0] == 403
    assert provider.transfer_count() == 0
