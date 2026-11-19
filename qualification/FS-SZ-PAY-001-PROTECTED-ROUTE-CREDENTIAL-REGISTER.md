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
| `Handler.POST /admin/reset` | Resets legacy in-memory ledger; fenced mode leaves durable provider transfer records intact | **No administrative authentication in reference service** | Unqualified administrative route |
| `Handler.GET /state` | Reads transfer count / sandbox balances | **No caller authentication** | Unqualified information exposure |
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
