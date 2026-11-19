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
