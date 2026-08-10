"""
AT-003 — Executor Binding

Adversarial test against the preserved v0.9 baseline.

Purpose:
Determine whether a protected financial consequence can occur without
a valid current ALLOW determination being consumed by the executor.

This test does not modify the v0.9 Runtime Authority implementation.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ProtectedPaymentState:
    executed: bool = False
    amount: float = 0.0
    beneficiary: Optional[str] = None


def legacy_payment_executor(
    state: ProtectedPaymentState,
    amount: float,
    beneficiary: str,
) -> None:
    """
    Represents an execution path that does not consume a Runtime
    Authority determination.

    This deliberately models the adversarial question raised by AT-003:
    can the protected consequence be produced independently of the
    Runtime Authority result?
    """
    state.executed = True
    state.amount = amount
    state.beneficiary = beneficiary


def test_at003_execution_without_authority_determination():
    """
    AT-003.1

    Attempt execution without supplying any Runtime Authority
    determination.

    Required invariant:

        NO VALID CURRENT ALLOW -> NO EXECUTION

    This test is expected to expose a control-boundary gap in the
    v0.9 baseline if execution remains possible independently of
    Runtime Authority.
    """

    protected_state = ProtectedPaymentState()

    legacy_payment_executor(
        protected_state,
        amount=25000.00,
        beneficiary="supplier-001",
    )

    assert protected_state.executed is False, (
        "AT-003 FAILURE: protected financial consequence occurred "
        "without a valid current ALLOW determination."
    )
