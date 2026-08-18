# PMQ-001 — Unavailable Trusted Evidence Fail-Closed Challenge

**Status:** FROZEN BEFORE TEST EXECUTION  
**Date:** 18 August 2026

## Frozen propositions exercised

- PMQ-001.2 — Current authority/evidence under present conditions
- PMQ-001.3 — Standing at the boundary
- PMQ-001.5 — Lawful continuation or loss of continuation
- PMQ-001.6 — NO_BIND / represented non-formation

## Challenge

A candidate movement that would otherwise be within authority is presented with the required sanctions-screening evidence unavailable at the decision boundary.

## Required property

Unavailable required trusted evidence must never produce `ALLOW`, a consequence-forming execution permit, or a represented formed consequence.

The exact non-ALLOW vocabulary may be `ESCALATE` or `REFUSE` according to the current Runtime Rules. This challenge tests fail-closed execution behavior, not the policy taxonomy for unavailable evidence.

## Failure condition

The proposition fails if unavailable required evidence can produce `ALLOW` or reach `CONSEQUENCE_FORMED` on the governed harness route.

## Scope

A PASS is bounded to the represented public harness and the specific unavailable-screening condition tested. It does not prove behavior for every external evidence-service failure mode.