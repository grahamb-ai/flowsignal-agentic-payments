# EC-001 — External Consequence-Boundary Challenge Results

**Status:** COMPLETE — BOUNDED PUBLIC HARNESS RESULT

**Date:** 17 August 2026

## Purpose

EC-001 records the application of an external adversarial consequence-boundary challenge to the public FlowSignal Agentic Payments Harness.

Each proposition was assessed against the implementation and available evidence. Where a stronger proof obligation was identified, the gap was preserved before strengthening and the proposition was retested. A final pre-merge review then checked whether each public conclusion was no stronger than the evidence supporting it.

The resulting evidence is intentionally bounded to the execution surfaces represented by the public reference harness.

## Challenge summary

| ID | Challenge | Initial classification | Final classification |
|---|---|---|---|
| EC-001.1 | Current Standing at Effect | Demonstrated | **PASS — bounded harness surface** |
| EC-001.2 | No Stale ALLOW | Demonstrated | **PASS — bounded harness surface** |
| EC-001.3 | Route Closure | Demonstrated | **PASS — bounded governed route** |
| EC-001.4 | No Independent Execution Authority | ND | **PARTIAL — permit enforcement demonstrated / capability isolation ND** |
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

A protected represented consequence boundary was introduced. Consequence formation requires a signed `ExecutionPermit` bound to the Authority Receipt, exact action, authority-state version and issue time.

Adversarial tests demonstrate that missing permits, arbitrary invalid signatures and action substitution are denied, while a permit produced through the tested gateway path for the exact action is accepted.

During final consistency review, the normal AP-001 demonstrator path was also wired through `execute_protected_consequence()` so `EXECUTION PERMITTED` is reported only after the protected represented consequence returns `CONSEQUENCE_FORMED`. A dedicated regression test exercises that path.

### Final pre-merge review finding

The permit mechanism demonstrates permit enforcement, but the stronger isolation proposition remains unproven. `issue_execution_permit()` is callable within the same Python codebase/process and the reference implementation contains a repository-visible default HMAC key when an external key is not supplied.

The current tests therefore do not prove that the proposing/executing actor is technically unable to invoke the minting capability or obtain signing authority.

**Final result:**

- `DEMONSTRATED — permit validation and exact-action binding on the represented harness surface`
- `DEMONSTRATED — normal AP-001 represented ALLOW path consumes the protected consequence boundary`
- `ND — independent permit-issuer/signing-authority isolation from the executor`
- `OVERALL EC-001.4 — PARTIAL`

Evidence:

- `EC-001.4_PRE_REMEDIATION.md`
- `EC-001.4_RESULT.md`
- `harness/tests/test_ec001_4_independent_execution_authority.py`
- `harness/agentic_demo.py`

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

Final consistency-review regression after wiring the normal demonstrator ALLOW path through the protected consequence boundary:

```text
..............................                                           [100%]
30 passed in 0.52s
```

Workflow run: `32023485529`

Head commit under test: `5ea9ab262c050266436e8deb47534a79af570d0f`

The test job completed successfully, including dependency installation and the full `pytest -q` harness suite.

## Final engineering conclusion

The external challenge materially strengthened the public reference implementation, but it did not produce six blanket PASS results.

The final evidence is deliberately differentiated:

- EC-001.1, EC-001.2 and bounded EC-001.3 are demonstrated on their tested harness surfaces;
- EC-001.4 improved from an untested proof gap to demonstrated permit enforcement and normal-path protected-boundary consumption, but independent issuer/credential isolation remains not demonstrated, so the overall result is PARTIAL;
- EC-001.5 is demonstrated only for the in-process serialization mechanism represented by the harness; and
- EC-001.6 demonstrates represented non-formation while external physical non-formation remains outside the proof surface.

The evidential value lies in the lineage rather than the aggregate test count:

`external challenge → proposition → observed evidence → proof gap preserved → strengthening → retest → pre-merge claim review → normal-path consistency check → bounded conclusion`

## Claim boundary

EC-001 does **not** establish:

- universal non-bypassability across systems not represented by the harness;
- production credential or permit-issuer isolation;
- production IAM, KMS or HSM enforcement;
- distributed atomic commit or consensus;
- transactional guarantees across independent external services;
- physical prevention of settlement across real banking or payment rails; or
- complete route closure against privileged administrative paths outside the demonstrated architecture.

EC-001 supports only the properties exercised and evidenced by the public reference implementation.
