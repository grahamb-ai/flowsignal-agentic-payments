"""SCB-001 failure-first structural-closure challenge.

Frozen proposition:
When invalidity is already knowable from the governing authority topology,
the authority domain MUST NOT issue the candidate identity that enables a
path toward protected consequence.  Rejecting the candidate later at the
runtime adjudicator is insufficient for this proposition: the consequential
edge must be absent rather than present-and-blocked.

The paired liveness assertion prevents the proposition from being satisfied
by disabling candidate issuance altogether.
"""

from dataclasses import replace
from pathlib import Path

import pytest

from app.engines.action_binding import action_binding_hash
from app.engines.candidate_lifecycle_store import (
    is_authority_issued_candidate_generation,
)
from harness.runner import issue_initial_generation, load_scenario


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SCENARIO = REPOSITORY_ROOT / "harness/harness/scenarios/AP-001_allow.json"


def test_known_invalid_action_has_no_authority_issued_consequential_path():
    """A statically prohibited action must fail before candidate issuance."""
    valid = load_scenario(SCENARIO)
    known_invalid = replace(
        valid,
        candidate_generation_id="PENDING_AUTHORITY_ISSUANCE",
        action="DELETE_ACCOUNT",
    )

    with pytest.raises(
        ValueError,
        match="known-invalid movement has no enabled consequential path",
    ):
        issue_initial_generation(known_invalid)


def test_valid_action_retains_authority_issued_consequential_path():
    """Structural closure must preserve liveness for an allowed movement."""
    valid = load_scenario(SCENARIO)

    assert is_authority_issued_candidate_generation(
        valid.candidate_generation_id,
        valid.scenario_id,
        action_binding_hash(valid),
    )
