from dataclasses import replace

from agentic_demo import evaluate_scenario
from app.engines.execution_gateway import ExecutionAttempt, validate_execution
from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario
from pathlib import Path


def test_at004_4_gateway_rejects_receipt_with_invalid_integrity_proof():
    req = load_scenario(Path("harness/scenarios/AP-001_allow.json"))
    response, receipt = evaluate_financial(req)

    assert response.decision == "ALLOW"
    assert receipt.receipt_hmac

    corrupted_receipt = replace(
        receipt,
        receipt_hmac="invalid-integrity-proof",
    )

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

    gateway = validate_execution(corrupted_receipt, attempt)

    assert gateway.status == "BLOCKED"
    assert gateway.reason_code == "AUTHORITY_RECEIPT_INTEGRITY_INVALID"


def test_at004_4_valid_receipt_still_reaches_gateway():
    result = evaluate_scenario("AP-001")

    assert result["financial_consequence"] == "EXECUTION PERMITTED"
    assert result["execution_gateway"] is not None
    assert result["execution_gateway"]["status"] == "PERMITTED"
    assert result["execution_gateway"]["reason_code"] == "BOUND_ALLOW_VALID"