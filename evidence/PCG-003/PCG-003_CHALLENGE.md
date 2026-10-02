# PCG-003 — Sibling Successor Branching

## Frozen proposition

Once an invalidated candidate generation has produced its permitted successor,
the same parent MUST NOT independently produce another concurrently standing
successor for the same scenario and canonical action unless branching is
explicitly represented as an allowed lifecycle transition.

## Required invariant

```text
ISSUED_SUCCESSOR(g0, g1)
→ ¬ENABLED(ISSUE_SUCCESSOR(g0, *))
```

No branching semantics are represented in the current bounded reference-MVP
surface. Therefore, after `g1` is issued, a second `g0 → g2` transition must be
unavailable. `g2` must not be created merely so that it can be rejected later.

## Falsification condition

The proposition is falsified if one terminally invalid parent can issue two
distinct successors for the same scenario and canonical action.

## Evidence discipline

1. Freeze this proposition and its executable test before implementation work.
2. Run the test against the unchanged implementation.
3. Preserve any failure in the repository history.
4. If justified, make the narrowest repair.
5. Rerun the identical focused test and relevant regressions.

## Scope

This challenge concerns only the represented parent-to-successor lifecycle
edge. Passing it does not establish topology-wide structural closure across all
routes, retries, composition, effects or bypass surfaces.
