# FS-RAI-IC-001-CL-005C — Authoritative Usage-Window Rollover

**Status:** CLOSED — TESTED R1 REFERENCE PATH

## Scope

This record preserves the bounded implementation evidence for NORM-PAY-001 aggregate usage-window rollover on the tested R1 reference path. It does not establish production-grade authoritative provenance, durable cross-process state, route-wide conformance, or independent certification.

## Failure and remediation sequence

1. **Missing legitimate rollover capability.** The positive-mirror test first failed because no authoritative usage-window transition existed (82 passed / 1 failed). The reference institutional-authority state was extended with a distinct usage-window identity, separate from the generic authority epoch.
2. **Positive rollover established.** Aggregate policy identity was derived from principal, mandate, source account, currency and authoritative usage window. Full regression reached 83/83 GREEN.
3. **Prior unresolved authority preserved.** A prior-window reservation moved to QUARANTINED remained charged to its original window across rollover while the new normative window obtained its own pool. Regression reached 84/84 GREEN.
4. **Rollback/replay surface exposed.** A failure-first test showed the implementation had not yet defined a presented-transition validator (84 passed / 1 failed). A monotonic/domain validator was added. Regression reached 85/85 GREEN.
5. **Duplicate and foreign-domain transitions rejected.** Equal-window and foreign-namespace transitions were rejected without changing authoritative state or fence. Regression reached 87/87 GREEN.
6. **Forward-value self-authorisation exposed.** A syntactically valid same-domain future value (DAY-999) was accepted merely because it was forward: 87 passed / 1 failed. This was a genuine authority defect: monotonicity was being treated as sufficient authority to advance the economic window.
7. **Transition authority remediation.** Presented transitions now require a bounded authoritative transition capability before domain/monotonic validation. Earlier authorised rollback/duplicate/domain tests were aligned to exercise that interface without weakening their assertions. Final regression: **88/88 GREEN**.

## Demonstrated properties

For the tested R1 reference path:

- authority epoch movement alone does not replenish aggregate economic capacity;
- an untrusted caller cannot manufacture a fresh aggregate policy/window;
- a competent normative usage-window transition can establish the next aggregate pool;
- unresolved prior-window usage remains attributed to its prior window through rollover;
- stale, equal and foreign-domain presented transitions do not mutate authoritative window state;
- syntactic forwardness alone is not authority to advance a usage window;
- a presented transition requires authoritative derivation before it can change economic scope.

## Architectural result

**A new normative usage window can establish a new aggregate capacity pool; merely naming, constructing, replaying, or monotonically advancing a window identifier cannot.**

Equivalently:

> **Monotonic state transition is not authorised state transition.**

## Boundaries and nonclaims

The reference implementation uses process-local state and a private Python capability to exercise authoritative-transition semantics. That capability is a bounded test/reference-harness mechanism, not a production security primitive, durable provenance mechanism, external attestation system, or proof of institutional/legal authority.

This closure is limited to the tested R1 reference path. It does not close route-wide R2–R6 enforcement, durable transactionality, environment identity, dependency locking, or other remaining FS-RAI-IC-001 implementation-conformance work.
