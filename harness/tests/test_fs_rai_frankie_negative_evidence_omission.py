from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_012_applicable_negative_proposition_can_be_omitted():
    """Completeness attack: all supplied evidence may be valid while a required
    adverse proposition is absent from the resolution context."""
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    req = load_scenario(scenario, rebase_to_now=False)
    response, receipt = evaluate_financial(req, sealed_at=req.requested_execution_time)
    assert response.decision == "ALLOW"

    # Candidate records what it evaluated but has no authoritative manifest of
    # every proposition required by the applicable semantic definition.
    snap = receipt.request_snapshot
    for field in (
        "required_proposition_set_id",
        "required_proposition_manifest_digest",
        "applicability_resolution_id",
        "omission_check_id",
    ):
        assert field not in snap
