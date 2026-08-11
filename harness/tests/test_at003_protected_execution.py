from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from harness.runner import load_scenario
from app.engines.financial_runtime import evaluate_financial
from app.engines.execution_gateway import (
    ExecutionAttempt,
    ProtectedPaymentState,
    execute_protected_payment,
)


SCENARIO = Path("harness/scenarios/AP-001_allow.json")


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


def test_at003_2_valid_allow_executes_protected_payment():
    request = load_scenario(SCENARIO)
    response, receipt = evaluate_financial(request)

    assert response.decision == "ALLOW"

    state = ProtectedPaymentState()
    attempt = _make_attempt(request)

    result, new_state = execute_protected_payment(state, receipt, attempt)

    assert result.status == "PERMITTED"
    assert new_state.executed is True
    assert new_state.amount == request.amount
    assert new_state.beneficiary == request.beneficiary
    assert new_state.authority_receipt_id == receipt.id


def test_at003_2_mismatched_action_is_blocked():
    request = load_scenario(SCENARIO)
    response, receipt = evaluate_financial(request)

    assert response.decision == "ALLOW"

    state = ProtectedPaymentState()
    attempt = _make_attempt(request, beneficiary="SUBSTITUTED-BENEFICIARY")

result, new_state = execute_protected_payment(state, receipt, attempt)
assert result.status == "BLOCKED"
assert result.reason_code == "ACTION_BINDING_MISMATCH"
assert new_state.executed is False
assert new_state.amount == 0.0
assert new_state.beneficiary == ""
assert new_state.authority_receipt_id == ""


def test_at003_2_expired_allow_is_blocked():
    request = load_scenario(SCENARIO)
    response, receipt = evaluate_financial(request)

    assert response.decision == "ALLOW"

    expired_receipt = replace(
        receipt,
      valid_until=request.requested_execution_time - timedelta(seconds=1),
    )

    state = ProtectedPaymentState()
    attempt = _make_attempt(request)

    result, new_state = execute_protected_payment(state, expired_receipt, attempt)

    assert result.status == "BLOCKED"
    assert result.reason_code == "AUTHORITY_DETERMINATION_EXPIRED"
    assert new_state is state
    assert new_state.amount == 0.0
    assert new_state.beneficiary == ""
    assert new_state.authority_receipt_id == ""


def test_at003_2_refuse_is_blocked():
    request = load_scenario(SCENARIO)
    response, receipt = evaluate_financial(request)

    refuse_receipt = replace(receipt, decision="REFUSE")

    state = ProtectedPaymentState()
    attempt = _make_attempt(request)

  result, new_state = execute_protected_payment(state, refuse_receipt, attempt)

    assert result.status == "BLOCKED"
    assert result.reason_code == "NO_APPLICABLE_ALLOW"
    assert new_state is state
    assert new_state.executed is False
    assert new_state.amount == 0.0
    assert new_state.beneficiary == ""
    assert new_state.authority_receipt_id == ""
