from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_013_not_applicable_has_no_authoritative_derivation():
    """An omitted check must not become N/A merely because the request shape
    does not present the trigger that would make it applicable."""
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    req = load_scenario(scenario, rebase_to_now=False)
    response, receipt = evaluate_financial(req, sealed_at=req.requested_execution_time)
    assert response.decision == "ALLOW"

    # There is no explicit applicability record binding each conditional
    # proposition to the authoritative facts that made it required or N/A.
    assert not any(
        all(k in ref for k in ("proposition_id", "applicability_status", "applicability_basis"))
        for ref in receipt.evidence_references
    )
