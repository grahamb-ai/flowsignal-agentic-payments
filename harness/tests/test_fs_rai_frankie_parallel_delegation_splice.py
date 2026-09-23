from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_021_parallel_delegations_cannot_be_spliced_into_super_scope():
    """Restrictions from separate grants must not be cherry-picked into authority
    that no single valid derivation path confers."""
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    req = load_scenario(scenario, rebase_to_now=False)
    response, receipt = evaluate_financial(req, sealed_at=req.requested_execution_time)
    assert response.decision == "ALLOW"

    # No path identity/effective-scope proof binds all relied-on authority
    # predicates to one coherent derivation path.
    for field in (
        "authority_derivation_path_id",
        "effective_authority_scope_id",
        "grant_set_id",
        "grant_composition_rule_id",
        "non_splice_proof_id",
    ):
        assert not hasattr(receipt, field)
