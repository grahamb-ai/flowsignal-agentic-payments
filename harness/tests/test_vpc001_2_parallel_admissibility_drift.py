"""VPC-001.2 — Parallel Admissibility Drift.

Frozen challenge derived from Vadym Partasyuk's public scenario:
Two independently valid actions are authorised against the same current
state. The first consequence changes the authoritative state before the
second reaches the final protected boundary. The second MUST NOT form on
stale authority.

This test does NOT claim universal multi-bank coordination. It tests the
bounded FlowSignal proposition that, once a materially newer authoritative
state commits, an execution permit bound to the previous state cannot form
its represented protected consequence.
"""

from pathlib import Path
from threading import Event, Thread

from app.engines.authority_store import advance_authority_state_version
from app.engines.execution_gateway import ExecutionAttempt, action_binding_hash, validate_execution
from app.engines.financial_runtime import evaluate_financial
from app.engines.protected_consequence import execute_protected_consequence
from harness.runner import load_scenario


def _fresh_permit():
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


def test_vpc001_2_first_consequence_changes_state_second_stale_permit_cannot_form():
    # Two independent actors obtain permits while the same authoritative state is current.
    permit_a, binding_a = _fresh_permit()
    permit_b, binding_b = _fresh_permit()
    assert permit_a.authority_state_version == permit_b.authority_state_version

    a_done = Event()
    state_changed = Event()
    results = {}

    def actor_a():
        results["a"] = execute_protected_consequence(
            permit=permit_a,
            attempted_action_binding_hash=binding_a,
        )
        assert results["a"] == "CONSEQUENCE_FORMED"
        a_done.set()

    def authoritative_state_update():
        assert a_done.wait(timeout=2.0)
        results["new_version"] = advance_authority_state_version()
        state_changed.set()

    def actor_b():
        # Actor B was independently valid when its permit was issued, but it must
        # resolve against the changed state at the final protected boundary.
        assert state_changed.wait(timeout=2.0)
        results["b"] = execute_protected_consequence(
            permit=permit_b,
            attempted_action_binding_hash=binding_b,
        )

    t_a = Thread(target=actor_a)
    t_update = Thread(target=authoritative_state_update)
    t_b = Thread(target=actor_b)

    t_a.start()
    t_update.start()
    t_b.start()

    for t in (t_a, t_update, t_b):
        t.join(timeout=3.0)
        assert not t.is_alive()

    assert results["a"] == "CONSEQUENCE_FORMED"
    assert results["b"] == "DENIED_AUTHORITY_STATE_STALE", (
        "VPC-001.2 FAILURE: second independently valid action formed a consequence "
        "after the first action had caused a newer authoritative state to commit"
    )
