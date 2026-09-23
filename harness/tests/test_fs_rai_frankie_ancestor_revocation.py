from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_020_delegation_chain_has_no_ancestor_revocation_proof():
    """A live child grant must not survive revocation of an authority-bearing ancestor
    unless the governing derivation semantics explicitly make it independent."""
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    req = load_scenario(scenario, rebase_to_now=False)
    response, receipt = evaluate_financial(req, sealed_at=req.requested_execution_time)
    assert response.decision == "ALLOW"

    # Candidate has no derivation-chain state binding from which current standing
    # of every authority-bearing ancestor can be revalidated at determination/bind.
    for field in (
        "delegation_chain_id",
        "ancestor_authority_state_cut_id",
        "ancestor_revocation_watermark",
        "derivation_standing_id",
        "revocation_propagation_rule_id",
    ):
        assert not hasattr(receipt, field)
