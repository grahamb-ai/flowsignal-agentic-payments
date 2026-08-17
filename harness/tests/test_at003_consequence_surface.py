"""
AT-003.3 — Consequence-Surface Closure (translated to current boundary)

Historical proof obligation:
Determine whether the protected financial consequence remains reachable
through an alternative execution path that does not consume the applicable
Runtime Authority determination.

The original v0.10 test targeted ProtectedPaymentState, which no longer exists.
This translation preserves the proof obligation against the current protected
consequence interface.
"""
from app.engines.execution_gateway import ExecutionAttempt, action_binding_hash
from app.engines.protected_consequence import execute_protected_consequence


def test_at003_3_alternative_path_without_permit_cannot_form_protected_consequence():
    attempted = ExecutionAttempt(
        actor_id="actor-001",
        principal_id="principal-001",
        action="PAY",
        target="supplier-001",
        amount=25000.00,
        currency="GBP",
        source_account="treasury-001",
        beneficiary="supplier-001",
        purpose="historical AT-003.3 reconciliation",
        mandate_id="MANDATE-TREASURY-001",
        attempted_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
    )

    result = execute_protected_consequence(
        permit=None,
        attempted_action_binding_hash=action_binding_hash(attempted),
    )

    assert result == "DENIED_NO_EXECUTION_PERMIT"
