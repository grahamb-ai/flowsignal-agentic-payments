from __future__ import annotations

import hashlib
import json
from decimal import Decimal, InvalidOperation
from typing import Any


_CURRENCY_EXPONENTS = {"GBP": 2, "USD": 2}
EC009_MANDATE_ID = "MANDATE-EC009-STRIPE-USD-001"


def amount_to_minor_units(amount: Any, currency: str) -> int:
    """Convert a major-unit amount without accepting lossy rounding."""
    code = currency.upper()
    if code not in _CURRENCY_EXPONENTS:
        raise ValueError(f"unsupported currency exponent: {code}")
    try:
        major = Decimal(str(amount))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("invalid monetary amount") from exc
    scale = Decimal(10) ** _CURRENCY_EXPONENTS[code]
    minor = major * scale
    if not minor.is_finite() or minor != minor.to_integral_value():
        raise ValueError("amount is not exactly representable in minor units")
    return int(minor)


def canonical_action_object(value: Any) -> dict[str, Any]:
    currency = str(value.currency).upper()
    return {
        "schema": "flowsignal.canonical-payment-action.v1",
        "actor_id": value.actor_id,
        "principal_id": value.principal_id,
        "action": value.action,
        "target": value.target,
        "amount_minor": amount_to_minor_units(value.amount, currency),
        "currency": currency,
        "source_account": value.source_account,
        "beneficiary": value.beneficiary,
        "purpose": value.purpose,
        "mandate_id": value.mandate_id,
    }


def canonical_action_bytes(value: Any) -> bytes:
    return json.dumps(
        canonical_action_object(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def action_binding_hash(value: Any) -> str:
    if value.mandate_id == EC009_MANDATE_ID:
        raw = canonical_action_bytes(value)
    else:
        # Preserve the existing receipt/evidence format for pre-EC-009 scenarios.
        payload = {
            "actor_id": value.actor_id,
            "principal_id": value.principal_id,
            "action": value.action,
            "target": value.target,
            "amount": value.amount,
            "currency": value.currency,
            "source_account": value.source_account,
            "beneficiary": value.beneficiary,
            "purpose": value.purpose,
            "mandate_id": value.mandate_id,
        }
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()
