"""
AT-003.3 — Consequence-Surface Closure

Adversarial test against the strengthened AT-003 execution boundary.

Purpose:
Determine whether the protected financial consequence remains reachable
through an alternative execution path that does not consume the applicable
Runtime Authority determination.

This test deliberately does not modify the Runtime Authority implementation.
"""
import pytest
from dataclasses import FrozenInstanceError

from app.engines.execution_gateway import ProtectedPaymentState


def alternative_payment_path(
    state: ProtectedPaymentState,
    *,
    amount: float,
    beneficiary: str,
) -> None:
    """
    Represents an alternative consequence-producing path.

    Critically, this path does not consume an AuthorityReceipt and does not
    invoke execute_protected_payment() or validate_execution().

    AT-003.3 asks whether the protected consequence remains reachable when
    such a path exists.
    """
    state.executed = True
    state.amount = amount
    state.beneficiary = beneficiary


def test_at003_3_alternative_path_cannot_produce_protected_consequence():
    """
    The protected financial consequence must not be reachable independently
    of the Runtime Authority enforcement dependency.

    Expected property:

        NO SUCCESSFUL AUTHORITY VALIDATION -> NO PROTECTED FINANCIAL CONSEQUENCE
    """

    protected_state = ProtectedPaymentState()

 with pytest.raises(FrozenInstanceError):
    alternative_payment_path(
        protected_state,
        amount=25000.00,
        beneficiary="supplier-001",
    )

assert protected_state.executed is False
assert protected_state.amount == 0.0
assert protected_state.beneficiary == ""
assert protected_state.authority_receipt_id == ""
       
