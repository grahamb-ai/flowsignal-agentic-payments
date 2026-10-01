"""Failure-first candidate-generation resurrection challenge.

Frozen proposition:
Once a specific candidate generation has entered invalid space under a
material condition, restoring that condition MUST NOT allow the same
generation to regain a path to protected consequence. A later valid attempt
must be represented as a fresh candidate generation and fully requalified.

This is deliberately stronger than stale-receipt or stale-permit rejection.
It tests whether a new receipt can silently resurrect the same candidate after
an explicit REFUSE when no fresh candidate-generation identity exists.
"""

from dataclasses import replace
from pathlib import Path

from app.engines.action_binding import action_binding_hash
from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SCENARIO = REPOSITORY_ROOT / "harness/harness/scenarios/AP-001_allow.json"

def test_invalid_candidate_generation_cannot_regain_execution_after_condition_restore():
    # Sigma0: generation g is valid.
    candidate_g = load_scenario(SCENARIO)
    candidate_g_identity = (candidate_g.scenario_id, action_binding_hash(candidate_g))

    initial_response, initial_receipt = evaluate_financial(candidate_g)
    assert initial_response.decision == "ALLOW"
    assert initial_receipt is not None

    # Sigma1: the same action candidate enters invalid space because a
    # load-bearing current condition fails. The action identity is unchanged.
    invalid_g = replace(candidate_g, account_status="SUSPENDED")
    assert (invalid_g.scenario_id, action_binding_hash(invalid_g)) == candidate_g_identity

    invalid_response, invalid_receipt = evaluate_financial(invalid_g)
    assert invalid_response.decision == "REFUSE"
    assert invalid_receipt is not None

    # Sigma2: the condition is restored while the caller retains the same
    # scenario/action identity and all earlier artefacts. Re-evaluating must not
    # manufacture a new ALLOW for generation g. The system must require an
    # explicit fresh generation identity before this action can qualify again.
    restored_response, restored_receipt = evaluate_financial(candidate_g)
    assert restored_receipt is not None

    assert restored_response.decision != "ALLOW", (
        "CANDIDATE-GENERATION RESURRECTION FAILURE: the same scenario/action "
        "identity moved ALLOW -> REFUSE -> ALLOW after condition restoration. "
        "FlowSignal issued a fresh receipt without requiring a fresh candidate "
        "generation, so the invalidated generation regained a path to protected "
        "consequence."
    )
