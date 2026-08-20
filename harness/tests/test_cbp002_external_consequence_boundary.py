from __future__ import annotations

import json
import socket
import subprocess
import sys
import time
from dataclasses import replace
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


def _post_json(url: str, payload: dict | None = None) -> dict:
    body = json.dumps(payload or {}).encode("utf-8")
    req = request.Request(
        url,
        data=body,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    with request.urlopen(req, timeout=2.0) as response:
        return json.loads(response.read().decode("utf-8"))


def _wait_until_ready(base_url: str) -> None:
    deadline = time.time() + 5.0
    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            if _get_json(f"{base_url}/health")["status"] == "ok":
                return
        except Exception as exc:  # service startup race only
            last_error = exc
            time.sleep(0.05)
    raise AssertionError(f"external consequence service did not start: {last_error}")


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


def test_cbp002_external_consequence_boundary(tmp_path, monkeypatch):
    # Isolate FlowSignal's represented durable execution state. The external
    # consequence service below runs as a separate OS process and owns its own
    # state, observed only through HTTP.
    monkeypatch.setenv(
        "FLOWSIGNAL_PERMIT_CONSUMPTION_STORE",
        str(tmp_path / "permit-consumption.sqlite3"),
    )
    monkeypatch.setenv(
        "FLOWSIGNAL_CONSEQUENCE_OUTCOME_STORE",
        str(tmp_path / "consequence-outcomes.sqlite3"),
    )
    monkeypatch.setenv(
        "FLOWSIGNAL_ROLLBACK_ANCHOR_STORE",
        str(tmp_path / "rollback-anchor.sqlite3"),
    )

    port = _free_port()
    base_url = f"http://127.0.0.1:{port}"
    service = subprocess.Popen(
        [
            sys.executable,
            "external_targets/cbp002_consequence_service.py",
            "--port",
            str(port),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    try:
        _wait_until_ready(base_url)

        # 1. Independent initial observation: this state is not FlowSignal's
        # consequence-outcome store.
        initial = _get_json(f"{base_url}/state")
        assert initial["transfer_count"] == 0
        assert initial["source_balance"] == 5_000_000.0

        # 2-3. POSITIVE CONTROL: current exact-action authority reaches the
        # protected adapter and causes an externally observable state change.
        _, control_attempt, control_permit = _fresh_allow_and_permit()
        control_outcome, control_receipt = execute_external_payment(
            permit=control_permit,
            attempt=control_attempt,
            payments_url=f"{base_url}/payments",
        )
        assert control_outcome == "CONSEQUENCE_FORMED"
        assert control_receipt.consequence_formed is True
        assert verify_consequence_outcome_receipt(control_receipt)

        after_control = _get_json(f"{base_url}/state")
        assert after_control["transfer_count"] == 1
        assert after_control["source_balance"] == initial["source_balance"] - control_attempt.amount
        assert after_control["beneficiary_balances"][control_attempt.beneficiary] == control_attempt.amount

        # 4. The external sandbox exposes an explicit administrative reset route.
        # It is outside the closure claim and is used only to create a distinct
        # challenged state. CBP-002 does not claim universal external-route closure.
        reset_state = _post_json(f"{base_url}/admin/reset")
        assert reset_state["transfer_count"] == 0
        challenged_before = _get_json(f"{base_url}/state")
        assert challenged_before == reset_state

        # 5-6. Obtain valid authority, then change the authoritative runtime
        # world after permit issuance but before the external bind.
        historical_receipt, historical_attempt, historical_permit = _fresh_allow_and_permit()
        old_state_version = historical_permit.authority_state_version
        new_state_version = advance_authority_state_version()
        assert new_state_version != old_state_version

        # 7-9. ATTEMPTED EXTERNAL BIND / NO_EXTERNAL_EFFECT.
        stale_outcome, stale_receipt = execute_external_payment(
            permit=historical_permit,
            attempt=historical_attempt,
            payments_url=f"{base_url}/payments",
        )
        assert stale_outcome == "DENIED_AUTHORITY_STATE_STALE", (
            "CBP-002 FAILURE — STALE AUTHORITY CAUSED EXTERNAL EFFECT OR WAS NOT "
            "DENIED BEFORE THE EXTERNAL CONSEQUENCE HOOK"
        )
        assert stale_receipt.authority_receipt_id == historical_receipt.id
        assert stale_receipt.consequence_formed is False
        assert stale_receipt.outcome == "DENIED_AUTHORITY_STATE_STALE"
        assert verify_consequence_outcome_receipt(stale_receipt)
        assert _get_json(f"{base_url}/state") == challenged_before, (
            "CBP-002 FAILURE — STALE AUTHORITY CAUSED EXTERNAL EFFECT"
        )

        # 10. Repeat the protected route with the same historical permit.
        retry_outcome, retry_receipt = execute_external_payment(
            permit=historical_permit,
            attempt=historical_attempt,
            payments_url=f"{base_url}/payments",
        )
        assert retry_outcome == "DENIED_AUTHORITY_STATE_STALE"
        assert retry_receipt.consequence_formed is False
        assert _get_json(f"{base_url}/state") == challenged_before

        # 11. Material action substitution under the historical permit cannot be
        # transferred onto a different external consequence.
        substituted_attempt = replace(
            historical_attempt,
            beneficiary="SUBSTITUTED-BENEFICIARY",
            amount=historical_attempt.amount + 1.00,
        )
        substitution_outcome, substitution_receipt = execute_external_payment(
            permit=historical_permit,
            attempt=substituted_attempt,
            payments_url=f"{base_url}/payments",
        )
        assert substitution_outcome == "DENIED_ACTION_BINDING_MISMATCH", (
            "CBP-002 FAILURE — ACTION SUBSTITUTION CAUSED EXTERNAL EFFECT"
        )
        assert substitution_receipt.consequence_formed is False
        assert _get_json(f"{base_url}/state") == challenged_before

        # 12. Reacquire current authority for the same intended action.
        fresh_receipt, fresh_attempt, fresh_permit = _fresh_allow_and_permit()
        assert fresh_receipt.id != historical_receipt.id
        assert fresh_permit.signature != historical_permit.signature
        assert fresh_permit.authority_state_version == new_state_version

        # 13. Historical replay remains unable to affect external state after
        # current-state authority has been reacquired.
        replay_outcome, replay_receipt = execute_external_payment(
            permit=historical_permit,
            attempt=historical_attempt,
            payments_url=f"{base_url}/payments",
        )
        assert replay_outcome == "DENIED_AUTHORITY_STATE_STALE", (
            "CBP-002 FAILURE — HISTORICAL PERMIT CAUSED EXTERNAL EFFECT AFTER "
            "CURRENT-STATE REACQUISITION"
        )
        assert replay_receipt.consequence_formed is False
        assert _get_json(f"{base_url}/state") == challenged_before

        # 14-15. Fresh current authority reaches the exact same protected external
        # adapter and the external service independently records exactly one effect.
        fresh_outcome, fresh_consequence_receipt = execute_external_payment(
            permit=fresh_permit,
            attempt=fresh_attempt,
            payments_url=f"{base_url}/payments",
        )
        assert fresh_outcome == "CONSEQUENCE_FORMED"
        assert fresh_consequence_receipt.consequence_formed is True
        assert verify_consequence_outcome_receipt(fresh_consequence_receipt)

        final_state = _get_json(f"{base_url}/state")
        assert final_state["transfer_count"] == 1
        assert final_state["source_balance"] == challenged_before["source_balance"] - fresh_attempt.amount
        assert final_state["beneficiary_balances"][fresh_attempt.beneficiary] == fresh_attempt.amount
        assert final_state["transfers"][0]["transaction_id"] == fresh_permit.signature
        assert final_state["transfers"][0]["beneficiary"] == fresh_attempt.beneficiary
        assert final_state["transfers"][0]["amount"] == fresh_attempt.amount

    finally:
        service.terminate()
        try:
            service.wait(timeout=3.0)
        except subprocess.TimeoutExpired:
            service.kill()
            service.wait(timeout=3.0)
