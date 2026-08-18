# PMQ-001 — Delayed Execution Permit Expiry Challenge

**Status:** FROZEN BEFORE TEST EXECUTION  
**Date:** 18 August 2026  
**Target:** FlowSignal Agentic Payments Runtime Authority MVP

## Frozen propositions exercised

- PMQ-001.2 — Current authority/evidence under present conditions
- PMQ-001.3 — Standing at the boundary
- PMQ-001.4 — Changed-condition loss of standing
- PMQ-001.5 — Lawful continuation or loss of continuation
- PMQ-001.7 — Credible bypass attempts and route closure

## Challenge

A valid ALLOW receipt may be valid when the Execution Gateway is invoked but cease to be temporally valid before the represented consequence actually forms.

The challenge asks whether a gateway-produced execution permit can be retained beyond the Authority Receipt validity window and then used later to form the represented consequence while authoritative state version remains unchanged.

## Required property

The represented consequence must not form after the temporal validity window that justified the execution permit has expired.

A permit must carry an integrity-protected expiry derived from the validated authority determination, and the final protected consequence boundary must reject an expired permit.

## Test method

1. Produce an authentic ALLOW receipt sealed sufficiently far in the past that its 60-second validity window has expired relative to wall-clock consequence time.
2. Construct the bound execution attempt at a time that was still inside that original validity window.
3. Pass that attempt through the Execution Gateway and obtain a valid execution permit.
4. Delay consequence formation until after the receipt validity window has expired.
5. Present the permit to the protected consequence boundary.

## Failure condition

The proposition fails on the tested surface if `execute_protected_consequence()` returns `CONSEQUENCE_FORMED` after the authority validity window has expired.

## Evidence discipline

If the failure is observed it must be preserved before remediation. The challenge must not be narrowed to gateway-time validity only.

Any later PASS is bounded to temporal expiry enforcement within the public in-process harness. Clock synchronization, trusted time sources and distributed timing guarantees remain deployment proof obligations.