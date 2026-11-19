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
