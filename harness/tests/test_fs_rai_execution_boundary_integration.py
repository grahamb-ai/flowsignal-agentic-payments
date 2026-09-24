from pathlib import Path

from app.engines.protected_consequence import execute_protected_consequence
from app.engines.runtime_authority_payment import prepare_payment_execution, final_bind_payment
from harness.runner import load_scenario


SCENARIO = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"


def test_legacy_protected_consequence_cannot_form_from_rai_constraint_alone():
    """Expose whether the new RAI chain is causally wired to the real boundary.

    A focused RAI final-bind PERMITTED result must not be mistaken for actual
    protected-execution authority. Until the legacy consequence boundary
    consumes an artifact causally derived from that exact determination,
    the two paths remain parallel rather than route-closed.
    """
    req = load_scenario(SCENARIO, rebase_to_now=False)
    prepared = prepare_payment_execution(
        req,
        route_id="R1",
        executor_id="PAYMENT-EXECUTOR-1",
        resolved_at=req.requested_execution_time,
    )
    final_bind = final_bind_payment(req, prepared, bind_at=req.requested_execution_time)
    assert final_bind.status == "PERMITTED"

    # The current protected consequence API still requires the legacy
    # ExecutionPermit. The RAI determination/constraint is not yet a causal
    # execution capability at this boundary.
    outcome = execute_protected_consequence(
        permit=None,
        attempted_action_binding_hash=prepared.operation.operation_id,
    )

    # Required architecture: a successful RAI final bind must produce/mediate
    # the exact capability consumed by the protected boundary. This assertion
    # is deliberately expected to fail on the current parallel architecture.
    assert outcome != "DENIED_NO_EXECUTION_PERMIT", (
        "RAI final-bind is not causally connected to protected consequence execution"
    )
