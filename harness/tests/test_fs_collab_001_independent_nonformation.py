from __future__ import annotations

import json
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib import request

from app.engines.authority_store import advance_authority_state_version
from app.engines.consequence_receipt import verify_consequence_outcome_receipt
from app.engines.execution_gateway import ExecutionAttempt, validate_execution
from app.engines.external_consequence_adapter import execute_external_payment
from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _get_json(url: str) -> dict:
    with request.urlopen(url, timeout=2.0) as response:
        return json.loads(response.read().decode("utf-8"))


def _wait_until_ready(base_url: str) -> None:
    deadline = time.time() + 5.0
    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            if _get_json(f"{base_url}/health")["status"] == "ok":
                return
        except Exception as exc:
            last_error = exc
            time.sleep(0.05)
    raise AssertionError(f"external consequence observer did not start: {last_error}")


def _fresh_allow_and_permit():
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
    return receipt, attempt, gateway.execution_permit


def test_fs_collab_001_independent_external_nonformation(tmp_path, monkeypatch):
    """Frozen neutral proposition: governed refusal is not external proof by itself."""

    monkeypatch.setenv("FLOWSIGNAL_PERMIT_CONSUMPTION_STORE", str(tmp_path / "permit-consumption.sqlite3"))
    monkeypatch.setenv("FLOWSIGNAL_CONSEQUENCE_OUTCOME_STORE", str(tmp_path / "consequence-outcomes.sqlite3"))
    monkeypatch.setenv("FLOWSIGNAL_ROLLBACK_ANCHOR_STORE", str(tmp_path / "rollback-anchor.sqlite3"))

    port = _free_port()
    base_url = f"http://127.0.0.1:{port}"
    service = subprocess.Popen(
        [sys.executable, "external_targets/cbp002_consequence_service.py", "--port", str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    try:
        _wait_until_ready(base_url)

        before = _get_json(f"{base_url}/state")
        assert before["transfer_count"] == 0

        authority_receipt, attempt, permit = _fresh_allow_and_permit()
        old_version = permit.authority_state_version
        new_version = advance_authority_state_version()
        assert new_version != old_version

        outcome, consequence_receipt = execute_external_payment(
            permit=permit,
            attempt=attempt,
            payments_url=f"{base_url}/payments",
        )
        assert outcome == "DENIED_AUTHORITY_STATE_STALE"

        assert consequence_receipt.authority_receipt_id == authority_receipt.id
        assert consequence_receipt.outcome == "DENIED_AUTHORITY_STATE_STALE"
        assert consequence_receipt.consequence_formed is False
        assert verify_consequence_outcome_receipt(consequence_receipt)

        after_refusal = _get_json(f"{base_url}/state")
        assert after_refusal == before, (
            "FS-COLLAB-001 FAILURE — governed refusal was recorded but the "
            "independently observed consequence target changed"
        )

        _, fresh_attempt, fresh_permit = _fresh_allow_and_permit()
        fresh_outcome, fresh_receipt = execute_external_payment(
            permit=fresh_permit,
            attempt=fresh_attempt,
            payments_url=f"{base_url}/payments",
        )
        assert fresh_outcome == "CONSEQUENCE_FORMED"
        assert fresh_receipt.consequence_formed is True
        assert verify_consequence_outcome_receipt(fresh_receipt)

        after_positive = _get_json(f"{base_url}/state")
        assert after_positive["transfer_count"] == before["transfer_count"] + 1
        assert after_positive["source_balance"] == before["source_balance"] - fresh_attempt.amount
        assert after_positive["beneficiary_balances"][fresh_attempt.beneficiary] == fresh_attempt.amount
        assert after_positive["transfers"][0]["transaction_id"] == fresh_permit.signature

    finally:
        service.terminate()
        try:
            service.wait(timeout=3.0)
        except subprocess.TimeoutExpired:
            service.kill()
            service.wait(timeout=3.0)
