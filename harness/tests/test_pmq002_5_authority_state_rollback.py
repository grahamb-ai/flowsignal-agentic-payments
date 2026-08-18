"""PMQ-002.5 failure-first authority-state rollback challenge.

Frozen proposition:
Once authority state version N has been superseded, the represented authority
state MUST NOT be able to move backwards to N such that an old permit regains
standing and forms the represented protected consequence.
"""

from pathlib import Path

from app.engines import authority_store
from app.engines.authority_store import advance_authority_state_version, get_authority_state_version
from app.engines.execution_gateway import ExecutionAttempt, action_binding_hash, validate_execution
from app.engines.financial_runtime import evaluate_financial
from app.engines.protected_consequence import execute_protected_consequence
from harness.runner import load_scenario


def _permit_at_current_state():
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


def test_pmq002_5_superseded_authority_state_cannot_be_resurrected(monkeypatch, tmp_path):
    monkeypatch.setenv(
        "FLOWSIGNAL_PERMIT_CONSUMPTION_STORE",
        str(tmp_path / "permit-consumption.sqlite3"),
    )

    permit, binding = _permit_at_current_state()
    original_version = get_authority_state_version()
    assert permit.authority_state_version == original_version

    newer_version = advance_authority_state_version()
    assert newer_version == original_version + 1

    # First prove the old permit lost standing after the newer state committed.
    stale_result = execute_protected_consequence(
        permit=permit,
        attempted_action_binding_hash=binding,
    )
    assert stale_result == "DENIED_AUTHORITY_STATE_STALE"

    # Adversarial rollback attempt against the represented authority store.
    # This deliberately uses the module's currently reachable state surface;
    # if that can move backwards, the frozen proposition has been falsified.
    authority_store._AUTHORITY_STATE_VERSION = original_version

    assert get_authority_state_version() != original_version, (
        "PMQ-002.5 FAILURE: the represented authority store accepted rollback "
        "to an already-superseded authority-state version"
    )

    replay_after_rollback = execute_protected_consequence(
        permit=permit,
        attempted_action_binding_hash=binding,
    )
    assert replay_after_rollback != "CONSEQUENCE_FORMED", (
        "PMQ-002.5 FAILURE: an old permit regained standing after authority-state "
        "rollback and formed the represented consequence"
    )
