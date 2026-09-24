from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_043_parameter_instantiator_authority_is_not_bound():
    """Even a valid parameter envelope does not authorise an arbitrary actor or
    mechanism to choose values inside it."""
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    req = load_scenario(scenario, rebase_to_now=False)
    response, receipt = evaluate_financial(req, sealed_at=req.requested_execution_time)
    assert response.decision == "ALLOW"

    for field in (
        "parameter_instantiator_subject_id",
        "parameter_instantiation_authority_id",
        "parameter_instantiation_scope_id",
        "instantiation_delegation_id",
        "instantiation_event_id",
    ):
        assert not hasattr(receipt, field)
