# FS-SZ-PAY-001 — Independent consequence evidence: experiment specification

**Status: DESIGN / NOT IMPLEMENTED / STRUCTURAL ZERO NOT QUALIFIED.**

## Threat model
The PostgreSQL superuser owns the protected tables and signed commit function and has demonstrated a direct unsigned INSERT (preserved run 45150627886). A verifier reading only those same PostgreSQL tables cannot reliably distinguish genuine signed-function execution from forged administrator rows, because the administrator can change both rows and in-database audit evidence.

## Required separation
An independent evidence authority must run under a separate security principal and storage trust domain, with signing material unavailable to the PostgreSQL administrator. It must issue an authenticated, append-only record at the consequence boundary, bound to exact instruction bytes, issuer identity, authority epoch, execution target, payment intent, durable outcome, and monotonic event identity.

A PostgreSQL row, application log or caller-supplied signature is not itself independent evidence of an actual external payment consequence.

## Hostile acceptance matrix

| ID | Challenge | Required observable result |
|---|---|---|
| IE-01 | Valid signed final commitment and genuine external consequence | Independently verifiable bound receipt, one unique consequence |
| IE-02 | Administrator inserts commitment row without independent receipt | UNVERIFIED/REFUSE; never classify as authorised |
| IE-03 | Administrator edits beneficiary/amount after receipt | Receipt-to-record mismatch detected |
| IE-04 | Administrator deletes or rewrites database audit rows | Independent receipt history remains detectable |
| IE-05 | Replay genuine receipt for another payment intent or executor | Cryptographic binding mismatch detected |
| IE-06 | Independent authority unavailable or receipt stale | No new consequence formed unless institution-approved fail-closed protocol is met |
| IE-07 | Administrator controls all database credentials but not independent authority | Cannot mint a valid independent receipt or alter its append-only history |
| IE-08 | Actual external rail outcome disagrees with local commitment | Explicit unresolved/contradictory outcome; never falsely assert settlement |

## Evidence and limitations
Preserve raw original RED, candidate REDs, verifier logs, immutable receipt bytes, signer identity, keys, timestamps, independent state transitions and repeatable harness commands. Independently attest signer key ownership and operator isolation. A reference receipt prototype without an actual execution boundary cannot close IE-01, IE-06 or IE-08.

**Decision gate:** BOUNDARY-02 remains open. Do not weaken the privileged deployment guard or describe the current PostgreSQL reference as universally non-bypassable. Do not change `main` or production.
