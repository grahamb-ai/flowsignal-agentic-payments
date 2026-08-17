"""
AT-003.2 — Protected Execution (translated to current boundary)

The original v0.10 test module targeted ProtectedPaymentState and
execute_protected_payment(), which have since been superseded. These tests
preserve the historical proof obligations against the current
ExecutionGateway + ExecutionPermit + protected consequence boundary.
"""
from datetime import timedelta
from pathlib import Path

from harness.runner import load_scenario
from app.engines.financial_runtime import evaluate_financial
from app.engines.execution_gateway import (
    ExecutionAttempt,
    action_binding_hash,
    validate_execution,
)
from app.engines.protected_consequence import execute_protected_consequence


ALLOW_SCENARIO = Path("harness/scenarios/AP-001_allow.json")
REFUSE_SCENARIO = Path("harness/scenarios/AP-003_post_approval_counterparty_change.json")


def _make_attempt(request, *, beneficiary=None, attempted_at=None):
    return ExecutionAttempt(
        actor_id=request.actor_id,
        principal_id=request.principal_id,
        action=request.action,
        target=request.target,
        amount=request.amount,
        currency=request.currency,
        source_account=request.source_account,
        beneficiary=beneficiary or request.beneficiary,
        purpose=request.purpose,
        mandate_id=request.mandate_id,
        attempted_at=attempted_at or request.requested_execution_time,
    )


def test_at003_2_valid_allow_forms_protected_consequence():
    request = load_scenario(ALLOW_SCENARIO)
    response, receipt = evaluate_financial(request)
    assert response.decision == "ALLOW"

    attempt = _make_attempt(request)
    gateway = validate_execution(receipt, attempt)

    assert gateway.status == "PERMITTED"
    assert gateway.execution_permit is not None

    consequence = execute_protected_consequence(
        gateway.execution_permit,
        action_binding_hash(attempt),
    )
    assert consequence == "CONSEQUENCE_FORMED"


def test_at003_2_mismatched_action_is_blocked():
    request = load_scenario(ALLOW_SCENARIO)
    response, receipt = evaluate_financial(request)
    assert response.decision == "ALLOW"

    attempt = _make_attempt(request, beneficiary="SUBSTITUTED-BENEFICIARY")
    gateway = validate_execution(receipt, attempt)

    assert gateway.status == "BLOCKED"
    assert gateway.reason_code == "ACTION_BINDING_MISMATCH"
    assert gateway.execution_permit is None

    consequence = execute_protected_consequence(
        gateway.execution_permit,
        action_binding_hash(attempt),
    )
    assert consequence == "DENIED_NO_EXECUTION_PERMIT"


def test_at003_2_expired_allow_is_blocked():
    request = load_scenario(ALLOW_SCENARIO)
    response, receipt = evaluate_financial(request)
    assert response.decision == "ALLOW"

    # Preserve the integrity-sealed receipt and move only the execution attempt
    # beyond the receipt validity window.
    attempt = _make_attempt(
        request,
        attempted_at=receipt.valid_until + timedelta(seconds=1),
    )
    gateway = validate_execution(receipt, attempt)

    assert gateway.status == "BLOCKED"
    assert gateway.reason_code == "AUTHORITY_DETERMINATION_EXPIRED"
    assert gateway.execution_permit is None


def test_at003_2_native_refuse_is_blocked():
    request = load_scenario(REFUSE_SCENARIO)
    response, receipt = evaluate_financial(request)
    assert response.decision == "REFUSE"

    # Use the natively issued, integrity-valid REFUSE receipt rather than
    # mutating a sealed ALLOW receipt after issuance.
    attempt = _make_attempt(request)
    gateway = validate_execution(receipt, attempt)

    assert gateway.status == "BLOCKED"
    assert gateway.reason_code == "NO_APPLICABLE_ALLOW"
    assert gateway.execution_permit is None
