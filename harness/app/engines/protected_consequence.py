from __future__ import annotations

import hashlib
import hmac
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone


# Reference-harness boundary secret. Production deployments MUST source this
# from a dedicated secret/KMS boundary inaccessible to the proposing executor.
_PERMIT_KEY = os.environ.get(
    "FLOWSIGNAL_EXECUTION_PERMIT_KEY",
    "flowsignal-reference-harness-ec0014-key",
).encode("utf-8")


@dataclass(frozen=True)
class ExecutionPermit:
    authority_receipt_id: str
    action_binding_hash: str
    authority_state_version: int
    issued_at: str
    signature: str


def _payload(
    authority_receipt_id: str,
    action_binding_hash: str,
    authority_state_version: int,
    issued_at: str,
) -> bytes:
    return json.dumps(
        {
            "authority_receipt_id": authority_receipt_id,
            "action_binding_hash": action_binding_hash,
            "authority_state_version": authority_state_version,
            "issued_at": issued_at,
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _sign(
    authority_receipt_id: str,
    action_binding_hash: str,
    authority_state_version: int,
    issued_at: str,
) -> str:
    return hmac.new(
        _PERMIT_KEY,
        _payload(
            authority_receipt_id,
            action_binding_hash,
            authority_state_version,
            issued_at,
        ),
        hashlib.sha256,
    ).hexdigest()


def issue_execution_permit(
    authority_receipt_id: str,
    action_binding_hash: str,
    authority_state_version: int,
) -> ExecutionPermit:
    """Mint a consequence capability after the Execution Gateway permits.

    This function represents the protected gateway-side capability minting
    boundary. It is not exposed through the executor-facing API.
    """
    issued_at = datetime.now(timezone.utc).isoformat()
    return ExecutionPermit(
        authority_receipt_id=authority_receipt_id,
        action_binding_hash=action_binding_hash,
        authority_state_version=authority_state_version,
        issued_at=issued_at,
        signature=_sign(
            authority_receipt_id,
            action_binding_hash,
            authority_state_version,
            issued_at,
        ),
    )


def execute_protected_consequence(
    permit: ExecutionPermit | None,
    attempted_action_binding_hash: str,
    current_authority_state_version: int,
) -> str:
    """Represent consequence formation behind a cryptographic permit boundary."""
    if permit is None:
        return "DENIED_NO_EXECUTION_PERMIT"

    expected = _sign(
        permit.authority_receipt_id,
        permit.action_binding_hash,
        permit.authority_state_version,
        permit.issued_at,
    )
    if not hmac.compare_digest(expected, permit.signature):
        return "DENIED_INVALID_EXECUTION_PERMIT"

    if permit.action_binding_hash != attempted_action_binding_hash:
        return "DENIED_ACTION_BINDING_MISMATCH"

    if permit.authority_state_version != current_authority_state_version:
        return "DENIED_AUTHORITY_STATE_STALE"

    return "CONSEQUENCE_FORMED"
