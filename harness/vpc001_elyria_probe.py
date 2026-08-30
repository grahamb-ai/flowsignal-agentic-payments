"""VPC-001.2 comparative probe against frozen Elyria Admission Runtime.

The probe is intentionally bounded:
- first observe two independently admissible movements with no represented
  shared collision signal;
- then supply an explicit material-change/revalidation condition to the second
  movement and observe whether admission is withheld.

It does not modify the target implementation.
"""

from consequence_twin.engine import assess_movement


def payload(movement_id: str, **overrides):
    data = {
        "movement_id": movement_id,
        "authority_present": True,
        "authority_scope_valid": True,
        "standing_active": True,
        "evidence_present": True,
        "evidence_sufficient": True,
        "custody_preserved": True,
        "refusal_condition_active": False,
        "revalidation_required": False,
        "receipt_available": True,
        "replay_available": True,
    }
    data.update(overrides)
    return data


a = assess_movement(payload("BANK-A"))
b_without_signal = assess_movement(payload("BANK-B"))
b_with_signal = assess_movement(payload("BANK-B", revalidation_required=True))

print("ELYRIA_A", a.verdict.value)
print("ELYRIA_B_WITHOUT_COLLISION_SIGNAL", b_without_signal.verdict.value)
print("ELYRIA_B_WITH_REVALIDATION_SIGNAL", b_with_signal.verdict.value)

assert a.verdict.value == "ADMIT"
assert b_without_signal.verdict.value == "ADMIT"
assert b_with_signal.verdict.value != "ADMIT"
