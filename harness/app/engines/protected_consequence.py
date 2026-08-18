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
from app.engines.rollback_anchor_store import claim_execution_anchor_once


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

    PMQ-002.9 commits permit consumption and CONSEQUENCE_OUTCOME_UNRESOLVED
    together through one attached-database transaction.

    PMQ-002.10 adds a separate surviving rollback anchor. Ordinary replay remains
    distinguishable from rollback: if the anchor already exists and the durable
    permit store also reports the permit consumed, the result remains the prior
    DENIED_EXECUTION_PERMIT_REPLAY. If the anchor already exists but the restored
    execution-state stores accept the permit as apparently unused, execution is
    stopped as DENIED_EXECUTION_STATE_ROLLBACK_OR_REPLAY before consequence
    formation.

    This is a reference-MVP local SQLite boundary. The rollback anchor only
    demonstrates detection when that separate anchor survives rollback of the
    permit-consumption and consequence-outcome stores. It is not claimed as
    resistance to rollback of all local state, production distributed
    transactionality, database HA, cross-host atomicity, fsync/power-loss
    durability, immutable/write-once audit, external payment idempotency or
    production process/IAM/KMS/HSM isolation.
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

        anchor_was_new = claim_execution_anchor_once(
            permit_signature=permit.signature,
            action_binding_hash=attempted_action_binding_hash,
        )

        consumption_was_new = consume_execution_permit_and_begin_outcome_once(
            permit.signature,
            attempted_action_binding_hash,
        )

        if not consumption_was_new:
            return "DENIED_EXECUTION_PERMIT_REPLAY"

        if not anchor_was_new:
            # The separate anchor remembers this execution while the restored
            # execution-state stores have accepted it as new. The consumption
            # transaction has safely re-established an unresolved record, but
            # represented consequence formation must stop here.
            return "DENIED_EXECUTION_STATE_ROLLBACK_OR_REPLAY"

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
