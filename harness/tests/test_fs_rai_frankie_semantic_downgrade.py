from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_014_semantics_has_no_current_applicability_watermark():
    """A signed/known semantic definition is not enough if superseded."""
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    req = load_scenario(scenario, rebase_to_now=False)
    response, receipt = evaluate_financial(req, sealed_at=req.requested_execution_time)
    assert response.decision == "ALLOW"

    # Receipt identifies semantics, but carries no independent applicability
    # authority/version/watermark proving that this semantic definition is the
    # currently governing one rather than a superseded definition.
    for field in (
        "authority_semantics_applicability_source_id",
        "authority_semantics_applicability_version",
        "authority_semantics_applicability_watermark",
        "authority_semantics_supersession_fence",
    ):
        assert not hasattr(receipt, field)
