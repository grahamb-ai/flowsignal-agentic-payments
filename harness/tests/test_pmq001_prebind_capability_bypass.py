"""PMQ-001 failure-first adversarial test.

Frozen propositions exercised:
- PMQ-001.1 Candidate movement before bind
- PMQ-001.6 NO_BIND / actual non-formation
- PMQ-001.7 Credible bypass attempts and route closure

The attack deliberately does NOT obtain an ALLOW or Authority Receipt from the
Runtime Authority. It asks whether execution-side-accessible permit issuance can
be used to form the represented protected consequence anyway.

If this test fails because CONSEQUENCE_FORMED is observed, preserve that failure
before remediation. Do not weaken the proposition or rewrite the test to green.
"""

from datetime import datetime, timezone

from app.engines.authority_store import get_authority_state_version
from app.engines.execution_gateway import ExecutionAttempt, action_binding_hash
from app.engines.protected_consequence import (
    execute_protected_consequence,
    issue_execution_permit,
)


def test_pmq001_no_runtime_authority_bind_cannot_mint_capability_and_form_consequence():
    # No evaluate_financial() call is made here. No Runtime Authority ALLOW and
    # no authentic Authority Receipt are obtained.
    attempt = ExecutionAttempt(
        actor_id="ATTACKER-EXECUTOR",
        principal_id="PRINCIPAL-UNBOUND",
        action="PAYMENT",
        target="PAYMENT-RAIL-REPRESENTED",
        amount=125000.00,
        currency="GBP",
        source_account="ACCOUNT-A",
        beneficiary="ATTACKER-CONTROLLED-BENEFICIARY",
        purpose="PMQ-001 direct capability bypass",
        mandate_id="MANDATE-NOT-RESOLVED-BY-RUNTIME-AUTHORITY",
        attempted_at=datetime.now(timezone.utc),
    )

    binding = action_binding_hash(attempt)

    # Adversarial step: invoke the execution-side-accessible permit issuer
    # directly, without an Authority Receipt having been produced or validated.
    permit = issue_execution_permit(
        authority_receipt_id="NO-AUTHORITY-RECEIPT-EXISTS",
        action_binding_hash=binding,
        authority_state_version=get_authority_state_version(),
    )

    result = execute_protected_consequence(
        permit=permit,
        attempted_action_binding_hash=binding,
    )

    # Frozen required property: absence of Runtime Authority bind must mean the
    # represented protected consequence cannot form.
    assert result != "CONSEQUENCE_FORMED", (
        "PMQ-001 FAILURE: represented consequence formed without a Runtime "
        "Authority ALLOW/Authority Receipt because permit-minting capability "
        "was independently reachable from the execution-side code boundary"
    )
