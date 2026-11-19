"""Provider authentication challenge: direct caller must not self-assert authority.

Frozen failure-first proposition. The reference provider must not form a payment
merely because caller-supplied mandate/epoch match service configuration.
"""
from app.engines.t24_provider_commit_fence_reference import ProviderCommitFence
from external_targets.cbp002_consequence_service import ExternalLedger


def test_direct_caller_cannot_self_assert_active_mandate(tmp_path):
    fence = ProviderCommitFence(tmp_path / "provider.sqlite3")
    fence.establish("MANDATE-A", epoch=1)
    ledger = ExternalLedger(fence=fence, mandate_id="MANDATE-A", authority_epoch=1)
    status, response = ledger.transfer({
        "transaction_id": "forged-direct-intent",
        "payment_intent_id": "forged-direct-intent",
        "mandate_id": "MANDATE-A",
        "authority_epoch": 1,
        "source_account": "TREASURY-001",
        "beneficiary": "ATTACKER",
        "amount": 750000.0,
        "currency": "GBP",
        "purpose": "unauthorised direct submission",
    })
    assert status in (401, 403), (
        "UNAUTHENTICATED_PROVIDER_COMMIT_RED: a direct caller formed a transfer "
        f"with self-asserted mandate/epoch; status={status}, response={response}"
    )
    assert fence.transfer_count() == 0

 
def test_provider_accepts_signed_exact_instruction_and_refuses_tampering(tmp_path):
    import json
    from datetime import datetime, timedelta, timezone
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from app.engines.provider_instruction_verifier import canonical_instruction
    issuer_private_key = Ed25519PrivateKey.generate()
    fence = ProviderCommitFence(tmp_path / "signed.sqlite3")
    fence.establish("MANDATE-A", epoch=1)
    ledger = ExternalLedger(fence=fence, mandate_id="MANDATE-A", authority_epoch=1,
                            authorization_public_key=issuer_private_key.public_key())
    payload = {"transaction_id": "institution-intent-001",
               "payment_intent_id": "institution-intent-001",
               "mandate_id": "MANDATE-A", "authority_epoch": 1,
               "source_account": "TREASURY-001", "beneficiary": "SUPPLIER-X",
               "amount": 750000.0, "currency": "GBP", "purpose": "settlement",
               "action": "payment.release", "target": "TREASURY-001"}
    expiry = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
    signed = json.dumps({"instruction": canonical_instruction(payload), "expires_at": expiry},
                        sort_keys=True, separators=(",", ":")).encode()
    payload["institutional_authorization"] = {
        "expires_at": expiry, "signature": issuer_private_key.sign(signed).hex()}
    changed = {**payload, "beneficiary": "ATTACKER"}
    status, _ = ledger.transfer(changed)
    assert status == 403 and fence.transfer_count() == 0
    status, _ = ledger.transfer(payload)
    assert status == 201 and fence.transfer_count() == 1
    status, _ = ledger.transfer(payload)
    assert status != 201 and fence.transfer_count() == 1


def test_signed_intent_cannot_be_relabelled_as_new_transaction(tmp_path):
    import json
    from datetime import datetime, timedelta, timezone
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from app.engines.provider_instruction_verifier import canonical_instruction
    key = Ed25519PrivateKey.generate()
    fence = ProviderCommitFence(tmp_path / "intent-relabel.sqlite3")
    fence.establish("MANDATE-A", epoch=1)
    ledger = ExternalLedger(fence=fence, mandate_id="MANDATE-A", authority_epoch=1,
                            authorization_public_key=key.public_key())
    payload = {"transaction_id": "original-intent", "payment_intent_id": "original-intent",
               "mandate_id": "MANDATE-A", "authority_epoch": 1,
               "source_account": "TREASURY-001", "beneficiary": "SUPPLIER-X",
               "amount": 100.0, "currency": "GBP", "purpose": "settlement",
               "action": "payment.release", "target": "external-payment-provider"}
    expiry = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
    message = json.dumps({"instruction": canonical_instruction(payload), "expires_at": expiry},
                         sort_keys=True, separators=(",", ":")).encode()
    payload["institutional_authorization"] = {"expires_at": expiry, "signature": key.sign(message).hex()}
    assert ledger.transfer(payload)[0] == 201
    relabelled = {**payload, "transaction_id": "different-provider-intent"}
    status, _ = ledger.transfer(relabelled)
    assert status in (401, 403, 409)
    assert fence.transfer_count() == 1
