from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_007_evidence_identity_not_bound_as_distinct_observation():
    """Two observations can collapse to the same scalar premise."""
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    req = load_scenario(scenario, rebase_to_now=False)
    response, receipt = evaluate_financial(req, sealed_at=req.requested_execution_time)
    assert response.decision == "ALLOW"

    ref = next(r for r in receipt.evidence_references if r.get("type") == "sanctions_screening")
    # There is no immutable observation/evidence identifier or source version,
    # so the runtime cannot distinguish two same-valued CLEAR observations.
    assert "evidence_id" not in ref
    assert "observation_id" not in ref
    assert "source_version" not in ref
