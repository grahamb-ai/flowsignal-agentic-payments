from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_027_old_generation_receipt_has_no_topology_generation_binding():
    """A determination from an old authority-source generation must not remain
    usable after an authoritative failover/recovery generation change."""
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    req = load_scenario(scenario, rebase_to_now=False)
    response, receipt = evaluate_financial(req, sealed_at=req.requested_execution_time)
    assert response.decision == "ALLOW"

    for field in (
        "authority_topology_generation_id",
        "authority_source_generation_id",
        "source_membership_epoch_id",
        "topology_fence",
    ):
        assert not hasattr(receipt, field)
