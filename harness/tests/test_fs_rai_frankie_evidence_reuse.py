from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_011_evidence_has_no_usage_or_replay_semantics():
    """Evidence may be true yet single-use or bounded-use under its authority model."""
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    req = load_scenario(scenario, rebase_to_now=False)

    r1, receipt1 = evaluate_financial(req, sealed_at=req.requested_execution_time)
    r2, receipt2 = evaluate_financial(req, sealed_at=req.requested_execution_time)
    assert r1.decision == r2.decision == "ALLOW"

    ref = next(r for r in receipt2.evidence_references if r.get("type") == "sanctions_screening")
    for field in (
        "usage_policy_id", "max_uses", "usage_count",
        "consumption_id", "reservation_id", "replay_scope"
    ):
        assert field not in ref
