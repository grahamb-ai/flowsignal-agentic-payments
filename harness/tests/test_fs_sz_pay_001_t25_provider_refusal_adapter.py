"""T25 failure-first: real FlowSignal adapter ignores provider REFUSED_AUTHORITY."""
from pathlib import Path
from app.engines import external_consequence_adapter
from app.engines.execution_gateway import ExecutionAttempt, validate_execution
from app.engines.financial_runtime import evaluate_financial
from app.engines.t24_provider_commit_fence_reference import ProviderCommitFence
from harness.runner import load_scenario

def test_t25_adapter_must_not_report_formed_on_provider_refusal(tmp_path,monkeypatch):
    monkeypatch.setenv("FLOWSIGNAL_PERMIT_CONSUMPTION_STORE",str(tmp_path/"permits.sqlite3"))
    monkeypatch.setenv("FLOWSIGNAL_CONSEQUENCE_OUTCOME_STORE",str(tmp_path/"outcomes.sqlite3"))
    monkeypatch.setenv("FLOWSIGNAL_ROLLBACK_ANCHOR_STORE",str(tmp_path/"anchors.sqlite3"))
    req=load_scenario(Path("harness/scenarios/AP-001_allow.json"))
    decision,receipt=evaluate_financial(req)
    assert decision.decision=="ALLOW"
    attempt=ExecutionAttempt(actor_id=req.actor_id,principal_id=req.principal_id,
        action=req.action,target=req.target,amount=req.amount,currency=req.currency,
        source_account=req.source_account,beneficiary=req.beneficiary,
        purpose=req.purpose,mandate_id=req.mandate_id,attempted_at=req.requested_execution_time)
    gateway=validate_execution(receipt, attempt, payment_intent_id='institution-payment-intent-001', provider_authority_epoch=1, provider_mandate_id=attempt.mandate_id)
    assert gateway.status=="PERMITTED"
    assert gateway.execution_permit is not None
    provider=ProviderCommitFence(tmp_path/"provider.sqlite3")
    provider.establish(attempt.mandate_id,epoch=1)
    provider.revoke(attempt.mandate_id) # effective before provider's commitment point
    def provider_response(url,payload,timeout_seconds):
        status=provider.commit(attempt.mandate_id,1,payload["transaction_id"])
        return {"status":status}
    monkeypatch.setattr(external_consequence_adapter,"_post_json",provider_response)
    outcome,receipt=external_consequence_adapter.execute_external_payment(
        permit=gateway.execution_permit,attempt=attempt,
        payments_url="http://cooperating-provider.invalid/payments")
    assert provider.count()==0
    assert outcome!="CONSEQUENCE_FORMED", (
        "T25 RED: FlowSignal recorded FORMATION after provider explicitly refused authority"
    )
