from dataclasses import replace
from pathlib import Path

from app.engines.authority_determination import (
    bind_authority_to_operation,
    issue_authorised_execution_constraint,
    materialise_protected_operation,
)
from app.engines.authority_resolution import resolve_payment_authority
from app.engines.authority_lineage import create_authority_exercise, create_execution_attempt
from app.engines.final_bind import revalidate_at_final_bind
from app.engines.institutional_authority import advance_authority_fence
from harness.runner import load_scenario


SCENARIO = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"


def _authorised_chain():
    req = load_scenario(SCENARIO, rebase_to_now=False)
    _, _, _, scope, context = resolve_payment_authority(
        req, resolved_at=req.requested_execution_time
    )
    exercise = create_authority_exercise(
            resolution_context_id=context.context_id,
            effective_authority_scope_id=scope.scope_id,
            protected_operation_class=context.protected_operation_class,
            created_at=req.requested_execution_time,
            authority_exercise_id="EX-001",
        )

    attempt = create_execution_attempt(
            authority_exercise_id=exercise.authority_exercise_id,
            route_id="R1",
            executor_id="PAYMENT-EXECUTOR-1",
            created_at=req.requested_execution_time,
            execution_attempt_id="ATT-001",
        )

    operation = materialise_protected_operation(
            req,
        route_id="R1",
        executor_id="PAYMENT-EXECUTOR-1",
        authority_exercise_id=exercise.authority_exercise_id,
        execution_attempt_id=attempt.execution_attempt_id,
    )
    binding = bind_authority_to_operation(scope, operation)
    determination, constraint = issue_authorised_execution_constraint(
        context=context,
        scope=scope,
        operation=operation,
        binding=binding,
        resolved_at=req.requested_execution_time,
        authority_exercise=exercise,
        execution_attempt=attempt,
    )
    return req, operation, determination, constraint


def test_slice_e_permits_unchanged_current_authority_and_operation():
    req, operation, determination, constraint = _authorised_chain()
    result = revalidate_at_final_bind(
        req,
        original_operation=operation,
        determination=determination,
        constraint=constraint,
        bind_at=req.requested_execution_time,
    )
    assert result.status == "PERMITTED"
    assert result.reason_code == "FINAL_BIND_AUTHORITY_REVALIDATED"


def test_authority_cut_change_blocks_at_final_bind():
    req, operation, determination, constraint = _authorised_chain()
    advance_authority_fence()
    result = revalidate_at_final_bind(
        req,
        original_operation=operation,
        determination=determination,
        constraint=constraint,
        bind_at=req.requested_execution_time,
    )
    assert result.status == "BLOCKED"
    assert result.reason_code == "AUTHORITY_CONTEXT_CHANGED"


def test_operation_change_after_determination_blocks():
    req, operation, determination, constraint = _authorised_chain()
    req.amount = req.amount + 1
    result = revalidate_at_final_bind(
        req,
        original_operation=operation,
        determination=determination,
        constraint=constraint,
        bind_at=req.requested_execution_time,
    )
    assert result.status == "BLOCKED"
    assert result.reason_code == "PROTECTED_OPERATION_CHANGED"


def test_attempt_substitution_blocks():
    req, operation, determination, constraint = _authorised_chain()
    substituted = replace(constraint, execution_attempt_id="ATT-ATTACKER")
    result = revalidate_at_final_bind(
        req,
        original_operation=operation,
        determination=determination,
        constraint=substituted,
        bind_at=req.requested_execution_time,
    )
    assert result.status == "BLOCKED"
    assert result.reason_code == "EXECUTION_ATTEMPT_MISMATCH"


def test_tampered_constraint_integrity_blocks():
    req, operation, determination, constraint = _authorised_chain()
    tampered = replace(constraint, integrity_material_id="00" * 32)
    result = revalidate_at_final_bind(
        req,
        original_operation=operation,
        determination=determination,
        constraint=tampered,
        bind_at=req.requested_execution_time,
    )
    assert result.status == "BLOCKED"
    assert result.reason_code == "AUTHORISED_EXECUTION_CONSTRAINT_INTEGRITY_INVALID"


def test_route_substitution_is_a_different_operation():
    req, operation, determination, constraint = _authorised_chain()
    substituted_operation = replace(operation, route_id="R2")
    result = revalidate_at_final_bind(
        req,
        original_operation=substituted_operation,
        determination=determination,
        constraint=constraint,
        bind_at=req.requested_execution_time,
    )
    assert result.status == "BLOCKED"
    assert result.reason_code == "PROTECTED_OPERATION_IDENTITY_MISMATCH"
