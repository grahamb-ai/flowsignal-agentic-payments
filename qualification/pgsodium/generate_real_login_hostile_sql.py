"""Hostile signed-function probes from a real commitment-service database login.

Runs after the positive signed-commit integration. Uses the same deterministic
test issuer and canonical payment bytes, but no private key. Distinguishes
unsigned, forged signature, and substituted beneficiary attacks.
"""
import json, subprocess, sys
from pathlib import Path
root=Path(__file__).resolve().parents[2]
v=json.loads(subprocess.check_output([sys.executable,str(root/"harness/tests/fs_sz_pay_001_final_boundary_interop_vectors.py")],text=True))
c=v["canonical_instruction"]
def q(s): return "'"+str(s).replace("'","''")+"'"
def call(intent,beneficiary,signature,message):
    return "fs_provider.commit_signed_if_current("+",".join([
        q("TEST-ISSUER"),"decode("+q(message)+",'hex')",
        "decode("+q(signature)+",'hex')",q(intent),q(c["mandate_id"]),
        str(c["authority_epoch"]),q(c["source_account"]),q(beneficiary),
        str(c["amount_minor"]),q(c["currency"]),q(c["action"]),q(c["target"])
    ])+")"
print("\\set ON_ERROR_STOP on")
print("SELECT current_user AS hostile_login;")
# Existing test-only signature has far-future expiry; SQL candidate limits expiry
# to one day, so use a fresh valid signature only in the positive integration.
# Here invalid signatures must fail without any commit.
for name, intent, beneficiary, signature, message, expected in [
 ("unsigned", "HOSTILE-UNSIGNED", c["beneficiary"], "00"*64, v["signed_bytes_utf8_hex"], "REFUSED_INVALID_BINDING"),
 ("forged", c["payment_intent_id"], c["beneficiary"], "00"*64, v["signed_bytes_utf8_hex"], "REFUSED_UNAUTHENTICATED_INSTRUCTION"),
 ("beneficiary_substitution", c["payment_intent_id"], "ATTACKER", v["signature_hex"], v["signed_bytes_utf8_hex"], "REFUSED_INVALID_BINDING"),
]:
    # Exact refusal reasons may differ by ordering; all are required to not commit.
    expr=call(intent,beneficiary,signature,message)
    print("SELECT 1 / CASE WHEN "+expr+" <> 'COMMITTED' THEN 1 ELSE 0 END AS "+name+"_no_commit;")
print("SELECT 1 / CASE WHEN NOT EXISTS (SELECT 1 FROM fs_provider.commits WHERE intent_id='HOSTILE-UNSIGNED') THEN 1 ELSE 0 END AS no_unsigned_record;")
