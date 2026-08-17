# EC-001 — Proposition-to-Evidence Mapping

**Status:** PUBLIC EVIDENCE INDEX  
**Date:** 17 August 2026

## Purpose

This document answers a specific evidential question: do the EC-001 classifications correspond to the external propositions that prompted the challenge, or only to narrower FlowSignal-defined statements?

It is an evidence map, not an aggregate score. The six challenge headings are frozen as used in EC-001. Where the public harness proves only a narrower surface than the proposition could imply, that narrowing is made explicit and the broader proposition is not claimed as proven.

The mapping format is:

`proposition → tested mechanism → test/evidence → original state/failure → change → rerun → demonstrated scope → residual gap`

## Summary

| ID | Frozen challenge proposition | Exact demonstrated scope | Broader proposition status |
|---|---|---|---|
| EC-001.1 | Current Standing at Effect | Current authority-state version is rechecked at the represented execution boundary | PASS on bounded harness surface; no claim about unrepresented external effectors |
| EC-001.2 | No Stale ALLOW | Earlier ALLOW receipt is rejected after authoritative state advances | PASS on bounded harness surface |
| EC-001.3 | Route Closure | Tested governed consequence route cannot continue with stale T0 receipt | PASS on tested governed route; universal route closure NOT DEMONSTRATED |
| EC-001.4 | No Independent Execution Authority | Permit enforcement and exact-action binding | PARTIAL; independent issuer/signing capability isolation NOT DEMONSTRATED |
| EC-001.5 | Atomic Boundary | In-process state guard serializes final standing check and represented consequence formation | PASS on in-process harness surface; distributed atomicity NOT DEMONSTRATED |
| EC-001.6 | Non-Formation | REFUSE/BLOCKED cases produce no represented harness consequence | PASS represented; external/physical non-formation NOT DEMONSTRATED |

---

## EC-001.1 — Current Standing at Effect

### Proposition

**Current Standing at Effect**

### Tested mechanism

The Execution Gateway compares the Authority Receipt's `authority_state_version` with the current authoritative state immediately before represented execution is permitted.

### Test / evidence

- `harness/tests/test_at004_6_context_freshness.py`
- `harness/app/engines/execution_gateway.py`

### Original state / observed result

This behaviour existed before EC-001 strengthening. A receipt created under an earlier authority-state version is rejected after state advancement.

Observed reason:

`AUTHORITY_STATE_STALE_REEVALUATION_REQUIRED`

### Change

No EC-001 remediation was required for this bounded mechanism.

### Rerun / regression

Included in the full EC-001 regression suite recorded in `EC-001_RESULTS.md`.

### Demonstrated scope

The represented Execution Gateway checks current authoritative state rather than relying solely on the earlier ALLOW determination.

### Residual gap

This does not prove that every possible external effector or privileged route performs the same standing check at physical effect.

**Classification:** `PASS — bounded public harness execution surface`.

---

## EC-001.2 — No Stale ALLOW

### Proposition

**No Stale ALLOW**

### Tested mechanism

Advance authoritative state after an ALLOW receipt has been produced, then attempt to execute using that earlier receipt.

### Test / evidence

- `harness/tests/test_at004_6_context_freshness.py`
- `harness/app/engines/execution_gateway.py`

### Original state / observed result

The earlier receipt is rejected after state advancement.

Observed reason:

`AUTHORITY_STATE_STALE_REEVALUATION_REQUIRED`

### Change

No EC-001 remediation was required for this bounded mechanism.

### Rerun / regression

Included in the full EC-001 regression suite.

### Demonstrated scope

A stale ALLOW cannot be reused through the tested Execution Gateway after the authoritative state version changes.

### Residual gap

This is not evidence that an unrepresented external executor lacking the gateway cannot ignore the receipt entirely.

**Classification:** `PASS — bounded public harness execution surface`.

---

## EC-001.3 — Route Closure

### Proposition

**Route Closure**

### Tested mechanism

The governed harness route is challenged after authority state changes. Continued represented execution must obtain a fresh determination/current receipt rather than carrying the T0 ALLOW forward.

### Test / evidence

- `harness/tests/test_fs_ct_002_route_closure.py`
- `evidence/FS-CT/FS-CT-001_RESULT.md`

### Original state / observed result

The tested governed route rejects continuation with the stale T0 receipt.

### Change

No claim is made that EC-001 created deployment-wide route closure. The evidence was reviewed and deliberately bounded to the route actually exercised.

### Rerun / regression

Included in the EC-001 regression suite.

### Demonstrated scope

The tested normal consequence-producing route cannot continue represented execution using the stale T0 Authority Receipt.

### Residual gap

Direct database mutation, privileged administrative paths, alternative services/APIs, external payment rails and other unrepresented consequence routes were not closed or tested by this harness.

**Classification:** `PASS — tested governed harness route`.

**Broader universal route-closure proposition:** `NOT DEMONSTRATED`.

---

## EC-001.4 — No Independent Execution Authority

### Proposition

**No Independent Execution Authority**

### Original proof gap

The normal demonstrator consumed the Execution Gateway, but consequence formation did not independently require a capability unavailable to the executor.

This was recorded as:

`ND — NOT YET DEMONSTRATED`

### Preserved evidence

- `evidence/EC-001/EC-001.4_PRE_REMEDIATION.md`

### Change

A protected represented consequence boundary and signed `ExecutionPermit` were introduced. The permit is bound to the Authority Receipt, exact action, authority-state version and issue time.

The normal AP-001 path was subsequently wired through the protected consequence boundary.

### Test / evidence

- `harness/tests/test_ec001_4_independent_execution_authority.py`
- `harness/app/engines/protected_consequence.py`
- `harness/app/engines/execution_gateway.py`
- `harness/agentic_demo.py`
- `evidence/EC-001/EC-001.4_RESULT.md`

Tests exercise missing permit, invalid signature, action substitution and the valid governed path.

### Rerun

The strengthened path passed the EC-001 focused tests and subsequent full regression.

### Demonstrated scope

- protected represented consequence requires a valid permit;
- permit is exact-action bound;
- normal AP-001 represented execution consumes the protected boundary.

### Residual gap — important

`issue_execution_permit()` remains callable in the same Python codebase/process and the reference implementation contains a repository-visible default HMAC key when no external key is supplied.

Therefore EC-001 does **not** demonstrate that the executor lacks independent access to permit minting/signing authority.

**Classification:** `PARTIAL — permit enforcement demonstrated / independent capability isolation NOT DEMONSTRATED`.

This is the explicit subject of the subsequent EC-002 capability-isolation challenge; EC-002 does not retrospectively change EC-001 evidence.

---

## EC-001.5 — Atomic Boundary

### Proposition

**Atomic Boundary**

### Original failure / proof gap

The harness had not demonstrated serialization between the final authority-standing resolution and represented consequence formation.

Recorded as:

`ND — NOT YET DEMONSTRATED`

### Preserved evidence

- `evidence/EC-001/EC-001.5_PRE_REMEDIATION.md`

### Change

Authority-state advancement and final represented consequence formation were placed under the same in-process authority-state guard.

### Test / evidence

- `harness/tests/test_ec001_5_atomic_boundary.py`
- `harness/app/engines/authority_store.py`
- `harness/app/engines/protected_consequence.py`
- `evidence/EC-001/EC-001.5_RESULT.md`

The adversarial test pauses after the final standing read while a concurrent state advancement attempts to commit. The state change cannot complete inside the guarded interval. The companion ordering test advances state first and verifies the older permit is rejected.

### Rerun

Strengthened EC-001.5 tests passed and remained green in the full EC-001 regression.

### Demonstrated scope

Serialization of the final standing check and represented consequence formation in the single-process reference harness.

### Residual gap

No claim is made for distributed transactions, external services, databases, consensus, payment rails or cross-system atomic commit.

**Classification:** `PASS after strengthening — in-process harness surface`.

**Broader distributed atomic-boundary proposition:** `NOT DEMONSTRATED`.

---

## EC-001.6 — Non-Formation

### Proposition

**Non-Formation**

### Tested mechanism

Challenge scenarios that are REFUSED or BLOCKED and inspect the represented consequence state.

### Test / evidence

- `harness/tests/test_ec001_6_non_formation.py`
- `evidence/EC-001/EC-001.6_RESULT.md`
- `evidence/FS-CT/FS-CT-001_RESULT.md`

### Observed cases

- AP-003 changed state → `REFUSE` → `BLOCKED` → `NO EXECUTION`
- AP-005 expired mandate → `REFUSE` → `BLOCKED` → `NO EXECUTION`
- AP-006 substituted action → `BLOCKED / ACTION_BINDING_MISMATCH` → `NO EXECUTION`

### Change

The evidence classification was bounded rather than upgraded to physical non-formation.

### Rerun / regression

Focused tests passed and were included in the full EC-001 regression.

### Demonstrated scope

No represented harness consequence is formed in the tested REFUSE/BLOCKED cases.

### Residual gap

The public harness has no independent banking/payment executor or external settlement surface. It cannot prove that no physical consequence forms through every external rail, datastore, privileged operator or integration.

**Classification:**

- `PASS — represented harness non-formation`
- `NOT DEMONSTRATED — external/universal physical non-formation`

---

## Failure and remediation lineage

EC-001 did not produce six unchanged PASS results.

- EC-001.1 and EC-001.2 already had bounded supporting mechanisms and were regression-tested.
- EC-001.3 was retained only as a bounded governed-route result; universal route closure is not claimed.
- EC-001.4 began `NOT DEMONSTRATED`, was strengthened, and remains `PARTIAL` because capability isolation is still not demonstrated.
- EC-001.5 began `NOT DEMONSTRATED`, was strengthened with an in-process serialization boundary, and passed only at that bounded surface.
- EC-001.6 is a represented non-formation result; external physical non-formation remains not demonstrated.

The pre-remediation records for EC-001.4 and EC-001.5 are intentionally retained in the repository rather than replaced by the final results.

## Regression record

The EC-001 final consistency-review regression recorded in `EC-001_RESULTS.md` was:

```text
30 passed in 0.52s
```

Workflow run: `32023485529`  
Head commit: `5ea9ab262c050266436e8deb47534a79af570d0f`

The aggregate count is not itself proof of the six propositions. The proposition-specific mapping above defines what each test result supports.

## Evidence boundary

This mapping intentionally distinguishes a **challenge heading** from the **scope actually demonstrated**. A PASS on a bounded harness surface must not be read as proof of a stronger deployment-wide proposition.

Accordingly EC-001 does not claim to demonstrate:

- universal route closure;
- independent production credential/permit-issuer isolation;
- production IAM/KMS/HSM controls;
- distributed atomicity;
- cross-system transaction guarantees; or
- external physical non-formation of a payment.

Where those broader propositions matter, they require additional proof surfaces rather than broader wording.
