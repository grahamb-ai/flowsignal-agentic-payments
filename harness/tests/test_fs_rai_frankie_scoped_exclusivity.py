from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_029_exclusive_authority_scope_is_not_partitioned_by_subject():
    """Two authority leaders can both be legitimate if their scopes are disjoint;
    exclusivity must therefore be scoped, not global."""
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    req = load_scenario(scenario, rebase_to_now=False)
    response, receipt = evaluate_financial(req, sealed_at=req.requested_execution_time)
    assert response.decision == "ALLOW"

    for field in (
        "authority_partition_key",
        "authority_exclusivity_scope_id",
        "authority_scope_lease_id",
        "authority_scope_fence",
        "scope_ownership_epoch_id",
    ):
        assert not hasattr(receipt, field)
