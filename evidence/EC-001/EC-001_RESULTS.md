# EC-001 — External Consequence-Boundary Challenge Results

**Status:** COMPLETE — BOUNDED PUBLIC HARNESS RESULT

**Date:** 17 August 2026

## Purpose

EC-001 records the application of an external adversarial consequence-boundary challenge to the public FlowSignal Agentic Payments Harness.

The challenge was treated as an engineering exercise rather than a debate. Each proposition was assessed against the implementation and available evidence. Where a stronger proof obligation was identified, the gap was preserved before remediation and the same proposition was retested after strengthening.

The resulting evidence is intentionally bounded to the execution surfaces represented by the public reference harness.

## Challenge summary

| ID | Challenge | Initial classification | Final classification |
|---|---|---|---|
| EC-001.1 | Current Standing at Effect | Demonstrated | **PASS — bounded harness surface** |
| EC-001.2 | No Stale ALLOW | Demonstrated | **PASS — bounded harness surface** |
| EC-001.3 | Route Closure | Demonstrated | **PASS — bounded governed route** |
| EC-001.4 | No Independent Execution Authority | ND | **PASS after strengthening — represented harness surface** |
| EC-001.5 | Atomic Boundary | ND | **PASS after strengthening — in-process harness surface** |
| EC-001.6 | Non-Formation | Partial | **PASS represented / ND external physical** |

## EC-001.1 — Current Standing at Effect

The harness rechecks authority-state standing at the execution boundary rather than relying solely on an earlier authority determination.

A receipt carrying an earlier authority-state version is rejected once current authoritative state has advanced.

**Result:** `PASS — demonstrated on the bounded public harness execution surface`.

## EC-001.2 — No Stale ALLOW

A previously valid `ALLOW` cannot continue through the governed execution path after an authority-state change using the earlier Authority Receipt.

Observed rejection:

`AUTHORITY_STATE_STALE_REEVALUATION_REQUIRED`

**Result:** `PASS — demonstrated on the bounded public harness execution surface`.

## EC-001.3 — Route Closure

The tested normal consequence-producing route cannot carry forward a stale T0 Authority Receipt after authority state changes. Continued represented execution requires a fresh determination and receipt under current authority state.

This is bounded route-closure evidence and does not claim every external route is closed.

**Result:** `PASS — demonstrated on the tested governed harness route`.

## EC-001.4 — No Independent Execution Authority

### Initial result

**ND — NOT YET DEMONSTRATED**

The existing harness required the normal demonstrator path to consume the Execution Gateway, but did not independently demonstrate that consequence formation itself required a capability unavailable to the executor.

### Strengthening

A protected represented consequence boundary was introduced. Consequence formation now requires a cryptographically signed `ExecutionPermit` minted only after successful Execution Gateway validation.

The permit is bound to:

- Authority Receipt identifier;
- exact action-binding hash;
- authority-state version;
- issue time; and
- integrity signature.

Adversarial tests demonstrate:

- no permit → denied;
- executor-fabricated permit → denied;
- substituted action → denied;
- valid gateway-minted permit for the exact action → represented consequence forms.

**Final result:** `PASS — demonstrated on the represented public harness execution surface`.

Evidence:

- `EC-001.4_PRE_REMEDIATION.md`
- `EC-001.4_RESULT.md`
- `harness/tests/test_ec001_4_independent_execution_authority.py`

## EC-001.5 — Atomic Boundary

### Initial result

**ND — NOT YET DEMONSTRATED**

The harness had not demonstrated serialization between final standing resolution and represented consequence formation.

### Strengthening

Authority-state advancement and final represented consequence formation now share the same in-process authority-state guard.

The adversarial test deliberately pauses execution after final standing resolution but before consequence formation while concurrently attempting authority-state advancement.

The competing state change cannot commit during the protected interval. If authority state changes first, the older execution permit is rejected as stale.

**Final result:** `PASS — demonstrated on the in-process public harness execution surface`.

Evidence:

- `EC-001.5_PRE_REMEDIATION.md`
- `EC-001.5_RESULT.md`
- `harness/tests/test_ec001_5_atomic_boundary.py`

## EC-001.6 — Non-Formation

The harness explicitly represents consequence state through `EXECUTION PERMITTED`, `EXECUTION WITHHELD`, and `NO EXECUTION`.

Focused tests confirm:

- AP-003 changed state → `REFUSE` → `BLOCKED` → `NO EXECUTION`;
- AP-005 expired mandate → `REFUSE` → `BLOCKED` → `NO EXECUTION`;
- AP-006 substituted action → `BLOCKED` / `ACTION_BINDING_MISMATCH` → `NO EXECUTION`.

The public harness does not contain an independently consequence-producing banking/payment executor. It therefore cannot prove physical non-formation across every external payment rail, datastore, cloud control plane, privileged operator, integration or administrative path.

**Final result:**

- `PASS — represented harness non-formation`
- `ND — external/universal physical non-formation`

Evidence:

- `EC-001.6_RESULT.md`
- `harness/tests/test_ec001_6_non_formation.py`
- `evidence/FS-CT/FS-CT-001_RESULT.md`

## Final regression evidence

GitHub Actions workflow: **EC-001 and Regression Tests**

Final EC-001 branch regression after EC-001.6 formalisation:

```text
.............................                                            [100%]
29 passed in 0.57s
```

Workflow run: `32021585230`

Commit under test: `7daf7883a40db6df8dae08e66bc2c48b735ce212`

## Final engineering conclusion

The external challenge materially strengthened the public reference implementation.

It did not produce a blanket claim that every consequence path is controlled. Instead it produced a differentiated result:

- three challenge propositions were already demonstrated on the bounded harness surface;
- two stronger proof obligations were initially not demonstrated and were preserved as such before remediation;
- both were subsequently strengthened and passed unchanged adversarial propositions on the represented harness surface; and
- non-formation is demonstrated only for the represented consequence boundary, while real-world external physical non-formation remains outside the proof surface.

The evidential value lies in the lineage rather than the aggregate test count:

`external challenge → proposition → observed evidence → proof gap preserved where present → remediation → unchanged retest → regression → bounded conclusion`

## Claim boundary

EC-001 does **not** establish:

- universal non-bypassability across systems not represented by the harness;
- production credential isolation or IAM enforcement;
- distributed atomic commit or consensus;
- transactional guarantees across independent external services;
- physical prevention of settlement across real banking or payment rails; or
- complete route closure against privileged administrative paths outside the demonstrated architecture.

EC-001 supports only the properties exercised and evidenced by the public reference implementation.
