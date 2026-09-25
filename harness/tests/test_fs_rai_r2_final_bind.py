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
from app.engines.institutional_authority import (
    advance_authority_fence,
    issue_authority_fence_transition_capability_for_test,
)
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
            )

    attempt = create_execution_attempt(
            authority_exercise_id=exercise.authority_exercise_id,
            route_id="R1",
            executor_id="PAYMENT-EXECUTOR-1",
            created_at=req.requested_execution_time,
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
    advance_authority_fence(
        transition_capability=issue_authority_fence_transition_capability_for_test(
            "institution-001:MANDATE-TREASURY-001"
        ),
    )
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


def test_r6_caller_cannot_self_register_forged_rai_binding_to_form_protected_consequence():
    """R6 failure-first route closure: registry write reachability is not RAI provenance.

    A caller reaching low-level reference helpers must not be able to mint a
    separately constructed permit, self-register matching RAI-looking fields,
    and thereby make the directly callable protected executor form the protected
    consequence without the successful integrated final-bind/mint chain.
    """
    from datetime import datetime, timedelta, timezone

    from app.engines.authority_store import get_authority_state_version
    from app.engines.execution_gateway import ExecutionAttempt, action_binding_hash
    from app.engines.institutional_authority import get_authority_snapshot
    from app.engines.permit_authority import _GATEWAY_MINT_CAPABILITY, issue_execution_permit
    from app.engines.protected_consequence import execute_protected_consequence
    from app.engines.rai_execution_registry import register_rai_execution_binding

    req = load_scenario(SCENARIO, rebase_to_now=False)
    snapshot = get_authority_snapshot(req.mandate_id)
    assert snapshot is not None

    attempted_hash = action_binding_hash(
        ExecutionAttempt(
            actor_id=req.actor_id,
            principal_id=req.principal_id,
            action=req.action,
            target=req.target,
            amount=req.amount,
            currency=req.currency,
            source_account=req.source_account,
            beneficiary=req.beneficiary,
            beneficiary_account_reference=req.beneficiary_account_reference,
            purpose=req.purpose,
            mandate_id=req.mandate_id,
            attempted_at=datetime.now(timezone.utc),
        )
    )

    permit = issue_execution_permit(
        authority_receipt_id="FORGED-R6-RECEIPT",
        action_binding_hash=attempted_hash,
        authority_state_version=get_authority_state_version(),
        authority_snapshot_id=snapshot.snapshot_id,
        authority_subject_principal_id=snapshot.mandate.principal_id,
        authority_subject_mandate_id=snapshot.mandate.mandate_id,
        authority_epoch_id=snapshot.authority_epoch_id,
        authority_fence_scope_key=snapshot.authority_fence_scope_key,
        authority_fence=snapshot.authority_fence,
        authoritative_source_id=snapshot.authoritative_source_id,
        source_competence_root_id=snapshot.source_competence_root_id,
        authority_semantics_version=snapshot.semantics.version,
        authority_semantics_definition_id=snapshot.semantics.definition_id,
        authority_semantics_source_id=snapshot.semantics.source_id,
        valid_until=(datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat(),
        rai_determination_id="FORGED-R6-DETERMINATION",
        rai_constraint_id="FORGED-R6-CONSTRAINT",
        rai_protected_operation_id="FORGED-R6-OPERATION",
        rai_authority_exercise_id="FORGED-R6-EXERCISE",
        rai_execution_attempt_id="FORGED-R6-ATTEMPT",
        mint_capability=_GATEWAY_MINT_CAPABILITY,
    )
    assert permit is not None

    # Public helper reachability must not be sufficient to manufacture the
    # causal RAI provenance required by the executor.
    try:
        register_rai_execution_binding(
            permit_signature=permit.signature,
            determination_id=permit.rai_determination_id,
            constraint_id=permit.rai_constraint_id,
            protected_operation_id=permit.rai_protected_operation_id,
            authority_exercise_id=permit.rai_authority_exercise_id,
            execution_attempt_id=permit.rai_execution_attempt_id,
            action_binding_hash=attempted_hash,
            usage_reservation_id="FORGED-R6-USAGE",
        )
    except ValueError:
        pass

    result = execute_protected_consequence(permit, attempted_hash)
    assert result != "CONSEQUENCE_FORMED", (
        "R6 route closure failure: low-level mint + self-registration formed "
        "the protected consequence without successful RAI final-bind provenance"
    )
    assert result == "DENIED_RAI_EXECUTION_BINDING_REQUIRED"
