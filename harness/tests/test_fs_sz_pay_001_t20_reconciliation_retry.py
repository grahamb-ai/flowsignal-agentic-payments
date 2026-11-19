"""T20 failure-first: new permit must not silently repeat an unresolved external effect."""
from pathlib import Path
import pytest
from app.engines import external_consequence_adapter
from app.engines.protected_consequence import ExternalOutcomeUnknown
from app.engines.execution_gateway import ExecutionAttempt, validate_execution
from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario

def _permit_and_attempt():
    req=load_scenario(Path("harness/scenarios/AP-001_allow.json"))
    response,receipt=evaluate_financial(req)
    assert response.decision=="ALLOW"
    attempt=ExecutionAttempt(
        actor_id=req.actor_id,principal_id=req.principal_id,action=req.action,
        target=req.target,amount=req.amount,currency=req.currency,
        source_account=req.source_account,beneficiary=req.beneficiary,
        purpose=req.purpose,mandate_id=req.mandate_id,
        attempted_at=req.requested_execution_time,
    )
    gateway=validate_execution(receipt,attempt)
    assert gateway.status=="PERMITTED"
    return gateway.execution_permit,attempt

def test_t20_new_permit_does_not_repeat_unresolved_payment(tmp_path,monkeypatch):
    monkeypatch.setenv("FLOWSIGNAL_PERMIT_CONSUMPTION_STORE",str(tmp_path/"permits.sqlite3"))
    monkeypatch.setenv("FLOWSIGNAL_CONSEQUENCE_OUTCOME_STORE",str(tmp_path/"outcomes.sqlite3"))
    monkeypatch.setenv("FLOWSIGNAL_ROLLBACK_ANCHOR_STORE",str(tmp_path/"anchors.sqlite3"))
    commits=[]
    def provider_commits_but_drops_ack(url,payload,timeout_seconds):
        commits.append(payload.copy())
        raise ConnectionResetError("provider committed, response lost")
    monkeypatch.setattr(external_consequence_adapter,"_post_json",provider_commits_but_drops_ack)
    first,attempt=_permit_and_attempt()
    assert first is not None
    with pytest.raises(ExternalOutcomeUnknown):
        external_consequence_adapter.execute_external_payment(
            permit=first,attempt=attempt,payments_url="http://provider.invalid/payments"
        )
    assert len(commits)==1

    # A newly issued permit may have a different signature but the same payment intent.
    second,attempt2=_permit_and_attempt()
    assert second is not None and second.signature!=first.signature
    try:
        external_consequence_adapter.execute_external_payment(
            permit=second,attempt=attempt2,payments_url="http://provider.invalid/payments"
        )
    except ExternalOutcomeUnknown:
        pass

    # FROZEN REQUIREMENT: same unresolved business payment must not form twice.
    # Existing permit-signature-only idempotency is expected to fail this test.
    assert len(commits)==1, "T20 RED: new permit duplicated unresolved payment intent"
