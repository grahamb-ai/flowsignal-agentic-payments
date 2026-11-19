"""End-to-end business-intent replay: a newly signed permit cannot redispatch.

The reference provider is a stub; the assertion is on the real protected
execution adapter and its durable payment-intent claim.
"""
from pathlib import Path
from app.engines import external_consequence_adapter
from app.engines.execution_gateway import ExecutionAttempt, validate_execution
from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_new_permit_same_business_intent_cannot_dispatch_twice(tmp_path, monkeypatch):
    monkeypatch.setenv("FLOWSIGNAL_PERMIT_CONSUMPTION_STORE", str(tmp_path/"permits.sqlite3"))
    monkeypatch.setenv("FLOWSIGNAL_CONSEQUENCE_OUTCOME_STORE", str(tmp_path/"outcomes.sqlite3"))
    monkeypatch.setenv("FLOWSIGNAL_ROLLBACK_ANCHOR_STORE", str(tmp_path/"anchors.sqlite3"))
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
    def issue():
        result=validate_execution(
            receipt,attempt,payment_intent_id="institution-payment-001",
            provider_authority_epoch=1,provider_mandate_id=attempt.mandate_id,
        )
        assert result.status=="PERMITTED"
        return result.execution_permit
    first,second=issue(),issue()
    assert first.signature!=second.signature
    dispatched=[]
    def provider(url,payload,timeout_seconds):
        dispatched.append(payload["transaction_id"])
        return {"status":"COMMITTED"}
    monkeypatch.setattr(external_consequence_adapter,"_post_json",provider)
    outcome,_=external_consequence_adapter.execute_external_payment(
        permit=first,attempt=attempt,payments_url="http://provider.invalid/payments")
    assert outcome=="CONSEQUENCE_FORMED"
    outcome,_=external_consequence_adapter.execute_external_payment(
        permit=second,attempt=attempt,payments_url="http://provider.invalid/payments")
    assert outcome=="DENIED_PAYMENT_INTENT_ALREADY_CLAIMED"
    assert dispatched==["institution-payment-001"]
