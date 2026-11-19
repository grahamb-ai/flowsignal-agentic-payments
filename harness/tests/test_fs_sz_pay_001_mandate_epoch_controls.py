from provider_signed_fixture import issuer, signed_payment, write_public_key
"""Mandate/epoch substitution negative controls on configured fenced route."""
from app.engines.t24_provider_commit_fence_reference import ProviderCommitFence
from external_targets.cbp002_consequence_service import ExternalLedger

def test_wrong_epoch_is_refused_without_transfer(tmp_path):
    fence=ProviderCommitFence(tmp_path/"provider.sqlite3")
    fence.establish("MANDATE-A",epoch=1)
    key=issuer()
    ledger=ExternalLedger(authorization_public_key=key.public_key(),fence=fence,mandate_id="MANDATE-A",authority_epoch=1)
    status,result=ledger.transfer(signed_payment(key, {
        "transaction_id":"intent-wrong-epoch","mandate_id":"MANDATE-A",
        "authority_epoch":2,"source_account":"TREASURY-001",
        "beneficiary":"SUPPLIER-X","amount":100.0,"currency":"GBP","purpose":"test"}))
    assert status==403 and result["status"]=="REFUSED_AUTHORITY"
    assert fence.transfer_count()==0

def test_matching_explicit_mandate_can_commit_before_revocation(tmp_path):
    fence=ProviderCommitFence(tmp_path/"provider.sqlite3")
    fence.establish("MANDATE-A",epoch=1)
    key=issuer()
    ledger=ExternalLedger(authorization_public_key=key.public_key(),fence=fence,mandate_id="MANDATE-A",authority_epoch=1)
    status,result=ledger.transfer(signed_payment(key, {
        "transaction_id":"intent-correct","mandate_id":"MANDATE-A",
        "authority_epoch":1,"source_account":"TREASURY-001",
        "beneficiary":"SUPPLIER-X","amount":100.0,"currency":"GBP","purpose":"test"}))
    assert status==201 and result["status"]=="TRANSFER_RECORDED"
    assert fence.transfer_count()==1
