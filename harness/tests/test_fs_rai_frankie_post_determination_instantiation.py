from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_044_post_determination_parameter_selection_is_not_bound():
    """A determination over a partially instantiated operation must not be treated
    as authority for later discretionary parameter choices unless semantics allow it."""
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    req = load_scenario(scenario, rebase_to_now=False)
    response, receipt = evaluate_financial(req, sealed_at=req.requested_execution_time)
    assert response.decision == "ALLOW"

    for field in (
        "operation_instantiation_state_id",
        "determination_parameter_set_id",
        "post_determination_instantiation_rule_id",
        "open_parameter_set_id",
        "final_instantiation_id",
    ):
        assert not hasattr(receipt, field)
