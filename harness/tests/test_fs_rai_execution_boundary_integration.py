from pathlib import Path
from dataclasses import replace
from datetime import datetime, timedelta, timezone

from app.engines.execution_gateway import ExecutionAttempt, action_binding_hash, validate_execution
from app.engines.financial_runtime import evaluate_financial
from app.engines.protected_consequence import execute_protected_consequence
from app.engines.runtime_authority_payment import (
    prepare_payment_execution,
    final_bind_payment,
    mint_rai_bound_execution_permit,
)
from harness.runner import load_scenario


SCENARIO = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"


def _attempt(req):
    return ExecutionAttempt(
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


def test_rai_final_bind_causally_mints_capability_consumed_by_protected_boundary():
    req = load_scenario(SCENARIO, rebase_to_now=False)
    prepared = prepare_payment_execution(
        req, route_id="R1", executor_id="PAYMENT-EXECUTOR-1",
        resolved_at=req.requested_execution_time,
    )
    final = final_bind_payment(req, prepared, bind_at=req.requested_execution_time)
    assert final.status == "PERMITTED"

    permit = mint_rai_bound_execution_permit(req, prepared, bind_at=req.requested_execution_time)
    assert permit is not None
    assert permit.rai_determination_id == prepared.determination.determination_id
    assert permit.rai_constraint_id == prepared.constraint.constraint_id
    assert permit.rai_protected_operation_id == prepared.operation.operation_id
    assert permit.rai_authority_exercise_id == prepared.determination.authority_exercise_id
    assert permit.rai_execution_attempt_id == prepared.determination.execution_attempt_id

    outcome = execute_protected_consequence(
        permit=permit,
        attempted_action_binding_hash=action_binding_hash(_attempt(req)),
    )
    assert outcome == "CONSEQUENCE_FORMED"


def test_rai_bound_permit_is_not_minted_when_final_bind_blocks():
    req = load_scenario(SCENARIO, rebase_to_now=False)
    prepared = prepare_payment_execution(
        req, route_id="R1", executor_id="PAYMENT-EXECUTOR-1",
        resolved_at=req.requested_execution_time,
    )
    req.amount = req.amount + 1
    permit = mint_rai_bound_execution_permit(req, prepared, bind_at=req.requested_execution_time)
    assert permit is None


def test_legacy_gateway_cannot_form_protected_consequence_without_rai_chain():
    """Failure-first route-closure challenge.

    The legacy receipt/gateway path must not retain an independent route to the
    protected consequence once RAI is claimed as mandatory for this operation.
    """
    req = load_scenario(SCENARIO, rebase_to_now=False)
    now = datetime.now(timezone.utc)
    req = replace(
        req,
        requested_execution_time=now,
        screening_captured_at=now,
        mandate_valid_until=now + timedelta(hours=1),
    )

    response, receipt = evaluate_financial(req, sealed_at=now)
    assert response.decision == "ALLOW"

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
        attempted_at=now,
    )
    gateway = validate_execution(receipt, attempt)
    assert gateway.status == "PERMITTED"
    assert gateway.execution_permit is not None
    assert gateway.execution_permit.rai_determination_id is None

    outcome = execute_protected_consequence(
        permit=gateway.execution_permit,
        attempted_action_binding_hash=action_binding_hash(attempt),
    )

    assert outcome != "CONSEQUENCE_FORMED", (
        "ROUTE CLOSURE FAILURE: legacy gateway formed the protected consequence "
        "without the mandatory RAI determination/final-bind chain"
    )
