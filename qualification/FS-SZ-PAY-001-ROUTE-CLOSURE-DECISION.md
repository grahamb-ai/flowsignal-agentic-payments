# FS-SZ-PAY-001 — Route closure: architecture decision

## Evidence and claim
Original failure: GitHub Actions run 44498510274 at commit
694811dbbe4168378675bfe32db956a28699e802.
The direct CBP-002 `ExternalLedger.transfer()` accepted a £750,000
simulated payment after the independent T24 authority store was revoked.
The fenced operation refused, while the direct route returned HTTP 201.

This is a valid counterexample for the *combined reference boundary*.
It is not evidence about a live bank or a third-party payment provider.

## Root cause
There are TWO distinct provider-side mutation implementations:
- `ProviderCommitFence.commit()` performs authority validation and an
  intent-unique insert under a single SQLite transaction.
- `ExternalLedger.transfer()` checks payment fields, balance and transaction
  ID only, and mutates a separate in-memory ledger.

The latter is a parallel consequence-forming route. Fixing only the FlowSignal
adapter cannot close it.

## Non-negotiable candidate design
1. Enumerate every in-scope consequence-forming entry point, including direct
   HTTP, capability, administrative, batch, retry and privileged paths.
2. Each entry point must call the SAME provider-owned commit primitive.
   No independent ledger mutation API may remain accessible.
3. The provider-owned commit primitive must validate current authoritative
   mandate standing, stable authenticated payment-intent identity, exact
   consequence fields and uniqueness **within the transaction that mutates
   the actual ledger**.
4. The provider's authority state and actual ledger mutation must have a
   common serialisation point. A check in one SQLite database followed by
   a transfer in an unrelated in-memory ledger is a TOCTOU window.
5. Fail closed on missing mandate, missing intent, stale epoch, unavailable
   authority or unknown provider state.
6. Ensure legitimate distinct intents with identical payment details still
   work; duplicate intent across routes must not.
7. Test revocation-before-commit, commit-before-revocation, simultaneous
   multi-process races, crash points, alternate routes and direct bypass.
8. Preserve original RED unchanged; only qualify the new implementation with
   separately recorded candidate evidence.

## Qualification status
DESIGN CONTRACT ONLY. No integrated route-closure GREEN claimed.
The T24 component GREEN and integrated concurrency GREEN do not close this
direct route. Structural Zero remains NOT QUALIFIED.
