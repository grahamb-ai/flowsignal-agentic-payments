from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_046_failed_commitment_has_no_authority_consumption_outcome_rule():
    """A reserved/single-use authority needs an explicit rule for what happens to
    authority usage when protected commitment does not form."""
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    req = load_scenario(scenario, rebase_to_now=False)
    response, receipt = evaluate_financial(req, sealed_at=req.requested_execution_time)
    assert response.decision == "ALLOW"

    for field in (
        "authority_consumption_outcome_rule_id",
        "usage_reservation_state_id",
        "commitment_nonformation_disposition_id",
        "authority_release_rule_id",
        "authority_burn_rule_id",
    ):
        assert not hasattr(receipt, field)
