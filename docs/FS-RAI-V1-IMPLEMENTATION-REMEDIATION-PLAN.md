# FS-RAI v1 Implementation Remediation Plan

**Branch:** `fs-rai-v1-remediation`  
**Frozen failed baseline:** `471d8af596044d61f86f774f70cd8c6ff2efc31c`  
**Governing fixture:** FS-RAI-FX-001 v1.0 @ `43791d0bb773c927b4bec4103fb087c2c00e2842`  
**Baseline result:** FS-RAI-IC-001-BL-001 — 8 independent FAIL classes  
**Status:** REMEDIATION DESIGN — NO CLAIM OF PASS

## Rule

The released fixture is not changed to accommodate this implementation. Each remediation must preserve the original failing baseline and be rerun against dependency-related tests.

## Architectural remediation groups

### R1 — Canonical monetary semantics
Closes IC-FAIL-001.

Replace authority-material payment/limit binary floats with exact canonical monetary representation. JSON/scenario parsing must preserve decimal lexical value rather than converting through float. Binding serialization must use one canonical amount representation.

### R2 — Authoritative institutional state model
Targets IC-FAIL-003, IC-FAIL-004, IC-FAIL-007 and IC-FAIL-008 together.

Introduce a versioned authoritative state object/root containing, at minimum:
- mandate identity/status/scope/limits/currency/source-account set;
- actor/principal standing where authority-material;
- competent source identity and competence-root evidence;
- authority epoch + fence scope + monotonic fence;
- authority semantics version + immutable definition identity + competent semantic source;
- coherent snapshot identity.

Unknown mandate/source state fails closed. Presented request values never become authoritative merely because authoritative lookup is absent.

### R3 — Approval authority model
Closes IC-FAIL-002.

If approval is required, ALLOW requires a current approval record bound to the exact payment instruction, approval authority, usage state and authority snapshot. No boolean-only approval substitute.

### R4 — Aggregate authority reservation
Closes IC-FAIL-005.

Introduce aggregate scope/window identity and coherent limit/CONSUMED/RESERVED/UNCERTAIN state. Reservation becomes authority-effective only after other required authority conditions are established and must bind exact exercise/instruction/attempt semantics. Commit/consume/release/reconciliation must preserve one-use accounting.

### R5 — Exercise / attempt / instruction lineage
Closes IC-FAIL-006.

Introduce distinct immutable:
- authority_exercise_id;
- execution_attempt_id;
- payment_instruction_id.

Retries and re-evaluations must not accidentally inherit the wrong authority exercise. Permits and evidence bind all required lineage.

## Remediation order

1. R1 exact money.
2. R2 authoritative state/snapshot/semantics/epoch.
3. R5 identity lineage.
4. R3 approval.
5. R4 aggregate reservation.
6. Rebuild gateway/permit binding over the accumulated canonical state.
7. Rerun existing regression plus FS-RAI mapping probes.
8. Preserve any new first failure before further remediation.

This order is chosen because approval and aggregate authority need the authoritative snapshot and identity model underneath them.

## Non-goals

This branch does not claim:
- production banking integration;
- distributed HA/consensus;
- legal validity of a real mandate;
- external settlement;
- KMS/HSM-grade isolation;
- independent third-party certification.

It is a reference implementation conformance remediation against the released canonical fixture.

## Exit gate

No GREEN claim until:
- all eight baseline FAIL classes have executable closure evidence;
- existing previously-green hostile tests remain green;
- deliberate defects are detected;
- positive capability still reaches the protected commitment path;
- full applicable CT/BT/CB + canonical mutation surface is run under one compatible campaign epoch.
