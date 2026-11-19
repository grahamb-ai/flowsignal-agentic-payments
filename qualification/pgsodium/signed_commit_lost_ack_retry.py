"""Signed final-commit retry after lost acknowledgement (isolated reference).

A first valid commit succeeds. Simulate lost acknowledgement by discarding the
returned result, then retry the identical signed instruction from the actual
service login. Exactly one durable record must exist.
"""
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
import psycopg2
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"harness"))
from app.engines.provider_instruction_verifier import canonical_instruction

ADMIN=dict(host="127.0.0.1",port=55432,dbname="postgres",user="postgres",password="qualification-only")
SERVICE=dict(host="127.0.0.1",port=55432,dbname="postgres",user="fs_commit_service",password="qualification-only-service")
intent="RETRY-LOST-ACK-001"
mandate="RETRY-MANDATE-001"
with psycopg2.connect(**ADMIN) as db:
    with db.cursor() as cur:
        cur.execute("INSERT INTO fs_provider.mandates(id,epoch,revoked) VALUES (%s,7,false)",(mandate,))
payload=dict(payment_intent_id=intent,transaction_id=intent,mandate_id=mandate,
             authority_epoch=7,source_account="SOURCE-001",beneficiary="BENEFICIARY-001",
             amount="750000.00",currency="GBP",action="transfer",target="protected-provider")
instruction=canonical_instruction(payload)
assert instruction is not None
raw=json.dumps({"instruction":instruction,"expires_at":(datetime.now(timezone.utc)+timedelta(minutes=10)).isoformat()},
               sort_keys=True,separators=(",",":")).encode()
signature=Ed25519PrivateKey.from_private_bytes(bytes(range(32))).sign(raw)
params=("TEST-ISSUER",raw,signature,intent,mandate,7,"SOURCE-001","BENEFICIARY-001",75000000,"GBP","transfer","protected-provider")
sql="SELECT fs_provider.commit_signed_if_current(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
with psycopg2.connect(**SERVICE) as db:
    with db.cursor() as cur:
        cur.execute(sql,params)
        first=cur.fetchone()[0]
assert first=="COMMITTED",first
# Simulate a transport-level lost acknowledgement AFTER transaction committed.
# Do not use the first result to decide whether to retry.
with psycopg2.connect(**SERVICE) as db:
    with db.cursor() as cur:
        cur.execute(sql,params)
        second=cur.fetchone()[0]
assert second=="REFUSED_DUPLICATE_INTENT",second
with psycopg2.connect(**ADMIN) as db:
    with db.cursor() as cur:
        cur.execute("SELECT count(*) FROM fs_provider.commits WHERE intent_id=%s",(intent,))
        count=cur.fetchone()[0]
assert count==1,count
print(f"LOST_ACK_RETRY: first={first}; retry={second}; durable_count={count}; PASS",flush=True)
print("SIMULATED ACK LOSS ONLY; process crash, network ambiguity and reconciliation NOT QUALIFIED")
