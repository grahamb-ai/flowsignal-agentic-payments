from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_030_scope_migration_has_no_ownership_epoch_binding():
    """A determination made under the old authority owner must not remain usable
    after the protected authority scope migrates to a new owner/domain."""
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    req = load_scenario(scenario, rebase_to_now=False)
    response, receipt = evaluate_financial(req, sealed_at=req.requested_execution_time)
    assert response.decision == "ALLOW"

    for field in (
        "authority_scope_owner_id",
        "authority_scope_ownership_epoch",
        "authority_scope_assignment_id",
        "authority_scope_migration_fence",
        "scope_assignment_version",
    ):
        assert not hasattr(receipt, field)
