from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_026_recovered_primary_has_no_rejoin_watermark():
    """A recovered former primary must not regain authority merely by becoming
    reachable if the active authority domain advanced during failover."""
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    req = load_scenario(scenario, rebase_to_now=False)
    response, receipt = evaluate_financial(req, sealed_at=req.requested_execution_time)
    assert response.decision == "ALLOW"

    for field in (
        "source_rejoin_rule_id",
        "source_rejoin_epoch_id",
        "authority_high_watermark",
        "recovered_source_watermark",
        "rejoin_authorisation_id",
        "source_generation_id",
    ):
        assert not hasattr(receipt, field)
