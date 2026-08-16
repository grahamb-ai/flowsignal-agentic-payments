from __future__ import annotations

from dataclasses import dataclass

from app.engines.financial_types import AuthorityReceipt
from app.engines.receipt_integrity import verify_receipt_hmac


@dataclass
class ReplayResult:
    decision: str
    reason_code: str
    authority_state_version: int
    action_binding_hash: str
    receipt_integrity_valid: bool


def replay_authority_receipt(receipt: AuthorityReceipt) -> ReplayResult:
    """
    Reconstruct the preserved historical Runtime Authority determination
    from the sealed Authority Receipt.

    Replay deliberately does not consult current authority state and does
    not perform a fresh Runtime Authority evaluation.

    It verifies the integrity of the preserved receipt and returns the
    historical determination bound into that receipt.
    """

    integrity_valid = verify_receipt_hmac(receipt)

    if not integrity_valid:
        raise ValueError("Historical Authority Receipt integrity validation failed")

    return ReplayResult(
        decision=receipt.decision,
        reason_code=receipt.reason_code,
        authority_state_version=receipt.authority_state_version,
        action_binding_hash=receipt.action_binding_hash,
        receipt_integrity_valid=True,
    )