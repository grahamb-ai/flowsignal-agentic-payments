"""Hostile reference: stolen commitment-service DB login bypasses Ed25519 verifier.

Intentionally RED until final boundary requires authenticated instruction evidence
at the commitment operation. No production secrets or real payment rail.
"""
import os
import psycopg

dsn = os.environ["FS_QUAL_COMMIT_SERVICE_DSN"]
admin = os.environ["FS_QUAL_ADMIN_DSN"]
with psycopg.connect(admin, autocommit=True) as db:
    db.execute("SET ROLE fs_authority_writer")
    db.execute(
        "INSERT INTO fs_provider.mandates(id,epoch,revoked) VALUES (%s,1,false)",
        ("MANDATE-STOLEN-CREDENTIAL",),
    )
    db.execute("RESET ROLE")

with psycopg.connect(dsn) as db:
    identity = db.execute("SELECT current_user").fetchone()[0]
    assert identity == "fs_commit_service", identity
    outcome = db.execute(
        "SELECT fs_provider.commit_if_current(%s,%s,%s,%s,%s)",
        ("STOLEN-CREDENTIAL-UNSIGNED", "MANDATE-STOLEN-CREDENTIAL",
         1, 75000000, "ATTACKER"),
    ).fetchone()[0]

with psycopg.connect(admin) as db:
    count = db.execute(
        "SELECT count(*) FROM fs_provider.commits WHERE intent_id=%s",
        ("STOLEN-CREDENTIAL-UNSIGNED",),
    ).fetchone()[0]

print(f"ACTUAL SERVICE LOGIN DIRECT SQL OUTCOME: {outcome}; durable records: {count}", flush=True)
assert outcome != "COMMITTED" and count == 0, (
    "BOUNDARY-02 RED: stolen service DB credential formed unsigned commitment"
)
