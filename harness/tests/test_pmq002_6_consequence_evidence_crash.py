"""PMQ-002.6 failure-first consequence/evidence crash-window challenge.

Frozen proposition:
If the represented protected consequence has formed, the reference system MUST
retain a recoverable durable record of that formation even when subsequent
consequence-receipt creation fails.
"""

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


def test_pmq002_6_consequence_formation_survives_receipt_write_failure(tmp_path, monkeypatch):
    permit_store = tmp_path / "permit-consumption.sqlite3"
    outcome_store = tmp_path / "consequence-outcomes.sqlite3"
    monkeypatch.setenv("FLOWSIGNAL_PERMIT_CONSUMPTION_STORE", str(permit_store))
    monkeypatch.setenv("FLOWSIGNAL_CONSEQUENCE_OUTCOME_STORE", str(outcome_store))

    permit, binding = _valid_permit_and_binding()

    def fail_receipt_creation(**_kwargs):
        raise RuntimeError("PMQ-002.6 injected receipt creation failure")

    monkeypatch.setattr(
        protected_consequence,
        "create_consequence_outcome_receipt",
        fail_receipt_creation,
    )

    with pytest.raises(RuntimeError, match="PMQ-002.6 injected receipt creation failure"):
        protected_consequence.execute_protected_consequence_with_receipt(
            permit=permit,
            attempted_action_binding_hash=binding,
        )

    assert outcome_store.exists(), (
        "PMQ-002.6 FAILURE: represented consequence formed, receipt creation failed, "
        "and no durable consequence-outcome store existed for recovery"
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

    assert rows == [(permit.signature, binding, "CONSEQUENCE_FORMED")], (
        "PMQ-002.6 FAILURE: represented consequence formed, receipt creation failed, "
        "but durable recoverable outcome evidence did not preserve the formation"
    )
