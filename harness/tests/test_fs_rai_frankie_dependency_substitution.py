from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_036_equal_value_dependency_is_not_equivalent_dependency():
    """A derived proposition must not accept a dependency replacement merely
    because the replacement yields the same visible value."""
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    req = load_scenario(scenario, rebase_to_now=False)
    response, receipt = evaluate_financial(req, sealed_at=req.requested_execution_time)
    assert response.decision == "ALLOW"

    for field in (
        "dependency_identity_set_id",
        "dependency_source_set_id",
        "dependency_semantics_set_id",
        "dependency_substitution_rule_id",
        "derivation_input_binding_id",
    ):
        assert not hasattr(receipt, field)
