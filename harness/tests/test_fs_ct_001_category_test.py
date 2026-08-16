from pathlib import Path

from app.engines.authority_store import advance_authority_state_version
from app.engines.execution_gateway import ExecutionAttempt, validate_execution
from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_fs_ct_001_lost_authority_cannot_reuse_prior_allow():
    """
    FS-CT-001 - Category Test: changed authority after ALLOW.

    Challenge:
    1. Establish a valid movement.
    2. Obtain ALLOW and its bound Authority Receipt.
    3. Change authoritative runtime state.
    4. Attempt to reuse the earlier ALLOW.
    5. Verify the represented consequence cannot pass the Execution Gateway.

    No production/runtime logic is modified by this test.
    """

    # T0 - candidate movement has valid authority.
    req = load_scenario(Path("harness/scenarios/AP-001_allow.json"))

    response, receipt = evaluate_financial(req)

    assert response.decision == "ALLOW"

    original_receipt_id = receipt.id
    original_binding_hash = receipt.action_binding_hash
    original_state_version = receipt.authority_state_version

    # T1 - governing authority state materially changes after ALLOW.
    advance_authority_state_version()

    # Attempt the exact movement previously authorised.
    attempt = ExecutionAttempt(
        actor_id=req.actor_id,
        principal_id=req.principal_id,
        action=req.action,
        target=req.target,
        amount=req.amount,
        currency=req.currency,
        source_account=req.source_account,
        beneficiary=req.beneficiary,
        purpose=req.purpose,
        mandate_id=req.mandate_id,
        attempted_at=req.requested_execution_time,
    )

    gateway = validate_execution(receipt, attempt)

    # The old ALLOW must no longer be capable of reaching the
    # represented consequence through the governed execution path.
    assert gateway.status == "BLOCKED"
    assert gateway.reason_code == "AUTHORITY_STATE_STALE_REEVALUATION_REQUIRED"

    # The historical receipt must remain the original receipt rather
    # than being rewritten to manufacture the changed-condition result.
    assert receipt.id == original_receipt_id
    assert receipt.action_binding_hash == original_binding_hash
    assert receipt.authority_state_version == original_state_version