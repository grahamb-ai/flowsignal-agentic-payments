from __future__ import annotations

import json
from urllib import request

from app.engines.execution_gateway import ExecutionAttempt, action_binding_hash
from app.engines.protected_consequence import (
    ExternalOutcomeUnknown,
    ProviderCommitRefused,
    execute_protected_consequence_with_receipt,
)
from app.engines.permit_authority import ExecutionPermit


def _external_payload(attempt: ExecutionAttempt, permit: ExecutionPermit, institutional_authorization: dict | None = None) -> dict:
    if not (permit.payment_intent_id and permit.provider_mandate_id == attempt.mandate_id
            and type(permit.provider_authority_epoch) is int and permit.provider_authority_epoch > 0):
        raise ValueError("signed provider authority and business payment intent required")
    payload = {
        "transaction_id": permit.payment_intent_id,
        "payment_intent_id": permit.payment_intent_id,
        "mandate_id": permit.provider_mandate_id,
        "authority_epoch": permit.provider_authority_epoch,
        "source_account": attempt.source_account,
        "beneficiary": attempt.beneficiary,
        "amount": attempt.amount,
        "currency": attempt.currency,
        "purpose": attempt.purpose,
        "action": attempt.action,
        "target": attempt.target,
    }
    if institutional_authorization is not None:
        payload["institutional_authorization"] = institutional_authorization
    return payload


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
    institutional_authorization: dict | None = None,
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
        try:
            provider_result = _post_json(
                payments_url,
                _external_payload(attempt, permit, institutional_authorization),
                timeout_seconds=timeout_seconds,
            )
            if not isinstance(provider_result, dict):
                raise ExternalOutcomeUnknown("provider response is not a structured outcome")
            status = provider_result.get("status")
            if status in ("REFUSED_AUTHORITY", "REFUSED_DUPLICATE_INTENT"):
                # BOUNDED: configured cooperating provider status, not signed evidence.
                raise ProviderCommitRefused(status)
            if status not in ("COMMITTED", "TRANSFER_RECORDED"):
                raise ExternalOutcomeUnknown("provider outcome is unrecognised")
        except (ProviderCommitRefused, ExternalOutcomeUnknown):
            raise
        except Exception as exc:
            # A transport/HTTP failure cannot establish provider non-commitment.
            raise ExternalOutcomeUnknown("external payment outcome requires reconciliation") from exc

    return execute_protected_consequence_with_receipt(
        permit=permit,
        attempted_action_binding_hash=attempted_binding,
        before_formation_hook=form_external_consequence,
    )
