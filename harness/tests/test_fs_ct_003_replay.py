from importlib import import_module
from pathlib import Path

from app.engines.authority_store import advance_authority_state_version
from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_fs_ct_003_historical_determination_is_replayable_without_current_state():
    """
    FS-CT-003 - Historical Determination Replay Challenge

    Invariant:

    A historical authority determination must be independently reproducible
    from preserved evidence without consulting or rewriting current authority
    state.

    A later authority-state change must not alter the historical result.

    This test intentionally challenges whether the current public harness
    exposes a genuine replay mechanism rather than simply performing a fresh
    evaluation.
    """

    # T0 - produce and preserve an historical authority determination.
    req = load_scenario(Path("harness/scenarios/AP-001_allow.json"))

    response, receipt = evaluate_financial(req)

    assert response.decision == "ALLOW"

    original_receipt_id = receipt.id
    original_decision = receipt.decision
    original_reason_code = receipt.reason_code
    original_binding_hash = receipt.action_binding_hash
    original_state_version = receipt.authority_state_version
    original_snapshot = receipt.request_snapshot.copy()

    # T1 - current authoritative state changes.
    advance_authority_state_version()

    # A true replay mechanism must operate on the preserved historical
    # evidence. A fresh call to evaluate_financial() is not replay.
    try:
        replay_module = import_module("app.engines.replay")
    except ModuleNotFoundError:
        assert False, (
            "No independent replay mechanism exists. "
            "The current harness can re-evaluate a request, but cannot "
            "reconstruct the historical determination from preserved evidence."
        )

    assert hasattr(replay_module, "replay_authority_receipt"), (
        "Replay module exists but does not expose replay_authority_receipt()."
    )

    replay_result = replay_module.replay_authority_receipt(receipt)

    # Historical truth must be reproducible independently of current state.
    assert replay_result.decision == original_decision
    assert replay_result.reason_code == original_reason_code
    assert replay_result.authority_state_version == original_state_version
    assert replay_result.action_binding_hash == original_binding_hash

    # Replay must not rewrite the original receipt.
    assert receipt.id == original_receipt_id
    assert receipt.decision == original_decision
    assert receipt.reason_code == original_reason_code
    assert receipt.action_binding_hash == original_binding_hash
    assert receipt.authority_state_version == original_state_version
    assert receipt.request_snapshot == original_snapshot