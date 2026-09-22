from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.engines.action_binding import action_binding_hash, canonical_action_object


EC009_ACCOUNT = "acct_1U06JYL6P3J1guFB"
EC009_TARGET = f"stripe:test:{EC009_ACCOUNT}:payment_intent.create"


def stripe_payment_intent_projection(action: Any) -> dict[str, Any]:
    canonical = canonical_action_object(action)
    if canonical["action"] != "payment.collect":
        raise ValueError("EC-009 requires payment.collect")
    if canonical["target"] != EC009_TARGET:
        raise ValueError("EC-009 target mismatch")
    if canonical["beneficiary"] != EC009_ACCOUNT:
        raise ValueError("EC-009 beneficiary mismatch")
    if canonical["source_account"] != "pm_card_visa":
        raise ValueError("EC-009 payment source mismatch")
    return {
        "amount": canonical["amount_minor"],
        "currency": canonical["currency"].lower(),
        "payment_method": canonical["source_account"],
        "payment_method_types": ["card"],
        "confirm": True,
        "description": canonical["purpose"],
        "metadata": {
            "flowsignal_action_binding_hash": action_binding_hash(action),
            "flowsignal_mandate_id": canonical["mandate_id"],
            "flowsignal_beneficiary": canonical["beneficiary"],
            "flowsignal_target": canonical["target"],
        },
    }


def cap_downstream_expiry(upstream_valid_until: datetime, requested_ttl_seconds: int, *, now: datetime) -> datetime:
    if requested_ttl_seconds <= 0:
        raise ValueError("requested TTL must be positive")
    if now.tzinfo is None or upstream_valid_until.tzinfo is None:
        raise ValueError("expiry values must be timezone-aware")
    candidate = now.astimezone(timezone.utc).timestamp() + requested_ttl_seconds
    requested = datetime.fromtimestamp(candidate, tz=timezone.utc)
    return min(upstream_valid_until.astimezone(timezone.utc), requested)
