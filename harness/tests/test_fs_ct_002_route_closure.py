from pathlib import Path

from app.engines.authority_store import advance_authority_state_version
from app.engines.execution_gateway import ExecutionAttempt, validate_execution
from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario
from agentic_demo import evaluate_scenario


def test_fs_ct_002_changed_authority_cannot_reach_permitted_consequence_via_governed_route():
    """
    FS-CT-002 - Category Test: route closure after authority-state change.

    Challenge:
    1. Establish an ALLOW and Authority Receipt at T0.
    2. Change authoritative runtime state at T1.
    3. Attempt to reuse the T0 receipt.
    4. Confirm the gateway blocks it.
    5. Attempt the normal harness consequence-producing route after
       the state change.
    6. Confirm that route cannot report EXECUTION PERMITTED using the
       stale T0 authority.

    Scope:
    This tests route closure across the represented harness execution
    surface. It does not claim closure of external banking/payment rails.
    """

    # T0 - establish valid authority and obtain ALLOW.
    req = load_scenario(Path("harness/scenarios/AP-001_allow.json"))
    response, receipt = evaluate_financial(req)

    assert response.decision == "ALLOW"

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

    # Establish that T0 genuinely could pass the gateway.
    t0_gateway = validate_execution(receipt, attempt)

    assert t0_gateway.status == "PERMITTED"
    assert t0_gateway.reason_code == "BOUND_ALLOW_VALID"

    # T1 - authoritative state changes.
    advance_authority_state_version()

    # Attack 1:
    # Reuse the previously valid Authority Receipt directly.
    stale_gateway = validate_execution(receipt, attempt)

    assert stale_gateway.status == "BLOCKED"
    assert (
        stale_gateway.reason_code
        == "AUTHORITY_STATE_STALE_REEVALUATION_REQUIRED"
    )

    # Attack 2:
    # Try the normal represented consequence-producing route.
    #
    # It must not be capable of reporting EXECUTION PERMITTED by
    # consuming the stale T0 receipt. The normal route performs a new
    # authority evaluation and gateway validation.
    rerun = evaluate_scenario("AP-001")

    assert rerun["execution_gateway"] is not None

    if rerun["financial_consequence"] == "EXECUTION PERMITTED":
        # A permitted consequence is acceptable only if it arose from
        # a NEW evaluation/receipt under the current authority state,
        # rather than reuse of the stale T0 receipt.
        assert rerun["authority_receipt"]["id"] != receipt.id
        assert (
            rerun["authority_receipt"]["authority_state_version"]
            != receipt.authority_state_version
        )
        assert rerun["execution_gateway"]["status"] == "PERMITTED"

    # The stale receipt itself must remain unusable.
    stale_gateway_again = validate_execution(receipt, attempt)

    assert stale_gateway_again.status == "BLOCKED"
    assert (
        stale_gateway_again.reason_code
        == "AUTHORITY_STATE_STALE_REEVALUATION_REQUIRED"
    )