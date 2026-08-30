from pathlib import Path

from app.engines.execution_gateway import ExecutionAttempt, validate_execution
from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_vpc001_1_unresolved_material_condition_cannot_autonomously_admit():
    """Bounded analogue of Vadym Partasyuk's irreversibility conflict.

    The runtime is not asked to invent the substantive medical/ethical rule.
    It is asked whether an otherwise-authorised consequential action may proceed
    autonomously while a material required condition remains unresolved.
    """

    req = load_scenario(Path("harness/scenarios/AP-004_stale_screening_evidence.json"))
    response, receipt = evaluate_financial(req)

    assert response.decision == "ESCALATE", (
        "VPC-001.1 FAILURE: unresolved required evidence was autonomously admitted"
    )

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
