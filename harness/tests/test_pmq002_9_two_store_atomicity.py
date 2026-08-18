"""PMQ-002.9 two-store atomicity crash challenge."""

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


def _two_store_crash_worker(permit, binding, permit_store: str, outcome_store: str):
    os.environ["FLOWSIGNAL_PERMIT_CONSUMPTION_STORE"] = permit_store
    os.environ["FLOWSIGNAL_CONSEQUENCE_OUTCOME_STORE"] = outcome_store

    from app.engines import authority_store, protected_consequence

    while authority_store.get_authority_state_version() < permit.authority_state_version:
        authority_store.advance_authority_state_version()

    original_record = protected_consequence.record_consequence_outcome

    def terminate_before_first_outcome_commit(*, permit_signature, action_binding_hash, outcome):
        # Target the exact cross-store gap: permit consumption has already committed,
        # but the first consequence-outcome write has not yet committed.
        os._exit(74)

    protected_consequence.record_consequence_outcome = terminate_before_first_outcome_commit
    try:
        protected_consequence.execute_protected_consequence(
            permit=permit,
            attempted_action_binding_hash=binding,
        )
    finally:
        protected_consequence.record_consequence_outcome = original_record


def test_pmq002_9_two_store_crash_cannot_leave_consumed_without_execution_state(tmp_path, monkeypatch):
    permit_store = tmp_path / "permit-consumption.sqlite3"
    outcome_store = tmp_path / "consequence-outcomes.sqlite3"
    monkeypatch.setenv("FLOWSIGNAL_PERMIT_CONSUMPTION_STORE", str(permit_store))
    monkeypatch.setenv("FLOWSIGNAL_CONSEQUENCE_OUTCOME_STORE", str(outcome_store))

    permit, binding = _valid_permit_and_binding()

    ctx = multiprocessing.get_context("spawn")
    process = ctx.Process(
        target=_two_store_crash_worker,
        args=(permit, binding, str(permit_store), str(outcome_store)),
    )
    process.start()
    process.join(timeout=10)

    assert not process.is_alive()
    assert process.exitcode == 74

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

    assert outcome_store.exists(), (
        "PMQ-002.9 FAILURE: permit consumption committed but the first outcome write "
        "was crash-separated, leaving no durable execution outcome store"
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

    assert rows, (
        "PMQ-002.9 FAILURE: permit consumption committed but no durable execution "
        "state exists for the same permit/action binding after the injected crash"
    )
    assert rows[0][0] == permit.signature
    assert rows[0][1] == binding
    assert rows[0][2] in {
        "CONSEQUENCE_OUTCOME_UNRESOLVED",
        "CONSEQUENCE_NOT_FORMED",
        "CONSEQUENCE_FORMED",
    }
