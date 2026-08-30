"""VPC-001.3 comparative probe against frozen Elyria Admission Runtime.

The target implementation is not modified.  The probe asks two separate
questions:
- does Elyria autonomously discover a cross-workflow semantic contradiction
  when both movements are otherwise locally admissible and no conflict signal
  is represented? (No credit is inferred merely from two ADMIT results.)
- once the material conflict is represented through Elyria's existing
  revalidation-required input, is autonomous admission withheld?
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


# A: needs X / disposes Y. B: needs Y / disposes X.  These semantic intents are
# intentionally NOT translated into an Elyria-native field because doing so
# would manufacture target capability.  We first observe the frozen runtime
# with two otherwise admissible movements.
a = assess_movement(payload("DEPT-A-DISPOSE-Y-ACQUIRE-X"))
b_without_signal = assess_movement(payload("DEPT-B-DISPOSE-X-ACQUIRE-Y"))

# Then represent the discovered correlated conflict using an existing target
# input: revalidation_required.  This tests enforcement after discovery, not
# autonomous semantic discovery itself.
b_with_conflict_signal = assess_movement(
    payload("DEPT-B-DISPOSE-X-ACQUIRE-Y", revalidation_required=True)
)

print("ELYRIA_DEPT_A", a.verdict.value)
print("ELYRIA_DEPT_B_WITHOUT_CONFLICT_SIGNAL", b_without_signal.verdict.value)
print("ELYRIA_DEPT_B_WITH_CONFLICT_SIGNAL", b_with_conflict_signal.verdict.value)

assert a.verdict.value == "ADMIT"
assert b_without_signal.verdict.value == "ADMIT"
assert b_with_conflict_signal.verdict.value != "ADMIT"
