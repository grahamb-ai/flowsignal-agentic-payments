from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_016_normative_grounding_has_no_acyclic_root():
    """A self-consistent authority circle is not external normative grounding."""
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    req = load_scenario(scenario, rebase_to_now=False)
    response, receipt = evaluate_financial(req, sealed_at=req.requested_execution_time)
    assert response.decision == "ALLOW"

    # Candidate identifies semantic/source/competence material, but does not
    # carry a derivation graph/root proving that applicability authority is
    # grounded outside the set of propositions it authorises.
    for field in (
        "normative_root_id",
        "authority_derivation_graph_id",
        "derivation_root_hash",
        "acyclic_grounding_proof_id",
    ):
        assert not hasattr(receipt, field)
