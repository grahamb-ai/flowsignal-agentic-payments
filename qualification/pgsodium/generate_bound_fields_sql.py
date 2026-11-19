"""SQL binding experiment: verify Ed25519 and compare every signed field to SQL fields.

The signed bytes are supplied by the caller, but PostgreSQL parses them and
requires equality to each typed commitment parameter. This is NOT an atomic
commit function, issuer trust validation, or production-qualified parser.
"""
import json
import subprocess
import sys
from pathlib import Path
root=Path(__file__).resolve().parents[2]
v=json.loads(subprocess.check_output([sys.executable,str(root/"harness/tests/fs_sz_pay_001_final_boundary_interop_vectors.py")],text=True))
canonical=v["canonical_instruction"]
msg=v["signed_bytes_utf8_hex"]
sig=v["signature_hex"]
pub=v["public_key_hex"]
def q(s):
    return "'" + str(s).replace("'","''") + "'"
def predicate(fields):
    comparisons=[
        f"(signed->'instruction'->>'{k}') = {q(fields[k])}"
        for k in ("payment_intent_id","mandate_id","source_account","beneficiary","currency","action","target")
    ]
    comparisons.extend([
        f"(signed->'instruction'->>'authority_epoch')::bigint = {fields['authority_epoch']}",
        f"(signed->'instruction'->>'amount_minor')::bigint = {fields['amount_minor']}",
    ])
    return " AND ".join(comparisons)
def test(name, fields, expect):
    expr=predicate(fields)
    return f"""WITH proof AS (
 SELECT convert_from(decode('{msg}','hex'),'UTF8')::jsonb AS signed,
 decode('{msg}','hex') AS raw,
 decode('{sig}','hex') AS signature,
 decode('{pub}','hex') AS pub
)
SELECT 1 / CASE WHEN (pgsodium.crypto_sign_verify_detached(signature,raw,pub)
 AND ({expr})) IS {('TRUE' if expect else 'FALSE')}
 THEN 1 ELSE 0 END AS {name}
FROM proof;
"""
print("\\set ON_ERROR_STOP on")
print(test("signed_fields_match",canonical,True))
for k,val in [("beneficiary","ATTACKER"),("amount_minor",75000001),("authority_epoch",8),("payment_intent_id","OTHER-INTENT"),("target","alternate-provider")]:
    fields={**canonical,k:val}
    print(test("changed_"+k+"_refused",fields,False))
