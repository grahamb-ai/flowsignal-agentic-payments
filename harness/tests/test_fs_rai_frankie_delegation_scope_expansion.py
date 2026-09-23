from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_018_derived_authority_has_no_monotonic_scope_proof():
    """A genuine delegation chain must not expand authority at an intermediate hop."""
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    req = load_scenario(scenario, rebase_to_now=False)
    response, receipt = evaluate_financial(req, sealed_at=req.requested_execution_time)
    assert response.decision == "ALLOW"

    # Candidate binds a mandate/subject but carries no delegation-chain object
    # proving every child scope is a subset of its parent's effective scope.
    for field in (
        "delegation_chain_id",
        "parent_authority_id",
        "derived_scope_proof_id",
        "scope_intersection_id",
        "delegation_depth",
    ):
        assert not hasattr(receipt, field)
