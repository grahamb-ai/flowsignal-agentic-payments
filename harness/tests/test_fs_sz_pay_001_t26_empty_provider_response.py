"""T26 failure-first: HTTP 200 with empty JSON is not commitment evidence."""
from pathlib import Path
from app.engines import external_consequence_adapter
from app.engines.execution_gateway import ExecutionAttempt,validate_execution
from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario
from app.engines.protected_consequence import ExternalOutcomeUnknown
import pytest
import sqlite3

def test_t26_empty_provider_response_cannot_prove_formation(tmp_path,monkeypatch):
    monkeypatch.setenv("FLOWSIGNAL_PERMIT_CONSUMPTION_STORE",str(tmp_path/"permits.sqlite3"))
    outcome_db=tmp_path/"outcomes.sqlite3"
    monkeypatch.setenv("FLOWSIGNAL_CONSEQUENCE_OUTCOME_STORE",str(outcome_db))
    monkeypatch.setenv("FLOWSIGNAL_ROLLBACK_ANCHOR_STORE",str(tmp_path/"anchors.sqlite3"))
    req=load_scenario(Path("harness/scenarios/AP-001_allow.json"))
    response,receipt=evaluate_financial(req)
    assert response.decision=="ALLOW"
    attempt=ExecutionAttempt(actor_id=req.actor_id,principal_id=req.principal_id,
        action=req.action,target=req.target,amount=req.amount,currency=req.currency,
        source_account=req.source_account,beneficiary=req.beneficiary,
        purpose=req.purpose,mandate_id=req.mandate_id,attempted_at=req.requested_execution_time)
    gateway=validate_execution(receipt,attempt)
    assert gateway.status=="PERMITTED"
    permit=gateway.execution_permit
    assert permit is not None
    monkeypatch.setattr(external_consequence_adapter,"_post_json",lambda *a,**kw: {})
    with pytest.raises(ExternalOutcomeUnknown):
        external_consequence_adapter.execute_external_payment(
            permit=permit,attempt=attempt,payments_url="http://provider.invalid/payments")
    with sqlite3.connect(outcome_db) as conn:
        outcome=conn.execute("SELECT outcome FROM consequence_outcomes WHERE permit_signature=?",(permit.signature,)).fetchone()
    assert outcome==("CONSEQUENCE_OUTCOME_UNRESOLVED",)
