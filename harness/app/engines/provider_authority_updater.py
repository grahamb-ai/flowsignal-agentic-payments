"""Reference signed mandate updater, separate from payment instruction signing.

This facade authenticates mandate-state changes before calling the reference
store. Direct SQLite and ProviderCommitFence methods remain an unclosed boundary.
"""
import json
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


def update_message(mandate_id, expected_epoch, operation):
    return json.dumps({"mandate_id": mandate_id, "expected_epoch": expected_epoch,
                       "operation": operation}, sort_keys=True,
                      separators=(",", ":")).encode()


def apply_signed_update(fence, *, mandate_id, expected_epoch, operation,
                        signature, updater_public_key):
    if operation != "REVOKE" or not isinstance(updater_public_key, Ed25519PublicKey):
        return "REFUSED_UPDATER"
    if type(expected_epoch) is not int or expected_epoch <= 0:
        return "REFUSED_UPDATER"
    try:
        updater_public_key.verify(bytes.fromhex(signature),
                                  update_message(mandate_id, expected_epoch, operation))
    except (ValueError, TypeError, Exception):
        return "REFUSED_UPDATER"
    # Fence method must perform version check and mutation atomically.
    return fence.revoke_if_epoch(mandate_id, expected_epoch)
