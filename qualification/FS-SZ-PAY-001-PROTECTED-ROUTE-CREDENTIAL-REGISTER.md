# FS-SZ-PAY-001 — Protected-route and credential closure register

## Evidence checkpoint
Candidate commit `2007dfa686ff920ac477bbe340fccc761becec2f`.
GitHub Actions: https://github.com/grahamb-ai/flowsignal-agentic-payments/actions/runs/44506931476
Focused **34/34 passed**; full **102 passed, 1 failed** (preserved historical T23).
These results qualify bounded reference behaviours, not universal route closure.

## Source-observed entry points and authority

| Surface | Consequence capability | Boundary | Current qualification |
|---|---|---|---|
| `external_consequence_adapter.execute_external_payment` | Calls provider `/payments` | FlowSignal signed permit, local durable intent claim; separately supplied institutional instruction | End-to-end reference test GREEN; credential origin not independently production-qualified |
| `Handler.POST /payments` | Fenced provider transfer | Ed25519 public-key verification, exact payment binding, provider-owned epoch/revocation and durable unique intent | Reference authenticated tests GREEN |
| `ExternalLedger.transfer` direct call | Same fenced transfer in configured mode | Same public-key verification and fence | Reference hostile direct-caller tests GREEN |
| `ProviderCommitFence.commit_transfer` direct method | Writes simulated transfer record | SQLite epoch/revocation/intent checks, **no independent issuer signature check in this method** | Internal trust boundary only; direct invocation must be restricted |
| `ProviderCommitFence.commit` direct method | Writes a commit claim, not transfer record | SQLite epoch/revocation/intent checks; no institutional proof | Internal reference helper; caller permissions unresolved |
| `Handler.POST /admin/reset` | Resets legacy in-memory ledger; fenced mode leaves durable provider transfer records intact | Fenced HTTP mode now refuses this route; legacy test mode remains unqualified | Candidate change, CI pending |
| `Handler.GET /state` | Reads transfer count / sandbox balances | Fenced HTTP mode now refuses this route; legacy test mode remains unqualified | Candidate change, CI pending |
| `Handler.POST /payments/reconcile` | Read-only lookup | Signed instruction verified; missing reference record is not proof of non-commitment | Bounded GREEN; global completeness not demonstrated |
| `ExternalLedger(legacy_test_mode=True)` | Unfenced sandbox payment | No mandate or institutional signature | Explicitly OUT OF SCOPE; must be inaccessible to protected credentials |
| `ProviderCommitFence.revoke` / `establish` | Mutates mandate authority | Local SQLite method, no demonstrated institutional updater IAM | Authoritative state provenance unresolved |

## Credential and deployment closure requirements

1. Identify real identities permitted to invoke provider HTTP payment, reconciliation, state, admin and direct store methods; no production credential inventory has been provided.
2. Prevent direct access to SQLite, private issuer keys and internal provider methods from the FlowSignal adapter and any untrusted caller. Source-level Python separation is not an IAM boundary.
3. Disable or isolate legacy-test-mode and administrative routes in any protected deployment. Confirm runtime arguments, service identity, firewall, network policy and database ACLs.
4. Restrict authoritative mandate updates to a qualified institutional source. Reject stale, forged, rollback and cross-mandate updates at the provider boundary.
5. Bind trusted issuer credentials to payment instruction signing; support expiry, rotation and revocation, including signer compromise.
6. Establish complete provider-side route inventory for batch, retry, privileged, alternate executor and actual rail integrations; **none are proven closed by this reference service**.
7. Do not infer `NOT_COMMITTED` from an empty reference ledger. Require completeness attestation covering every in-scope route before any authoritative negative result.
8. Preserve original RED cases and maintain separate candidate test evidence.

## Decision
**REFERENCE ROUTE TESTS GREEN; PROTECTED DEPLOYMENT ROUTE/CREDENTIAL CLOSURE OPEN.**
Do not merge to main or assert production Structural Zero.

## Fenced HTTP closure candidate (unverified until CI)
- `/admin/reset` and `/state` now return HTTP 403 when the service is configured with an authoritative fence. This is an HTTP surface restriction, not a database ACL or institutional IAM control.
- The new hostile HTTP test checks that reset and state access are denied while a prior payment remains recorded and later revocation still refuses a payment.
- Direct Python access to `ProviderCommitFence` and filesystem-level SQLite access remain open in this reference harness. Do not claim complete route closure.

## Authority updater qualification — unresolved direct method routes
- Verified historical run https://github.com/grahamb-ai/flowsignal-agentic-payments/actions/runs/44508105473: focused 37 passed / 1 failed, full 105 passed / 2 failed, including T23.
- `ProviderCommitFence.revoke` accepts a direct unauthenticated caller. This is a preserved hostile RED.
- `ProviderCommitFence.revoke_if_epoch` is also directly callable without the signed updater facade. A separate hostile test is now frozen; result pending.
- The signed `apply_signed_update` facade is not an access-control boundary while direct store methods or the SQLite file remain reachable.
- A qualified closure requires a provider-owned isolated state-mutation service with updater identity verification and storage ACLs; Python method naming or a shared process-local token alone is insufficient.
- No production IAM, key ownership, or database permission evidence has been provided. Do not claim authority-update route closure.

## Authority-state writer attack inventory
- Direct `ProviderCommitFence.revoke`: observed RED, unauthenticated epoch advance.
- Direct `ProviderCommitFence.revoke_if_epoch`: observed RED, expected epoch alone is insufficient.
- Direct `ProviderCommitFence.establish`: new frozen hostile challenge, result pending CI.
- Direct SQLite writer: outside the signed facade, must be denied by deployment credentials; Python visibility restrictions do not constitute a trust boundary.
- Required architecture: separate institutional authority updater identity and write permission; payment executor read/commit-only access; durable monotonic per-mandate update ordering and no rollback; issuer public-key trust anchor independent of caller input.
- Do not patch these failures with a shared in-process Python token and claim production isolation. Prefer a provider-owned updater service and OS/database credential separation, then qualify direct access from the payment-executor identity.

## Integrated PostgreSQL HTTP reference — 19 November 2026
- Verified CI https://github.com/grahamb-ai/flowsignal-agentic-payments/actions/runs/44518541084: gateway-to-separate-process HTTP payment and hostile signed-instruction substitution GREEN.
- The provider HTTP service exposes POST /payments; administrative/state routes are unavailable in this service.
- The provider database connection is authenticated as fs_payment_executor. PostgreSQL grants no direct mandate mutation or commitment-table INSERT to this role; a guarded SECURITY DEFINER function performs the atomic current-authority check and commitment.
- Additional direct-INSERT alternate-executor challenge committed after this checkpoint; CI pending.
- **Not closed:** identities with database-owner or superuser rights, role membership escalation, compromised issuer key, external rail routes, production network/IAM and independently authenticated mandate writer service. PostgreSQL reference grants are not a proof of deployed route inventory completeness.
- The full historical regression remains RED from preserved SQLite authority-state bypasses and T23; these are not silently excluded from the archive.

## Direct guarded-function credential route — hostile negative control
A restricted PostgreSQL executor role has EXECUTE on `fs_provider.commit_if_current`. This function checks mandate standing and duplicate intent, but does **not** authenticate an institutional payment instruction. The HTTP provider verifies the signature before calling the function. A holder of the executor database credential may therefore bypass HTTP signature verification by calling the SQL function directly while the mandate is active. The direct-INSERT permission test does not address this route.

Failure-first evidence workflow: `.github/workflows/fs-sz-pay-001-direct-function-negative-control.yml`. The raw probe intentionally attempts an unsigned £750,000 direct function commitment; its failure must be preserved. Until independently restricted service credential possession and direct-function invocation are established, **protected route closure is OPEN**. Do not claim bounded Structural Zero merely because the HTTP and PostgreSQL workflows pass.
