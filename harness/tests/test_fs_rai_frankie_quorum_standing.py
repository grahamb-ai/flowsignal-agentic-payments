from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_040_quorum_member_standing_semantics_are_not_bound():
    """Whether an assembled quorum survives later loss of member standing is a
    governing semantic rule; the candidate cannot represent or enforce it."""
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    req = load_scenario(scenario, rebase_to_now=False)
    response, receipt = evaluate_financial(req, sealed_at=req.requested_execution_time)
    assert response.decision == "ALLOW"

    for field in (
        "quorum_standing_rule_id",
        "approver_standing_cut_id",
        "approver_standing_version_set_id",
        "approval_survival_rule_id",
        "quorum_revalidation_rule_id",
    ):
        assert not hasattr(receipt, field)
