from __future__ import annotations

"""Integrated Runtime Authority payment path.

Composes R2 resolution, R3 approval, R5 lineage, R4 usage and Slice D/E
operation binding/final-bind revalidation without claiming downstream success.
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from app.engines.authority_determination import (
    AuthorityDetermination,
    bind_authority_to_operation,
    issue_authorised_execution_constraint,
    materialise_protected_operation,
)
from app.engines.authority_domain import (
    AuthorisedExecutionConstraint,
    AuthorityUsageMode,
    AuthorityUsagePolicy,
    ProtectedOperation,
)
from app.engines.authority_lineage import create_authority_exercise, create_execution_attempt
from app.engines.authority_resolution import AuthorityResolutionError, resolve_payment_authority
from app.engines.authority_usage import register_usage_policy, reserve_authority_usage
from app.engines.final_bind import FinalBindResult, revalidate_at_final_bind


@dataclass(frozen=True)
class PreparedAuthorityExecution:
    operation: ProtectedOperation
    determination: AuthorityDetermination
    constraint: AuthorisedExecutionConstraint
    usage_reservation_id: str
    usage_policy_id: str


def prepare_payment_execution(
    req,
    *,
    route_id: str,
    executor_id: str,
    resolved_at: datetime,
) -> PreparedAuthorityExecution:
    _, _, _, scope, context = resolve_payment_authority(req, resolved_at=resolved_at)

    exercise = create_authority_exercise(
        resolution_context_id=context.context_id,
        effective_authority_scope_id=scope.scope_id,
        protected_operation_class=context.protected_operation_class,
        created_at=resolved_at,
    )
    attempt = create_execution_attempt(
        authority_exercise_id=exercise.authority_exercise_id,
        route_id=route_id,
        executor_id=executor_id,
        created_at=resolved_at,
    )
    operation = materialise_protected_operation(
        req,
        route_id=route_id,
        executor_id=executor_id,
        authority_exercise_id=exercise.authority_exercise_id,
        execution_attempt_id=attempt.execution_attempt_id,
    )
    binding = bind_authority_to_operation(scope, operation)

    # NORM-PAY-001 reference usage: one authority exercise may reach one
    # commitment attempt unless a later governing usage semantics explicitly
    # permits more.  Retry requires a new attempt and fresh reservation.
    policy = AuthorityUsagePolicy(
        usage_policy_id=f"USAGE-POLICY:{exercise.authority_exercise_id}",
        authority_scope_id=scope.scope_id,
        mode=AuthorityUsageMode.SINGLE,
        scope_key=f"EXERCISE:{exercise.authority_exercise_id}",
        capacity=1,
        window_id=None,
        disposition_rule_id="NORM-PAY-001:usage:v1",
    )
    register_usage_policy(policy)
    reservation_id = f"USAGE-RES:{attempt.execution_attempt_id}"
    reserve_authority_usage(
        reservation_id=reservation_id,
        usage_policy_id=policy.usage_policy_id,
        authority_exercise_id=exercise.authority_exercise_id,
        execution_attempt_id=attempt.execution_attempt_id,
        amount_or_units=1,
    )

    determination, constraint = issue_authorised_execution_constraint(
        context=context,
        scope=scope,
        operation=operation,
        binding=binding,
        resolved_at=resolved_at,
        authority_exercise=exercise,
        execution_attempt=attempt,
    )
    return PreparedAuthorityExecution(
        operation=operation,
        determination=determination,
        constraint=constraint,
        usage_reservation_id=reservation_id,
        usage_policy_id=policy.usage_policy_id,
    )


def final_bind_payment(
    req,
    prepared: PreparedAuthorityExecution,
    *,
    bind_at: datetime,
) -> FinalBindResult:
    return revalidate_at_final_bind(
        req,
        original_operation=prepared.operation,
        determination=prepared.determination,
        constraint=prepared.constraint,
        bind_at=bind_at,
    )
