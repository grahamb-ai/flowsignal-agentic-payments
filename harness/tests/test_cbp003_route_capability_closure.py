from __future__ import annotations

import json
import socket
import subprocess
import sys
import time
from dataclasses import replace
from pathlib import Path
from urllib import error, request

from app.engines.authority_store import advance_authority_state_version
from app.engines.capability_external_adapter import execute_capability_protected_payment
from app.engines.consequence_receipt import verify_consequence_outcome_receipt
from app.engines.execution_gateway import ExecutionAttempt, action_binding_hash, validate_execution
from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _get_json(url: str) -> dict:
    with request.urlopen(url, timeout=2.0) as response:
        return json.loads(response.read().decode("utf-8"))


def _post_json(
    url: str,
    payload: dict | None = None,
    *,
    bearer_token: str | None = None,
) -> tuple[int, dict]:
    body = json.dumps(payload or {}, sort_keys=True).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if bearer_token is not None:
        headers["Authorization"] = f"Bearer {bearer_token}"
    req = request.Request(url, data=body, method="POST", headers=headers)
    try:
        with request.urlopen(req, timeout=2.0) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


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
    raise AssertionError(f"CBP-003 capability target did not start: {last_error}")


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


def _release_payload(permit, attempt: ExecutionAttempt) -> dict:
    return {
        "permit_signature": permit.signature,
        "action_binding_hash": action_binding_hash(attempt),
        "source_account": attempt.source_account,
        "beneficiary": attempt.beneficiary,
        "amount": attempt.amount,
        "currency": attempt.currency,
        "purpose": attempt.purpose,
    }


def _payment_payload(transaction_id: str, attempt: ExecutionAttempt) -> dict:
    return {
        "transaction_id": transaction_id,
        "source_account": attempt.source_account,
        "beneficiary": attempt.beneficiary,
        "amount": attempt.amount,
        "currency": attempt.currency,
        "purpose": attempt.purpose,
    }


def test_cbp003_protected_external_route_capability_closure(tmp_path, monkeypatch):
    permit_store = tmp_path / "permit-consumption.sqlite3"
    outcome_store = tmp_path / "consequence-outcomes.sqlite3"
    rollback_store = tmp_path / "rollback-anchor.sqlite3"

    monkeypatch.setenv("FLOWSIGNAL_PERMIT_CONSUMPTION_STORE", str(permit_store))
    monkeypatch.setenv("FLOWSIGNAL_CONSEQUENCE_OUTCOME_STORE", str(outcome_store))
    monkeypatch.setenv("FLOWSIGNAL_ROLLBACK_ANCHOR_STORE", str(rollback_store))

    port = _free_port()
    base_url = f"http://127.0.0.1:{port}"
    service = subprocess.Popen(
        [
            sys.executable,
            "external_targets/cbp003_capability_service.py",
            "--port",
            str(port),
            "--permit-store",
            str(permit_store),
            "--outcome-store",
            str(outcome_store),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    try:
        _wait_until_ready(base_url)
        release_url = f"{base_url}/capabilities/release"
        payments_url = f"{base_url}/payments"

        # 1. Independently observable external state.
        initial = _get_json(f"{base_url}/state")
        assert initial["transfer_count"] == 0
        assert initial["issued_capability_count"] == 0
        assert initial["source_balance"] == 5_000_000.0

        # 2. The protected consequence endpoint cannot be invoked by an ordinary
        # caller without a released capability.
        _, direct_attempt, direct_permit = _fresh_allow_and_permit()
        direct_status, direct_result = _post_json(
            payments_url,
            _payment_payload("DIRECT-WITHOUT-CAPABILITY", direct_attempt),
        )
        assert direct_status == 401
        assert direct_result["error"] == "CAPABILITY_REQUIRED"
        assert _get_json(f"{base_url}/state") == initial, (
            "CBP-003 FAILURE — PROTECTED CONSEQUENCE FORMED WITHOUT RELEASED CAPABILITY"
        )

        # A valid FlowSignal permit alone is also insufficient to obtain the
        # external capability by bypassing the protected consequence interval:
        # durable permit consumption + unresolved exact-action state do not yet exist.
        release_status, release_result = _post_json(
            release_url,
            _release_payload(direct_permit, direct_attempt),
        )
        assert release_status == 403
        assert release_result["error"] == "CAPABILITY_RELEASE_NOT_AUTHORISED"
        assert _get_json(f"{base_url}/state") == initial

        # 3-5. POSITIVE CONTROL. Current exact-action authority enters the
        # protected interval, where durable consumption/unresolved state becomes
        # the precondition for capability release. The target then validates and
        # consumes that capability to form exactly one external consequence.
        _, control_attempt, control_permit = _fresh_allow_and_permit()
        control_outcome, control_receipt, control_capability = execute_capability_protected_payment(
            permit=control_permit,
            attempt=control_attempt,
            capability_release_url=release_url,
            payments_url=payments_url,
        )
        assert control_outcome == "CONSEQUENCE_FORMED"
        assert control_receipt.consequence_formed is True
        assert verify_consequence_outcome_receipt(control_receipt)
        assert isinstance(control_capability, str) and control_capability

        after_control = _get_json(f"{base_url}/state")
        assert after_control["transfer_count"] == 1
        assert after_control["issued_capability_count"] == 1
        assert after_control["used_capability_count"] == 1
        assert after_control["source_balance"] == initial["source_balance"] - control_attempt.amount

        # 6. Administrative reset is only a test-fixture power and remains outside
        # the bounded ordinary-caller route-closure claim.
        reset_status, reset_state = _post_json(f"{base_url}/admin/reset")
        assert reset_status == 200
        assert reset_state["transfer_count"] == 0
        assert reset_state["issued_capability_count"] == 0
        challenged_before = _get_json(f"{base_url}/state")
        assert challenged_before == reset_state

        # 7-8. Obtain a second current permit, then change authoritative state
        # after permit issuance but before capability release / external effect.
        historical_receipt, historical_attempt, historical_permit = _fresh_allow_and_permit()
        old_state_version = historical_permit.authority_state_version
        new_state_version = advance_authority_state_version()
        assert new_state_version != old_state_version

        # 9-10. STALE AUTHORITY: the existing protected boundary refuses before
        # the capability-release hook is reached. No capability and no external effect.
        stale_outcome, stale_receipt, stale_capability = execute_capability_protected_payment(
            permit=historical_permit,
            attempt=historical_attempt,
            capability_release_url=release_url,
            payments_url=payments_url,
        )
        assert stale_outcome == "DENIED_AUTHORITY_STATE_STALE", (
            "CBP-003 FAILURE — STALE AUTHORITY OBTAINED OR EXERCISED CONSEQUENCE CAPABILITY"
        )
        assert stale_capability is None
        assert stale_receipt.authority_receipt_id == historical_receipt.id
        assert stale_receipt.consequence_formed is False
        assert verify_consequence_outcome_receipt(stale_receipt)
        assert _get_json(f"{base_url}/state") == challenged_before

        # 11. Material action substitution cannot reach capability release.
        substituted_attempt = replace(
            historical_attempt,
            beneficiary="CBP003-SUBSTITUTED-BENEFICIARY",
            amount=historical_attempt.amount + 1.00,
        )
        substitution_outcome, substitution_receipt, substitution_capability = (
            execute_capability_protected_payment(
                permit=historical_permit,
                attempt=substituted_attempt,
                capability_release_url=release_url,
                payments_url=payments_url,
            )
        )
        assert substitution_outcome == "DENIED_ACTION_BINDING_MISMATCH", (
            "CBP-003 FAILURE — ACTION SUBSTITUTION OBTAINED OR EXERCISED CONSEQUENCE CAPABILITY"
        )
        assert substitution_capability is None
        assert substitution_receipt.consequence_formed is False
        assert _get_json(f"{base_url}/state") == challenged_before

        # 12. Direct consequence invocation still fails without a valid released
        # capability even though a historical FlowSignal permit exists.
        bypass_status, bypass_result = _post_json(
            payments_url,
            _payment_payload("BYPASS-AFTER-STALE", historical_attempt),
        )
        assert bypass_status == 401
        assert bypass_result["error"] == "CAPABILITY_REQUIRED"
        assert _get_json(f"{base_url}/state") == challenged_before

        # Direct capability release with that stale historical permit also fails:
        # the protected interval never consumed it under current authority.
        stale_release_status, stale_release_result = _post_json(
            release_url,
            _release_payload(historical_permit, historical_attempt),
        )
        assert stale_release_status == 403
        assert stale_release_result["error"] == "CAPABILITY_RELEASE_NOT_AUTHORISED"
        assert _get_json(f"{base_url}/state") == challenged_before

        # 13. Reacquire current authority for the same exact intended action.
        fresh_receipt, fresh_attempt, fresh_permit = _fresh_allow_and_permit()
        assert fresh_receipt.id != historical_receipt.id
        assert fresh_permit.signature != historical_permit.signature
        assert fresh_permit.authority_state_version == new_state_version

        # 14. Historical permit remains unable to obtain/exercise the capability
        # after current authority has been reacquired.
        replay_outcome, replay_receipt, replay_capability = execute_capability_protected_payment(
            permit=historical_permit,
            attempt=historical_attempt,
            capability_release_url=release_url,
            payments_url=payments_url,
        )
        assert replay_outcome == "DENIED_AUTHORITY_STATE_STALE", (
            "CBP-003 FAILURE — HISTORICAL PERMIT OBTAINED OR EXERCISED CAPABILITY AFTER REACQUISITION"
        )
        assert replay_capability is None
        assert replay_receipt.consequence_formed is False
        assert _get_json(f"{base_url}/state") == challenged_before

        # 15. Fresh current exact-action authority reaches the same capability
        # route and forms exactly one independently observable external consequence.
        fresh_outcome, fresh_consequence_receipt, fresh_capability = (
            execute_capability_protected_payment(
                permit=fresh_permit,
                attempt=fresh_attempt,
                capability_release_url=release_url,
                payments_url=payments_url,
            )
        )
        assert fresh_outcome == "CONSEQUENCE_FORMED"
        assert fresh_consequence_receipt.consequence_formed is True
        assert verify_consequence_outcome_receipt(fresh_consequence_receipt)
        assert isinstance(fresh_capability, str) and fresh_capability

        final_once = _get_json(f"{base_url}/state")
        assert final_once["transfer_count"] == 1
        assert final_once["issued_capability_count"] == 1
        assert final_once["used_capability_count"] == 1
        assert final_once["transfers"][0]["transaction_id"] == fresh_permit.signature
        assert final_once["transfers"][0]["beneficiary"] == fresh_attempt.beneficiary
        assert final_once["transfers"][0]["amount"] == fresh_attempt.amount

        # 16. The external capability is one-time. Reusing the exact capability
        # cannot create a second external effect.
        capability_replay_status, capability_replay_result = _post_json(
            payments_url,
            _payment_payload("CAPABILITY-REPLAY", fresh_attempt),
            bearer_token=fresh_capability,
        )
        assert capability_replay_status == 409, (
            "CBP-003 FAILURE — CAPABILITY REPLAY CAUSED DUPLICATE EXTERNAL EFFECT"
        )
        assert capability_replay_result["error"] == "CAPABILITY_ALREADY_USED"

        # 17. Preserve independent final external state. FlowSignal's internal
        # consequence record is not the sole observation used by the qualification.
        final_state = _get_json(f"{base_url}/state")
        assert final_state == final_once
        assert final_state["transfer_count"] == 1

    finally:
        service.terminate()
        try:
            service.wait(timeout=3.0)
        except subprocess.TimeoutExpired:
            service.kill()
            service.wait(timeout=3.0)
