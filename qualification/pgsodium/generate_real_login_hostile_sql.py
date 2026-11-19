"""Isolated real-login hostile probes with fresh valid Ed25519 proof.

Every hostile case is independently checked against a baseline that would
commit with the same unexpired signed instruction. Test-only seed only.
"""
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

root = Path(__file__).resolve().parents[2]
v = json.loads(subprocess.check_output(
    [sys.executable, str(root / "harness/tests/fs_sz_pay_001_final_boundary_interop_vectors.py")],
    text=True))
c = {**v["canonical_instruction"], "payment_intent_id": "HOSTILE-FRESH-001"}
expiry = (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat()
message = json.dumps(
    {"instruction": c, "expires_at": expiry},
    sort_keys=True, separators=(",", ":")).encode("utf-8")
signature = Ed25519PrivateKey.from_private_bytes(bytes(range(32))).sign(message).hex()
def q(s):
    return "'" + str(s).replace("'", "''") + "'"
def call(*, intent=None, beneficiary=None, sig=None, raw=None):
    return "fs_provider.commit_signed_if_current(" + ",".join([
        q("TEST-ISSUER"),
        "decode(" + q((raw if raw is not None else message.hex())) + ",'hex')",
        "decode(" + q((sig if sig is not None else signature)) + ",'hex')",
        q(intent if intent is not None else c["payment_intent_id"]),
        q(c["mandate_id"]), str(c["authority_epoch"]),
        q(c["source_account"]), q(beneficiary if beneficiary is not None else c["beneficiary"]),
        str(c["amount_minor"]), q(c["currency"]), q(c["action"]), q(c["target"])
    ]) + ")"

print("\\set ON_ERROR_STOP on")
print("SELECT current_user AS hostile_login;")
# Test baseline signature separately, without creating a commitment.
print("SELECT 1 / CASE WHEN pgsodium.crypto_sign_verify_detached(" +
      "decode(" + q(signature) + ",'hex'),decode(" + q(message.hex()) +
      ",'hex'),decode(" + q(v["public_key_hex"]) + ",'hex'))" +
      " THEN 1 ELSE 0 END AS fresh_signature_cryptographically_valid;")
for name, expression in (
    ("unsigned_refused", call(sig="00"*64)),
    ("beneficiary_substitution_refused", call(beneficiary="ATTACKER")),
    ("intent_substitution_refused", call(intent="HOSTILE-DIFFERENT-INTENT")),
    ("signed_message_mutation_refused", call(raw=("00" if message.hex()[:2] != "00" else "01") + message.hex()[2:])),
):
    print("SELECT 1 / CASE WHEN " + expression + " <> 'COMMITTED' THEN 1 ELSE 0 END AS " + name + ";")
print("SELECT 1 / CASE WHEN NOT EXISTS (SELECT 1 FROM fs_provider.commits WHERE intent_id LIKE 'HOSTILE-%') THEN 1 ELSE 0 END AS zero_hostile_commitments;")

# Positive control: prove that these exact signed bytes and service-login
# privileges can commit when the fields are not altered.
print("SELECT 1 / CASE WHEN " + call() +
      " = 'COMMITTED' THEN 1 ELSE 0 END AS real_login_valid_positive_control;")
print("SELECT 1 / CASE WHEN (SELECT count(*) FROM fs_provider.commits " +
      "WHERE intent_id = 'HOSTILE-FRESH-001') = 1 THEN 1 ELSE 0 END AS positive_control_durable_once;")
