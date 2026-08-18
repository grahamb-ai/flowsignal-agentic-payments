from __future__ import annotations

from datetime import datetime, timedelta, timezone

import app.engines.authority_store as authority_store
from app.engines.authority_store import advance_authority_state_version, get_authority_state_version
from app.engines.permit_authority import _GATEWAY_MINT_CAPABILITY, issue_execution_permit
from app.engines.protected_consequence import execute_protected_consequence


def test_pmq002_5_older_authority_state_cannot_be_restored_to_resurrect_stale_permit(tmp_path, monkeypatch):
    """Frozen PMQ-002.5 proposition: stale authority must not be resurrectable.

    The challenge intentionally looks for a supported authority-store mutation
    operation capable of restoring an older version. Absence of such an
    operation is part of the represented interface property under test; direct
    mutation of module-private process memory is explicitly outside this
    proposition's scope.
    """
    monkeypatch.setenv(
        "FLOWSIGNAL_PERMIT_CONSUMPTION_STORE",
        str(tmp_path / "permit-consumption.sqlite3"),
    )

    version_n = get_authority_state_version()
    binding = "pmq0025-fixed-action-binding"
    permit = issue_execution_permit(
        authority_receipt_id="PMQ-002.5-RECEIPT",
        action_binding_hash=binding,
        authority_state_version=version_n,
        valid_until=(datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat(),
        mint_capability=_GATEWAY_MINT_CAPABILITY,
    )
    assert permit is not None

    version_n_plus_1 = advance_authority_state_version()
    assert version_n_plus_1 > version_n

    stale_outcome = execute_protected_consequence(
        permit=permit,
        attempted_action_binding_hash=binding,
    )
    assert stale_outcome == "DENIED_AUTHORITY_STATE_STALE"

    # Challenge the supported authority-store interface. A setter/restore/
    # rollback operation would create a potential stale-state resurrection
    # surface and must not permit movement back to N.
    rollback_candidates = [
        "set_authority_state_version",
        "restore_authority_state_version",
        "rollback_authority_state_version",
        "reset_authority_state_version",
    ]
    exposed = [name for name in rollback_candidates if callable(getattr(authority_store, name, None))]

    for name in exposed:
        operation = getattr(authority_store, name)
        try:
            operation(version_n)
        except (ValueError, RuntimeError, PermissionError, TypeError):
            pass

    assert get_authority_state_version() >= version_n_plus_1, (
        "PMQ-002.5 FAILURE: supported authority-store mutation surface restored an "
        "older authority-state version after a newer state had committed"
    )

    # The previously stale permit must remain stale after every supported
    # rollback attempt.
    resurrected_outcome = execute_protected_consequence(
        permit=permit,
        attempted_action_binding_hash=binding,
    )
    assert resurrected_outcome != "CONSEQUENCE_FORMED", (
        "PMQ-002.5 FAILURE: a previously stale permit formed the represented "
        "consequence after authority-state rollback"
    )
    assert resurrected_outcome == "DENIED_AUTHORITY_STATE_STALE"
