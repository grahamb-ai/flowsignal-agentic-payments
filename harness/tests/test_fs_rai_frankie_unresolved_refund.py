from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_047_unresolved_outcome_must_not_refund_consumptive_authority():
    """An unresolved external/protected outcome cannot safely be treated as
    demonstrated non-formation for purposes of releasing consumptive authority."""
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    req = load_scenario(scenario, rebase_to_now=False)
    response, receipt = evaluate_financial(req, sealed_at=req.requested_execution_time)
    assert response.decision == "ALLOW"

    for field in (
        "outcome_resolution_state_id",
        "authority_usage_quarantine_id",
        "reconciliation_required_rule_id",
        "nonformation_evidence_id",
        "usage_release_evidence_id",
    ):
        assert not hasattr(receipt, field)
