from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_050_same_operation_has_no_cross_primitive_context_identity():
    """Individually valid semantics, evidence, derivation, usage and operation
    bindings must belong to one compatible authority-resolution context."""
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    req = load_scenario(scenario, rebase_to_now=False)
    response, receipt = evaluate_financial(req, sealed_at=req.requested_execution_time)
    assert response.decision == "ALLOW"

    for field in (
        "authority_resolution_context_id",
        "authority_context_compatibility_rule_id",
        "authority_context_cut_id",
        "authority_context_member_set_id",
        "authority_context_version",
    ):
        assert not hasattr(receipt, field)
