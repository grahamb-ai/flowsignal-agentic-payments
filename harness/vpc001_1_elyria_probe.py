from consequence_twin.engine import assess_movement


def payload(**overrides):
    data = {
        "movement_id": "VPC-001.1",
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


baseline = assess_movement(payload())
unresolved = assess_movement(payload(evidence_sufficient=False))
revalidation = assess_movement(payload(revalidation_required=True))

print("ELYRIA_BASELINE", baseline.verdict.value)
print("ELYRIA_UNRESOLVED_REQUIRED_CONDITION", unresolved.verdict.value)
print("ELYRIA_REVALIDATION_REQUIRED", revalidation.verdict.value)

assert baseline.verdict.value == "ADMIT"
assert unresolved.verdict.value != "ADMIT"
assert revalidation.verdict.value != "ADMIT"
