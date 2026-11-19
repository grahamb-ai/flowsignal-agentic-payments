"""Failure-first route-closure challenge against actual CBP-002 external ledger.

The direct /payments endpoint is a separate execution route from the
cooperating provider-fence reference. This test deliberately checks whether
the provider itself enforces revocation on that route.

No live payment rail is involved.
"""
from app.engines.t24_provider_commit_fence_reference import ProviderCommitFence
from external_targets.cbp002_consequence_service import ExternalLedger


def test_direct_provider_route_cannot_commit_after_authoritative_revocation(tmp_path):
    fence=ProviderCommitFence(tmp_path/"provider-authority.sqlite3")
    fence.establish("MANDATE-TREASURY-001",epoch=1)
    fence.revoke("MANDATE-TREASURY-001")

    # CBP-002 direct target is a distinct execution surface. Its transfer()
    # implementation currently checks payment fields/balance but not mandate
    # revocation or the provider-side fence.
    direct=ExternalLedger(fence=fence, mandate_id='MANDATE-TREASURY-001', authority_epoch=1)
    status,result=direct.transfer({
        "transaction_id":"new-permit-after-revocation",
        "source_account":"TREASURY-001",
        "beneficiary":"SUPPLIER-X",
        "amount":750000.0,
        "currency":"GBP",
        "purpose":"supplier settlement",
    })

    assert fence.commit("MANDATE-TREASURY-001",1,"separate-intent")=="REFUSED_AUTHORITY"
    assert direct.snapshot()["transfer_count"]==0, (
        "ROUTE-CLOSURE RED: direct provider payment route committed after "
        "revocation without invoking the qualified commitment fence; "
        f"status={status}, response={result}"
    )


def test_fenced_direct_route_commits_before_revocation_and_refuses_after(tmp_path):
    fence=ProviderCommitFence(tmp_path/"provider.sqlite3")
    fence.establish("MANDATE-TREASURY-001",epoch=1)
    direct=ExternalLedger(fence=fence,mandate_id="MANDATE-TREASURY-001",authority_epoch=1)
    payload={"transaction_id":"intent-1","source_account":"TREASURY-001",
             "beneficiary":"SUPPLIER-X","amount":750000.0,
             "currency":"GBP","purpose":"supplier settlement"}
    status,result=direct.transfer(payload)
    assert status==201 and result["status"]=="TRANSFER_RECORDED"
    assert direct.snapshot()["transfer_count"]==1
    fence.revoke("MANDATE-TREASURY-001")
    status,result=direct.transfer({**payload,"transaction_id":"intent-2"})
    assert status==403 and result["status"]=="REFUSED_AUTHORITY"
    assert direct.snapshot()["transfer_count"]==1


def test_unconfigured_legacy_route_remains_unqualified():
    # Explicitly document the scope limitation: default legacy ledger bypasses fence.
    direct=ExternalLedger()
    status,_=direct.transfer({"transaction_id":"legacy","source_account":"TREASURY-001",
                             "beneficiary":"SUPPLIER-X","amount":1.0,
                             "currency":"GBP","purpose":"sandbox"})
    assert status==201
