"""PMQ-002.3 failure-first concurrent authority revocation challenge.

Frozen proposition:
Once a newer authority state has committed, a permit bound to the previous
state version MUST NOT subsequently form the represented protected consequence.

The test also verifies ordering at the represented atomic boundary: if execution
owns the authority-state guard first, a concurrent revocation cannot commit
inside the final standing-to-consequence interval.
"""

from pathlib import Path
from threading import Event, Thread

from app.engines.authority_store import advance_authority_state_version, get_authority_state_version
from app.engines.execution_gateway import ExecutionAttempt, action_binding_hash, validate_execution
from app.engines.financial_runtime import evaluate_financial
from app.engines.protected_consequence import execute_protected_consequence
from harness.runner import load_scenario


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
    return gateway.execution_permit, action_binding_hash(attempt)


def test_pmq002_3_committed_revocation_before_final_boundary_denies_old_permit():
    permit, binding = _permitted_case()
    version_before = get_authority_state_version()

    revocation_committed = Event()
    release_execution = Event()
    result = {}

    def revoke():
        result["new_version"] = advance_authority_state_version()
        revocation_committed.set()

    def execute_after_commit():
        assert revocation_committed.wait(timeout=2.0)
        assert release_execution.wait(timeout=2.0)
        result["execution"] = execute_protected_consequence(
            permit=permit,
            attempted_action_binding_hash=binding,
        )

    execution_thread = Thread(target=execute_after_commit)
    revocation_thread = Thread(target=revoke)
    execution_thread.start()
    revocation_thread.start()

    assert revocation_committed.wait(timeout=2.0)
    assert result["new_version"] == version_before + 1
    release_execution.set()

    execution_thread.join(timeout=2.0)
    revocation_thread.join(timeout=2.0)

    assert result["execution"] == "DENIED_AUTHORITY_STATE_STALE", (
        "PMQ-002.3 FAILURE: consequence was not denied after a newer authority "
        "state had committed before the final protected execution boundary"
    )


def test_pmq002_3_revocation_cannot_commit_inside_final_standing_to_formation_interval():
    permit, binding = _permitted_case()
    version_before = get_authority_state_version()

    final_boundary_owned = Event()
    release_formation = Event()
    revocation_started = Event()
    revocation_committed = Event()
    result = {}

    def hold_inside_boundary():
        final_boundary_owned.set()
        assert release_formation.wait(timeout=2.0)

    def execute():
        result["execution"] = execute_protected_consequence(
            permit=permit,
            attempted_action_binding_hash=binding,
            before_formation_hook=hold_inside_boundary,
        )

    def revoke():
        revocation_started.set()
        result["new_version"] = advance_authority_state_version()
        revocation_committed.set()

    execution_thread = Thread(target=execute)
    execution_thread.start()
    assert final_boundary_owned.wait(timeout=2.0)

    revocation_thread = Thread(target=revoke)
    revocation_thread.start()
    assert revocation_started.wait(timeout=2.0)

    assert not revocation_committed.wait(timeout=0.10), (
        "PMQ-002.3 FAILURE: authority revocation committed inside the final "
        "standing-to-consequence protected interval"
    )

    release_formation.set()
    execution_thread.join(timeout=2.0)
    revocation_thread.join(timeout=2.0)

    assert result["execution"] == "CONSEQUENCE_FORMED"
    assert revocation_committed.is_set()
    assert result["new_version"] == version_before + 1
