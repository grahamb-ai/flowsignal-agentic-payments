from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_022_parent_capacity_has_no_delegation_allocation_semantics():
    """Two individually valid child grants may over-allocate a parent's bounded
    delegable capacity if the normative model treats that capacity as aggregate."""
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    req = load_scenario(scenario, rebase_to_now=False)
    response, receipt = evaluate_financial(req, sealed_at=req.requested_execution_time)
    assert response.decision == "ALLOW"

    # Candidate has no representation of whether an amount ceiling is
    # per-operation or aggregate delegable capacity, nor reservations/allocation.
    for field in (
        "delegable_capacity_scope_id",
        "capacity_semantics_id",
        "delegation_allocation_id",
        "delegation_reservation_id",
        "remaining_delegable_capacity",
    ):
        assert not hasattr(receipt, field)
