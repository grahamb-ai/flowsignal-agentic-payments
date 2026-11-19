"""T19 failure-first: capability adapter must not assert non-formation after lost acknowledgement."""
from pathlib import Path
import sqlite3
import pytest

from app.engines import capability_external_adapter
from app.engines.execution_gateway import ExecutionAttempt, validate_execution
from app.engines.financial_runtime import evaluate_financial
from app.engines.protected_consequence import ExternalOutcomeUnknown
from harness.runner import load_scenario


def test_t19_capability_payment_committed_but_ack_lost(tmp_path, monkeypatch):
    outcome_path = tmp_path / "outcomes.sqlite3"
    monkeypatch.setenv("FLOWSIGNAL_PERMIT_CONSUMPTION_STORE", str(tmp_path / "permits.sqlite3"))
    monkeypatch.setenv("FLOWSIGNAL_CONSEQUENCE_OUTCOME_STORE", str(outcome_path))
    monkeypatch.setenv("FLOWSIGNAL_ROLLBACK_ANCHOR_STORE", str(tmp_path / "anchor.sqlite3"))

    req = load_scenario(Path("harness/scenarios/AP-001_allow.json"))
    response, receipt = evaluate_financial(req)
    assert response.decision == "ALLOW"
    attempt = ExecutionAttempt(
        actor_id=req.actor_id, principal_id=req.principal_id,
        action=req.action, target=req.target, amount=req.amount,
        currency=req.currency, source_account=req.source_account,
        beneficiary=req.beneficiary, purpose=req.purpose,
        mandate_id=req.mandate_id, attempted_at=req.requested_execution_time,
    )
    gateway = validate_execution(receipt, attempt)
    assert gateway.status == "PERMITTED"
    permit = gateway.execution_permit
    assert permit is not None

    committed = []
    def fake_post(url, payload, *, timeout_seconds, bearer_token=None):
        if url.endswith("/release"):
            return {"capability": "test-only-capability"}
        committed.append(payload["transaction_id"])
        raise ConnectionResetError("provider committed; acknowledgement lost")

    monkeypatch.setattr(capability_external_adapter, "_post_json", fake_post)
    with pytest.raises(ExternalOutcomeUnknown):
        capability_external_adapter.execute_capability_protected_payment(
            permit=permit, attempt=attempt,
            capability_release_url="http://provider.invalid/release",
            payments_url="http://provider.invalid/payments",
        )
    with sqlite3.connect(outcome_path) as c:
        outcome = c.execute(
            "SELECT outcome FROM consequence_outcomes WHERE permit_signature=?",
            (permit.signature,),
        ).fetchone()
    assert committed == [permit.signature]
    assert outcome == ("CONSEQUENCE_OUTCOME_UNRESOLVED",)
