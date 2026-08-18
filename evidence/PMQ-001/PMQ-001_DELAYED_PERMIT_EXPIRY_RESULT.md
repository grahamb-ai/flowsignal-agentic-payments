# PMQ-001 — Delayed Permit Expiry Result

**Status:** PASS AFTER REMEDIATION — BOUNDED IN-PROCESS CLOCK SURFACE  
**Date:** 18 August 2026  
**Initial mechanism-failure run:** `32101085351` (run #60)  
**Temporal-regression run:** `32101162964` (run #63)  
**Successful full rerun:** `32101309367` (run #65)  
**Current head under successful test:** `debd3ef85ab40df3f7fab841f0fb61521a49cc25`

## Frozen challenge

A gateway-produced execution permit must not remain consequence-forming after the Authority Receipt temporal validity window has expired.

## Initial mechanism failure

The corrected failure-first test established a genuine ALLOW and gateway permit inside the validity window, then presented the permit after expiry.

Observed:

```text
CONSEQUENCE_FORMED
```

Classification at that point:

**FAIL — temporal standing was checked at the gateway but not preserved to the final protected consequence boundary.**

## Remediation

The execution permit now carries the Authority Receipt `valid_until` value inside its HMAC-protected payload.

The protected consequence boundary verifies the signed expiry and rejects:

- missing expiry;
- malformed expiry;
- expired permits.

Expired permits return:

```text
DENIED_EXECUTION_PERMIT_EXPIRED
```

## Regression discovered during strengthening

The first full regression after adding the final wall-clock check produced `8 failed, 26 passed` because deterministic scenario fixtures contained historical absolute timestamps while the strengthened protected boundary correctly compared expiry with current process time.

That regression was preserved separately rather than weakening the expiry check.

## Clock-semantics correction

`load_scenario()` now treats public scenario JSON timestamps as deterministic fixture anchors for normal/live execution. By default it rebases the requested execution time to the current UTC harness clock and shifts mandate expiry and screening capture timestamps by the same delta.

Relative facts are therefore preserved:

- screening evidence age;
- mandate-valid / mandate-expired relationship;
- scenario-to-scenario temporal differences.

Tests that genuinely require literal historical time may opt out with `rebase_to_now=False` or explicitly inject `sealed_at`.

This avoids allowing stale fixture dates to masquerade as current execution time while preserving deterministic scenario semantics.

## Successful rerun

GitHub Actions run `32101309367` completed:

```text
34 passed in 0.57s
```

The delayed-expiry challenge passed together with the existing AT-004, FS-CT, EC-001 and PMQ-001 regression surface present on the branch.

## Classification

**PASS — signed permit expiry and final-boundary temporal rejection demonstrated on the public in-process harness using its current UTC process clock.**

## Residual limitations

This does not demonstrate:

- trusted hardware time;
- NTP/clock-source integrity;
- bounded clock skew between distributed services;
- cross-host temporal consensus;
- payment-rail time semantics.

Those remain deployment/integration proof obligations.