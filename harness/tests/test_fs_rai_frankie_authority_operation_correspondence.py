from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_051_valid_authority_graph_has_no_exact_operation_correspondence_proof():
    """A valid authority graph is insufficient if the committed operation cannot
    be proven to be the exact operation reached by that graph."""
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    req = load_scenario(scenario, rebase_to_now=False)
    response, receipt = evaluate_financial(req, sealed_at=req.requested_execution_time)
    assert response.decision == "ALLOW"

    for field in (
        "effective_authority_scope_id",
        "protected_operation_identity",
        "authority_to_operation_correspondence_id",
        "operation_materialization_id",
        "commitment_correspondence_proof_id",
    ):
        assert not hasattr(receipt, field)
