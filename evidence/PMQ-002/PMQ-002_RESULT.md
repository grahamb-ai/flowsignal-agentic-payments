# PMQ-002 — Persistence, Concurrency and Failure-Boundary Qualification

**Status:** QUALIFIED DRAFT EVIDENCE STATE  
**Date:** 2026-08-18  
**Final integrated regression:** **53 passed / 0 failed**  
**Production certification:** No

## Purpose

PMQ-002 challenged the Agentic Payments reference MVP at persistence, concurrency, temporal and failure boundaries where Runtime Authority may have made the correct determination but a represented consequence could still be duplicated, formed under stale standing, or become ambiguous during recovery.

The qualification method was failure-first: freeze a falsifiable proposition, execute the challenge, preserve genuine failures, remediate the mechanism rather than weaken the proposition, rerun the same semantic challenge, and require the maintained regression to remain green.

## Master qualification record

| Test | Proposition / boundary | Initial evidence | Final classification | Demonstrated scope |
|---|---|---|---|---|
| PMQ-002.1 | Consumed permit after represented restart | **FAIL** — restart replay formed a second represented consequence | **PASS** — represented restart replay blocked after remediation | Same durable SQLite consumption store remains available across represented component reload |
| PMQ-002.2 | Exact permit raced across two represented executor processes | Initial fixture **NOT EVALUATED**; corrected run exposed concurrent SQLite initialization **FAIL** | **PASS** — represented two-process shared-store replay blocked | Two Python processes sharing the tested SQLite permit-consumption store; exactly one represented consequence |
| PMQ-002.3 | Authority revocation concurrent with final execution boundary | Passed first execution | **PASS** — represented in-process authority revocation ordering enforced | Shared in-process authority-state guard orders revocation and represented formation |
| PMQ-002.4 | Permit expires while waiting for final protected boundary | **FAIL** — expired permit formed consequence after boundary wait | **PASS** — expiry revalidated at final boundary acquisition | Local UTC expiry rechecked after acquiring represented in-process boundary |
| PMQ-002.5 | Superseded authority state moved backwards | **FAIL** — superseded authority state resurrected | **PASS** — tested reachable authority-state rollback path blocked | Represented in-process authority-store mutation surface is forward-only for the exercised path |
| PMQ-002.6 | Consequence forms, subsequent receipt creation fails | **FAIL** — consequence formed without recoverable outcome evidence | **PASS** — represented formation remains recoverable after injected receipt failure | Durable reference outcome record exists before represented executor returns formation |
| PMQ-002.7 | Permit consumed, catchable executor failure before formation | **FAIL** — consumed permit left without recoverable non-formation outcome | **PASS** — represented injected pre-formation exception leaves recoverable non-formation state | Catchable post-consumption/pre-formation exception records `CONSEQUENCE_NOT_FORMED` |
| PMQ-002.8 | Hard process termination after consumption before terminal outcome | Initial fixture **NOT EVALUATED**; corrected run **FAIL** — consumed permit had no explicit outcome | **PASS** — represented hard-crash window exposes durable unresolved outcome | Tested `os._exit(73)` point leaves `CONSEQUENCE_OUTCOME_UNRESOLVED` recoverable and permit replay-blocked |
| PMQ-002.9 | Crash separates permit consumption from initial outcome creation | **FAIL** — consumed permit survived without durable execution outcome; first remediation then regressed PMQ-002.2 | **PASS** — represented local SQLite transition survives tested cross-store crash while preserving tested concurrency | Permit consumption + initial unresolved state committed in one attached-database transaction on represented local SQLite boundary |
| PMQ-002.10 | Restore execution-state stores to pre-execution snapshots | **FAIL** — restored stores re-enabled same permit to form a second represented consequence; first remediation regressed three prior behaviors | **PASS** — represented rollback detected when separate rollback anchor survives | Restoring tested permit/outcome stores does not re-enable the same permit when separate reference rollback anchor survives |

## Failure lineage

PMQ-002 did not progress as a sequence of tests designed to pass. Material weaknesses were exposed and preserved:

- restart destroyed process-local replay memory;
- concurrent durable-store initialization failed under the tested race;
- an execution permit could expire while waiting and still form a consequence;
- a reachable authority-state surface could resurrect superseded standing;
- represented consequence formation could become unrecoverable when later evidence creation failed;
- consumed-before-formation failures could leave recovery unable to distinguish formed from non-formed state;
- hard process termination exposed the same ambiguity when exception handling could not run;
- separate durable commits left a crash window between permit consumption and initial outcome state;
- restoring both execution-state stores to an older snapshot resurrected a consumed permit;
- and remediation itself twice exposed regressions in previously qualified behavior, which were corrected before qualification was accepted.

The historical failures remain part of the evidence record. A later PASS does not erase the earlier falsification.

## Final integrated rerun

GitHub Actions run: **32172467695**  
Workflow: **EC-001 and Regression Tests**  
Result: **53 passed in 1.93s — 0 failed**

This run exercised the complete current draft regression on the PMQ-002.10 candidate implementation, including the earlier persistence, concurrency, crash-recovery and replay properties that had been affected by later remediation.

## What PMQ-002 demonstrates

Within the declared represented reference-MVP boundaries exercised by the PMQ-002 corpus, the tested execution path now demonstrates bounded controls for restart replay, tested two-process shared-store replay, in-process authority-state ordering, final-boundary permit expiry, the exercised authority-state rollback path, recoverable formed/non-formed/unresolved consequence state, the tested hard-process-crash point, local SQLite atomic initialization of execution outcome state, and rollback detection when the separate reference anchor survives restoration of the two tested execution-state stores.

The strongest safe aggregate statement is:

> **Within the represented reference-MVP boundaries and adversarial conditions exercised by PMQ-002.1 through PMQ-002.10, the frozen challenges no longer demonstrate a consequence-producing bypass or unrecoverable execution-state ambiguity on the tested paths. The integrated draft regression completed with 53 passed / 0 failed.**

## Residual limitations / NOT DEMONSTRATED

PMQ-002 does **not** establish production-grade guarantees for:

- production process/IAM/KMS/HSM execution-capability isolation;
- universal external consequence-route closure;
- physical payment-rail consequence prevention or cancellation;
- external payment settlement, reconciliation, idempotency or exactly-once semantics;
- distributed transactions across independent production systems;
- database HA, replication, failover or multi-region behavior;
- distributed consensus or serializability beyond the represented local mechanisms;
- network partitions and independent non-shared executor stores;
- trusted/attested/distributed time or malicious host-clock manipulation;
- filesystem, fsync, disk-controller or power-loss guarantees;
- immutable/write-once audit storage;
- privileged storage-administrator or host compromise resistance;
- rollback where the separate PMQ-002.10 rollback anchor is itself restored, deleted, corrupted or compromised;
- trusted external monotonic counters or externally anchored ledgers;
- real evidence-service transport/outage semantics unless separately exercised; or
- external physical non-formation.

These are deployment, integration, trust-boundary or distributed-system proof obligations and must not be implied by the bounded PMQ-002 PASS record.

## Qualification conclusion

**PMQ-002 is complete as a bounded reference-MVP qualification phase.**

The record supports a robust MVP engineering baseline for the represented surfaces tested. It does not constitute production certification, independent commercial endorsement, or evidence that every possible consequence-producing route has been closed.

The correct claim remains evidence first and scope explicit: failures were preserved, remediations were rerun against unchanged semantic propositions, regressions introduced by remediation were not ignored, and residual limitations remain attached to the final result.
