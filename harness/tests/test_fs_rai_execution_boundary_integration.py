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


def test_signed_rai_labels_without_registered_final_bind_cannot_form_consequence():
    """Second-order route-closure challenge: labels are not provenance.

    A caller that can reach the low-level permit signer must not be able to make
    an execution capability acceptable merely by supplying plausible RAI IDs.
    """
    from app.engines.authority_store import get_authority_state_version
    from app.engines.institutional_authority import get_authority_snapshot
    from app.engines.permit_authority import _GATEWAY_MINT_CAPABILITY, issue_execution_permit

    req = load_scenario(SCENARIO, rebase_to_now=False)
    now = datetime.now(timezone.utc)
    req = replace(
        req,
        requested_execution_time=now,
        screening_captured_at=now,
        mandate_valid_until=now + timedelta(hours=1),
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
        attempted_at=now,
    )
    attempted_hash = action_binding_hash(attempt)
    snapshot = get_authority_snapshot(req.mandate_id)
    assert snapshot is not None

    permit = issue_execution_permit(
        authority_receipt_id="FORGED-RAI-PROVENANCE",
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
        valid_until=(now + timedelta(seconds=60)).isoformat(),
        rai_determination_id="DET-ATTACKER-SUPPLIED",
        rai_constraint_id="CONSTRAINT-ATTACKER-SUPPLIED",
        rai_protected_operation_id="OP-ATTACKER-SUPPLIED",
        rai_authority_exercise_id="EX-ATTACKER-SUPPLIED",
        rai_execution_attempt_id="ATT-ATTACKER-SUPPLIED",
        mint_capability=_GATEWAY_MINT_CAPABILITY,
    )
    assert permit is not None
    assert permit.rai_determination_id is not None

    outcome = execute_protected_consequence(
        permit=permit,
        attempted_action_binding_hash=attempted_hash,
    )
    assert outcome == "DENIED_RAI_EXECUTION_BINDING_REQUIRED"


def test_registered_rai_capability_cannot_be_rebound_to_different_action():
    """Third-order correspondence challenge against a genuine registered permit."""
    req = load_scenario(SCENARIO, rebase_to_now=False)
    prepared = prepare_payment_execution(
        req, route_id="R1", executor_id="PAYMENT-EXECUTOR-1",
        resolved_at=req.requested_execution_time,
    )
    permit = mint_rai_bound_execution_permit(
        req, prepared, bind_at=req.requested_execution_time
    )
    assert permit is not None

    substituted = _attempt(req)
    substituted.amount = substituted.amount + 1
    substituted_hash = action_binding_hash(substituted)
    assert substituted_hash != permit.action_binding_hash

    outcome = execute_protected_consequence(
        permit=permit,
        attempted_action_binding_hash=substituted_hash,
    )
    assert outcome == "DENIED_ACTION_BINDING_MISMATCH"


def test_registered_rai_capability_signature_copy_with_changed_lineage_is_rejected():
    """Third-order challenge: genuine registry entry cannot bless altered lineage."""
    from dataclasses import replace as dc_replace

    req = load_scenario(SCENARIO, rebase_to_now=False)
    prepared = prepare_payment_execution(
        req, route_id="R1", executor_id="PAYMENT-EXECUTOR-1",
        resolved_at=req.requested_execution_time,
    )
    permit = mint_rai_bound_execution_permit(
        req, prepared, bind_at=req.requested_execution_time
    )
    assert permit is not None

    altered = dc_replace(
        permit,
        rai_execution_attempt_id="ATT-SUBSTITUTED-AFTER-MINT",
    )
    outcome = execute_protected_consequence(
        permit=altered,
        attempted_action_binding_hash=permit.action_binding_hash,
    )
    assert outcome == "DENIED_INVALID_EXECUTION_PERMIT"


def test_genuine_registered_rai_capability_is_single_use_at_commit_boundary():
    """Fourth-order challenge: a genuine capability cannot be replayed."""
    req = load_scenario(SCENARIO, rebase_to_now=False)
    prepared = prepare_payment_execution(
        req, route_id="R1", executor_id="PAYMENT-EXECUTOR-1",
        resolved_at=req.requested_execution_time,
    )
    permit = mint_rai_bound_execution_permit(
        req, prepared, bind_at=req.requested_execution_time
    )
    assert permit is not None
    attempted_hash = action_binding_hash(_attempt(req))

    first = execute_protected_consequence(
        permit=permit,
        attempted_action_binding_hash=attempted_hash,
    )
    second = execute_protected_consequence(
        permit=permit,
        attempted_action_binding_hash=attempted_hash,
    )

    assert first == "CONSEQUENCE_FORMED"
    assert second == "DENIED_EXECUTION_PERMIT_REPLAY"


def test_protected_consequence_cannot_form_if_prepared_usage_reservation_is_not_currently_reserved():
    """Failure-first: usage reservation must be a causal commitment prerequisite.

    A genuine RAI final-bind/permit must not remain sufficient if the authority
    usage reservation that justified this exact attempt has already been
    dispositioned before protected consequence formation.
    """
    from app.engines.authority_usage import release_authority_usage

    req = load_scenario(SCENARIO, rebase_to_now=False)
    prepared = prepare_payment_execution(
        req, route_id="R1", executor_id="PAYMENT-EXECUTOR-1",
        resolved_at=req.requested_execution_time,
    )
    permit = mint_rai_bound_execution_permit(
        req, prepared, bind_at=req.requested_execution_time
    )
    assert permit is not None

    release_authority_usage(
        prepared.usage_reservation_id,
        evidence_ids=("COMPETENT-NONFORMATION-BEFORE-COMMIT",),
    )

    outcome = execute_protected_consequence(
        permit=permit,
        attempted_action_binding_hash=action_binding_hash(_attempt(req)),
    )
    assert outcome != "CONSEQUENCE_FORMED", (
        "USAGE CAUSALITY FAILURE: protected consequence formed even though the "
        "exact prepared authority-usage reservation was no longer RESERVED"
    )


def test_successful_protected_commitment_consumes_the_exact_authority_usage_reservation():
    """Failure-first: commitment must disposition the exact supporting usage."""
    from app.engines.authority_usage import get_usage_reservation

    req = load_scenario(SCENARIO, rebase_to_now=False)
    prepared = prepare_payment_execution(
        req, route_id="R1", executor_id="PAYMENT-EXECUTOR-1",
        resolved_at=req.requested_execution_time,
    )
    permit = mint_rai_bound_execution_permit(
        req, prepared, bind_at=req.requested_execution_time
    )
    assert permit is not None
    before = get_usage_reservation(prepared.usage_reservation_id)
    assert before is not None and before.state.value == "reserved"

    outcome = execute_protected_consequence(
        permit=permit,
        attempted_action_binding_hash=action_binding_hash(_attempt(req)),
    )
    assert outcome == "CONSEQUENCE_FORMED"

    after = get_usage_reservation(prepared.usage_reservation_id)
    assert after is not None
    assert after.state.value == "consumed", (
        "USAGE DISPOSITION FAILURE: protected commitment formed but the exact "
        "supporting authority-usage reservation remained unconsumed"
    )


def test_failure_after_unresolved_commitment_entry_does_not_leave_usage_merely_reserved():
    """Failure-first: uncertainty after commitment entry must quarantine usage.

    Once the protected boundary has durably consumed the permit and opened an
    unresolved outcome, an exception before represented formation must not leave
    the exact authority usage reservation looking freely RESERVED.
    """
    import pytest
    from app.engines.authority_usage import get_usage_reservation

    req = load_scenario(SCENARIO, rebase_to_now=False)
    prepared = prepare_payment_execution(
        req, route_id="R1", executor_id="PAYMENT-EXECUTOR-1",
        resolved_at=req.requested_execution_time,
    )
    permit = mint_rai_bound_execution_permit(
        req, prepared, bind_at=req.requested_execution_time
    )
    assert permit is not None

    def fail_inside_commitment_interval():
        raise RuntimeError("synthetic failure after unresolved commitment entry")

    with pytest.raises(RuntimeError, match="synthetic failure"):
        execute_protected_consequence(
            permit=permit,
            attempted_action_binding_hash=action_binding_hash(_attempt(req)),
            before_formation_hook=fail_inside_commitment_interval,
        )

    after = get_usage_reservation(prepared.usage_reservation_id)
    assert after is not None
    assert after.state.value == "quarantined", (
        "USAGE UNCERTAINTY FAILURE: commitment interval was entered and execution "
        "failed before represented formation, but the exact authority usage "
        "reservation remained available as RESERVED rather than QUARANTINED"
    )


def test_commitment_interval_failure_must_not_claim_competent_nonformation():
    """Failure-first: local interruption is not proof of consequence non-formation.

    After durable permit consumption and unresolved outcome creation, failure of
    the local formation hook establishes uncertainty unless competent external
    evidence proves non-formation. The stored outcome must not overclaim.
    """
    import pytest
    from app.engines.consequence_outcome_store import get_consequence_outcome

    req = load_scenario(SCENARIO, rebase_to_now=False)
    prepared = prepare_payment_execution(
        req, route_id="R1", executor_id="PAYMENT-EXECUTOR-1",
        resolved_at=req.requested_execution_time,
    )
    permit = mint_rai_bound_execution_permit(
        req, prepared, bind_at=req.requested_execution_time
    )
    assert permit is not None
    attempted_hash = action_binding_hash(_attempt(req))

    def fail_inside_commitment_interval():
        raise RuntimeError("synthetic unresolved commitment interval failure")

    with pytest.raises(RuntimeError, match="synthetic unresolved"):
        execute_protected_consequence(
            permit=permit,
            attempted_action_binding_hash=attempted_hash,
            before_formation_hook=fail_inside_commitment_interval,
        )

    stored = get_consequence_outcome(permit.signature, attempted_hash)
    assert stored is not None
    assert stored.outcome == "CONSEQUENCE_OUTCOME_UNRESOLVED", (
        "OUTCOME EVIDENCE FAILURE: local commitment-interval interruption was "
        "recorded as competent non-formation rather than preserved as unresolved"
    )


def test_quarantined_usage_cannot_be_released_by_unstructured_evidence_id_alone():
    """Failure-first: release requires competent outcome evidence, not a string.

    A quarantined reservation represents unresolved post-commit consequence
    state. An arbitrary caller-supplied evidence identifier must not be enough
    to turn that uncertainty into reusable authority capacity.
    """
    import pytest
    from app.engines.authority_usage import (
        get_usage_reservation,
        quarantine_authority_usage,
        release_authority_usage,
    )

    req = load_scenario(SCENARIO, rebase_to_now=False)
    prepared = prepare_payment_execution(
        req, route_id="R1", executor_id="PAYMENT-EXECUTOR-1",
        resolved_at=req.requested_execution_time,
    )

    quarantine_authority_usage(
        prepared.usage_reservation_id,
        evidence_ids=("SYNTHETIC-UNRESOLVED-EVIDENCE",),
    )
    quarantined = get_usage_reservation(prepared.usage_reservation_id)
    assert quarantined is not None
    assert quarantined.state.value == "quarantined"

    with pytest.raises(ValueError):
        release_authority_usage(
            prepared.usage_reservation_id,
            evidence_ids=("CALLER-SAYS-NOT-FORMED",),
        )

    after = get_usage_reservation(prepared.usage_reservation_id)
    assert after is not None
    assert after.state.value == "quarantined"


def test_quarantined_usage_can_be_released_only_by_competent_nonformation_resolution():
    """Positive control: quarantine must be resolvable to RELEASED by competent non-formation evidence."""
    from app.engines.authority_usage import (
        get_usage_reservation,
        quarantine_authority_usage,
        resolve_quarantined_authority_usage,
    )

    req = load_scenario(SCENARIO, rebase_to_now=False)
    prepared = prepare_payment_execution(
        req, route_id="R1", executor_id="PAYMENT-EXECUTOR-1",
        resolved_at=req.requested_execution_time,
    )
    quarantine_authority_usage(
        prepared.usage_reservation_id,
        evidence_ids=("UNRESOLVED:LOCAL-INTERRUPTION",),
    )

    resolve_quarantined_authority_usage(
        prepared.usage_reservation_id,
        resolution="NON_FORMATION",
        evidence_ids=("COMPETENT-NONFORMATION:EXACT-EXECUTION",),
    )

    after = get_usage_reservation(prepared.usage_reservation_id)
    assert after is not None
    assert after.state.value == "released"


def test_quarantined_usage_can_be_consumed_only_by_competent_formation_resolution():
    """Positive control: quarantine must be resolvable to CONSUMED by competent formation evidence."""
    from app.engines.authority_usage import (
        get_usage_reservation,
        quarantine_authority_usage,
        resolve_quarantined_authority_usage,
    )

    req = load_scenario(SCENARIO, rebase_to_now=False)
    prepared = prepare_payment_execution(
        req, route_id="R1", executor_id="PAYMENT-EXECUTOR-1",
        resolved_at=req.requested_execution_time,
    )
    quarantine_authority_usage(
        prepared.usage_reservation_id,
        evidence_ids=("UNRESOLVED:LOCAL-INTERRUPTION",),
    )

    resolve_quarantined_authority_usage(
        prepared.usage_reservation_id,
        resolution="FORMATION",
        evidence_ids=("COMPETENT-FORMATION:EXACT-EXECUTION",),
    )

    after = get_usage_reservation(prepared.usage_reservation_id)
    assert after is not None
    assert after.state.value == "consumed"
