from dataclasses import replace
from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_009_cross_subject_evidence_has_no_subject_binding():
    """Evidence status/source may be valid but for a different beneficiary."""
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    req = load_scenario(scenario, rebase_to_now=False)

    # The current request type carries screening status/source/time but no
    # independently bound screened-subject identity/evidence subject.
    response, receipt = evaluate_financial(req, sealed_at=req.requested_execution_time)
    assert response.decision == "ALLOW"

    ref = next(r for r in receipt.evidence_references if r.get("type") == "sanctions_screening")
    for field in (
        "subject_id", "screened_subject_id", "subject_binding_hash",
        "beneficiary_binding", "counterparty_binding"
    ):
        assert field not in ref
