from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_038_threshold_rule_has_no_distinct_approver_identity_set():
    """A k-of-n authority rule requires k distinct eligible authority subjects,
    not merely k approval artefacts."""
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    req = load_scenario(scenario, rebase_to_now=False)
    response, receipt = evaluate_financial(req, sealed_at=req.requested_execution_time)
    assert response.decision == "ALLOW"

    for field in (
        "threshold_rule_id",
        "required_distinct_approver_count",
        "eligible_approver_set_id",
        "distinct_approver_identity_set_id",
        "approval_cardinality_proof_id",
    ):
        assert not hasattr(receipt, field)
