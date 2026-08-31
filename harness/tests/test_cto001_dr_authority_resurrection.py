"""CTO-001 disaster-recovery authority resurrection challenge.

Failure-first qualification against the public reference-MVP.

This is a represented local-state rollback/restart challenge, not a claim of
cloud-provider, database-HA, multi-region or production disaster-recovery
validation.

Invariant under test:
    Restoration/restart of older local authority state must not be sufficient
    to make superseded authority exercisable again.
"""

from importlib import reload
from pathlib import Path

from app.engines import authority_store
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


def test_cto001_restored_old_authority_state_cannot_resurrect_superseded_authority(tmp_path, monkeypatch):
    """An old local authority snapshot/restart must not revive an old permit."""

    # Isolate the consequence-side durable stores so the challenge measures
    # authority-state rollback rather than replay state from another test.
    monkeypatch.setenv(
        "FLOWSIGNAL_PERMIT_CONSUMPTION_STORE",
        str(tmp_path / "permit-consumption.sqlite3"),
    )
    monkeypatch.setenv(
        "FLOWSIGNAL_CONSEQUENCE_OUTCOME_STORE",
        str(tmp_path / "consequence-outcomes.sqlite3"),
    )
    monkeypatch.setenv(
        "FLOWSIGNAL_ROLLBACK_ANCHOR_STORE",
        str(tmp_path / "rollback-anchor.sqlite3"),
    )

    # T0: authority state N is current and an action obtains a valid permit.
    permit, binding = _permit_at_current_state()
    state_n = permit.authority_state_version
    assert authority_store.get_authority_state_version() == state_n

    # T1: institutional authority changes/revokes; state advances to N+1.
    state_n_plus_1 = authority_store.advance_authority_state_version()
    assert state_n_plus_1 > state_n

    # Positive control: before rollback/restart, the old permit is stale.
    denied_before_restore = execute_protected_consequence(
        permit=permit,
        attempted_action_binding_hash=binding,
    )
    assert denied_before_restore == "DENIED_AUTHORITY_STATE_STALE"

    # T2: represent disaster recovery restoring/restarting an older local
    # authority-state image. In the current reference implementation the state
    # is process-local and initialises from a fixed value on module load.
    reload(authority_store)

    assert authority_store.get_authority_state_version() == state_n, (
        "Challenge precondition not met: represented restore/restart did not "
        "return local authority state to the older version"
    )

    # T3: re-present the exact old action/permit after the older state returns.
    after_restore = execute_protected_consequence(
        permit=permit,
        attempted_action_binding_hash=binding,
    )

    assert after_restore != "CONSEQUENCE_FORMED", (
        "CTO-001 FAILURE: restoring/restarting older local authority state "
        "made superseded authority appear current again and allowed the old "
        "permit/action binding to form a represented consequence"
    )
