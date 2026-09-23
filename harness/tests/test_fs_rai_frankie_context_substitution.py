from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_010_evidence_has_no_purpose_or_context_binding():
    """Right subject/fact/source can still be inadmissible for this purpose."""
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    req = load_scenario(scenario, rebase_to_now=False)
    response, receipt = evaluate_financial(req, sealed_at=req.requested_execution_time)
    assert response.decision == "ALLOW"

    ref = next(r for r in receipt.evidence_references if r.get("type") == "sanctions_screening")
    for field in (
        "purpose_id", "authority_context_id", "use_scope",
        "permitted_action", "institutional_context_id"
    ):
        assert field not in ref
