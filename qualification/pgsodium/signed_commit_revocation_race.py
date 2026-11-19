"""Concurrent signed-commit vs revocation: deterministic row-lock orderings.

Runs on isolated PostgreSQL 16 container exposed at localhost:55432.
Uses qualification-only test issuer seed. Never deploy to production.
"""
import json
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import psycopg2

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "harness"))
from app.engines.provider_instruction_verifier import canonical_instruction

ADMIN = dict(host="127.0.0.1", port=55432, dbname="postgres", user="postgres", password="qualification-only")
SERVICE = dict(host="127.0.0.1", port=55432, dbname="postgres", user="fs_commit_service", password="qualification-only-service")
KEY = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
SQL = """SELECT fs_provider.commit_signed_if_current(
%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""

def signed_call(intent, mandate):
    payload = dict(payment_intent_id=intent, transaction_id=intent, mandate_id=mandate,
                   authority_epoch=7, source_account="SOURCE-001", beneficiary="BENEFICIARY-001",
                   amount="750000.00", currency="GBP", action="transfer", target="protected-provider")
    instruction = canonical_instruction(payload)
    assert instruction is not None
    raw = json.dumps({"instruction":instruction,"expires_at":(datetime.now(timezone.utc)+timedelta(minutes=10)).isoformat()},
                     sort_keys=True,separators=(",",":")).encode()
    return ("TEST-ISSUER",raw,KEY.sign(raw),intent,mandate,7,"SOURCE-001","BENEFICIARY-001",
            75000000,"GBP","transfer","protected-provider")

def admin_exec(sql, params=()):
    with psycopg2.connect(**ADMIN) as conn:
        with conn.cursor() as cur:
            cur.execute(sql,params)
            if cur.description:
                return cur.fetchone()[0]

def commit(intent, mandate, outcome):
    with psycopg2.connect(**SERVICE) as conn:
        with conn.cursor() as cur:
            cur.execute(SQL,signed_call(intent,mandate))
            outcome.append(cur.fetchone()[0])

def run_ordering(label, revocation_first):
    mandate="RACE-"+label
    intent="RACE-INTENT-"+label
    admin_exec("INSERT INTO fs_provider.mandates(id,epoch,revoked) VALUES (%s,7,false)",(mandate,))
    lock_acquired=threading.Event()
    release_lock=threading.Event()
    done=threading.Event()
    outcomes=[]
    errors=[]
    worker_pid=[]
    worker_connected=threading.Event()
    def locker():
        try:
            with psycopg2.connect(**ADMIN) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT id FROM fs_provider.mandates WHERE id=%s FOR UPDATE",(mandate,))
                    lock_acquired.set()
                    if not release_lock.wait(15):
                        raise TimeoutError("row lock release timed out")
                    if revocation_first:
                        cur.execute("UPDATE fs_provider.mandates SET revoked=true WHERE id=%s",(mandate,))
        except Exception as exc:
            errors.append(repr(exc))
    def worker():
        try:
            with psycopg2.connect(**SERVICE) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT pg_backend_pid()")
                    worker_pid.append(cur.fetchone()[0])
                    worker_connected.set()
                    cur.execute(SQL,signed_call(intent,mandate))
                    outcomes.append(cur.fetchone()[0])
        except Exception as exc:
            errors.append(repr(exc))
        finally:
            done.set()
    t1=threading.Thread(target=locker)
    t1.start()
    assert lock_acquired.wait(10), "failed to establish row lock"
    t2=threading.Thread(target=worker)
    t2.start()
    try:
        assert worker_connected.wait(10), "service login did not connect"
        # Observe the actual PostgreSQL backend waiting on the row-lock
        # dependency. A timeout or a merely unfinished thread is insufficient.
        observed_lock_wait=False
        deadline=time.monotonic()+10
        while time.monotonic()<deadline:
            if admin_exec("SELECT wait_event_type = 'Lock' FROM pg_stat_activity WHERE pid=%s",
                          (worker_pid[0],)) is True:
                observed_lock_wait=True
                break
            if done.is_set():
                break
            time.sleep(0.05)
        assert observed_lock_wait, ("service backend not observed waiting on a PostgreSQL lock",
                                    worker_pid,errors,outcomes)
        assert not done.is_set(), "commit completed while mandate lock held"
    finally:
        release_lock.set()
        t1.join(20)
        t2.join(20)
    assert not t1.is_alive() and not t2.is_alive() and not errors, (errors, outcomes)
    expected="REFUSED_AUTHORITY" if revocation_first else "COMMITTED"
    assert outcomes == [expected], (label,outcomes,expected)
    count=admin_exec("SELECT count(*) FROM fs_provider.commits WHERE intent_id=%s",(intent,))
    assert count == (0 if revocation_first else 1), (label,count)
    if not revocation_first:
        admin_exec("UPDATE fs_provider.mandates SET revoked=true WHERE id=%s",(mandate,))
        assert admin_exec("SELECT count(*) FROM fs_provider.commits WHERE intent_id=%s",(intent,)) == 1
    print(f"{label}: {expected}; durable_commit_count={count}; observed_pg_lock_wait=PASS",flush=True)

run_ordering("REVOKE-FIRST",True)
run_ordering("COMMIT-FIRST",False)
print("TWO SIGNED COMMIT/REVOCATION ROW-LOCK ORDERINGS PASS; crash/recovery NOT QUALIFIED")
