# PMQ-001 — Existing Evidence Inventory

**Status:** BASELINE INVENTORY — BEFORE PMQ-001-SPECIFIC REMEDIATION  
**Date:** 18 August 2026

## Purpose

This inventory maps the frozen PMQ-001 propositions to evidence already present on `main`. It does **not** inherit earlier PASS classifications automatically and it does **not** constitute the final PMQ-001 result.

The purpose is to identify where existing tests genuinely exercise the frozen proposition and where new adversarial tests are required.

## Coverage summary

| PMQ ID | Frozen proposition | Existing relevant evidence | Baseline coverage assessment | New testing required |
|---|---|---|---|---|
| PMQ-001.1 | Candidate movement before bind | EC-001.4 protected consequence / permit tests | **INSUFFICIENT / material gap** | **YES — direct independent permit-minting and pre-bind consequence attempt** |
| PMQ-001.2 | Current authority/evidence under present conditions | AT-004.6, FS-CT-001, execution gateway state-version check | **STRONG bounded coverage** | YES — broaden evidence/clock/error-state cases |
| PMQ-001.3 | Standing at the boundary | EC-001.5 final state guard; stale permit rejection | **STRONG in-process coverage** | YES — direct bypass and failure-mode variants |
| PMQ-001.4 | Changed-condition loss of standing | FS-CT-001, AT-004.6, EC-001.5 | **STRONG bounded coverage** | YES — additional material-condition classes |
| PMQ-001.5 | Lawful continuation or loss of continuation | FS-CT-002 governed-route reevaluation | **PARTIAL / bounded route** | **YES — retry/recovery/restart/alternate continuation paths** |
| PMQ-001.6 | NO_BIND / actual non-formation | EC-001.4 missing/invalid permit; EC-001.6 represented non-formation | **PARTIAL** | **YES — direct consequence path and independent permit-minting attack** |
| PMQ-001.7 | Credible bypass attempts and route closure | AT-004.3, FS-CT-002, EC-001.4 | **PARTIAL / known capability-isolation gap** | **YES — direct issuer, direct consequence, duplicate/reuse and alternate call-path attacks** |
| PMQ-001.8 | Receipt of what formed or did not form | AT-004.4/.5 receipt integrity; agentic demo outcome fields; EC-001.6 | **PARTIAL** | YES — explicit formation/non-formation evidence lineage and tamper tests |
| PMQ-001.9 | Same-condition and changed-condition replay | FS-CT-003 replay; FS-CT-001 changed-state rejection | **MATERIAL coverage** | YES — same-condition determinism plus execution/replay separation and restart cases |

## Existing evidence reviewed

### FS-CT-001 — changed authority after ALLOW

`harness/tests/test_fs_ct_001_category_test.py`

The test obtains a genuine ALLOW and receipt, advances authoritative state, then attempts the exact previously authorised movement. The Execution Gateway rejects the stale receipt with:

`AUTHORITY_STATE_STALE_REEVALUATION_REQUIRED`

Useful for PMQ-001.2 and PMQ-001.4. It also contributes to PMQ-001.5, but only on the governed gateway path.

### FS-CT-002 — governed route closure

`harness/tests/test_fs_ct_002_route_closure.py`

The test demonstrates that the stale T0 receipt cannot be reused and that the normal harness route must perform a new evaluation/current-state receipt before represented execution can be permitted.

Useful for PMQ-001.5 and PMQ-001.7, but explicitly bounded to the represented governed harness route. It is not proof of universal route closure.

### FS-CT-003 — historical replay

`harness/tests/test_fs_ct_003_replay.py`

The test requires a historical determination to be reconstructed from preserved evidence after current authority state changes, without rewriting the original receipt or treating a fresh evaluation as replay.

Useful for the historical-reconstruction component of PMQ-001.9. Additional PMQ testing is still needed to distinguish historical replay from present-time executability and to exercise same-condition replay explicitly.

### AT-004.4 — receipt integrity

`harness/tests/test_at004_4_receipt_integrity.py`

A corrupted receipt HMAC is rejected by the Execution Gateway with `AUTHORITY_RECEIPT_INTEGRITY_INVALID`.

Useful for PMQ-001.8 and hostile/tamper extensions.

### AT-004.5 — evidential integrity

`harness/tests/test_at004_5_receipt_evidence_integrity.py`

Modification of the sealed request snapshot causes receipt integrity verification to fail.

Useful for PMQ-001.8 and evidence-tampering extensions.

### EC-001.4 — protected consequence and permits

`harness/tests/test_ec001_4_independent_execution_authority.py`

Existing tests demonstrate:

- no permit → denied;
- arbitrary invalid signature → denied;
- valid gateway-produced permit is exact-action bound;
- valid gateway-produced permit can form the represented consequence;
- the normal AP-001 route consumes the protected consequence boundary.

However, the current implementation also exposes permit issuance/signing within the same Python code/process boundary. EC-001 correctly records independent capability isolation as NOT DEMONSTRATED.

This is a material unresolved issue for PMQ-001.1, PMQ-001.6 and PMQ-001.7 and requires a direct consequence-producing bypass attempt, not merely source inspection.

### EC-001.5 — final in-process atomic interval

`harness/tests/test_ec001_5_atomic_boundary.py`

A state advancement cannot commit while represented consequence formation is paused inside the final guarded interval. If state advancement commits first, the older permit is denied as stale.

Strong bounded evidence for PMQ-001.3 and PMQ-001.4. It does not establish distributed atomicity.

### EC-001.6 — represented non-formation

`harness/tests/test_ec001_6_non_formation.py`

REFUSE/BLOCKED scenarios AP-003, AP-005 and AP-006 report `NO EXECUTION` on the represented harness surface.

Useful for PMQ-001.6 and PMQ-001.8, but it is not sufficient by itself because PMQ-001.6 explicitly requires testing whether another represented path can still form the consequence.

## Highest-priority uncovered attack

The first new PMQ-001 attack should challenge the known EC-001.4 gap as a **consequence-producing bypass**, rather than only checking that permit-issuer symbols or key material are visible.

Attack construction:

1. Do **not** obtain an ALLOW receipt through Runtime Authority.
2. Construct the exact action binding for a represented action.
3. Attempt to use any execution-side-accessible permit-minting capability directly.
4. Present the resulting permit to the protected consequence function.
5. Observe whether `CONSEQUENCE_FORMED` can occur without the required Runtime Authority bind.

If consequence formation succeeds, preserve the result as a PMQ-001 failure before changing the mechanism.

This attack directly bears on:

- PMQ-001.1 — candidate movement before bind;
- PMQ-001.6 — NO_BIND / actual non-formation; and
- PMQ-001.7 — credible bypass attempts / route closure.

## Baseline conclusion

The current suite already provides substantial evidence for stale-state rejection, changed-condition handling, bounded governed-route closure, receipt integrity, historical replay and the in-process final standing interval.

The largest known unresolved proof burden is **independent consequence capability isolation**. PMQ-001 should attack that first because a successful independent permit-minting path would be a materially stronger counterexample than a source-code inspection finding alone.
