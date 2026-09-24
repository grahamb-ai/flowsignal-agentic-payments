from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_037_derivation_rule_identity_is_not_bound():
    """The same inputs can produce different authority conclusions under different
    derivation/composition rules; input integrity alone is insufficient."""
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    req = load_scenario(scenario, rebase_to_now=False)
    response, receipt = evaluate_financial(req, sealed_at=req.requested_execution_time)
    assert response.decision == "ALLOW"

    for field in (
        "derivation_rule_id",
        "derivation_rule_version",
        "derivation_semantics_source_id",
        "composition_operator_id",
        "derivation_rule_applicability_id",
    ):
        assert not hasattr(receipt, field)
