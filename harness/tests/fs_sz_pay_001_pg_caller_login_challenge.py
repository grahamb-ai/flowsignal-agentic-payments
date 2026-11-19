"""Hostile PostgreSQL login separation: untrusted caller must not become executor.

Ephemeral CI-only identities. Tests actual authenticated sessions, not SET ROLE
from a superuser migration session. Does not qualify production credential custody.
"""
import os
import psycopg

def main():
    caller_dsn = os.environ["FS_QUAL_CALLER_DSN"]
    executor_dsn = os.environ["FS_QUAL_EXECUTOR_DSN"]
    with psycopg.connect(caller_dsn) as db:
        with db.cursor() as cur:
            assert cur.execute("SELECT current_user, session_user").fetchone() == (
                "fs_payment_caller", "fs_payment_caller"
            )
            for query in (
                "SELECT fs_provider.commit_if_current('LOGIN-FORGED','MANDATE-CALLER',1,75000000,'ATTACKER')",
                "INSERT INTO fs_provider.commits(intent_id,mandate_id,epoch,amount_minor,beneficiary) VALUES ('LOGIN-DIRECT','MANDATE-CALLER',1,75000000,'ATTACKER')",
                "SET ROLE fs_payment_executor",
                "SET ROLE fs_authority_writer",
            ):
                try:
                    cur.execute(query)
                except psycopg.errors.InsufficientPrivilege:
                    db.rollback()
                else:
                    raise AssertionError(f"untrusted caller unexpectedly allowed: {query}")
    with psycopg.connect(executor_dsn) as db:
        with db.cursor() as cur:
            assert cur.execute("SELECT current_user").fetchone()[0] == "fs_payment_executor"
            assert cur.execute("SELECT COUNT(*) FROM fs_provider.commits WHERE mandate_id='MANDATE-CALLER'").fetchone()[0] == 0
    print("CALLER LOGIN ISOLATION PASS: denied direct function, INSERT, executor role, writer role")

if __name__ == "__main__":
    main()
