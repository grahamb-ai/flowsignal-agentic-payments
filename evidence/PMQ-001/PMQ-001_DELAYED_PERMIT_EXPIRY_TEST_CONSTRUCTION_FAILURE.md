# PMQ-001 — Delayed Permit Expiry Test-Construction Failure

**Status:** PRESERVED TEST-CONSTRUCTION FAILURE — PROPOSITION NOT REACHED  
**Date:** 18 August 2026  
**GitHub Actions run:** `32101030718` (run #59)  
**Head commit under test:** `2be1d8fdacc29fb9e0055fcc1a128392d440bd9d`

## Intended challenge

The frozen challenge asks whether a gateway-produced permit can form the represented consequence after the Authority Receipt temporal validity window has expired.

## Observed failure

The first construction attempted to seal AP-001 two minutes in the past while leaving the scenario's original screening timestamp unchanged.

That made the screening evidence stale relative to the artificial seal time, so Runtime Authority correctly returned:

```text
ESCALATE
```

rather than the intended baseline `ALLOW`.

The test failed before a permit was issued:

```text
assert response.decision == "ALLOW"
AssertionError: assert 'ESCALATE' == 'ALLOW'
```

Full suite result:

```text
1 failed, 33 passed in 0.41s
```

## Classification

**TEST-CONSTRUCTION FAILURE — no conclusion on the frozen delayed-expiry proposition.**

This is not evidence that the mechanism passed or failed the delayed-expiry challenge.

## Correction

The challenge remains unchanged. The test setup will be corrected so screening evidence is fresh at the historical seal time, allowing a genuine ALLOW and gateway permit to be established before the permit is tested after expiry.

The corrected test must still ask the same question: can the permit form the represented consequence after the authority validity window has expired?