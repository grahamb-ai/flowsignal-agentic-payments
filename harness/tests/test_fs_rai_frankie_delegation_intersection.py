from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_019_delegation_restrictions_have_no_intersection_proof():
    """Different restrictions at different hops must compose by intersection."""
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    req = load_scenario(scenario, rebase_to_now=False)
    response, receipt = evaluate_financial(req, sealed_at=req.requested_execution_time)
    assert response.decision == "ALLOW"

    # No object proves the effective authority is the intersection of all
    # inherited restrictions rather than a cherry-picked union/last-hop view.
    for field in (
        "effective_authority_scope_id",
        "scope_intersection_digest",
        "inherited_restrictions_digest",
        "derivation_rule_id",
    ):
        assert not hasattr(receipt, field)
