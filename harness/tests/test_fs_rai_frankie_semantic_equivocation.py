from dataclasses import replace
from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_005_semantic_equivocation_same_label_different_meaning():
    """Same lexical status must not imply same institutional proposition."""
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    req = load_scenario(scenario, rebase_to_now=False)

    equivocated = replace(
        req,
        screening_status="CLEAR",
        screening_source="VENDOR-CLEAR-MEANS-NO-INTERNAL-HIT",
        screening_captured_at=req.requested_execution_time,
    )
    response, receipt = evaluate_financial(equivocated, sealed_at=req.requested_execution_time)

    assert response.decision == "ALLOW"
    # No bound semantic definition identifies what CLEAR means for this source.
    ref = next(r for r in receipt.evidence_references if r.get("type") == "sanctions_screening")
    assert "semantic_definition_id" not in ref
    assert "proposition_id" not in ref
