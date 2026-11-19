"""T23 failure-first: local authority guard cannot enforce provider-side revocation.

The provider is a deterministic simulated independent authority/commitment domain.
It revokes its own mandate *after* FlowSignal's local standing check, but before
the external payment commits. A provider without an authoritative fence accepts.
The frozen requirement expects no commitment after effective revocation.
"""
from pathlib import Path
import pytest
from app.engines import external_consequence_adapter
from app.engines.execution_gateway import ExecutionAttempt, validate_execution
from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario

def test_t23_provider_revocation_before_commit_cannot_form(tmp_path, monkeypatch):
    monkeypatch.setenv("FLOWSIGNAL_PERMIT_CONSUMPTION_STORE",str(tmp_path/"permits.sqlite3"))
    monkeypatch.setenv("FLOWSIGNAL_CONSEQUENCE_OUTCOME_STORE",str(tmp_path/"outcomes.sqlite3"))
    monkeypatch.setenv("FLOWSIGNAL_ROLLBACK_ANCHOR_STORE",str(tmp_path/"anchors.sqlite3"))
    req=load_scenario(Path("harness/scenarios/AP-001_allow.json"))
    decision,receipt=evaluate_financial(req)
    assert decision.decision=="ALLOW"
    attempt=ExecutionAttempt(
        actor_id=req.actor_id,principal_id=req.principal_id,
        action=req.action,target=req.target,amount=req.amount,
        currency=req.currency,source_account=req.source_account,
        beneficiary=req.beneficiary,purpose=req.purpose,
        mandate_id=req.mandate_id,attempted_at=req.requested_execution_time,
    )
    gateway=validate_execution(receipt,attempt)
    assert gateway.status=="PERMITTED"
    assert gateway.execution_permit is not None
    provider={"mandate_revoked":False,"commits":[]}
    def external_provider_without_fence(url,payload,timeout_seconds):
        # Independent institutional revocation takes effect after local check,
        # immediately before the provider's consequence-forming operation.
        provider["mandate_revoked"]=True
        # Existing adapter sends no provider-side authoritative revocation
        # token/fence; this deliberately unqualified provider still commits.
        provider["commits"].append(payload["transaction_id"])
        return {"status":"committed"}
    monkeypatch.setattr(external_consequence_adapter,"_post_json",external_provider_without_fence)
    external_consequence_adapter.execute_external_payment(
        permit=gateway.execution_permit,attempt=attempt,
        payments_url="http://unqualified-provider.invalid/payments",
    )
    assert provider["mandate_revoked"]
    assert provider["commits"]==[], (
        "T23 RED: provider committed after its authoritative revocation; "
        "local FlowSignal lock is not a provider-side commitment fence"
    )
