"""PMQ-001 unavailable trusted evidence fail-closed challenge."""

from dataclasses import replace
from pathlib import Path

from app.engines.execution_gateway import ExecutionAttempt, validate_execution
from app.engines.financial_runtime import evaluate_financial
from app.engines.protected_consequence import execute_protected_consequence
from harness.runner import load_scenario


def test_pmq001_unavailable_required_screening_evidence_cannot_form_consequence():
    req = load_scenario(Path("harness/scenarios/AP-001_allow.json"))
    req = replace(req, screening_status="UNAVAILABLE")

    response, receipt = evaluate_financial(req)
    assert response.decision != "ALLOW"

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
    assert gateway.execution_permit is None

    protected = execute_protected_consequence(
        permit=gateway.execution_permit,
        attempted_action_binding_hash=receipt.action_binding_hash,
    )
    assert protected != "CONSEQUENCE_FORMED"
