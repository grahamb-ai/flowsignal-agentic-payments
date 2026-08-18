# PMQ-001 — Delayed Permit Expiry Failure

**Status:** PRESERVED FAILURE  
**Date:** 18 August 2026  
**GitHub Actions run:** `32101085351` (run #60)  
**Head commit under test:** `35c4ea77ad78b6f8413789969b149644d7449c89`

## Frozen challenge

The corrected challenge established a genuine ALLOW and gateway-produced execution permit while the Authority Receipt was still temporally valid, then presented that permit to the protected consequence boundary after the receipt validity window had expired.

## Observed result

The protected consequence still formed:

```text
CONSEQUENCE_FORMED
```

The frozen assertion failed:

```text
assert 'CONSEQUENCE_FORMED' != 'CONSEQUENCE_FORMED'
```

Full suite result:

```text
1 failed, 33 passed in 0.61s
```

## Initial classification

**FAIL — a gateway-produced execution permit remained consequence-forming after the Authority Receipt temporal validity window had expired on the in-process harness surface.**

## Mechanism gap

The Execution Gateway checked `receipt.valid_until` only at gateway validation time. The resulting `ExecutionPermit` did not carry an integrity-protected expiry derived from the Authority Receipt, and `execute_protected_consequence()` therefore had no temporal standing check to apply at the final represented consequence boundary.

The permit could remain usable after the authority window that justified its issuance had expired, provided authority-state version had not changed and the permit had not already been consumed.

## Scope

This is a bounded public reference-harness failure. It is not a claim about trusted clock infrastructure, distributed systems or external payment rails.

## Remediation constraint

The frozen delayed-expiry test must remain unchanged. Remediation must bind the permit to the Authority Receipt validity window and enforce that signed expiry at the protected consequence boundary.

Any later PASS remains bounded to the in-process reference harness and its local clock.