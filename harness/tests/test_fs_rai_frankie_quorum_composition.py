from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_039_threshold_membership_has_no_role_or_conflict_constraints():
    """Distinct identities are insufficient when quorum semantics constrain roles,
    organisational domains, separation of duties, or conflicts of interest."""
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    req = load_scenario(scenario, rebase_to_now=False)
    response, receipt = evaluate_financial(req, sealed_at=req.requested_execution_time)
    assert response.decision == "ALLOW"

    for field in (
        "quorum_composition_rule_id",
        "approver_role_binding_set_id",
        "separation_of_duties_rule_id",
        "conflict_of_interest_rule_id",
        "quorum_composition_proof_id",
    ):
        assert not hasattr(receipt, field)
