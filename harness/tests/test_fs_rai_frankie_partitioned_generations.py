from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_028_authority_generation_has_no_exclusive_succession_proof():
    """Generation labels do not establish that only one successor authority domain
    can legitimately govern after a partition."""
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    req = load_scenario(scenario, rebase_to_now=False)
    response, receipt = evaluate_financial(req, sealed_at=req.requested_execution_time)
    assert response.decision == "ALLOW"

    for field in (
        "exclusive_succession_proof_id",
        "authority_lease_id",
        "authority_lease_fence",
        "successor_quorum_id",
        "generation_parent_id",
        "generation_branch_id",
    ):
        assert not hasattr(receipt, field)
