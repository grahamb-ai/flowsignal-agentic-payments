from dataclasses import replace

from app.engines.permit_authority import verify_execution_permit


AUTHORITY_FIELDS = (
    ("authority_snapshot_id", "attacker-snapshot"),
    ("authority_epoch_id", "attacker-epoch"),
    ("authority_fence_scope_key", "attacker:scope"),
    ("authority_fence", 999999),
    ("authoritative_source_id", "attacker-source"),
    ("source_competence_root_id", "attacker-competence"),
    ("authority_semantics_version", "attacker-version"),
    ("authority_semantics_definition_id", "attacker-definition"),
    ("authority_semantics_source_id", "attacker-semantic-source"),
)


def assert_authority_mutations_break_signed_permit(permit):
    """Shared hostile assertion for a valid permit produced by the gateway."""
    assert verify_execution_permit(permit)
    for field, attacker_value in AUTHORITY_FIELDS:
        mutated = replace(permit, **{field: attacker_value})
        assert not verify_execution_permit(mutated), field
