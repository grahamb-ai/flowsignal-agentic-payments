from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable

from app.engines.authority_store import (
    authority_state_guard,
    get_authority_state_version_unlocked,
)
from app.engines.consequence_receipt import (
    ConsequenceOutcomeReceipt,
    create_consequence_outcome_receipt,
)
from app.engines.permit_authority import ExecutionPermit, verify_execution_permit


# In-process one-time-consumption registry for execution permits. The registry
# remains bounded to the lifetime of this reference process. Durable duplicate
# suppression across restart or multiple instances is a separate proof burden.
_CONSUMED_PERMIT_SIGNATURES: set[str] = set()


def _aware(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def execute_protected_consequence(
    permit: ExecutionPermit | None,
    attempted_action_binding_hash: str,
    *,
    before_formation_hook: Callable[[], None] | None = None,
) -> str:
    """Consume, but do not mint, a consequence-authorising execution permit.

    Permit issuance/signing lives in the separate reference permit-authority
    component. This represented execution component verifies the permit, checks
    exact action binding and temporal/current-state standing, enforces one-time
    use and forms the represented consequence.

    The separation is a reference component/module boundary. It is not claimed
    as production process/IAM/KMS/HSM isolation.
    """
    if permit is None:
        return "DENIED_NO_EXECUTION_PERMIT"

    if not verify_execution_permit(permit):
        return "DENIED_INVALID_EXECUTION_PERMIT"

    if permit.action_binding_hash != attempted_action_binding_hash:
        return "DENIED_ACTION_BINDING_MISMATCH"

    if permit.valid_until is None:
        return "DENIED_EXECUTION_PERMIT_EXPIRY_MISSING"

    try:
        permit_expiry = _aware(datetime.fromisoformat(permit.valid_until))
    except (TypeError, ValueError):
        return "DENIED_EXECUTION_PERMIT_EXPIRY_INVALID"

    if datetime.now(timezone.utc) > permit_expiry:
        return "DENIED_EXECUTION_PERMIT_EXPIRED"

    with authority_state_guard():
        current_authority_state_version = get_authority_state_version_unlocked()
        if permit.authority_state_version != current_authority_state_version:
            return "DENIED_AUTHORITY_STATE_STALE"

        if permit.signature in _CONSUMED_PERMIT_SIGNATURES:
            return "DENIED_EXECUTION_PERMIT_REPLAY"

        _CONSUMED_PERMIT_SIGNATURES.add(permit.signature)

        if before_formation_hook is not None:
            before_formation_hook()

        return "CONSEQUENCE_FORMED"


def execute_protected_consequence_with_receipt(
    permit: ExecutionPermit | None,
    attempted_action_binding_hash: str,
    *,
    before_formation_hook: Callable[[], None] | None = None,
) -> tuple[str, ConsequenceOutcomeReceipt]:
    outcome = execute_protected_consequence(
        permit=permit,
        attempted_action_binding_hash=attempted_action_binding_hash,
        before_formation_hook=before_formation_hook,
    )
    receipt = create_consequence_outcome_receipt(
        authority_receipt_id=(permit.authority_receipt_id if permit is not None else None),
        action_binding_hash=attempted_action_binding_hash,
        authority_state_version=(permit.authority_state_version if permit is not None else None),
        outcome=outcome,
    )
    return outcome, receipt
