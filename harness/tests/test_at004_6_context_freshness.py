from pathlib import Path

from app.engines.authority_store import advance_authority_state_version
from app.engines.execution_gateway import ExecutionAttempt, validate_execution
from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_at004_6_still_valid_receipt_is_blocked_after_authority_state_changes():
    req = load_scenario(Path("harness/scenarios/AP-001_allow.json"))

    response, receipt = evaluate_financial(req)

    assert response.decision == "ALLOW"

    advance_authority_state_version()

    attempt = ExecutionAttempt(
        actor_id=req.actor_id,
        principal_id=req.principal_id,
        action=req.action,
        target=req.target,
        amount=req.amount,
        currency=req.currency,
        source_account=req.source_account,
        beneficiary=req.beneficiary,
        purpose=req.purpose,
        mandate_id=req.mandate_id,
        attempted_at=req.requested_execution_time,
    )

    gateway = validate_execution(receipt, attempt)

    assert gateway.status == "BLOCKED"
    assert gateway.reason_code == "AUTHORITY_STATE_STALE_REEVALUATION_REQUIRED"