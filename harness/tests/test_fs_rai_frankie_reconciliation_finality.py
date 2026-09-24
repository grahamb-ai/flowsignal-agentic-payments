from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_049_reconciliation_finality_is_not_bound():
    """A competent reconciliation observation may still be provisional; authority
    usage must not treat it as final unless governing semantics permit that."""
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    req = load_scenario(scenario, rebase_to_now=False)
    response, receipt = evaluate_financial(req, sealed_at=req.requested_execution_time)
    assert response.decision == "ALLOW"

    for field in (
        "reconciliation_finality_rule_id",
        "reconciliation_finality_state_id",
        "reconciliation_watermark",
        "reversal_window_id",
        "finality_evidence_id",
    ):
        assert not hasattr(receipt, field)
