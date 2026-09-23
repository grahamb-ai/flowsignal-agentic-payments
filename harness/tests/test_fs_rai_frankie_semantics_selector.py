from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_015_semantics_selector_competence_not_bound():
    """Who is competent to choose the governing semantics is itself authority."""
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    req = load_scenario(scenario, rebase_to_now=False)
    response, receipt = evaluate_financial(req, sealed_at=req.requested_execution_time)
    assert response.decision == "ALLOW"

    # Existing semantic source identity describes the definition source, not a
    # separately grounded selector/competence grant for choosing applicability.
    for field in (
        "semantics_selector_id",
        "semantics_selector_competence_grant_id",
        "semantics_selection_decision_id",
        "semantics_selection_basis",
    ):
        assert not hasattr(receipt, field)
