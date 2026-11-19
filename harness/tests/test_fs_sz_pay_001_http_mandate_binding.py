"""Failure-first: configured provider mandate cannot silently authorise another mandate.

Current HTTP provider uses a single startup mandate/epoch rather than a
consequence-bound mandate supplied and verified per request. This test is a
bounded source-level negative control for the configured provider route.
"""
from app.engines.t24_provider_commit_fence_reference import ProviderCommitFence
from external_targets.cbp002_consequence_service import ExternalLedger

def test_provider_rejects_wrong_mandate_even_if_configured_mandate_is_active(tmp_path):
    fence=ProviderCommitFence(tmp_path/"provider.sqlite3")
    fence.establish("MANDATE-ALLOWED",epoch=1)
    fence.establish("MANDATE-REVOKED",epoch=1)
    fence.revoke("MANDATE-REVOKED")
    ledger=ExternalLedger(fence=fence,mandate_id="MANDATE-ALLOWED",authority_epoch=1)
    status,response=ledger.transfer({
        "transaction_id":"intent-under-revoked-mandate",
        "mandate_id":"MANDATE-REVOKED",
        "authority_epoch":1,
        "source_account":"TREASURY-001",
        "beneficiary":"SUPPLIER-X",
        "amount":750000.0,
        "currency":"GBP",
        "purpose":"supplier settlement",
    })
    assert status==403 and response["status"]=="REFUSED_AUTHORITY"
    assert fence.transfer_count()==0
