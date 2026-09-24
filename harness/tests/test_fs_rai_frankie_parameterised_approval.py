from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_042_parameterised_approval_has_no_bound_parameter_envelope():
    """An approval issued before final operation instantiation is safe only if the
    governing semantics bind an admissible parameter envelope and instantiation rule."""
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    req = load_scenario(scenario, rebase_to_now=False)
    response, receipt = evaluate_financial(req, sealed_at=req.requested_execution_time)
    assert response.decision == "ALLOW"

    for field in (
        "approval_parameter_envelope_id",
        "approval_instantiation_rule_id",
        "approved_parameter_constraints_id",
        "operation_instantiation_binding_id",
        "parameter_envelope_semantics_id",
    ):
        assert not hasattr(receipt, field)
