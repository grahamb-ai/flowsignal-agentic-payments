from __future__ import annotations

import hashlib
import hmac
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable

from app.engines.authority_store import (
    authority_state_guard,
    get_authority_state_version_unlocked,
)


# Reference-harness boundary secret. Production deployments MUST source this
# from a dedicated secret/KMS boundary inaccessible to the proposing executor.
_PERMIT_KEY = os.environ.get(
    "FLOWSIGNAL_EXECUTION_PERMIT_KEY",
    "flowsignal-reference-harness-ec0014-key",
).encode("utf-8")

# In-process reference capability used only to prevent the public permit issuer
# from being independently usable without the governed gateway path. This is
# deliberately NOT described as production-grade process/IAM/KMS isolation.
_GATEWAY_MINT_CAPABILITY = object()

# In-process one-time-consumption registry for execution permits. The registry
# is intentionally bounded to the lifetime of this reference process. Durable
# duplicate suppression across restarts or multiple service instances remains a
# separate production proof obligation.
_CONSUMED_PERMIT_SIGNATURES: set[str] = set()


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
    *,
    mint_capability: object | None = None,
) -> ExecutionPermit | None:
    """Mint a consequence capability only for the governed gateway path.

    Direct callers that do not possess the exact in-process gateway capability
    receive no permit. This closes the specific PMQ-001 no-bind bypass on the
    public reference harness surface, while leaving production-grade capability
    isolation as a separate proof obligation.
    """
    if mint_capability is not _GATEWAY_MINT_CAPABILITY:
        return None

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
    *,
    before_formation_hook: Callable[[], None] | None = None,
) -> str:
    """Form the represented consequence inside the final authority-state guard.

    Permit consumption is serialized inside the same in-process authority-state
    guard as the final standing read and represented consequence formation. This
    means one valid permit can form at most one represented consequence during
    the lifetime of the reference process.

    The optional hook exists only to make the critical interval observable to
    adversarial tests. Authority-state advancement uses the same guard, so it
    cannot commit between this function's final standing read and represented
    consequence formation.
    """
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

    with authority_state_guard():
        current_authority_state_version = get_authority_state_version_unlocked()
        if permit.authority_state_version != current_authority_state_version:
            return "DENIED_AUTHORITY_STATE_STALE"

        if permit.signature in _CONSUMED_PERMIT_SIGNATURES:
            return "DENIED_EXECUTION_PERMIT_REPLAY"

        # Mark consumed before the represented formation step so duplicate or
        # concurrent retries fail closed. If a later formation step were to
        # raise, this reference harness deliberately does not make the permit
        # reusable; recovery/idempotency across real external rails is a
        # separate integration obligation.
        _CONSUMED_PERMIT_SIGNATURES.add(permit.signature)

        if before_formation_hook is not None:
            before_formation_hook()

        return "CONSEQUENCE_FORMED"
