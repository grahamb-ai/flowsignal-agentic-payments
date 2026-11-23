"""Kill a service PostgreSQL backend after signed function returns but before COMMIT.

This is an in-flight transaction/backend termination, not a full database
power-loss or external settlement test. The signed function's INSERT must roll
back, and retrying the exact instruction must commit exactly once.
"""
import json
import sys
from datetime import datetime,timedelta,timezone
from pathlib import Path
import psycopg2
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"harness"))
from app.engines.provider_instruction_verifier import canonical_instruction

ADMIN=dict(host="127.0.0.1",port=55432,dbname="postgres",user="postgres",password="qualification-only")
SERVICE=dict(host="127.0.0.1",port=55432,dbname="postgres",user="fs_commit_service",password="qualification-only-service")
intent="INFLIGHT-KILLED-001"
mandate="INFLIGHT-MANDATE-001"
with psycopg2.connect(**ADMIN) as conn:
    with conn.cursor() as cur:
        cur.execute("INSERT INTO fs_provider.mandates(id,epoch,revoked) VALUES (%s,7,false)",(mandate,))
payload=dict(payment_intent_id=intent,transaction_id=intent,mandate_id=mandate,
             authority_epoch=7,source_account="SOURCE-001",beneficiary="BENEFICIARY-001",
             amount="750000.00",currency="GBP",action="transfer",target="protected-provider")
ins=canonical_instruction(payload)
assert ins is not None
raw=json.dumps({"instruction":ins,"expires_at":(datetime.now(timezone.utc)+timedelta(minutes=10)).isoformat()},
               sort_keys=True,separators=(",",":")).encode()
signature=Ed25519PrivateKey.from_private_bytes(bytes(range(32))).sign(raw)
params=("TEST-ISSUER",raw,signature,intent,mandate,7,"SOURCE-001","BENEFICIARY-001",75000000,"GBP","transfer","protected-provider")
sql="SELECT fs_provider.commit_signed_if_current(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
# psycopg2 starts a transaction automatically. Do not commit this connection.
victim=psycopg2.connect(**SERVICE)
try:
    with victim.cursor() as cur:
        cur.execute("SELECT pg_backend_pid()")
        pid=cur.fetchone()[0]
        cur.execute(sql,params)
        before_commit=cur.fetchone()[0]
    assert before_commit=="COMMITTED",before_commit
    with psycopg2.connect(**ADMIN) as admin:
        with admin.cursor() as cur:
            cur.execute("SELECT count(*) FROM fs_provider.commits WHERE intent_id=%s",(intent,))
            invisible=cur.fetchone()[0]
            assert invisible==0,("uncommitted row visible",invisible)
            cur.execute("SELECT pg_terminate_backend(%s)",(pid,))
            assert cur.fetchone()[0] is True
finally:
    try: victim.close()
    except Exception: pass
with psycopg2.connect(**ADMIN) as admin:
    with admin.cursor() as cur:
        cur.execute("SELECT count(*) FROM fs_provider.commits WHERE intent_id=%s",(intent,))
        rolled_back=cur.fetchone()[0]
assert rolled_back==0,("uncommitted insert survived backend termination",rolled_back)
with psycopg2.connect(**SERVICE) as conn:
    with conn.cursor() as cur:
        cur.execute(sql,params)
        retry=cur.fetchone()[0]
assert retry=="COMMITTED",retry
with psycopg2.connect(**ADMIN) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM fs_provider.commits WHERE intent_id=%s",(intent,))
        durable=cur.fetchone()[0]
assert durable==1,durable
print(f"INFLIGHT_BACKEND_KILL: pre_commit_function={before_commit}; invisible_before_kill={invisible}; rolled_back={rolled_back}; retry={retry}; durable={durable}; PASS",flush=True)
print("IN-FLIGHT BACKEND TERMINATION ONLY: whole-server crash and external payment outcome NOT QUALIFIED")
