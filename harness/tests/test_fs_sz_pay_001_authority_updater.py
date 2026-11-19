"""Failure-first institutional mandate updater challenge.

Direct callers must not establish or revoke authoritative provider mandate state
merely by invoking the internal reference store. Preserved as a RED until the
updater credential boundary is qualified.
"""
from app.engines.t24_provider_commit_fence_reference import ProviderCommitFence


def test_unauthenticated_caller_cannot_revoke_active_mandate(tmp_path):
    fence = ProviderCommitFence(tmp_path / "provider.sqlite3")
    fence.establish("MANDATE-A", epoch=1)
    # Caller has no institutional updater credential.
    try:
        result = fence.revoke("MANDATE-A")
    except PermissionError:
        return
    # A later valid epoch-1 commit must still be possible if revocation was refused.
    status = fence.commit("MANDATE-A", 1, "post-forgery-intent")
    assert status == "COMMITTED", (
        "UNAUTHENTICATED_AUTHORITY_UPDATE_RED: caller revoked mandate "
        f"without institutional updater proof; result={result}, commit={status}"
    )


def test_direct_versioned_updater_cannot_bypass_institutional_signature(tmp_path):
    fence = ProviderCommitFence(tmp_path / "provider-versioned.sqlite3")
    fence.establish("MANDATE-A", epoch=1)
    # A correct expected epoch is not an institutional updater credential.
    try:
        result = fence.revoke_if_epoch("MANDATE-A", 1)
    except PermissionError:
        return
    assert fence.commit("MANDATE-A", 1, "after-direct-versioned-update") == "COMMITTED", (
        "UNAUTHENTICATED_VERSIONED_UPDATER_RED: direct revoke_if_epoch "
        f"accepted unauthenticated mutation: {result}"
    )


def test_unauthenticated_caller_cannot_establish_new_mandate(tmp_path):
    fence = ProviderCommitFence(tmp_path / "provider-establish.sqlite3")
    # This is a distinct authority creation path, not just a revocation bypass.
    try:
        result = fence.establish("FORGED-MANDATE", epoch=1)
    except PermissionError:
        return
    status = fence.commit("FORGED-MANDATE", 1, "forged-mandate-payment")
    assert status == "REFUSED_AUTHORITY", (
        "UNAUTHENTICATED_MANDATE_ESTABLISH_RED: direct caller created "
        f"active mandate; establish={result}, commit={status}"
    )
