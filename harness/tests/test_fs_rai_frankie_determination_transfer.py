from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_032_determination_has_no_cross_domain_transfer_authority():
    """An ALLOW produced under authority domain A must not become authority under
    domain B merely because B accepts/re-signs/reissues the old result."""
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    req = load_scenario(scenario, rebase_to_now=False)
    response, receipt = evaluate_financial(req, sealed_at=req.requested_execution_time)
    assert response.decision == "ALLOW"

    # No object binds the determination to an authority-domain identity and no
    # transfer/revalidation rule proves that a successor domain independently
    # established current authority before issuing its own constraint.
    for field in (
        "authority_domain_id",
        "determination_domain_id",
        "determination_transfer_rule_id",
        "transfer_authorisation_id",
        "successor_revalidation_id",
        "predecessor_determination_id",
    ):
        assert not hasattr(receipt, field)
