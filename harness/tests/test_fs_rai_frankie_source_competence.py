from dataclasses import replace
from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_004_source_competence_laundering():
    """A source can be fresh/well-formed yet lack competence for the proposition."""
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    req = load_scenario(scenario, rebase_to_now=False)

    laundered = replace(
        req,
        screening_status="CLEAR",
        screening_source="SIGNED-WEATHER-SERVICE-001",
        screening_captured_at=req.requested_execution_time,
    )
    response, receipt = evaluate_financial(laundered, sealed_at=req.requested_execution_time)

    # Current candidate accepts freshness/status without proving the source is
    # institutionally competent to establish sanctions-screening clearance.
    assert response.decision == "ALLOW"
    refs = receipt.evidence_references
    assert any(r.get("source") == "SIGNED-WEATHER-SERVICE-001" for r in refs)
    assert not any("competence" in r for r in refs)
