"""PCG-003 failure-first challenge: sibling successor branching.

Frozen proposition:
Once an invalidated candidate generation has produced its permitted successor,
the same parent must not independently produce another concurrently standing
successor for the same scenario and canonical action unless branching is
explicitly represented as an allowed lifecycle transition.
"""

from dataclasses import replace
from pathlib import Path

import pytest

from app.engines.financial_runtime import evaluate_financial
from harness.runner import issue_successor_generation, load_scenario


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SCENARIO = REPOSITORY_ROOT / "harness/harness/scenarios/AP-001_allow.json"


def test_terminal_parent_cannot_issue_two_concurrent_successors(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setenv(
        "FLOWSIGNAL_CANDIDATE_LIFECYCLE_STORE",
        str(tmp_path / "candidate-lifecycle.sqlite3"),
    )

    parent = load_scenario(SCENARIO)
    refused, _ = evaluate_financial(
        replace(parent, account_status="SUSPENDED")
    )
    assert refused.decision == "REFUSE"

    first_successor = issue_successor_generation(parent)

    with pytest.raises(
        ValueError,
        match="successor transition is no longer enabled",
    ):
        issue_successor_generation(parent)

    first_response, _ = evaluate_financial(first_successor)
    assert first_response.decision == "ALLOW"
