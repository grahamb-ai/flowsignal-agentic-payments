from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_045_parameterised_allow_cannot_be_reused_for_multiple_instantiations():
    """A parameterised ALLOW may authorise one instantiation, many, or a bounded
    number; without usage semantics the same authority can be multiplied."""
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    req = load_scenario(scenario, rebase_to_now=False)
    response, receipt = evaluate_financial(req, sealed_at=req.requested_execution_time)
    assert response.decision == "ALLOW"

    for field in (
        "parameterised_authority_usage_policy_id",
        "instantiation_max_uses",
        "instantiation_usage_reservation_id",
        "instantiation_consumption_id",
        "parameterised_authority_instance_id",
    ):
        assert not hasattr(receipt, field)
