"""Actual localhost HTTP boundary: FlowSignal gateway -> signed PostgreSQL provider."""
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib import request, error

import psycopg
import pytest
from app.engines.execution_gateway import ExecutionAttempt, validate_execution
from app.engines.financial_runtime import evaluate_financial
from app.engines.external_consequence_adapter import execute_external_payment, _external_payload
from harness.runner import load_scenario
from tests.provider_signed_fixture import issuer, signed_payment, write_public_key


@pytest.mark.skipif(not os.environ.get("FS_QUAL_EXECUTOR_DSN"), reason="requires ephemeral PostgreSQL executor login")
def test_gateway_to_separate_postgres_http_provider(tmp_path, monkeypatch):
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
        actor_id=req.actor_id, principal_id=req.principal_id, action=req.action,
        target=req.target, amount=req.amount, currency=req.currency,
        source_account=req.source_account, beneficiary=req.beneficiary,
        purpose=req.purpose, mandate_id=req.mandate_id,
        attempted_at=req.requested_execution_time)
    permit_result = validate_execution(
        receipt, attempt, payment_intent_id="GATEWAY-PG-HTTP-001",
        provider_authority_epoch=1, provider_mandate_id=attempt.mandate_id)
    assert permit_result.status == "PERMITTED"
    with psycopg.connect(os.environ["FS_QUAL_WRITER_DSN"]) as db:
        with db.cursor() as cur:
            cur.execute(
                "INSERT INTO fs_provider.mandates(id,epoch,revoked) VALUES (%s,1,false) ON CONFLICT (id) DO NOTHING",
                (attempt.mandate_id,),
            )
            cur.execute("SELECT epoch, revoked FROM fs_provider.mandates WHERE id=%s", (attempt.mandate_id,))
            assert cur.fetchone() == (1, False), "HTTP qualification requires active matching institutional mandate"
    key = issuer()
    key_file = write_public_key(key, tmp_path / "issuer.pem")
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    env = dict(os.environ)
    process = subprocess.Popen(
        [sys.executable, "-m", "external_targets.fs_sz_pay_001_postgres_http_service",
         "--port", str(port), "--mandate-id", attempt.mandate_id,
         "--issuer-public-key-file", str(key_file)],
        env=env, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    base = f"http://127.0.0.1:{port}"
    try:
        for _ in range(50):
            if process.poll() is not None:
                raise AssertionError(f"provider exited: {process.stderr.read().decode()}")
            try:
                request.urlopen(base + "/state", timeout=0.2)
            except error.HTTPError as exc:
                if exc.code == 404:
                    break
            except (error.URLError, TimeoutError):
                time.sleep(0.1)
        else:
            raise AssertionError("provider did not start")
        signed = signed_payment(key, _external_payload(attempt, permit_result.execution_permit))
        result, _ = execute_external_payment(
            permit=permit_result.execution_permit, attempt=attempt,
            payments_url=base + "/payments",
            institutional_authorization=signed["institutional_authorization"])
        assert result == "CONSEQUENCE_FORMED"
        for path in ("/state", "/admin/reset"):
            try:
                request.urlopen(base + path, timeout=2)
                raise AssertionError(f"unqualified route exposed: {path}")
            except error.HTTPError as exc:
                assert exc.code == 404
        with psycopg.connect(os.environ["FS_QUAL_EXECUTOR_DSN"]) as db:
            with db.cursor() as cur:
                assert cur.execute(
                    "SELECT count(*) FROM fs_provider.commits WHERE intent_id=%s",
                    ("GATEWAY-PG-HTTP-001",)).fetchone()[0] == 1
    finally:
        process.terminate()
        process.wait(timeout=5)
