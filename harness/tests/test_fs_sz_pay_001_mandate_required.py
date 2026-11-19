from provider_signed_fixture import issuer, signed_payment, write_public_key
"""Frozen challenge: a configured fence must not silently supply missing authority."""
from app.engines.t24_provider_commit_fence_reference import ProviderCommitFence
from external_targets.cbp002_consequence_service import ExternalLedger

def test_missing_mandate_and_epoch_must_refuse(tmp_path):
    f=ProviderCommitFence(tmp_path/"provider.sqlite3")
    f.establish("MANDATE-A",epoch=1)
    key=issuer()
    ledger=ExternalLedger(authorization_public_key=key.public_key(),fence=f,mandate_id="MANDATE-A",authority_epoch=1)
    status,response=ledger.transfer({
        "transaction_id":"intent-missing-authority",
        "source_account":"TREASURY-001","beneficiary":"SUPPLIER-X",
        "amount":750000.0,"currency":"GBP","purpose":"supplier settlement",
    })
    assert status==403 and response["status"]=="REFUSED_UNAUTHENTICATED_INSTRUCTION"
    assert f.transfer_count()==0

def test_explicit_correct_mandate_epoch_can_commit(tmp_path):
    f=ProviderCommitFence(tmp_path/"provider.sqlite3")
    f.establish("MANDATE-A",epoch=1)
    key=issuer()
    ledger=ExternalLedger(authorization_public_key=key.public_key(),fence=f,mandate_id="MANDATE-A",authority_epoch=1)
    status,response=ledger.transfer(signed_payment(key, {
        "transaction_id":"intent-correct-authority",
        "mandate_id":"MANDATE-A","authority_epoch":1,
        "source_account":"TREASURY-001","beneficiary":"SUPPLIER-X",
        "amount":750000.0,"currency":"GBP","purpose":"supplier settlement",
    }))
    assert status==201 and response["status"]=="TRANSFER_RECORDED"
    assert f.transfer_count()==1
