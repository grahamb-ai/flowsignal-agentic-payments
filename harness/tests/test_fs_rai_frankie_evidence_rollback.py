from dataclasses import replace
from datetime import timedelta
from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def test_frankie_008_fresh_but_superseded_evidence_has_no_watermark():
    """Freshness cannot detect rollback to an older authoritative observation."""
    from pathlib import Path
    scenario = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"
    req = load_scenario(scenario, rebase_to_now=False)
    t = req.requested_execution_time

    old_but_fresh = replace(
        req,
        screening_status="CLEAR",
        screening_captured_at=t - timedelta(seconds=5),
        screening_source="SANCTIONS-SOURCE-001",
    )
    response, receipt = evaluate_financial(old_but_fresh, sealed_at=t)
    assert response.decision == "ALLOW"

    ref = next(r for r in receipt.evidence_references if r.get("type") == "sanctions_screening")
    # Candidate has no monotonic source version/watermark/fence proving this is
    # the latest admissible observation rather than a fresh-but-superseded one.
    for field in ("source_version", "source_watermark", "source_fence", "supersedes"):
        assert field not in ref
