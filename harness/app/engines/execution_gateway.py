from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone

from app.engines.financial_types import AuthorityReceipt


@dataclass
class ExecutionAttempt:
    actor_id: str
    principal_id: str
    action: str
    target: str
    amount: float
    currency: str
    source_account: str
    beneficiary: str
    purpose: str
    mandate_id: str
    attempted_at: datetime


@dataclass
class GatewayResult:
    status: str
    reason_code: str
    authority_receipt_id: str
    expected_action_binding_hash: str
    attempted_action_binding_hash: str


def _aware(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def action_binding_hash(attempt: ExecutionAttempt) -> str:
    payload = {
        "actor_id": attempt.actor_id,
        "principal_id": attempt.principal_id,
        "action": attempt.action,
        "target": attempt.target,
        "amount": attempt.amount,
        "currency": attempt.currency,
        "source_account": attempt.source_account,
        "beneficiary": attempt.beneficiary,
        "purpose": attempt.purpose,
        "mandate_id": attempt.mandate_id,
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def validate_execution(
    receipt: AuthorityReceipt,
    attempt: ExecutionAttempt,
) -> GatewayResult:
    attempted_hash = action_binding_hash(attempt)

    if receipt.decision != "ALLOW":
        return GatewayResult(
            status="BLOCKED",
            reason_code="NO_APPLICABLE_ALLOW",
            authority_receipt_id=receipt.id,
            expected_action_binding_hash=receipt.action_binding_hash,
            attempted_action_binding_hash=attempted_hash,
        )

    if receipt.valid_until is None or _aware(attempt.attempted_at) > _aware(receipt.valid_until):
        return GatewayResult(
            status="BLOCKED",
            reason_code="AUTHORITY_DETERMINATION_EXPIRED",
            authority_receipt_id=receipt.id,
            expected_action_binding_hash=receipt.action_binding_hash,
            attempted_action_binding_hash=attempted_hash,
        )

    if attempted_hash != receipt.action_binding_hash:
        return GatewayResult(
            status="BLOCKED",
            reason_code="ACTION_BINDING_MISMATCH",
            authority_receipt_id=receipt.id,
            expected_action_binding_hash=receipt.action_binding_hash,
            attempted_action_binding_hash=attempted_hash,
        )

    return GatewayResult(
        status="PERMITTED",
        reason_code="BOUND_ALLOW_VALID",
        authority_receipt_id=receipt.id,
        expected_action_binding_hash=receipt.action_binding_hash,
        attempted_action_binding_hash=attempted_hash,
    )
@dataclass(frozen=True)
class ProtectedPaymentState:
    executed: bool = False
    amount: float = 0.0
    beneficiary: str = ""
    authority_receipt_id: str = ""


def execute_protected_payment(
    state: ProtectedPaymentState,
    receipt: AuthorityReceipt,
    attempt: ExecutionAttempt,
) -> tuple[GatewayResult, ProtectedPaymentState]:
    """
    v0.10 protected execution path.

    The protected financial consequence is produced only after the
    applicable Runtime Authority determination has been successfully
    validated by the execution gateway.

    This function deliberately separates:

        determination -> gateway validation -> consequence formation

    A BLOCKED gateway result must leave protected state unchanged.
    """

    gateway_result = validate_execution(receipt, attempt)


if gateway_result.status != "PERMITTED":
    return gateway_result, state

new_state = ProtectedPaymentState(
    executed=True,
    amount=attempt.amount,
    beneficiary=attempt.beneficiary,
    authority_receipt_id=receipt.id,
)

return gateway_result, new_state
