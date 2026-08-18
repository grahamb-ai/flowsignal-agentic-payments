from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable

from app.engines.authority_store import (
    authority_state_guard,
    get_authority_state_version_unlocked,
)
from app.engines.consequence_outcome_store import record_consequence_outcome
from app.engines.consequence_receipt import (
    ConsequenceOutcomeReceipt,
    create_consequence_outcome_receipt,
)
from app.engines.permit_authority import ExecutionPermit, verify_execution_permit
from app.engines.permit_consumption_store import consume_execution_permit_and_begin_outcome_once


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
    exact action binding and temporal/current-state standing, and establishes
    durable permit consumption together with an initial unresolved execution
    outcome before entering the remaining consequence-formation interval.

    Temporal standing is checked once before waiting for the final authority
    boundary and again immediately after that boundary is acquired. This closes
    the represented expiry time-of-check/time-of-use interval exercised by
    PMQ-002.4.

    PMQ-002.9 demonstrated that separate commits for permit consumption and the
    first outcome record leave a crash window. The reference SQLite mechanism
    now commits permit consumption and CONSEQUENCE_OUTCOME_UNRESOLVED together
    through one attached-database transaction before formation proceeds.

    A normal represented failure before formation replaces the unresolved state
    with CONSEQUENCE_NOT_FORMED; successful represented formation replaces it
    with CONSEQUENCE_FORMED. Abrupt termination after the initial transaction
    therefore leaves an explicit unresolved state for recovery.

    This is a reference-MVP local SQLite boundary. It is not claimed as
    production distributed transactionality, database HA, cross-host atomicity,
    fsync/power-loss durability, write-once audit, external payment idempotency
    or production process/IAM/KMS/HSM isolation.
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
        if datetime.now(timezone.utc) > permit_expiry:
            return "DENIED_EXECUTION_PERMIT_EXPIRED"

        current_authority_state_version = get_authority_state_version_unlocked()
        if permit.authority_state_version != current_authority_state_version:
            return "DENIED_AUTHORITY_STATE_STALE"

        if not consume_execution_permit_and_begin_outcome_once(
            permit.signature,
            attempted_action_binding_hash,
        ):
            return "DENIED_EXECUTION_PERMIT_REPLAY"

        if before_formation_hook is not None:
            try:
                before_formation_hook()
            except Exception:
                record_consequence_outcome(
                    permit_signature=permit.signature,
                    action_binding_hash=attempted_action_binding_hash,
                    outcome="CONSEQUENCE_NOT_FORMED",
                )
                raise

        record_consequence_outcome(
            permit_signature=permit.signature,
            action_binding_hash=attempted_action_binding_hash,
            outcome="CONSEQUENCE_FORMED",
        )

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
