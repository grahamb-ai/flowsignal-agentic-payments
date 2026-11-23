# IE-W10 — Independent replay authority qualification gate (DESIGN / NOT RUN)

Baseline: IE-W09 reference GREEN, with administrator-deletion RED preserved.
This is an acceptance contract, **not evidence that separate administrative domains exist**.

## Trust boundary

- Payment executor identity can only request consume/status for a bound rail event. No database, backup, IAM, key, service deployment, or administrator permissions.
- Replay authority uses a different service identity and administrative control plane. It owns durable, conditional create-only event records.
- Independent witness/anchor retains monotonic sequence or signed checkpoints under a distinct principal; replay authority operators cannot reset it.
- Signing-key revocation is read from an authoritative versioned key-state source, not caller-provided flags.
- Rail attestation is signed by a separately controlled source and binds intent, rail event ID, outcome, issuer, key ID, issued time, expiry and source epoch.
- Missing, stale, conflicting or unreachable authority state produces UNRESOLVED, never SETTLED.

## Required hostile experiments

| ID | Attack | Required observable result |
| --- | --- | --- |
| W10-01 | Executor tries ledger delete/reset | Permission denied; original event remains consumed |
| W10-02 | Two executor identities consume same event simultaneously | Exactly one accepted; one replay refused; durable one-record proof |
| W10-03 | Executor restarted, replaced or moved | Event remains consumed across process and host boundaries |
| W10-04 | Replay authority unavailable | No successful rail classification; no consequential retry without reconciliation |
| W10-05 | Replay store record deleted by store administrator | Witness detects rollback or loss; **fail closed** (preserve RED if not) |
| W10-06 | Authentic older checkpoint restored | Monotonic external anchor refuses rollback |
| W10-07 | Signing key revoked after earlier valid attestation | Fresh independent key epoch refuses subsequent use |
| W10-08 | Attestation forged, wrong intent, future dated or expired | No successful classification |
| W10-09 | Concurrent retry after lost acknowledgement | Same durable event/receipt; no second settlement instruction |
| W10-10 | Independent rail reports REJECTED after local COMMITTED | Explicit contradiction; never silently SETTLED |

## Evidence required

Capture immutable commit SHA, workflow/run ID, identities and effective IAM policy,
separate authority logs, signed input/output bytes, timestamps and clock source,
durable store readbacks before and after restart, external witness version,
actual independently observed non-production rail outcome, and original hostile
RED artifacts. No production credentials or secrets in public CI artifacts.

## Stop conditions

Any successful replay after deletion, any unauthorized alternate commit route,
or any inability to prove independent custody means **STRUCTURAL ZERO NOT QUALIFIED**.

Do not modify `main` or production. Do not substitute a same-host SQLite,
in-memory key flag or mocked rail for independent-domain qualification.
