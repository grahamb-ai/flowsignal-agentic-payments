from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_041_approval_survival_cannot_ignore_operation_change():
    """Even durable approval cannot automatically survive a material change to the
    protected operation or authority-relevant context it approved."""
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    req = load_scenario(scenario, rebase_to_now=False)
    response, receipt = evaluate_financial(req, sealed_at=req.requested_execution_time)
    assert response.decision == "ALLOW"

    for field in (
        "approval_scope_binding_id",
        "approval_context_binding_id",
        "approval_change_invalidation_rule_id",
        "material_change_rule_id",
        "approval_reuse_compatibility_id",
    ):
        assert not hasattr(receipt, field)
