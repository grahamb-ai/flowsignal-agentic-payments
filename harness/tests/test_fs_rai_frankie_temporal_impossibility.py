from dataclasses import replace
from datetime import timedelta

from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_002_temporally_impossible_allow():
    """FRANKIE-002: individually plausible premises, no proved common-validity cut.

    The candidate accepts each authority-material request/evidence assertion as a
    current scalar. It carries no valid_from/valid_to or source version for actor,
    KYA, counterparty, account or risk standing, and only screening has a capture
    timestamp. Therefore it cannot prove that all ALLOW premises coexisted.
    """
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    base = load_scenario(scenario, rebase_to_now=False)
    t_commit = base.requested_execution_time

    # Represent a screening observation from an earlier cut while all other
    # mutable standing assertions are merely presented as current. Nothing in
    # the candidate binds their source versions or common validity interval.
    mixed = replace(
        base,
        actor_authenticated=True,
        kya_status="VERIFIED",
        counterparty_status="APPROVED",
        account_status="ACTIVE",
        risk_state="NORMAL",
        screening_status="CLEAR",
        screening_captured_at=t_commit - timedelta(seconds=30),
    )
    response, receipt = evaluate_financial(mixed, sealed_at=t_commit)

    assert response.decision == "ALLOW"
    assert receipt.authority_snapshot_id
    snap = receipt.request_snapshot
    # These authority-material premises have values but no coherent-cut identity.
    for field in (
        "actor_authenticated", "kya_status", "counterparty_status",
        "account_status", "risk_state"
    ):
        assert field in snap
    assert "authority_context_cut_id" not in snap
    assert "standing_source_versions" not in snap
    assert "standing_validity_intersection" not in snap
