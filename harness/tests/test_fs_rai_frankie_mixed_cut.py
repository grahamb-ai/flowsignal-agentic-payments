from dataclasses import replace
from datetime import timedelta

from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_request_presented_runtime_state_can_form_allow(tmp_path):
    """FRANKIE-001: demonstrate mixed-cut authority premises.

    Mandate authority is read from the authoritative snapshot, while actor/KYA,
    counterparty/account/risk and screening premises remain request/evidence
    supplied. The test intentionally changes those request-side premises without
    changing the authoritative snapshot identity. If both evaluations ALLOW with
    the same snapshot id, the snapshot is not a coherent cut of all premises
    used for ALLOW.
    """
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    base = load_scenario(scenario, rebase_to_now=False)

    r1, receipt1 = evaluate_financial(base, sealed_at=base.requested_execution_time)
    assert r1.decision == "ALLOW"

    # Create a second set of independently presented runtime premises while
    # retaining the same institutionally authoritative mandate state.
    altered = replace(
        base,
        screening_source="ATTACKER-CONTROLLED-CLEAR-SOURCE",
        screening_captured_at=base.requested_execution_time,
        counterparty_status="APPROVED",
        account_status="ACTIVE",
        risk_state="NORMAL",
        actor_authenticated=True,
        kya_status="VERIFIED",
    )
    r2, receipt2 = evaluate_financial(altered, sealed_at=base.requested_execution_time)

    assert r2.decision == "ALLOW"
    assert receipt2.authority_snapshot_id == receipt1.authority_snapshot_id
    assert receipt2.authoritative_source_id == receipt1.authoritative_source_id
    assert receipt2.authority_fence == receipt1.authority_fence
    assert receipt2.request_snapshot["screening_source"] != receipt1.request_snapshot["screening_source"]
