from dataclasses import replace
from pathlib import Path

from harness.runner import load_scenario
from app.engines.financial_runtime import evaluate_financial
from app.engines.execution_gateway import ExecutionAttempt, action_binding_hash, validate_execution
from app.engines.authority_store import get_authority_state_version
from app.engines.protected_consequence import ExecutionPermit, execute_protected_consequence


def _allow_case():
    req = load_scenario(Path("harness/scenarios/AP-001_allow.json"))
    response, receipt = evaluate_financial(req)
    assert response.decision == "ALLOW"
    attempt = ExecutionAttempt(
        actor_id=req.actor_id,
        principal_id=req.principal_id,
        action=req.action,
        target=req.target,
        amount=req.amount,
        currency=req.currency,
        source_account=req.source_account,
        beneficiary=req.beneficiary,
        purpose=req.purpose,
        mandate_id=req.mandate_id,
        attempted_at=req.requested_execution_time,
    )
    return receipt, attempt


def test_ec001_4_missing_permit_is_denied():
    _, attempt = _allow_case()
    result = execute_protected_consequence(
        permit=None,
        attempted_action_binding_hash=action_binding_hash(attempt),
    )
    assert result == "DENIED_NO_EXECUTION_PERMIT"


def test_ec001_4_arbitrarily_fabricated_signature_is_denied():
    _, attempt = _allow_case()
    forged = ExecutionPermit(
        authority_receipt_id="forged-receipt",
        action_binding_hash=action_binding_hash(attempt),
        authority_state_version=get_authority_state_version(),
        issued_at="2026-08-17T10:00:00+00:00",
        signature="executor-controlled-value",
    )
    result = execute_protected_consequence(
        permit=forged,
        attempted_action_binding_hash=action_binding_hash(attempt),
    )
    assert result == "DENIED_INVALID_EXECUTION_PERMIT"


def test_ec001_4_gateway_permit_is_bound_to_exact_action():
    receipt, attempt = _allow_case()
    gateway = validate_execution(receipt, attempt)
    assert gateway.status == "PERMITTED"
    assert gateway.execution_permit is not None

    substituted = replace(attempt, beneficiary="ATTACKER-CONTROLLED-BENEFICIARY")
    result = execute_protected_consequence(
        permit=gateway.execution_permit,
        attempted_action_binding_hash=action_binding_hash(substituted),
    )
    assert result == "DENIED_ACTION_BINDING_MISMATCH"


def test_ec001_4_gateway_produced_permit_forms_represented_consequence():
    receipt, attempt = _allow_case()
    gateway = validate_execution(receipt, attempt)
    assert gateway.status == "PERMITTED"
    assert gateway.execution_permit is not None

    result = execute_protected_consequence(
        permit=gateway.execution_permit,
        attempted_action_binding_hash=action_binding_hash(attempt),
    )
    assert result == "CONSEQUENCE_FORMED"
