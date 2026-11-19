"""T18 frozen hostile test: external commit followed by lost acknowledgement."""
from pathlib import Path
import sqlite3
import pytest

from app.engines import external_consequence_adapter
from app.engines.protected_consequence import ExternalOutcomeUnknown
from app.engines.execution_gateway import ExecutionAttempt, validate_execution
from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_t18_external_commit_lost_ack_remains_unresolved(tmp_path, monkeypatch):
    monkeypatch.setenv("FLOWSIGNAL_PERMIT_CONSUMPTION_STORE", str(tmp_path / "permits.sqlite3"))
    outcome_path = tmp_path / "outcomes.sqlite3"
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

    provider_commits = []
    def provider_commits_then_drops_ack(url, payload, timeout_seconds):
        provider_commits.append(payload["transaction_id"])
        raise ConnectionResetError("ack lost after provider commit")

    monkeypatch.setattr(external_consequence_adapter, "_post_json", provider_commits_then_drops_ack)
    with pytest.raises(ExternalOutcomeUnknown):
        external_consequence_adapter.execute_external_payment(
            permit=permit, attempt=attempt, payments_url="http://provider.invalid/payments"
        )

    with sqlite3.connect(outcome_path) as c:
        rows = c.execute(
            "SELECT outcome FROM consequence_outcomes WHERE permit_signature=?",
            (permit.signature,),
        ).fetchall()
    assert rows == [("CONSEQUENCE_OUTCOME_UNRESOLVED",)]
    assert provider_commits == [permit.signature]

    # Reusing the consumed permit must not dispatch a second payment.
    outcome, _ = external_consequence_adapter.execute_external_payment(
        permit=permit, attempt=attempt, payments_url="http://provider.invalid/payments"
    )
    assert outcome == "DENIED_EXECUTION_PERMIT_REPLAY"
    assert provider_commits == [permit.signature]
