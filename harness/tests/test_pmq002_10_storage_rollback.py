"""PMQ-002.10 durable execution-state rollback challenge.

Failure-first qualification. This test intentionally restores both represented
execution-state SQLite stores to their exact pre-execution snapshots and then
re-presents the exact same execution permit/action binding.
"""

from pathlib import Path
import shutil
import sqlite3

from app.engines import authority_store
from app.engines.execution_gateway import ExecutionAttempt, action_binding_hash, validate_execution
from app.engines.financial_runtime import evaluate_financial
from app.engines.protected_consequence import execute_protected_consequence
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


def _initialise_empty_snapshot(permit_store: Path, outcome_store: Path) -> None:
    """Create concrete closed pre-execution SQLite snapshots."""
    connection = sqlite3.connect(permit_store)
    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS consumed_execution_permits (
                signature TEXT PRIMARY KEY,
                consumed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.commit()
    finally:
        connection.close()

    connection = sqlite3.connect(outcome_store)
    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS consequence_outcomes (
                permit_signature TEXT PRIMARY KEY,
                action_binding_hash TEXT NOT NULL,
                outcome TEXT NOT NULL,
                recorded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.commit()
    finally:
        connection.close()


def test_pmq002_10_restored_old_execution_state_cannot_resurrect_consumed_permit(tmp_path, monkeypatch):
    permit_store = tmp_path / "permit-consumption.sqlite3"
    outcome_store = tmp_path / "consequence-outcomes.sqlite3"
    permit_snapshot = tmp_path / "permit-consumption.pre-execution.sqlite3"
    outcome_snapshot = tmp_path / "consequence-outcomes.pre-execution.sqlite3"

    monkeypatch.setenv("FLOWSIGNAL_PERMIT_CONSUMPTION_STORE", str(permit_store))
    monkeypatch.setenv("FLOWSIGNAL_CONSEQUENCE_OUTCOME_STORE", str(outcome_store))

    # Freeze a concrete older durable state before the permit is consumed.
    _initialise_empty_snapshot(permit_store, outcome_store)
    shutil.copy2(permit_store, permit_snapshot)
    shutil.copy2(outcome_store, outcome_snapshot)

    permit, binding = _valid_permit_and_binding()
    while authority_store.get_authority_state_version() < permit.authority_state_version:
        authority_store.advance_authority_state_version()

    first = execute_protected_consequence(
        permit=permit,
        attempted_action_binding_hash=binding,
    )
    assert first == "CONSEQUENCE_FORMED"

    connection = sqlite3.connect(permit_store)
    try:
        consumed = connection.execute(
            "SELECT signature FROM consumed_execution_permits WHERE signature = ?",
            (permit.signature,),
        ).fetchall()
    finally:
        connection.close()
    assert consumed == [(permit.signature,)]

    connection = sqlite3.connect(outcome_store)
    try:
        outcome = connection.execute(
            "SELECT outcome FROM consequence_outcomes WHERE permit_signature = ?",
            (permit.signature,),
        ).fetchone()
    finally:
        connection.close()
    assert outcome == ("CONSEQUENCE_FORMED",)

    # Adversarial condition: restore both represented durable stores to the
    # exact pre-execution snapshots, removing the durable evidence that this
    # permit was consumed and that its consequence formed.
    shutil.copy2(permit_snapshot, permit_store)
    shutil.copy2(outcome_snapshot, outcome_store)

    second = execute_protected_consequence(
        permit=permit,
        attempted_action_binding_hash=binding,
    )

    assert second != "CONSEQUENCE_FORMED", (
        "PMQ-002.10 FAILURE: restoring both represented durable execution-state "
        "stores to their pre-execution snapshots made the consumed permit appear "
        "unused and allowed the same permit/action binding to form a second "
        "represented consequence without rollback detection"
    )
