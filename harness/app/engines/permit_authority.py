from __future__ import annotations

import hashlib
import hmac
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone


# Reference-harness permit-authority secret. This is deliberately located in the
# permit-authority component rather than the represented consequence executor.
# Production deployments require an actual isolated process/service and
# externally managed protected key material.
_PERMIT_KEY = os.environ.get(
    "FLOWSIGNAL_EXECUTION_PERMIT_KEY",
    "flowsignal-reference-harness-ec0014-key",
).encode("utf-8")

# Reference gateway capability. It prevents ordinary callers from using the
# issuer directly on the public module path. It is not production IAM/KMS.
_GATEWAY_MINT_CAPABILITY = object()


@dataclass(frozen=True)
class ExecutionPermit:
    authority_receipt_id: str
    action_binding_hash: str
    authority_state_version: int
    issued_at: str
    signature: str
    valid_until: str | None = None


def _payload(
    authority_receipt_id: str,
    action_binding_hash: str,
    authority_state_version: int,
    issued_at: str,
    valid_until: str | None,
) -> bytes:
    return json.dumps(
        {
            "authority_receipt_id": authority_receipt_id,
            "action_binding_hash": action_binding_hash,
            "authority_state_version": authority_state_version,
            "issued_at": issued_at,
            "valid_until": valid_until,
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _sign(
    authority_receipt_id: str,
    action_binding_hash: str,
    authority_state_version: int,
    issued_at: str,
    valid_until: str | None,
) -> str:
    return hmac.new(
        _PERMIT_KEY,
        _payload(
            authority_receipt_id,
            action_binding_hash,
            authority_state_version,
            issued_at,
            valid_until,
        ),
        hashlib.sha256,
    ).hexdigest()


def issue_execution_permit(
    authority_receipt_id: str,
    action_binding_hash: str,
    authority_state_version: int,
    *,
    valid_until: str | None = None,
    mint_capability: object | None = None,
) -> ExecutionPermit | None:
    if mint_capability is not _GATEWAY_MINT_CAPABILITY:
        return None
    if valid_until is None:
        return None

    issued_at = datetime.now(timezone.utc).isoformat()
    return ExecutionPermit(
        authority_receipt_id=authority_receipt_id,
        action_binding_hash=action_binding_hash,
        authority_state_version=authority_state_version,
        issued_at=issued_at,
        valid_until=valid_until,
        signature=_sign(
            authority_receipt_id,
            action_binding_hash,
            authority_state_version,
            issued_at,
            valid_until,
        ),
    )


def verify_execution_permit(permit: ExecutionPermit) -> bool:
    expected = _sign(
        permit.authority_receipt_id,
        permit.action_binding_hash,
        permit.authority_state_version,
        permit.issued_at,
        permit.valid_until,
    )
    return hmac.compare_digest(expected, permit.signature)
