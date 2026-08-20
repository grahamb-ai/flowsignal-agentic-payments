from __future__ import annotations

import json
from urllib import request

from app.engines.execution_gateway import ExecutionAttempt, action_binding_hash
from app.engines.permit_authority import ExecutionPermit
from app.engines.protected_consequence import execute_protected_consequence_with_receipt


def _post_json(
    url: str,
    payload: dict,
    *,
    timeout_seconds: float,
    bearer_token: str | None = None,
) -> dict:
    body = json.dumps(payload, sort_keys=True).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if bearer_token is not None:
        headers["Authorization"] = f"Bearer {bearer_token}"
    req = request.Request(url, data=body, method="POST", headers=headers)
    with request.urlopen(req, timeout=timeout_seconds) as response:
        raw = response.read()
        if response.status < 200 or response.status >= 300:
            raise RuntimeError(f"external capability target returned {response.status}")
        return json.loads(raw.decode("utf-8")) if raw else {}


def _action_payload(attempt: ExecutionAttempt) -> dict:
    return {
        "source_account": attempt.source_account,
        "beneficiary": attempt.beneficiary,
        "amount": attempt.amount,
        "currency": attempt.currency,
        "purpose": attempt.purpose,
    }


def execute_capability_protected_payment(
    *,
    permit: ExecutionPermit | None,
    attempt: ExecutionAttempt,
    capability_release_url: str,
    payments_url: str,
    timeout_seconds: float = 2.0,
):
    """Release and exercise a one-time external capability inside the protected interval.

    The ordinary caller supplies a FlowSignal execution permit and attempted action,
    not the external payment capability. The target releases that capability only
    after the existing protected consequence boundary has durably consumed the
    permit and established an unresolved outcome for the same action binding.

    The target separately enforces capability scope and one-time use before its own
    external state mutation. This is a bounded reference integration, not a claim
    of production process/IAM isolation or universal privileged-route closure.
    """

    attempted_binding = action_binding_hash(attempt)
    released: dict[str, str | None] = {"token": None}

    def release_and_form_external_consequence() -> None:
        if permit is None:
            raise RuntimeError("capability hook reached without execution permit")

        release_payload = {
            "permit_signature": permit.signature,
            "action_binding_hash": attempted_binding,
            **_action_payload(attempt),
        }
        release_result = _post_json(
            capability_release_url,
            release_payload,
            timeout_seconds=timeout_seconds,
        )
        capability = release_result.get("capability")
        if not isinstance(capability, str) or not capability:
            raise RuntimeError("external target did not release a usable capability")
        released["token"] = capability

        payment_payload = {
            "transaction_id": permit.signature,
            **_action_payload(attempt),
        }
        _post_json(
            payments_url,
            payment_payload,
            timeout_seconds=timeout_seconds,
            bearer_token=capability,
        )

    outcome, receipt = execute_protected_consequence_with_receipt(
        permit=permit,
        attempted_action_binding_hash=attempted_binding,
        before_formation_hook=release_and_form_external_consequence,
    )
    return outcome, receipt, released["token"]
