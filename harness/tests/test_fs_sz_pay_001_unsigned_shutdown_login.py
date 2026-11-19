"""BOUNDARY-01: verify the staged unsigned-function shutdown with a real executor login.

This deliberately tests a fail-closed database. It does not qualify a
replacement authenticated commit operation or production credential custody.
"""
import os
import psycopg
import pytest

@pytest.mark.skipif(not os.environ.get("FS_QUAL_EXECUTOR_DSN"), reason="requires executor login")
def test_real_executor_login_cannot_use_unsigned_commit():
    with psycopg.connect(os.environ["FS_QUAL_EXECUTOR_DSN"]) as db:
        with db.cursor() as cur:
            cur.execute("SELECT current_user")
            assert cur.fetchone()[0] == "fs_payment_executor"
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                cur.execute(
                    "SELECT fs_provider.commit_if_current(%s,%s,%s,%s,%s)",
                    ("REAL-LOGIN-UNSIGNED", "MANDATE-DISABLED-LEGACY", 1, 75000000, "ATTACKER"),
                )
            db.rollback()
            cur.execute(
                "SELECT count(*) FROM fs_provider.commits WHERE intent_id=%s",
                ("REAL-LOGIN-UNSIGNED",),
            )
            assert cur.fetchone()[0] == 0
