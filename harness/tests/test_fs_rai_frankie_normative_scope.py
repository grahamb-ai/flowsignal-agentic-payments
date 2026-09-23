from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_017_normative_root_has_no_scope_correspondence():
    """Even a genuine external root may be competent for the wrong domain."""
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    req = load_scenario(scenario, rebase_to_now=False)
    response, receipt = evaluate_financial(req, sealed_at=req.requested_execution_time)
    assert response.decision == "ALLOW"

    # No bound root-scope object establishes that the normative authority
    # actually covers this institution/action/source-account/payment domain.
    for field in (
        "normative_root_scope_id",
        "normative_root_institution_id",
        "normative_root_action_scope",
        "normative_root_resource_scope",
        "normative_root_jurisdiction_scope",
    ):
        assert not hasattr(receipt, field)
