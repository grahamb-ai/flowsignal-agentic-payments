from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_025_source_failover_has_no_authorised_transition_proof():
    """Failover from primary to secondary authority source is itself a governed
    transition, not merely an availability choice."""
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    req = load_scenario(scenario, rebase_to_now=False)
    response, receipt = evaluate_financial(req, sealed_at=req.requested_execution_time)
    assert response.decision == "ALLOW"

    for field in (
        "source_topology_id",
        "failover_rule_id",
        "failover_epoch_id",
        "failover_authorisation_id",
        "source_transition_fence_id",
    ):
        assert not hasattr(receipt, field)
