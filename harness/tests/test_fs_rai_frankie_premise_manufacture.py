from dataclasses import replace
from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_003_request_can_claim_mutable_standing_without_source_identity():
    """FRANKIE-003: premise manufacture remains possible outside mandate state."""
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    req = load_scenario(scenario, rebase_to_now=False)

    attacker_presented = replace(
        req,
        actor_authenticated=True,
        kya_status="VERIFIED",
        counterparty_status="APPROVED",
        account_status="ACTIVE",
        risk_state="NORMAL",
    )
    response, receipt = evaluate_financial(attacker_presented, sealed_at=req.requested_execution_time)
    assert response.decision == "ALLOW"

    # No independently authoritative source identity/version exists for these
    # mutable premises in the receipt snapshot.
    snap = receipt.request_snapshot
    for source_field in (
        "actor_standing_source_id",
        "kya_source_id",
        "counterparty_source_id",
        "account_source_id",
        "risk_source_id",
    ):
        assert source_field not in snap
