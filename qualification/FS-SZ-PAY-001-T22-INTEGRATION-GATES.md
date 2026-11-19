# FS-SZ-PAY-001 T22 integration acceptance gates — DESIGN ONLY

T21 run 44494148851: 61 passed, 1 failed (preserved T20 duplicate-dispatch RED).
T21 standalone claim store tests passed in the full run. This store is NOT wired into payment execution.

## Critical requirements before integrating the claim store

1. **Identity**: An authenticated, immutable business payment_intent_id must be present in the authority request, receipt, execution permit, exact-action binding and provider idempotency key. Never derive identity solely from amount/beneficiary.
2. **Atomic boundary**: Reservation of the intent, consumption of the permit and creation of the initial UNRESOLVED outcome must be one durable transaction or an equivalently qualified protocol. A separate reserve_intent() call followed by execute_protected_consequence() introduces a crash window and must NOT be treated as closure.
3. **Shared enforcement**: Both standard and capability external adapters, plus all other qualified consequence routes, must pass through the same protected boundary. A new permit or executor route cannot reset the intent claim.
4. **Outcome semantics**: Dispatch timeout, lost acknowledgement and eventual-consistency NOT_FOUND leave the intent UNRESOLVED. Only authenticated, authoritative provider evidence may resolve it.
5. **Retries**: An unresolved intent must not dispatch again. Once committed, it must not dispatch again. A proven non-commitment may require fresh current authority and a formally defined retry policy; never blindly recycle a permit.
6. **Durability**: Test two-process races, hard crashes at each commit point, cross-host shared-state assumptions, provider outages and provider-route substitution.
7. **No false equivalence**: The current SQLite store demonstrates a local/shared-filesystem reference property only. It does not prove distributed provider-side atomicity or Structural Zero.

## Required evidence sequence
- Freeze T20 original RED (run 44493861540).
- Qualify T21 reservation component separately.
- Design and implement authenticated payment intent propagation.
- Extend transactional consumption-and-outcome operation to include intent reservation.
- Run original tests plus T20, distinct-intent positive control and hostile cross-route tests.
- Preserve first RED and all subsequent candidate results; no production claim until provider boundary is qualified.
