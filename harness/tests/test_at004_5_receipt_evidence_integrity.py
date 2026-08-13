from dataclasses import replace
from pathlib import Path

from app.engines.financial_runtime import evaluate_financial
from app.engines.receipt_integrity import verify_receipt_hmac
from harness.runner import load_scenario


def test_at004_5_receipt_evidence_is_inside_integrity_boundary():
    req = load_scenario(Path("harness/scenarios/AP-001_allow.json"))
    response, receipt = evaluate_financial(req)

    assert response.decision == "ALLOW"
    assert verify_receipt_hmac(receipt)

    changed_snapshot = dict(receipt.request_snapshot)
    changed_snapshot["screening_status"] = "CHANGED_AFTER_SEAL"

    changed_receipt = replace(
        receipt,
        request_snapshot=changed_snapshot,
    )

    assert not verify_receipt_hmac(changed_receipt), (
        "Authority Receipt evidential content changed while "
        "receipt integrity verification still succeeded"
    )