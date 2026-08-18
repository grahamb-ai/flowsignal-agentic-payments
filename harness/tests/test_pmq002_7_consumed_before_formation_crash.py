"""PMQ-002.7 consumed-before-formation crash recovery challenge."""

from pathlib import Path
import sqlite3

import pytest

from app.engines.execution_gateway import ExecutionAttempt, action_binding_hash, validate_execution
from app.engines.financial_runtime import evaluate_financial
from app.engines import protected_consequence
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


def test_pmq002_7_consumed_permit_crash_before_formation_is_recoverable(tmp_path, monkeypatch):
    permit_store = tmp_path / "permit-consumption.sqlite3"
    outcome_store = tmp_path / "consequence-outcomes.sqlite3"
    monkeypatch.setenv("FLOWSIGNAL_PERMIT_CONSUMPTION_STORE", str(permit_store))
    monkeypatch.setenv("FLOWSIGNAL_CONSEQUENCE_OUTCOME_STORE", str(outcome_store))

    permit, binding = _valid_permit_and_binding()

    def crash_after_consumption_before_formation():
        raise RuntimeError("PMQ-002.7 injected crash after permit consumption before formation")

    with pytest.raises(RuntimeError, match="PMQ-002.7 injected crash"):
        protected_consequence.execute_protected_consequence(
            permit=permit,
            attempted_action_binding_hash=binding,
            before_formation_hook=crash_after_consumption_before_formation,
        )

    # The permit really was durably consumed before the injected failure.
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

    # Frozen recovery requirement: durable evidence must distinguish the
    # consumed-but-not-formed state from a successfully formed consequence.
    assert outcome_store.exists(), (
        "PMQ-002.7 FAILURE: permit was durably consumed and execution failed before "
        "formation, but no durable outcome state exists to establish non-formation"
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

    assert rows == [(permit.signature, binding, "CONSEQUENCE_NOT_FORMED")], (
        "PMQ-002.7 FAILURE: recovery cannot explicitly distinguish consumed permit + "
        "non-formation from consumed permit + formed consequence"
    )

    # A retry may be denied because the permit is already consumed, but that
    # denial must not be the only evidence available about the earlier attempt.
    retry = protected_consequence.execute_protected_consequence(
        permit=permit,
        attempted_action_binding_hash=binding,
    )
    assert retry == "DENIED_EXECUTION_PERMIT_REPLAY"
