from __future__ import annotations

import json
from urllib import request

from app.engines.execution_gateway import ExecutionAttempt, action_binding_hash
from app.engines.protected_consequence import execute_protected_consequence_with_receipt
from app.engines.permit_authority import ExecutionPermit


def _external_payload(attempt: ExecutionAttempt, permit: ExecutionPermit) -> dict:
    return {
        "transaction_id": permit.signature,
        "source_account": attempt.source_account,
        "beneficiary": attempt.beneficiary,
        "amount": attempt.amount,
        "currency": attempt.currency,
        "purpose": attempt.purpose,
    }


def _post_json(url: str, payload: dict, timeout_seconds: float) -> dict:
    body = json.dumps(payload, sort_keys=True).encode("utf-8")
    req = request.Request(
        url,
        data=body,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    with request.urlopen(req, timeout=timeout_seconds) as response:
        raw = response.read()
        if response.status < 200 or response.status >= 300:
            raise RuntimeError(f"external consequence target returned {response.status}")
        return json.loads(raw.decode("utf-8")) if raw else {}


def execute_external_payment(
    *,
    permit: ExecutionPermit | None,
    attempt: ExecutionAttempt,
    payments_url: str,
    timeout_seconds: float = 2.0,
):
    """Attempt one external payment only inside the protected formation interval.

    The exact action binding is recomputed from the attempted external action.
    The HTTP state mutation is invoked through `before_formation_hook`, which is
    reached only after the existing protected-consequence boundary has verified
    permit integrity, exact action binding, expiry, current authority-state
    version, rollback anchor and one-time permit consumption.

    This adapter does not claim that the external service has no other credentials
    or administrative mutation routes. CBP-002 separately observes and documents
    the closure boundary provided by this integration.
    """

    attempted_binding = action_binding_hash(attempt)

    def form_external_consequence() -> None:
        if permit is None:
            raise RuntimeError("external consequence hook reached without permit")
        _post_json(
            payments_url,
            _external_payload(attempt, permit),
            timeout_seconds=timeout_seconds,
        )

    return execute_protected_consequence_with_receipt(
        permit=permit,
        attempted_action_binding_hash=attempted_binding,
        before_formation_hook=form_external_consequence,
    )
