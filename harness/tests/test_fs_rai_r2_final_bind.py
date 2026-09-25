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
            final_bind_provenance_id="FORGED-R6-FINAL-BIND-PROVENANCE",
        )
    except ValueError:
        pass

    result = execute_protected_consequence(permit, attempted_hash)
    assert result != "CONSEQUENCE_FORMED", (
        "R6 route closure failure: low-level mint + self-registration formed "
        "the protected consequence without successful RAI final-bind provenance"
    )
    assert result == "DENIED_RAI_EXECUTION_BINDING_REQUIRED"


def test_r6_possession_of_registry_capability_cannot_manufacture_rai_provenance():
    """R6 second-order attack: registry capability possession is not causal provenance.

    Even a caller that can reach both low-level reference capabilities must not
    turn attacker-chosen RAI identifiers into execution authority merely by
    minting a permit and inserting a matching registry row.
    """
    from datetime import datetime, timedelta, timezone

    from app.engines.authority_store import get_authority_state_version
    from app.engines.execution_gateway import ExecutionAttempt, action_binding_hash
    from app.engines.institutional_authority import get_authority_snapshot
    from app.engines.permit_authority import _GATEWAY_MINT_CAPABILITY, issue_execution_permit
    from app.engines.protected_consequence import execute_protected_consequence
    from app.engines.rai_execution_registry import (
        _RAI_BINDING_REGISTRATION_CAPABILITY,
        register_rai_execution_binding,
    )

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
        authority_receipt_id="FORGED-R6-CAP-RECEIPT",
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
        rai_determination_id="FORGED-R6-CAP-DETERMINATION",
        rai_constraint_id="FORGED-R6-CAP-CONSTRAINT",
        rai_protected_operation_id="FORGED-R6-CAP-OPERATION",
        rai_authority_exercise_id="FORGED-R6-CAP-EXERCISE",
        rai_execution_attempt_id="FORGED-R6-CAP-ATTEMPT",
        mint_capability=_GATEWAY_MINT_CAPABILITY,
    )
    assert permit is not None

    register_rai_execution_binding(
        permit_signature=permit.signature,
        determination_id=permit.rai_determination_id,
        constraint_id=permit.rai_constraint_id,
        protected_operation_id=permit.rai_protected_operation_id,
        authority_exercise_id=permit.rai_authority_exercise_id,
        execution_attempt_id=permit.rai_execution_attempt_id,
        action_binding_hash=attempted_hash,
        usage_reservation_id="FORGED-R6-CAP-USAGE",
        final_bind_provenance_id="FORGED-R6-CAP-FINAL-BIND-PROVENANCE",
        registration_capability=_RAI_BINDING_REGISTRATION_CAPABILITY,
    )

    result = execute_protected_consequence(permit, attempted_hash)
    assert result != "CONSEQUENCE_FORMED", (
        "R6 route closure failure: possession of low-level mint and registry "
        "capabilities manufactured executable RAI provenance"
    )


def test_r6_low_level_capabilities_plus_forged_usage_cannot_form_consequence():
    """R6 third-order attack: writable usage state must not complete forged provenance.

    The attacker is given the reference mint, RAI-registration and usage-policy
    registration capabilities, then constructs a matching RESERVED usage record.
    Protected commitment must still require a causally established RAI chain.
    """
    from datetime import datetime, timedelta, timezone
    from decimal import Decimal

    from app.engines.authority_domain import AuthorityUsageMode, AuthorityUsagePolicy
    from app.engines.authority_store import get_authority_state_version
    from app.engines.authority_usage import (
        _POLICY_REGISTRATION_CAPABILITY,
        register_usage_policy,
        reserve_authority_usage,
    )
    from app.engines.execution_gateway import ExecutionAttempt, action_binding_hash
    from app.engines.institutional_authority import get_authority_snapshot
    from app.engines.permit_authority import _GATEWAY_MINT_CAPABILITY, issue_execution_permit
    from app.engines.protected_consequence import execute_protected_consequence
    from app.engines.rai_execution_registry import (
        _RAI_BINDING_REGISTRATION_CAPABILITY,
        register_rai_execution_binding,
    )

    req = load_scenario(SCENARIO, rebase_to_now=False)
    snapshot = get_authority_snapshot(req.mandate_id)
    assert snapshot is not None

    attempted_hash = action_binding_hash(
        ExecutionAttempt(
            actor_id=req.actor_id, principal_id=req.principal_id, action=req.action,
            target=req.target, amount=req.amount, currency=req.currency,
            source_account=req.source_account, beneficiary=req.beneficiary,
            beneficiary_account_reference=req.beneficiary_account_reference,
            purpose=req.purpose, mandate_id=req.mandate_id,
            attempted_at=datetime.now(timezone.utc),
        )
    )

    exercise_id = "FORGED-R6-USAGE-EXERCISE"
    attempt_id = "FORGED-R6-USAGE-ATTEMPT"
    reservation_id = "FORGED-R6-USAGE-RESERVATION"
    policy_id = "FORGED-R6-USAGE-POLICY"

    register_usage_policy(
        AuthorityUsagePolicy(
            usage_policy_id=policy_id,
            authority_scope_id="FORGED-R6-SCOPE",
            mode=AuthorityUsageMode.AGGREGATE,
            scope_key="FORGED-R6-USAGE-SCOPE",
            capacity=Decimal("1000000"),
            window_id=snapshot.usage_window_id,
            disposition_rule_id="FORGED-R6-RULE",
        ),
        registration_capability=_POLICY_REGISTRATION_CAPABILITY,
    )
    reserve_authority_usage(
        reservation_id=reservation_id,
        usage_policy_id=policy_id,
        authority_exercise_id=exercise_id,
        execution_attempt_id=attempt_id,
        amount_or_units=req.amount,
    )

    permit = issue_execution_permit(
        authority_receipt_id="FORGED-R6-USAGE-RECEIPT",
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
        rai_determination_id="FORGED-R6-USAGE-DETERMINATION",
        rai_constraint_id="FORGED-R6-USAGE-CONSTRAINT",
        rai_protected_operation_id="FORGED-R6-USAGE-OPERATION",
        rai_authority_exercise_id=exercise_id,
        rai_execution_attempt_id=attempt_id,
        mint_capability=_GATEWAY_MINT_CAPABILITY,
    )
    assert permit is not None

    register_rai_execution_binding(
        permit_signature=permit.signature,
        determination_id=permit.rai_determination_id,
        constraint_id=permit.rai_constraint_id,
        protected_operation_id=permit.rai_protected_operation_id,
        authority_exercise_id=exercise_id,
        execution_attempt_id=attempt_id,
        action_binding_hash=attempted_hash,
        usage_reservation_id=reservation_id,
        final_bind_provenance_id="FORGED-R6-FINAL-BIND-PROVENANCE",
        registration_capability=_RAI_BINDING_REGISTRATION_CAPABILITY,
    )

    result = execute_protected_consequence(permit, attempted_hash)
    assert result != "CONSEQUENCE_FORMED", (
        "R6 route closure failure: low-level capabilities plus caller-manufactured "
        "usage state formed the protected consequence without causal RAI final-bind"
    )
    assert result == "DENIED_FINAL_BIND_PROVENANCE_REQUIRED"


def test_r6_valid_final_bind_provenance_cannot_be_reused_for_a_second_permit_signature():
    """R6 fourth-order failure-first: valid provenance must not be transferable to a second permit.

    Start with a genuinely successful integrated final-bind/mint chain. A caller
    that can reach the low-level mint and registry capabilities then mints a
    second, separately signed permit carrying the same legitimate RAI lineage
    and registers it against the first permit's genuine final-bind provenance.
    Protected commitment must not treat provenance established for one mint as
    reusable authority for another permit signature.
    """
    from datetime import datetime, timedelta, timezone

    from app.engines.authority_store import get_authority_state_version
    from app.engines.execution_gateway import ExecutionAttempt, action_binding_hash
    from app.engines.institutional_authority import get_authority_snapshot
    from app.engines.permit_authority import _GATEWAY_MINT_CAPABILITY, issue_execution_permit
    from app.engines.protected_consequence import execute_protected_consequence
    from app.engines.rai_execution_registry import (
        _RAI_BINDING_REGISTRATION_CAPABILITY,
        get_rai_execution_binding,
        register_rai_execution_binding,
    )
    from app.engines.runtime_authority_payment import (
        mint_rai_bound_execution_permit,
        prepare_payment_execution,
    )

    req = load_scenario(SCENARIO, rebase_to_now=False)
    prepared = prepare_payment_execution(
        req,
        route_id="R1",
        executor_id="PAYMENT-EXECUTOR-1",
        resolved_at=req.requested_execution_time,
    )
    original_permit = mint_rai_bound_execution_permit(
        req,
        prepared,
        bind_at=req.requested_execution_time,
    )
    assert original_permit is not None

    original_binding = get_rai_execution_binding(original_permit.signature)
    assert original_binding is not None

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
    assert attempted_hash == original_binding.action_binding_hash

    transplanted_permit = issue_execution_permit(
        authority_receipt_id="R6-TRANSPLANTED-PROVENANCE-SECOND-MINT",
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
        rai_determination_id=original_binding.determination_id,
        rai_constraint_id=original_binding.constraint_id,
        rai_protected_operation_id=original_binding.protected_operation_id,
        rai_authority_exercise_id=original_binding.authority_exercise_id,
        rai_execution_attempt_id=original_binding.execution_attempt_id,
        mint_capability=_GATEWAY_MINT_CAPABILITY,
    )
    assert transplanted_permit is not None
    assert transplanted_permit.signature != original_permit.signature

    register_rai_execution_binding(
        permit_signature=transplanted_permit.signature,
        determination_id=original_binding.determination_id,
        constraint_id=original_binding.constraint_id,
        protected_operation_id=original_binding.protected_operation_id,
        authority_exercise_id=original_binding.authority_exercise_id,
        execution_attempt_id=original_binding.execution_attempt_id,
        action_binding_hash=original_binding.action_binding_hash,
        usage_reservation_id=original_binding.usage_reservation_id,
        final_bind_provenance_id=original_binding.final_bind_provenance_id,
        registration_capability=_RAI_BINDING_REGISTRATION_CAPABILITY,
    )

    result = execute_protected_consequence(transplanted_permit, attempted_hash)
    assert result != "CONSEQUENCE_FORMED", (
        "R6 provenance transfer failure: one genuine successful final-bind "
        "provenance authorised a separately minted permit signature"
    )


def test_r6_valid_final_bind_provenance_cannot_be_transplanted_to_second_chain():
    """R6 next-order: genuine final-bind provenance is chain-specific, not bearer authority.

    Establish two independently valid prepared chains for the same proposed payment.
    Then register chain B's permit against chain B's identifiers while deliberately
    transplanting chain A's genuine final-bind provenance identifier. Protected
    commitment must reject the cross-chain provenance mismatch.
    """
    from datetime import datetime, timezone

    from app.engines.execution_gateway import ExecutionAttempt, action_binding_hash
    from app.engines.final_bind_provenance import (
        _FINAL_BIND_PROVENANCE_ISSUANCE_CAPABILITY,
        establish_final_bind_provenance,
    )
    from app.engines.protected_consequence import execute_protected_consequence
    from app.engines.rai_execution_registry import (
        _RAI_BINDING_REGISTRATION_CAPABILITY,
        register_rai_execution_binding,
    )
    from app.engines.runtime_authority_payment import (
        mint_rai_bound_execution_permit,
        prepare_payment_execution,
    )

    from dataclasses import replace
    from decimal import Decimal

    req = replace(
        load_scenario(SCENARIO, rebase_to_now=False),
        amount=Decimal("100000.00"),
        institutional_operation_id="R6-PROVENANCE-TRANSPLANT",
    )

    prepared_a = prepare_payment_execution(
        req, route_id="R1", executor_id="PAYMENT-EXECUTOR-1",
        resolved_at=req.requested_execution_time,
    )
    prepared_b = prepare_payment_execution(
        req, route_id="R1", executor_id="PAYMENT-EXECUTOR-1",
        resolved_at=req.requested_execution_time,
    )

    permit_b = mint_rai_bound_execution_permit(
        req, prepared_b, bind_at=req.requested_execution_time,
    )
    assert permit_b is not None

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

    provenance_a = establish_final_bind_provenance(
        determination_id=prepared_a.determination.determination_id,
        constraint_id=prepared_a.constraint.constraint_id,
        protected_operation_id=prepared_a.operation.operation_id,
        authority_exercise_id=prepared_a.determination.authority_exercise_id,
        execution_attempt_id=prepared_a.determination.execution_attempt_id,
        action_binding_hash=attempted_hash,
        usage_reservation_id=prepared_a.usage_reservation_id,
        permit_signature="CHAIN-A-PROVENANCE-ORIGIN",
        issuance_capability=_FINAL_BIND_PROVENANCE_ISSUANCE_CAPABILITY,
    )

    # Replace B's legitimate registry row with an internally consistent B row
    # carrying A's genuine provenance identifier. The provenance is real, but
    # belongs to a different causal chain.
    register_rai_execution_binding(
        permit_signature=permit_b.signature,
        determination_id=prepared_b.determination.determination_id,
        constraint_id=prepared_b.constraint.constraint_id,
        protected_operation_id=prepared_b.operation.operation_id,
        authority_exercise_id=prepared_b.determination.authority_exercise_id,
        execution_attempt_id=prepared_b.determination.execution_attempt_id,
        action_binding_hash=attempted_hash,
        usage_reservation_id=prepared_b.usage_reservation_id,
        final_bind_provenance_id=provenance_a.provenance_id,
        registration_capability=_RAI_BINDING_REGISTRATION_CAPABILITY,
    )

    result = execute_protected_consequence(permit_b, attempted_hash)
    assert result != "CONSEQUENCE_FORMED", (
        "R6 provenance transplant failure: genuine final-bind provenance from "
        "one chain authorised protected commitment on a different chain"
    )
    assert result == "DENIED_FINAL_BIND_PROVENANCE_REQUIRED"
