# MRQ-001 — Master Runtime Qualification Regression

**Status:** FROZEN BEFORE CONSOLIDATED EXECUTION  
**Date:** 18 August 2026

## Purpose

MRQ-001 asks whether the principal historical and current regression baselines can all be executed in one GitHub Actions run against their exact recorded repository states.

The purpose is evidence reconciliation, not arithmetic aggregation.

Historical test totals are not assumed to represent unique independent propositions. A result such as `60 + 30 + 42` must therefore not be described as `132 unique tests passed` without a separate deduplication exercise.

## Exact baselines

### AT-004 historical assurance baseline

Repository evidence at commit `d9dab01eb1cc6d8a0c7fb50eadbdb1560a7d6ce1` records:

`60 passed` — non-database regression baseline.

This is the verifiable repository baseline currently found for the earlier AT-004 assurance period. A separate `52 passed` baseline recalled from earlier discussion has not yet been located in the current repository evidence and is therefore not substituted or asserted.

### EC-001 bounded regression baseline

Commit `b154b82bd429d1d1f2a1e63306099de3e18423ff` is the final pre-merge EC-001 head associated with the documented 30-test regression.

### Qualified MVP baseline

Merge commit `8ac87bfce7110fdd9aa5d22a3f1df5622fbb679d` records the PMQ-001 / EC-002 qualified MVP baseline with 42 passing tests.

## Required property

One workflow must execute all three exact baselines independently and report each result without rewriting historical code to make it compatible with the current implementation.

A historical baseline that no longer installs or executes in the present CI environment must be classified as a historical reproducibility issue, not silently translated into a current PASS.

## Next stage

If the three exact baselines reproduce successfully, MRQ-001 will then inventory and deduplicate individual proof obligations to determine the number of unique current-and-historical challenges represented across the three generations.
