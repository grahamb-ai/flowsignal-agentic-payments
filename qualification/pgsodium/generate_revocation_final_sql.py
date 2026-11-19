"""Generate signed final-function revocation and epoch hostile qualification.

Runs after initial atomic and real-login tests. Uses test-only Ed25519 seed.
Sequential precommit orderings only; not a concurrent race or crash test.
"""
import json, subprocess, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
root=Path(__file__).resolve().parents[2]
v=json.loads(subprocess.check_output([sys.executable,str(root/"harness/tests/fs_sz_pay_001_final_boundary_interop_vectors.py")],text=True))
base=v["canonical_instruction"]
def lit(x):return "'"+str(x).replace("'","''")+"'"
def call(intent,epoch):
    instruction={**base,"payment_intent_id":intent,"authority_epoch":epoch}
    raw=json.dumps({"instruction":instruction,"expires_at":(datetime.now(timezone.utc)+timedelta(minutes=10)).isoformat()},sort_keys=True,separators=(",",":")).encode()
    sig=Ed25519PrivateKey.from_private_bytes(bytes(range(32))).sign(raw)
    return "fs_provider.commit_signed_if_current("+",".join([
      lit("TEST-ISSUER"),"decode("+lit(raw.hex())+",'hex')","decode("+lit(sig.hex())+",'hex')",
      lit(intent),lit(instruction["mandate_id"]),str(epoch),lit(instruction["source_account"]),
      lit(instruction["beneficiary"]),str(instruction["amount_minor"]),lit(instruction["currency"]),
      lit(instruction["action"]),lit(instruction["target"])])+")"
print("\\set ON_ERROR_STOP on")
print("SELECT current_user AS revocation_test_login;")
for name,intent,epoch in [("revoked_mandate","REVOKED-AFTER-SIGN",7),("stale_epoch","STALE-EPOCH-AFTER-ROTATION",7)]:
 print("SELECT 1 / CASE WHEN "+call(intent,epoch)+" = 'REFUSED_AUTHORITY' THEN 1 ELSE 0 END AS "+name+"_refused;")
print("SELECT 1 / CASE WHEN NOT EXISTS (SELECT 1 FROM fs_provider.commits WHERE intent_id IN ('REVOKED-AFTER-SIGN','STALE-EPOCH-AFTER-ROTATION')) THEN 1 ELSE 0 END AS zero_post_revocation_commitments;")
