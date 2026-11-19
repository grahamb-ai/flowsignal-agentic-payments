"""Generate SQL Ed25519 interoperability probes from deterministic test-only vectors.

This checks cryptographic byte interoperability only. It does NOT establish
canonical field derivation, issuer trust, or atomic final commitment.
"""
import json
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[2]
raw = subprocess.check_output(
    [sys.executable, str(root / "harness/tests/fs_sz_pay_001_final_boundary_interop_vectors.py")],
    text=True,
)
v = json.loads(raw)
pub = v["public_key_hex"]
sig = v["signature_hex"]
msg = v["signed_bytes_utf8_hex"]
assert all(len(s) % 2 == 0 and all(c in "0123456789abcdef" for c in s) for s in (pub, sig, msg))
assert len(pub) == 64 and len(sig) == 128
# The valid signature must verify, while changing even one message byte fails.
altered = ("00" if msg[:2] != "00" else "01") + msg[2:]
sql = f"""\\set ON_ERROR_STOP on
SELECT 1 / CASE WHEN pgsodium.crypto_sign_verify_detached(
 decode('{sig}','hex'),decode('{msg}','hex'),decode('{pub}','hex')
) THEN 1 ELSE 0 END AS valid_ed25519_accepted;
SELECT 1 / CASE WHEN NOT pgsodium.crypto_sign_verify_detached(
 decode('{sig}','hex'),decode('{altered}','hex'),decode('{pub}','hex')
) THEN 1 ELSE 0 END AS changed_message_refused;
SELECT 1 / CASE WHEN NOT pgsodium.crypto_sign_verify_detached(
 decode('{('00' if sig[:2] != '00' else '01') + sig[2:]}','hex'),
 decode('{msg}','hex'),decode('{pub}','hex')
) THEN 1 ELSE 0 END AS changed_signature_refused;
"""
print(sql)
