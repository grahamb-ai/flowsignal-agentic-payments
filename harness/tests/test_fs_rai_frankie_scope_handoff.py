from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_031_scope_migration_has_no_handoff_cut():
    """Even if old/new ownership epochs are known, migration needs a handoff rule
    preventing an authority gap or overlap at the protected commitment boundary."""
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    req = load_scenario(scenario, rebase_to_now=False)
    response, receipt = evaluate_financial(req, sealed_at=req.requested_execution_time)
    assert response.decision == "ALLOW"

    for field in (
        "authority_handoff_id",
        "handoff_cut_id",
        "old_owner_fence",
        "new_owner_activation_fence",
        "migration_completion_id",
        "migration_rule_id",
    ):
        assert not hasattr(receipt, field)
