# FS-SZ-PAY-001 — Integrated commitment qualification decision record

**Frozen candidate:** commit `4433b7025d7b598696cf179c46afa00459955866`  
**GitHub Actions run:** https://github.com/grahamb-ai/flowsignal-agentic-payments/actions/runs/44497987207  
**Artifact:** FS-SZ-PAY-001-integrated-commitment  
**Result:** 8 passed in 0.43s, exit code 0.

## Original claim
No covered payment commits after the institution's authority to make that payment has been effectively revoked.

## Boundary actually tested
- FlowSignal's actual standard external payment adapter and protected-consequence execution path.
- A cooperating *simulated* provider with SQLite-authoritative mandate epoch/revocation and commitment in a shared transaction.
- Three integrated sequential orderings: revoke before call; revoke during provider dispatch before commit; commit then revoke.
- Five provider component tests, including a two-process revoke/commit race and duplicate-intent refusal.
- Provider result returned as an ordinary status string; not a signed/independently authenticated provider receipt.

## Observed outcome
The integrated tests refuse formation when provider revocation precedes commitment and permit commitment when commitment precedes revocation. The provider component serialises the competing operations. These are bounded observations, not universal proof.

## Preserved counterexample
T23 unfenced provider: run https://github.com/grahamb-ai/flowsignal-agentic-payments/actions/runs/44495734050 — 58 passed, 1 failed; simulated provider committed after effective revocation.

## Remaining gates — required before Structural Zero claim
1. **Independent authority semantics**: demonstrate who owns revocation, its effective instant, authoritative delivery, updater permissions and stale/rollback protection.
2. **Provider enforcement and route closure**: verify every in-scope executor, capability, alternate API and privileged path is forced through the same provider commitment fence.
3. **Concurrent integration**: test FlowSignal adapter and independent provider under revocation/commit races, including separate processes and restart.
4. **Crash and outage**: hard-kill before/after provider commit, during authority updates and after acknowledgement loss; preserve no-unsafe-retry.
5. **Payment intent identity**: authenticated stable intent across new permits and routes; provider uniqueness independent of permit signature.
6. **Evidence authenticity**: independently verify provider commitment/refusal records bound to exact payment details and authoritative state.
7. **State-space/model proof**: specify model, assumptions, finite horizon and safety invariant; model-check or otherwise exhaustively verify covered transitions, then test implementation conformance.

## Decision
**BOUNDED INTEGRATION GREEN — STRUCTURAL ZERO NOT YET QUALIFIED.**

Next experiment should test **integrated cross-route closure and concurrent revocation/commit**, not add unrelated outcome-classification tests. Do not merge to main or represent as live-rail certification.
