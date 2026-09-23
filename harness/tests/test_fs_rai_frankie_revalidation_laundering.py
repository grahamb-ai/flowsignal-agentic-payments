from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_033_revalidation_must_not_be_signature_refresh_only():
    """A successor 'revalidation' must establish current premises, not merely wrap
    an old determination in a new timestamp/signature."""
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    req = load_scenario(scenario, rebase_to_now=False)
    response, receipt = evaluate_financial(req, sealed_at=req.requested_execution_time)
    assert response.decision == "ALLOW"

    for field in (
        "revalidation_basis_id",
        "revalidated_proposition_set_id",
        "revalidated_authority_context_id",
        "revalidation_evidence_cut_id",
        "revalidation_resolution_id",
    ):
        assert not hasattr(receipt, field)
