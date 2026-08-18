# PMQ-001 — Duplicate / Retry / Concurrent Permit Replay Challenge

**Status:** FROZEN BEFORE TEST EXECUTION  
**Date:** 18 August 2026  
**Target:** FlowSignal Agentic Payments Runtime Authority MVP

## Frozen propositions exercised

- PMQ-001.5 — Lawful continuation or loss of continuation
- PMQ-001.6 — NO_BIND / actual non-formation
- PMQ-001.7 — Credible bypass attempts and route closure
- PMQ-001.8 — Receipt of what formed or did not form
- PMQ-001.9 — Same-condition and changed-condition replay

## Challenge

A valid Runtime Authority determination and gateway-produced execution permit must not be usable as an independently repeatable consequence-forming capability.

The challenge asks two questions:

1. **Sequential replay:** after one represented consequence has formed, can the exact same execution permit be presented again and form the consequence a second time?
2. **Concurrent replay:** if two execution attempts present the exact same valid permit concurrently, can more than one represented consequence form?

## Required property

Within the represented in-process MVP consequence surface, one execution permit may authorize at most one represented consequence formation.

A retry, duplicate delivery or concurrent replay of an already-consumed permit must fail closed and must not form an additional represented consequence.

## Test method

1. Obtain a genuine ALLOW and Authority Receipt through Runtime Authority.
2. Pass the exact bound action through the governed Execution Gateway.
3. Obtain the gateway-produced execution permit.
4. Execute the represented protected consequence once and establish that it forms.
5. Reuse the identical permit sequentially and observe whether a second consequence forms.
6. In a separate test, present one identical permit from two concurrent threads and count consequence-forming outcomes.

## Failure condition

The proposition fails on the tested surface if either:

- the same permit returns `CONSEQUENCE_FORMED` more than once sequentially; or
- two concurrent uses of the same permit can both return `CONSEQUENCE_FORMED`.

## Evidence discipline

If either failure is observed it must be preserved before remediation. The frozen challenge and assertion must not be weakened after the result is known.

Any later PASS is bounded to the represented in-process harness surface. It does not by itself prove duplicate suppression across process restart, multiple service instances, distributed payment rails or external idempotency systems.