"""IE-04 reference: independently held hash-chain checkpoint detects DB audit rewrite.

This is a local deterministic characterisation, NOT external immutable storage.
A compromised operator with both the checkpoint and ledger can rewrite both.
"""
import hashlib
import json

def wire(event):
    return json.dumps(event,sort_keys=True,separators=(",",":")).encode("utf-8")

def digest(previous,event):
    return hashlib.sha256(bytes.fromhex(previous)+wire(event)).hexdigest()

def verify(events,expected_checkpoint):
    previous="00"*32
    for event in events:
        previous=digest(previous,event)
    return previous==expected_checkpoint

def main():
    original=[
      {"event_id":1,"intent":"IE04-A","outcome":"COMMITTED_REFERENCE","amount_minor":100},
      {"event_id":2,"intent":"IE04-B","outcome":"REFUSED_REFERENCE","amount_minor":200},
    ]
    checkpoint="00"*32
    for event in original: checkpoint=digest(checkpoint,event)
    assert verify(original,checkpoint)
    print("IE-04 BASELINE: retained independent checkpoint matches complete local ledger")
    rewritten=[dict(original[0],amount_minor=900),original[1]]
    assert not verify(rewritten,checkpoint)
    print("IE-04 ALTER: administrator-edited event mismatches retained checkpoint")
    assert not verify(original[:1],checkpoint)
    print("IE-04 DELETE: truncated audit ledger mismatches retained checkpoint")
    assert not verify(list(reversed(original)),checkpoint)
    print("IE-04 REORDER: reordered events mismatch retained checkpoint")
    print("LIMITATION: checkpoint is only simulated as independent; no separate principal, append-only service, external settlement or anti-rollback anchor")

if __name__=="__main__":main()
