# FS-SZ-PAY-001 — Independent witness deployment acceptance gate

**Status: DESIGN GATE / NOT DEPLOYED / STRUCTURAL ZERO NOT QUALIFIED.**

## Evidence motivating the gate
- Run 45150627886: PostgreSQL administrator inserted a direct unsigned commitment (preserved RED).
- Run 45153861204: ledger and unsigned checkpoint dual rewrite accepted (preserved RED).
- Run 45155297234: genuine older signed anchor accepted by signature/hash-only checks (preserved rollback RED).
- Run 45155552706: separate SQLite high-water persisted across reconnect, but deleting the witness store reset rollback protection (preserved witness compromise RED).

## Required separation before a qualification claim
1. **Institution-owned identity:** a separately administered principal with no role inheritance, service-account key access, or operator credentials shared with the PostgreSQL administrator, payment executor, or migration automation.
2. **Protected durable state:** monotonic per-stream sequence and checkpoint digest under independent access control, protected against deletion, replacement, restore-to-old-version and alternate-writer bypass. Storage durability and backup rollback must be challenged, not assumed.
3. **Atomic issuance:** compare-and-set sequence progression and signing must be transactionally tied to a durable accepted event. Concurrent duplicate, crash-before-ack, restart, and partial-write cases must have defined outcomes.
4. **Independent key custody:** signing key inaccessible to database administrators; public-key pinning, rotation, revocation and compromised-key handling must be tested.
5. **Actual boundary binding:** witness must observe a verified, consequence-bound event, not trust a caller-supplied COMMITTED flag or a mutable database row.
6. **External rail distinction:** a witness receipt must never be presented as proof of payment settlement without independent rail confirmation.
7. **Fail closed:** absent, stale, equivocated, rolled-back or unavailable witness state must refuse any new consequence under the institutional protocol.
8. **Operator and evidence review:** frozen source, immutable artifact retention, principal/permission inventory, independent reviewer and hostile tests in the intended deployment.

## Next executable hostile tests
- IE-W01: PostgreSQL administrator cannot read or invoke witness signing credentials.
- IE-W02: administrator modifies/deletes database ledger; independently retained signed witness rejects reconciliation.
- IE-W03: witness storage deletion/rollback cannot reset the high-water mark without externally detectable alarm.
- IE-W04: two concurrent issuers cannot both advance from the same sequence.
- IE-W05: signer crashes before/after durable append; retry cannot create two authoritative receipts.
- IE-W06: compromised old signing key and authentic old anchor cannot override current epoch/key status.
- IE-W07: witness outage or unverified source outcome never yields false COMMITTED/SETTLED.
- IE-W08: independent rail outcome contradicts local DB; report UNRESOLVED/CONTRADICTORY.

## Decision
The SQLite witness is a **local reference only**. Do not weaken the privileged deployment guard, close BOUNDARY-02, merge to main, deploy to production or advertise Structural Zero. Preserve every RED, including expected failures.
