"""Demonstrate why a valid Ed25519 signature alone does not bind SQL commit fields.

The signed canonical message is authentic, but a caller can submit unrelated
SQL commitment fields alongside it. A final-boundary function MUST derive the
signed message from the exact values it commits, not trust supplied bytes.
This is a deliberately preserved hostile characterization, not a remedy.
"""
import json
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[2]
v = json.loads(subprocess.check_output(
    [sys.executable, str(root / "harness/tests/fs_sz_pay_001_final_boundary_interop_vectors.py")],
    text=True))
pub, sig, message = v["public_key_hex"], v["signature_hex"], v["signed_bytes_utf8_hex"]
expected = v["canonical_instruction"]
assert expected["beneficiary"] != "ATTACKER"
sql = f"""\\set ON_ERROR_STOP on
-- An authentic signature over VECTOR-001 can coexist with unrelated caller
-- fields. This must NEVER be accepted as authorization to commit those fields.
WITH supplied AS (
 SELECT 'ATTACKER'::text AS beneficiary,
        decode('{message}','hex') AS claimed_signed_message,
        decode('{sig}','hex') AS signature,
        decode('{pub}','hex') AS issuer_public_key
)
SELECT 1 / CASE WHEN
 pgsodium.crypto_sign_verify_detached(signature,claimed_signed_message,issuer_public_key)
 AND beneficiary <> '{expected["beneficiary"]}'
 THEN 1 ELSE 0 END AS RED_signature_valid_but_sql_beneficiary_unbound
FROM supplied;
"""
print(sql)
