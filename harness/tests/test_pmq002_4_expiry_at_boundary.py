"""PMQ-002.4 failure-first expiry-at-boundary challenge.

Frozen proposition:
An execution permit MUST still be temporally valid when the protected
consequence boundary is acquired. A permit that expires while waiting to enter
that boundary MUST NOT form the represented consequence.
"""

from datetime import datetime, timedelta, timezone
from threading import Event, Thread
import time

from app.engines.authority_store import authority_state_guard, get_authority_state_version
from app.engines.execution_gateway import _GATEWAY_MINT_CAPABILITY
from app.engines.permit_authority import issue_execution_permit
from app.engines.protected_consequence import execute_protected_consequence


def test_pmq002_4_permit_expiring_while_waiting_for_final_boundary_cannot_form_consequence(tmp_path, monkeypatch):
    # Isolate durable replay state for this challenge.
    monkeypatch.setenv(
        "FLOWSIGNAL_PERMIT_CONSUMPTION_STORE",
        str(tmp_path / "permit-consumption.sqlite3"),
    )

    binding = "pmq0024-fixed-action-binding"
    valid_until = datetime.now(timezone.utc) + timedelta(milliseconds=300)
    permit = issue_execution_permit(
        authority_receipt_id="PMQ-002.4-RECEIPT",
        action_binding_hash=binding,
        authority_state_version=get_authority_state_version(),
        valid_until=valid_until.isoformat(),
        mint_capability=_GATEWAY_MINT_CAPABILITY,
    )
    assert permit is not None

    started = Event()
    finished = Event()
    result = {}

    def execute():
        started.set()
        result["execution"] = execute_protected_consequence(
            permit=permit,
            attempted_action_binding_hash=binding,
        )
        finished.set()

    # Hold the final authority-state boundary before starting execution. The
    # executor can perform its pre-boundary temporal check, but cannot enter the
    # protected critical section until this context releases the guard.
    with authority_state_guard():
        worker = Thread(target=execute)
        worker.start()
        assert started.wait(timeout=1.0)

        # Give the executor time to reach the boundary while the permit is still
        # valid, then keep the boundary unavailable until expiry has passed.
        time.sleep(0.45)
        assert datetime.now(timezone.utc) > valid_until
        assert not finished.is_set()

    worker.join(timeout=2.0)
    assert finished.is_set()

    assert result["execution"] != "CONSEQUENCE_FORMED", (
        "PMQ-002.4 FAILURE: permit expired while waiting for the final protected "
        "boundary but still formed the represented consequence after entering it"
    )
