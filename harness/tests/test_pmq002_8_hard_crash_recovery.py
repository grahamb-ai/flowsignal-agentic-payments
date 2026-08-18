"""PMQ-002.8 hard process-crash recovery challenge."""

import multiprocessing
import os
from pathlib import Path
import sqlite3

from app.engines.execution_gateway import ExecutionAttempt, action_binding_hash, validate_execution
from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def _valid_permit_and_binding():
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


def _hard_crash_worker(permit, binding, permit_store: str, outcome_store: str):
    os.environ["FLOWSIGNAL_PERMIT_CONSUMPTION_STORE"] = permit_store
    os.environ["FLOWSIGNAL_CONSEQUENCE_OUTCOME_STORE"] = outcome_store

    from app.engines import protected_consequence

    def terminate_after_consumption_before_outcome_record():
        # os._exit bypasses Python exception handling/finally cleanup and models
        # abrupt executor process termination at the represented crash point.
        os._exit(73)

    protected_consequence.execute_protected_consequence(
        permit=permit,
        attempted_action_binding_hash=binding,
        before_formation_hook=terminate_after_consumption_before_outcome_record,
    )


def test_pmq002_8_hard_crash_after_consumption_exposes_unresolved_outcome(tmp_path, monkeypatch):
    permit_store = tmp_path / "permit-consumption.sqlite3"
    outcome_store = tmp_path / "consequence-outcomes.sqlite3"
    monkeypatch.setenv("FLOWSIGNAL_PERMIT_CONSUMPTION_STORE", str(permit_store))
    monkeypatch.setenv("FLOWSIGNAL_CONSEQUENCE_OUTCOME_STORE", str(outcome_store))

    permit, binding = _valid_permit_and_binding()

    ctx = multiprocessing.get_context("spawn")
    process = ctx.Process(
        target=_hard_crash_worker,
        args=(permit, binding, str(permit_store), str(outcome_store)),
    )
    process.start()
    process.join(timeout=10)

    assert not process.is_alive()
    assert process.exitcode == 73

    # The crash point is meaningful only if permit consumption survived.
    assert permit_store.exists()
    connection = sqlite3.connect(permit_store)
    try:
        consumed = connection.execute(
            "SELECT signature FROM consumed_execution_permits WHERE signature = ?",
            (permit.signature,),
        ).fetchall()
    finally:
        connection.close()
    assert consumed == [(permit.signature,)]

    # Frozen recovery requirement: after abrupt termination the durable outcome
    # surface must explicitly expose that the execution is unresolved. A missing
    # row plus an ordinary replay denial is not enough to establish what formed.
    assert outcome_store.exists(), (
        "PMQ-002.8 FAILURE: permit consumption survived hard process termination, "
        "but no durable outcome store exists to expose the unresolved execution"
    )

    connection = sqlite3.connect(outcome_store)
    try:
        rows = connection.execute(
            "SELECT permit_signature, action_binding_hash, outcome "
            "FROM consequence_outcomes WHERE permit_signature = ?",
            (permit.signature,),
        ).fetchall()
    finally:
        connection.close()

    assert rows == [(permit.signature, binding, "CONSEQUENCE_OUTCOME_UNRESOLVED")], (
        "PMQ-002.8 FAILURE: hard crash left a durably consumed permit without an "
        "explicit unresolved consequence outcome"
    )

    # Recovery must still preserve at-most-once safety. This denial is useful,
    # but it must not be mistaken for evidence that the earlier consequence formed.
    from app.engines import protected_consequence

    retry = protected_consequence.execute_protected_consequence(
        permit=permit,
        attempted_action_binding_hash=binding,
    )
    assert retry == "DENIED_EXECUTION_PERMIT_REPLAY"
