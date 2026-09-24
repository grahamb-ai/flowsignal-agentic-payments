from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_048_reconciliation_source_authority_is_not_bound():
    """Evidence resolving an ambiguous outcome must come from a source competent
    to establish that proposition for the relevant protected operation."""
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    req = load_scenario(scenario, rebase_to_now=False)
    response, receipt = evaluate_financial(req, sealed_at=req.requested_execution_time)
    assert response.decision == "ALLOW"

    for field in (
        "reconciliation_source_id",
        "reconciliation_source_competence_id",
        "reconciliation_proposition_id",
        "reconciliation_subject_binding_id",
        "reconciliation_evidence_id",
    ):
        assert not hasattr(receipt, field)
