from dataclasses import replace
from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_006_competence_has_no_bind_time_standing():
    """Evidence competence is not represented as mutable bind-time state."""
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    req = load_scenario(scenario, rebase_to_now=False)

    response, receipt = evaluate_financial(req, sealed_at=req.requested_execution_time)
    assert response.decision == "ALLOW"

    # Screening evidence has a source and capture time, but no competence
    # grant/version/validity identity that could be revalidated at bind time.
    ref = next(r for r in receipt.evidence_references if r.get("type") == "sanctions_screening")
    for field in (
        "competence_grant_id",
        "competence_version",
        "competence_valid_from",
        "competence_valid_until",
        "competence_revocation_fence",
    ):
        assert field not in ref
