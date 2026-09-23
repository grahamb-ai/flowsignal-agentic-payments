from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_035_inherited_evidence_dependency_closure_is_not_bound():
    """An inherited proposition may depend on other premises that changed; carrying
    only the leaf value forward can hide invalidated dependencies."""
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    req = load_scenario(scenario, rebase_to_now=False)
    response, receipt = evaluate_financial(req, sealed_at=req.requested_execution_time)
    assert response.decision == "ALLOW"

    for field in (
        "proposition_dependency_graph_id",
        "inherited_dependency_closure_id",
        "dependency_version_set_id",
        "dependency_compatibility_proof_id",
        "derived_proposition_provenance_id",
    ):
        assert not hasattr(receipt, field)
