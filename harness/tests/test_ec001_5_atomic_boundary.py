from pathlib import Path
from threading import Event, Thread

from harness.runner import load_scenario
from app.engines.financial_runtime import evaluate_financial
from app.engines.execution_gateway import ExecutionAttempt, action_binding_hash, validate_execution
from app.engines.authority_store import advance_authority_state_version, get_authority_state_version
from app.engines.protected_consequence import execute_protected_consequence


def _permitted_case():
    req = load_scenario(Path("harness/scenarios/AP-001_allow.json"))
    response, receipt = evaluate_financial(req)
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
        attempted_at=req.requested_execution_time,
    )
    gateway = validate_execution(receipt, attempt)
    assert gateway.status == "PERMITTED"
    assert gateway.execution_permit is not None
    return gateway.execution_permit, attempt


def test_ec001_5_state_change_cannot_commit_inside_final_check_to_formation_interval():
    permit, attempt = _permitted_case()
    version_before = get_authority_state_version()

    final_check_reached = Event()
    release_formation = Event()
    advance_started = Event()
    advance_finished = Event()
    result = {}

    def hold_inside_atomic_boundary():
        final_check_reached.set()
        assert release_formation.wait(timeout=2.0)

    def execute():
        result["execution"] = execute_protected_consequence(
            permit=permit,
            attempted_action_binding_hash=action_binding_hash(attempt),
            before_formation_hook=hold_inside_atomic_boundary,
        )

    def advance_state():
        advance_started.set()
        result["new_version"] = advance_authority_state_version()
        advance_finished.set()

    execution_thread = Thread(target=execute)
    execution_thread.start()
    assert final_check_reached.wait(timeout=2.0)

    state_thread = Thread(target=advance_state)
    state_thread.start()
    assert advance_started.wait(timeout=2.0)

    # The state change is attempting to commit while execution is deliberately
    # paused after final standing resolution but before consequence formation.
    # It must remain blocked by the shared authority-state guard.
    assert not advance_finished.wait(timeout=0.10)
    assert get_authority_state_version() == version_before

    release_formation.set()
    execution_thread.join(timeout=2.0)
    state_thread.join(timeout=2.0)

    assert result["execution"] == "CONSEQUENCE_FORMED"
    assert advance_finished.is_set()
    assert result["new_version"] == version_before + 1


def test_ec001_5_state_change_committed_before_final_boundary_denies_stale_permit():
    permit, attempt = _permitted_case()
    advance_authority_state_version()

    result = execute_protected_consequence(
        permit=permit,
        attempted_action_binding_hash=action_binding_hash(attempt),
    )

    assert result == "DENIED_AUTHORITY_STATE_STALE"
