"""EC-002 — Capability Isolation

Frozen failure-first adversarial tests.

Proposition: code acting only as the represented execution component must not
possess an independent usable capability to mint a consequence-authorising
permit.
"""
import inspect

from app.engines import protected_consequence


def test_ec002_executor_module_does_not_expose_permit_issuer():
    issuer = getattr(protected_consequence, "issue_execution_permit", None)
    assert issuer is None or not callable(issuer), (
        "CAPABILITY_ISOLATION_FAILURE: execution-side module exposes a callable "
        "permit issuer"
    )


def test_ec002_executor_module_does_not_hold_signing_key():
    assert not hasattr(protected_consequence, "_PERMIT_KEY"), (
        "CAPABILITY_ISOLATION_FAILURE: execution-side module contains permit "
        "signing-key material"
    )


def test_ec002_executor_module_does_not_expose_signing_primitive():
    signer = getattr(protected_consequence, "_sign", None)
    assert signer is None or not callable(signer), (
        "CAPABILITY_ISOLATION_FAILURE: execution-side module exposes permit "
        "signing capability"
    )


def test_ec002_no_reference_permit_secret_embedded_in_executor_source():
    source = inspect.getsource(protected_consequence)
    assert "flowsignal-reference-harness-ec0014-key" not in source, (
        "CAPABILITY_ISOLATION_FAILURE: reference permit secret is embedded in "
        "execution-side source"
    )
