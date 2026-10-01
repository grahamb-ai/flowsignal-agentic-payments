"""PCG-002 failure-first challenge: caller-minted successor substitution.

Frozen proposition:
Once candidate generation g has entered terminal invalid space, a caller MUST
NOT regain a path to protected consequence merely by replacing g with an
arbitrary identifier. Any successor generation must be issued by the
authority-owned lifecycle service, linked to g, and bound to the same canonical
action.
"""

from dataclasses import replace
from pathlib import Path
import uuid

from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SCENARIO = REPOSITORY_ROOT / "harness/harness/scenarios/AP-001_allow.json"


def test_caller_minted_successor_cannot_bypass_terminal_invalidation():
    candidate_g = load_scenario(SCENARIO)

    initial_response, _ = evaluate_financial(candidate_g)
    assert initial_response.decision == "ALLOW"

    invalid_response, _ = evaluate_financial(
        replace(candidate_g, account_status="SUSPENDED")
    )
    assert invalid_response.decision == "REFUSE"

    # The caller keeps the same action and restored conditions, but substitutes
    # an arbitrary UUID for the invalidated generation. This is not an
    # authority-issued successor and has no authenticated parent lineage.
    fabricated_successor = replace(
        candidate_g,
        candidate_generation_id=str(uuid.uuid4()),
    )
    fabricated_response, fabricated_receipt = evaluate_financial(
        fabricated_successor
    )

    assert fabricated_response.decision == "REFUSE", (
        "UNAUTHORISED SUCCESSOR-GENERATION FAILURE: replacing a terminally "
        "invalidated generation with a caller-chosen UUID restored ALLOW. "
        "Candidate identity is caller-asserted rather than authority-issued."
    )
    assert fabricated_receipt is not None
    assert any(
        check.name == "candidate_generation_authority_issued"
        and not check.passed
        for check in fabricated_receipt.checks
    )
