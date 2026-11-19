"""Full FlowSignal gateway -> protected adapter -> signed PostgreSQL provider.

Runs only in the ephemeral role-separated PostgreSQL qualification workflow.
The transport is injected in-process; HTTP/network and live rail remain unqualified.
"""
import os
from pathlib import Path
import psycopg
import pytest
from app.engines.execution_gateway import ExecutionAttempt, validate_execution
from app.engines.financial_runtime import evaluate_financial
from app.engines.external_consequence_adapter import execute_external_payment, _external_payload
from app.engines.fs_sz_pay_001_postgres_provider import PostgreSQLProtectedLedger
from harness.runner import load_scenario
from tests.provider_signed_fixture import issuer, signed_payment


@pytest.mark.skipif(not os.environ.get("FS_QUAL_EXECUTOR_DSN"), reason="requires ephemeral PostgreSQL executor login")
def test_gateway_to_restricted_postgres_provider(tmp_path, monkeypatch):
    for key, name in [
        ("FLOWSIGNAL_PERMIT_CONSUMPTION_STORE", "permits.sqlite3"),
        ("FLOWSIGNAL_CONSEQUENCE_OUTCOME_STORE", "outcomes.sqlite3"),
        ("FLOWSIGNAL_ROLLBACK_ANCHOR_STORE", "anchors.sqlite3"),
    ]:
        monkeypatch.setenv(key, str(tmp_path / name))
    req = load_scenario(Path("harness/scenarios/AP-001_allow.json"))
    decision, receipt = evaluate_financial(req)
    assert decision.decision == "ALLOW"
    attempt = ExecutionAttempt(
        actor_id=req.actor_id, principal_id=req.principal_id,
        action=req.action, target=req.target, amount=req.amount,
        currency=req.currency, source_account=req.source_account,
        beneficiary=req.beneficiary, purpose=req.purpose,
        mandate_id=req.mandate_id, attempted_at=req.requested_execution_time)
    permit_result = validate_execution(
        receipt, attempt, payment_intent_id="GATEWAY-PG-INTEGRATED-001",
        provider_authority_epoch=1, provider_mandate_id=attempt.mandate_id)
    assert permit_result.status == "PERMITTED"
    # Provision the exact gateway scenario mandate through the distinct writer login.\n    with psycopg.connect(os.environ["FS_QUAL_WRITER_DSN"]) as writer_db:\n        with writer_db.cursor() as cur:\n            assert cur.execute("SELECT current_user").fetchone()[0] == "fs_authority_writer"\n            cur.execute("INSERT INTO fs_provider.mandates(id,epoch,revoked) VALUES (%s,1,false)", (attempt.mandate_id,))\n    key = issuer()\n    ledger = PostgreSQLProtectedLedger(
        connect=lambda: psycopg.connect(os.environ["FS_QUAL_EXECUTOR_DSN"]),
        verification_key=key.public_key(), mandate_id=attempt.mandate_id)
    signed = signed_payment(key, _external_payload(attempt, permit_result.execution_permit))
    observed = []
    def post(_url, payload, timeout_seconds):
        observed.append(payload)
        status, result = ledger.transfer(payload)
        if status != 201:
            raise RuntimeError(f"provider refused: {status} {result}")
        return result
    from app.engines import external_consequence_adapter
    monkeypatch.setattr(external_consequence_adapter, "_post_json", post)
    result, _ = execute_external_payment(
        permit=permit_result.execution_permit, attempt=attempt,
        payments_url="http://reference-provider.invalid/payments",
        institutional_authorization=signed["institutional_authorization"])
    assert result == "CONSEQUENCE_FORMED"
    assert len(observed) == 1
    with psycopg.connect(os.environ["FS_QUAL_EXECUTOR_DSN"]) as db:
        with db.cursor() as cur:
            assert cur.execute(
                "SELECT count(*) FROM fs_provider.commits WHERE intent_id=%s",
                ("GATEWAY-PG-INTEGRATED-001",)).fetchone()[0] == 1
