"""Restart/ack-loss qualification for the authenticated cooperating provider.

The same durable provider database is reopened after an acknowledgement is lost.
A new service instance must not form a second transfer for the same signed intent.
"""
from app.engines.t24_provider_commit_fence_reference import ProviderCommitFence
from external_targets.cbp002_consequence_service import ExternalLedger
from tests.provider_signed_fixture import issuer, signed_payment


def test_signed_payment_lost_ack_restart_fresh_attempt_cannot_duplicate(tmp_path):
    path = tmp_path / "provider-durable.sqlite3"
    first_fence = ProviderCommitFence(path)
    first_fence.establish("MANDATE-A", epoch=1)
    key = issuer()
    first = ExternalLedger(fence=first_fence, mandate_id="MANDATE-A",
                           authority_epoch=1, authorization_public_key=key.public_key())
    payment = signed_payment(key, {
        "transaction_id": "stable-institution-intent-001",
        "mandate_id": "MANDATE-A", "authority_epoch": 1,
        "source_account": "TREASURY-001", "beneficiary": "SUPPLIER-X",
        "amount": 750000.0, "currency": "GBP", "purpose": "supplier settlement",
    })
    status, response = first.transfer(payment)
    assert status == 201 and response["status"] == "TRANSFER_RECORDED"
    # Simulate lost HTTP acknowledgement: caller never receives the above result.
    del first
    del first_fence

    restarted_fence = ProviderCommitFence(path)
    restarted = ExternalLedger(fence=restarted_fence, mandate_id="MANDATE-A",
                               authority_epoch=1, authorization_public_key=key.public_key())
    status, response = restarted.transfer(payment)
    assert status == 409 and response["status"] == "REFUSED_DUPLICATE_INTENT"
    assert restarted_fence.transfer_count() == 1
    assert restarted_fence.count() == 1
