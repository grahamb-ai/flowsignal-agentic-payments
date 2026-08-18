# MRQ-001 — Master Runtime Qualification Regression Result

**Status:** COMPLETE — COUNT RECONCILIATION ESTABLISHED  
**Date:** 18 August 2026  
**GitHub Actions run:** `32104692207`

## Concurrent execution result

The three selected repository states were executed concurrently in one GitHub Actions matrix using Python 3.11 and the `pytest -q` command from each exact checked-out `harness` directory.

### AT-004 historical commit

Commit: `d9dab01eb1cc6d8a0c7fb50eadbdb1560a7d6ce1`

Repository documentation at this commit states a `60 passed` non-database assurance baseline.

Exact present-day reproduction result:

```text
17 passed in 0.40s
```

Classification:

**HISTORICAL COUNT NOT REPRODUCED — exact committed repository state is green, but the documented 60-test total is not reproduced by the committed `pytest -q` surface.**

This is not a mechanism failure. The 17 committed tests that are collected at this exact state all pass. The discrepancy means the historical `60 passed` total must not be reused as a presently reproduced count until its original command, additional test sources or uncommitted environment are independently recovered.

The earlier recalled `52 passed` figure also remains not located in the committed evidence examined during MRQ-001.

### EC-001 bounded regression baseline

Commit: `b154b82bd429d1d1f2a1e63306099de3e18423ff`

Exact reproduction result:

```text
30 passed in 0.55s
```

Classification:

**PASS — historical 30-test EC-001 regression reproduced exactly from the committed repository state.**

### Qualified MVP baseline

Commit: `8ac87bfce7110fdd9aa5d22a3f1df5622fbb679d`

Exact reproduction result:

```text
42 passed in 0.64s
```

Classification:

**PASS — current qualified 42-test MVP regression reproduced exactly from the merged baseline.**

## Deduplication finding

The historical totals are not additive.

Repository comparison shows that the committed AT-004 tests present at `d9dab01...` were not deleted on the path to the current qualified baseline. The EC-001 baseline likewise remains in the ancestry of the qualified MVP baseline, with later qualification work adding further tests rather than creating an independent test population.

Accordingly:

- `17 + 30 + 42` must **not** be presented as 89 unique tests;
- `60 + 30 + 42` must **not** be presented as 132 unique tests;
- the recalled `52 + 30 + 42` must **not** be presented as 124 unique tests.

The maintained current regression surface is the defensible current count:

```text
42 passed
```

Those 42 tests incorporate the surviving committed historical regression surface and the later EC-001, PMQ-001 and EC-002 qualification additions.

## What MRQ-001 demonstrates

MRQ-001 establishes two different forms of evidence:

1. **Lineage reproducibility:** the EC-001 30-test baseline and qualified MVP 42-test baseline reproduce exactly from their committed states; the earlier AT-004 committed state is green but reproduces 17 tests rather than the documented 60.
2. **Current regression position:** 42 is the current maintained regression count and should be used for present technical claims unless and until additional unique historical proof obligations are recovered and added to the maintained suite.

## Claim discipline

The strongest safe statement is:

> The qualified FlowSignal Agentic Payments MVP currently reproduces 42 passing tests. The earlier 30-test EC-001 regression also reproduces exactly from its historical commit. An older AT-004 repository note recorded 60 passing non-database tests, but the exact committed state currently reproduces 17 collected tests, so the 60-test and recalled 52-test totals are retained as historical claims rather than added to the current regression count.

No additive historical test total should be used in buyer-facing material without individual proof-obligation recovery and deduplication.
