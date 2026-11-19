# FS-SZ-PAY-001 — Authority-state isolation acceptance gate

## Evidence and disposition (19 November 2026)
- Frozen CI: https://github.com/grahamb-ai/flowsignal-agentic-payments/actions/runs/44508853708
- Focused: **37 passed, 3 failed**; full: **105 passed, 4 failed** (three updater bypasses plus historical T23).
- Unauthenticated direct `establish`, `revoke`, and `revoke_if_epoch` calls changed provider-owned mandate state. These are genuine REDs, not fixture failures.
- The signed institutional updater facade is insufficient while direct state-mutating methods or writable SQLite remain accessible to the payment executor.

## Required deployment architecture
1. **Authority writer:** a separately deployed institutional updater identity exclusively holds authority-state write permissions and verifies issuer-signed state transitions. Signing credentials are unavailable to payment executors and the provider read/commit service.
2. **Commit executor:** may read authoritative mandate state and atomically commit an authorised payment, but cannot INSERT/UPDATE/DELETE mandate rows or invoke privileged state mutation. Separate database roles and permissions are required; a Python wrapper, object capability, or shared SQLite connection is not a security boundary.
3. **State version:** per-mandate monotonic epoch and signed transition identity; reject rollback, duplicate, out-of-order and cross-mandate updates in the same transaction as the mutation.
4. **Revocation ordering:** revocation and payment commitment must linearise against the same authoritative state; fail closed if that state is unavailable or stale.
5. **Evidence:** record issuer key ID, signed transition digest, mandate, previous/new epoch, effective time, applied time and outcome; preserve first RED and candidate GREEN independently.

## Hostile acceptance matrix
| Test | Caller / attempt | Required outcome |
|---|---|---|
| AUTH-01 | Payment executor invokes establish | Permission denied; no mandate created |
| AUTH-02 | Payment executor invokes revoke | Permission denied; epoch unchanged |
| AUTH-03 | Payment executor invokes revoke_if_epoch with correct epoch | Permission denied; epoch unchanged |
| AUTH-04 | Payment executor writes mandate table directly | Database permission denied |
| AUTH-05 | Institutional writer submits signed correct transition | Exactly one durable mutation |
| AUTH-06 | Wrong issuer / expired or modified signature | Refused, no mutation |
| AUTH-07 | Stale, replayed, rollback or wrong-mandate transition | Refused, no mutation |
| AUTH-08 | Concurrent revocation and commit | One authoritative serial order, no commit after effective revocation |
| AUTH-09 | Writer unavailable / state stale | No new protected commitment |
| AUTH-10 | Restart, lost acknowledgement and reconciliation | No duplicate; unknown remains unresolved without authoritative evidence |

## Implementation sequencing
- **First:** select a database/service boundary that supports independently enforceable roles (e.g. PostgreSQL roles with separate service identities). The current shared SQLite reference cannot demonstrate role-based isolation.
- **Second:** implement the writer service and provider executor with distinct credentials, and collect permission-denial evidence for AUTH-01 through AUTH-04 before positive tests.
- **Third:** run AUTH-05 through AUTH-10 against the same deployment, preserve complete logs and immutable commit SHA.
- **Fourth:** reconcile the legacy T23 unfenced-route counterexample by documenting its out-of-scope boundary; never delete or silently xfail the RED.

## Claims boundary
**BLOCKED / NOT MERGE-READY.** Reference payment authentication, revocation, replay and reconciliation tests do not establish protected authority-state mutation while the same process or filesystem identity can write the authority database. No production IAM, database ACL or real rail has been qualified. Keep main untouched.
