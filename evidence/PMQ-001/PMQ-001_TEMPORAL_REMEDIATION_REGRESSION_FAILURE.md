# PMQ-001 — Temporal-Boundary Remediation Regression Failure

**Status:** PRESERVED REGRESSION FAILURE — TIME MODEL INCONSISTENCY EXPOSED  
**Date:** 18 August 2026  
**GitHub Actions run:** `32101162964` (run #63)  
**Head commit under test:** `3f4121e8433a484947730f51540972d6c947195e`

## Context

The delayed-permit-expiry failure showed that a gateway-produced permit could remain consequence-forming after the Authority Receipt validity window had expired.

The remediation bound `valid_until` into the signed execution permit and added a final wall-clock expiry check at the protected consequence boundary.

## Regression result

The full regression then produced:

```text
8 failed, 26 passed in 2.47s
```

The failures were concentrated in previously valid AP-001 / EC-001 / PMQ execution paths, which now returned:

```text
DENIED_EXECUTION_PERMIT_EXPIRED
```

or the resulting represented `NO EXECUTION`.

## Cause identified

The public harness currently has inconsistent clock semantics across its layers:

- `evaluate_financial()` defaults its seal time to `req.requested_execution_time`;
- scenario fixtures contain fixed historical timestamps;
- the Execution Gateway evaluates receipt validity against the represented attempt time;
- the strengthened protected consequence boundary evaluates permit expiry against the current trusted process wall clock.

A normal fixture can therefore be considered valid by Runtime Authority and the gateway using its represented historical time, while already expired against the actual consequence-time wall clock.

## Classification

**REGRESSION / TIME-MODEL INCONSISTENCY — the delayed-expiry proposition remains valid and unchanged.**

This run is not eight independent Runtime Authority proposition failures. It demonstrates that strengthening the final temporal boundary exposed an inconsistent model of 'current time' in the reference harness.

## Remediation constraint

Do not remove or weaken the final expiry check simply to restore green tests.

The correction must establish explicit clock semantics:

- normal/live harness evaluation must use a current trusted harness clock for sealing and consequence validity;
- historical/replay/adversarial tests may explicitly inject a historical `sealed_at` where required;
- executor-controlled timestamps must not be able to extend or resurrect an expired authority window.

After correction, the delayed-expiry challenge and the full existing regression suite must both be rerun.