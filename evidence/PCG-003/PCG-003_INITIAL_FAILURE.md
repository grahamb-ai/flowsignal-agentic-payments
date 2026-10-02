# PCG-003 — Preserved Initial Failure

**Frozen challenge commit:**
`86bc6d7523ec798558da569940c429aef978c924`

## Command

```text
python -m pytest -q tests/test_pcg003_sibling_successor_branching.py
```

## Result

```text
FAILED tests/test_pcg003_sibling_successor_branching.py::test_terminal_parent_cannot_issue_two_concurrent_successors
1 failed
```

## Failure

```text
Failed: DID NOT RAISE ValueError
```

The unchanged implementation allowed the same authority-issued, terminally
invalid parent to issue two distinct successors for the same scenario and
canonical action.

## Classification

**FAIL — sibling successor branching was implicitly enabled.**

The parent-to-successor edge was checked independently on each invocation and
was not consumed by the first successful successor issuance. The current
lifecycle topology therefore did not determine that the second transition was
unavailable.
