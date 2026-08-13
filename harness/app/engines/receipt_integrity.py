from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from typing import Any


# Harness-only shared integrity key.
# This demonstrates keyed receipt verification; it is not production key management.
# TEST HARNESS ONLY.
# This fixed key exists solely to demonstrate receipt-integrity behaviour
# in the public proof-of-concept. It is not a production secret, key-management
# mechanism, trust boundary, or recommended deployment pattern.
# Production implementations require externally managed protected key material.
_RECEIPT_HMAC_KEY = b"flowsignal-at0044-harness-key"


def _utc_text(value: datetime | None) -> str | None:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat()


def _normalise(value: Any) -> Any:
    if isinstance(value, datetime):
        return _utc_text(value)

    if is_dataclass(value):
        return _normalise(asdict(value))

    if isinstance(value, dict):
        return {
            str(key): _normalise(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }

    if isinstance(value, (list, tuple)):
        return [_normalise(item) for item in value]

    return value


def compute_receipt_hmac(
    *,
    receipt_id: str,
    scenario_id: str,
    decision: str,
    reason_code: str,
    sealed_at: datetime,
    valid_until: datetime | None,
    action_binding_hash: str,
    authority_state_version: int,
    request_snapshot: dict,
    checks: list,
    evidence_references: list,
) -> str:
    payload = {
        "receipt_id": receipt_id,
        "scenario_id": scenario_id,
        "decision": decision,
        "reason_code": reason_code,
        "sealed_at": _utc_text(sealed_at),
        "valid_until": _utc_text(valid_until),
        "action_binding_hash": action_binding_hash,
        "authority_state_version": authority_state_version,
        "request_snapshot": _normalise(request_snapshot),
        "checks": _normalise(checks),
        "evidence_references": _normalise(evidence_references),
    }

    raw = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hmac.new(
        _RECEIPT_HMAC_KEY,
        raw,
        hashlib.sha256,
    ).hexdigest()


def verify_receipt_hmac(receipt) -> bool:
    expected = compute_receipt_hmac(
        receipt_id=receipt.id,
        scenario_id=receipt.scenario_id,
        decision=receipt.decision,
        reason_code=receipt.reason_code,
        sealed_at=receipt.sealed_at,
        valid_until=receipt.valid_until,
        action_binding_hash=receipt.action_binding_hash,
        authority_state_version=receipt.authority_state_version,
        request_snapshot=receipt.request_snapshot,
        checks=receipt.checks,
        evidence_references=receipt.evidence_references,
    )

    return hmac.compare_digest(
        receipt.receipt_hmac,
        expected,
    )