"""Characterise noncanonical but validly signed JSON accepted by SQL final gate.

An attacker holding an institution's signing key is not the assumed threat.
This test asks whether the boundary enforces a single canonical wire encoding,
rather than treating any signed parseable JSON as canonical. It must preserve
the observed outcome and NEVER claim closure from a refusal for other reasons.
"""
import json,sys
from datetime import datetime,timedelta,timezone
from pathlib import Path
import psycopg2
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"harness"))
from app.engines.provider_instruction_verifier import canonical_instruction
ADMIN=dict(host="127.0.0.1",port=55432,dbname="postgres",user="postgres",password="qualification-only")
SERVICE=dict(host="127.0.0.1",port=55432,dbname="postgres",user="fs_commit_service",password="qualification-only-service")
intent="NONCANONICAL-001"
mandate="NONCANONICAL-MANDATE"
with psycopg2.connect(**ADMIN) as db:
    with db.cursor() as cur:
        cur.execute("INSERT INTO fs_provider.mandates(id,epoch,revoked) VALUES (%s,7,false)",(mandate,))
payload=dict(payment_intent_id=intent,transaction_id=intent,mandate_id=mandate,
             authority_epoch=7,source_account="SOURCE-001",beneficiary="BENEFICIARY-001",
             amount="750000.00",currency="GBP",action="transfer",target="protected-provider")
ins=canonical_instruction(payload)
assert ins is not None
expiry=(datetime.now(timezone.utc)+timedelta(minutes=10)).isoformat()
canonical=json.dumps({"instruction":ins,"expires_at":expiry},sort_keys=True,separators=(",",":")).encode()
# Exact same JSON object, but pretty-printed noncanonical wire bytes.
noncanonical=json.dumps({"instruction":ins,"expires_at":expiry},sort_keys=True,indent=2).encode()
assert canonical!=noncanonical and json.loads(canonical)==json.loads(noncanonical)
signature=Ed25519PrivateKey.from_private_bytes(bytes(range(32))).sign(noncanonical)
params=("TEST-ISSUER",noncanonical,signature,intent,mandate,7,"SOURCE-001","BENEFICIARY-001",75000000,"GBP","transfer","protected-provider")
with psycopg2.connect(**SERVICE) as db:
    with db.cursor() as cur:
        cur.execute("SELECT fs_provider.commit_signed_if_current(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",params)
        outcome=cur.fetchone()[0]
with psycopg2.connect(**ADMIN) as db:
    with db.cursor() as cur:
        cur.execute("SELECT count(*) FROM fs_provider.commits WHERE intent_id=%s",(intent,))
        count=cur.fetchone()[0]
assert (outcome=="COMMITTED")== (count==1),(outcome,count)
print(f"NONCANONICAL_SIGNED_WIRE: outcome={outcome}; durable={count}; canonical_bytes_equal=false")
if outcome=="COMMITTED":
    print("PRESERVED RED CHARACTERISATION: SQL gate accepts signed noncanonical JSON bytes; strict wire canonicalisation NOT ENFORCED")
else:
    print("NONCANONICAL REFUSED: investigate exact reason before claiming canonicalisation enforcement")
