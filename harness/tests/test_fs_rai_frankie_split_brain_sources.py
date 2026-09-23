from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_024_conflicting_authoritative_sources_need_resolution_rule():
    """Two individually authoritative sources may disagree; selecting the favourable
    one is not itself an authority-resolution rule."""
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    req = load_scenario(scenario, rebase_to_now=False)
    response, receipt = evaluate_financial(req, sealed_at=req.requested_execution_time)
    assert response.decision == "ALLOW"

    # No bound conflict/precedence object establishes what to do if two sources
    # competent for the same proposition simultaneously disagree.
    for field in (
        "source_precedence_rule_id",
        "conflict_resolution_rule_id",
        "authoritative_source_set_id",
        "conflict_resolution_decision_id",
        "conflict_evidence_set_id",
    ):
        assert not hasattr(receipt, field)
