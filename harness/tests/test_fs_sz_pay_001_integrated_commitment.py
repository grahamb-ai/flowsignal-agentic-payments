"""Integrated Structural Zero qualification: FlowSignal adapter -> cooperating provider fence.

These tests cover the qualified reference route only. No live rail or alternate
provider credentials are covered. Institutional revocation is represented by
the provider fence's authoritative SQLite state, not FlowSignal's local RLock.
"""
from pathlib import Path
import sqlite3
from app.engines import external_consequence_adapter
from app.engines.execution_gateway import ExecutionAttempt, validate_execution
from app.engines.financial_runtime import evaluate_financial
from app.engines.t24_provider_commit_fence_reference import ProviderCommitFence
from harness.runner import load_scenario


def _authorized():
    req=load_scenario(Path("harness/scenarios/AP-001_allow.json"))
    decision,receipt=evaluate_financial(req)
    assert decision.decision=="ALLOW"
    attempt=ExecutionAttempt(
        actor_id=req.actor_id,principal_id=req.principal_id,action=req.action,
        target=req.target,amount=req.amount,currency=req.currency,
        source_account=req.source_account,beneficiary=req.beneficiary,
        purpose=req.purpose,mandate_id=req.mandate_id,
        attempted_at=req.requested_execution_time,
    )
    gateway=validate_execution(receipt, attempt, payment_intent_id='institution-payment-intent-001', provider_authority_epoch=1, provider_mandate_id=attempt.mandate_id)
    assert gateway.status=="PERMITTED"
    return attempt,gateway.execution_permit


def _setup(tmp_path,monkeypatch):
    monkeypatch.setenv("FLOWSIGNAL_PERMIT_CONSUMPTION_STORE",str(tmp_path/"permits.sqlite3"))
    outcome=tmp_path/"outcomes.sqlite3"
    monkeypatch.setenv("FLOWSIGNAL_CONSEQUENCE_OUTCOME_STORE",str(outcome))
    monkeypatch.setenv("FLOWSIGNAL_ROLLBACK_ANCHOR_STORE",str(tmp_path/"anchors.sqlite3"))
    attempt,permit=_authorized()
    assert permit is not None
    provider=ProviderCommitFence(tmp_path/"provider.sqlite3")
    provider.establish(attempt.mandate_id,epoch=1)
    return attempt,permit,provider,outcome


def _outcome(path,permit):
    with sqlite3.connect(path) as db:
        return db.execute("SELECT outcome FROM consequence_outcomes WHERE permit_signature=?",
                          (permit.signature,)).fetchone()[0]


def test_integrated_revocation_first_refuses_formation(tmp_path,monkeypatch):
    attempt,permit,provider,outcome_db=_setup(tmp_path,monkeypatch)
    provider.revoke(attempt.mandate_id)
    def post(url,payload,timeout_seconds):
        return {"status":provider.commit(attempt.mandate_id,1,payload["transaction_id"])}
    monkeypatch.setattr(external_consequence_adapter,"_post_json",post)
    result,receipt=external_consequence_adapter.execute_external_payment(
        permit=permit,attempt=attempt,payments_url="http://cooperating-provider.invalid/payments")
    assert result=="DENIED_PROVIDER_COMMIT_REFUSED"
    assert provider.count()==0
    assert _outcome(outcome_db,permit)=="CONSEQUENCE_NOT_FORMED"


def test_integrated_revocation_inside_dispatch_refuses_formation(tmp_path,monkeypatch):
    attempt,permit,provider,outcome_db=_setup(tmp_path,monkeypatch)
    def post(url,payload,timeout_seconds):
        # Effective revocation after FlowSignal's final local standing check.
        provider.revoke(attempt.mandate_id)
        return {"status":provider.commit(attempt.mandate_id,1,payload["transaction_id"])}
    monkeypatch.setattr(external_consequence_adapter,"_post_json",post)
    result,_=external_consequence_adapter.execute_external_payment(
        permit=permit,attempt=attempt,payments_url="http://cooperating-provider.invalid/payments")
    assert result=="DENIED_PROVIDER_COMMIT_REFUSED"
    assert provider.count()==0
    assert _outcome(outcome_db,permit)=="CONSEQUENCE_NOT_FORMED"


def test_integrated_commit_first_then_revocation(tmp_path,monkeypatch):
    attempt,permit,provider,outcome_db=_setup(tmp_path,monkeypatch)
    def post(url,payload,timeout_seconds):
        status=provider.commit(attempt.mandate_id,1,payload["transaction_id"])
        provider.revoke(attempt.mandate_id)
        return {"status":status}
    monkeypatch.setattr(external_consequence_adapter,"_post_json",post)
    result,_=external_consequence_adapter.execute_external_payment(
        permit=permit,attempt=attempt,payments_url="http://cooperating-provider.invalid/payments")
    assert result=="CONSEQUENCE_FORMED"
    assert provider.count()==1
    assert _outcome(outcome_db,permit)=="CONSEQUENCE_FORMED"
    assert provider.commit(attempt.mandate_id,1,"later-intent")=="REFUSED_AUTHORITY"
