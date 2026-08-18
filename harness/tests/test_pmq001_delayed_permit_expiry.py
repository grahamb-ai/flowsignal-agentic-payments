"""PMQ-001 failure-first delayed permit expiry challenge.

Frozen challenge:
`evidence/PMQ-001/PMQ-001_DELAYED_PERMIT_EXPIRY_CHALLENGE.md`
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.engines.execution_gateway import ExecutionAttempt, action_binding_hash, validate_execution
from app.engines.financial_runtime import evaluate_financial
from app.engines.protected_consequence import execute_protected_consequence
from harness.runner import load_scenario


def test_pmq001_gateway_permit_cannot_form_consequence_after_authority_window_expires():
    req = load_scenario(Path("harness/scenarios/AP-001_allow.json"))

    sealed_at = datetime.now(timezone.utc) - timedelta(minutes=2)
    response, receipt = evaluate_financial(req, sealed_at=sealed_at)
    assert response.decision == "ALLOW"
    assert receipt.valid_until is not None
    assert receipt.valid_until < datetime.now(timezone.utc)

    # The represented execution attempt occurred while the original ALLOW was
    # still temporally valid, so the gateway can legitimately produce a permit.
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
        attempted_at=sealed_at + timedelta(seconds=30),
    )

    gateway = validate_execution(receipt, attempt)
    assert gateway.status == "PERMITTED"
    assert gateway.execution_permit is not None

    result = execute_protected_consequence(
        permit=gateway.execution_permit,
        attempted_action_binding_hash=action_binding_hash(attempt),
    )

    assert result != "CONSEQUENCE_FORMED", (
        "PMQ-001 FAILURE: gateway-produced execution permit remained capable "
        "of forming the represented consequence after the authority validity "
        "window had expired"
    )
