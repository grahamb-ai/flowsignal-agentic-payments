from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_034_partial_revalidation_has_no_carry_forward_rule():
    """A successor resolution may reuse prior evidence only where governing
    semantics establish that the evidence remains admissible in the new context."""
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    req = load_scenario(scenario, rebase_to_now=False)
    response, receipt = evaluate_financial(req, sealed_at=req.requested_execution_time)
    assert response.decision == "ALLOW"

    for field in (
        "evidence_carry_forward_rule_id",
        "inherited_evidence_set_id",
        "recomputed_proposition_set_id",
        "inherited_proposition_set_id",
        "carry_forward_compatibility_proof_id",
    ):
        assert not hasattr(receipt, field)
