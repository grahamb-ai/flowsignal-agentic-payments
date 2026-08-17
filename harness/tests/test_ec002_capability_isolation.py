"""EC-002 — Capability Isolation

Pre-remediation adversarial tests.

Proposition: code acting only as the execution component must not possess a
usable independent capability to mint a consequence-authorising permit.

These tests intentionally inspect the current reference-harness trust boundary.
They are expected to FAIL before remediation if permit issuance/signing remains
available in the execution component's process/module boundary.
"""
import inspect

from app.engines import protected_consequence


def test_ec002_executor_module_does_not_expose_permit_issuer():
    """The consequence/executor module must not expose a callable permit issuer."""
    issuer = getattr(protected_consequence, "issue_execution_permit", None)
    assert issuer is None or not callable(issuer), (
        "CAPABILITY_ISOLATION_FAILURE: execution-side module exposes a callable "
        "permit issuer"
    )


def test_ec002_executor_module_does_not_hold_signing_key():
    """The execution-side module must not hold permit signing-key material."""
    assert not hasattr(protected_consequence, "_PERMIT_KEY"), (
        "CAPABILITY_ISOLATION_FAILURE: execution-side module contains permit "
        "signing-key material"
    )


def test_ec002_executor_module_does_not_expose_signing_primitive():
    """The execution-side module must not expose its permit signing primitive."""
    signer = getattr(protected_consequence, "_sign", None)
    assert signer is None or not callable(signer), (
        "CAPABILITY_ISOLATION_FAILURE: execution-side module exposes permit "
        "signing capability"
    )


def test_ec002_no_reference_permit_secret_embedded_in_executor_source():
    """No permit signing secret/default secret may be embedded in executor source."""
    source = inspect.getsource(protected_consequence)
    assert "flowsignal-reference-harness-ec0014-key" not in source, (
        "CAPABILITY_ISOLATION_FAILURE: reference permit secret is embedded in "
        "execution-side source"
    )
