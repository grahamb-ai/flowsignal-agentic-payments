from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_023_delegation_issue_and_execution_have_no_shared_ordering_fence():
    """Concurrent delegation/authority mutations require a common ordering domain
    or a determination may be valid against a state that never governed commit."""
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    req = load_scenario(scenario, rebase_to_now=False)
    response, receipt = evaluate_financial(req, sealed_at=req.requested_execution_time)
    assert response.decision == "ALLOW"

    # Existing authority fence is bounded to current reference authority state;
    # no explicit shared ordering identity ties delegation mutations, semantic
    # applicability, evidence watermarks and protected commitment into one
    # comparable ordering domain.
    for field in (
        "authority_ordering_domain_id",
        "delegation_state_version",
        "delegation_watermark",
        "resolution_cut_id",
        "commit_order_fence_id",
    ):
        assert not hasattr(receipt, field)
