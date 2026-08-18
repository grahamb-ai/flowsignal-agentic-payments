from dataclasses import replace

from agentic_demo import evaluate_scenario
from app.engines.consequence_receipt import (
    ConsequenceOutcomeReceipt,
    verify_consequence_outcome_receipt,
)


def _receipt_from_result(result) -> ConsequenceOutcomeReceipt:
    raw = result["consequence_outcome_receipt"]
    return ConsequenceOutcomeReceipt(**raw)


def test_pmq001_allow_path_emits_integrity_protected_formed_outcome_receipt():
    result = evaluate_scenario("AP-001")

    assert result["financial_consequence"] == "EXECUTION PERMITTED"
    receipt = _receipt_from_result(result)

    assert receipt.authority_receipt_id == result["authority_receipt"]["id"]
    assert receipt.action_binding_hash == result["authority_receipt"]["action_binding_hash"]
    assert receipt.outcome == "CONSEQUENCE_FORMED"
    assert receipt.consequence_formed is True
    assert verify_consequence_outcome_receipt(receipt)


def test_pmq001_blocked_path_emits_integrity_protected_nonformation_outcome_receipt():
    result = evaluate_scenario("AP-006")

    assert result["financial_consequence"] == "NO EXECUTION"
    receipt = _receipt_from_result(result)

    assert receipt.authority_receipt_id == result["authority_receipt"]["id"]
    assert receipt.outcome.startswith("GATEWAY_BLOCKED:")
    assert receipt.consequence_formed is False
    assert verify_consequence_outcome_receipt(receipt)


def test_pmq001_consequence_outcome_receipt_tampering_is_detected():
    result = evaluate_scenario("AP-001")
    receipt = _receipt_from_result(result)
    assert verify_consequence_outcome_receipt(receipt)

    tampered = replace(
        receipt,
        outcome="CONSEQUENCE_NOT_FORMED",
        consequence_formed=False,
    )

    assert not verify_consequence_outcome_receipt(tampered)
