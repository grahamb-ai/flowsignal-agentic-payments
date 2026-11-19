"""Bounded signed updater qualification; does not close direct store access."""
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from app.engines.provider_authority_updater import apply_signed_update, update_message
from app.engines.t24_provider_commit_fence_reference import ProviderCommitFence


def test_signed_revocation_requires_correct_issuer_and_epoch(tmp_path):
    fence = ProviderCommitFence(tmp_path / "provider.sqlite3")
    fence.establish("MANDATE-A", epoch=1)
    trusted = Ed25519PrivateKey.generate()
    attacker = Ed25519PrivateKey.generate()
    msg = update_message("MANDATE-A", 1, "REVOKE")
    forged = attacker.sign(msg).hex()
    assert apply_signed_update(fence, mandate_id="MANDATE-A", expected_epoch=1,
                               operation="REVOKE", signature=forged,
                               updater_public_key=trusted.public_key()) == "REFUSED_UPDATER"
    assert fence.commit("MANDATE-A", 1, "still-authorised") == "COMMITTED"
    valid = trusted.sign(msg).hex()
    assert apply_signed_update(fence, mandate_id="MANDATE-A", expected_epoch=1,
                               operation="REVOKE", signature=valid,
                               updater_public_key=trusted.public_key()) == "REVOKED"
    assert fence.commit("MANDATE-A", 1, "after-revocation") == "REFUSED_AUTHORITY"
    assert apply_signed_update(fence, mandate_id="MANDATE-A", expected_epoch=1,
                               operation="REVOKE", signature=valid,
                               updater_public_key=trusted.public_key()) == "REFUSED_STALE_UPDATE"


def test_signed_update_cannot_substitute_mandate_or_epoch(tmp_path):
    fence = ProviderCommitFence(tmp_path / "provider.sqlite3")
    fence.establish("MANDATE-A", epoch=1)
    fence.establish("MANDATE-B", epoch=1)
    trusted = Ed25519PrivateKey.generate()
    signature = trusted.sign(update_message("MANDATE-A", 1, "REVOKE")).hex()
    assert apply_signed_update(fence, mandate_id="MANDATE-B", expected_epoch=1,
                               operation="REVOKE", signature=signature,
                               updater_public_key=trusted.public_key()) == "REFUSED_UPDATER"
    assert apply_signed_update(fence, mandate_id="MANDATE-A", expected_epoch=2,
                               operation="REVOKE", signature=signature,
                               updater_public_key=trusted.public_key()) == "REFUSED_UPDATER"
    assert fence.commit("MANDATE-B", 1, "mandate-b-active") == "COMMITTED"
