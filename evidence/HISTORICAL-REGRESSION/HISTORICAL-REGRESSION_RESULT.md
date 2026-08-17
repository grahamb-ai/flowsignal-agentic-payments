# Historical Regression Reconciliation — Final Result

**Date:** 17 August 2026

## Objective

Test the current EC-001-strengthened FlowSignal Agentic Payments Harness against the recoverable historical AT-003 regression surface preserved in the public `adversarial-testing-v0.10` branch.

## Historical baseline provenance

The AT-004 documentation committed on 13 August 2026 recorded:

```text
60 passed
```

as the **non-database regression baseline** at that time.

The current public Git history does not expose sixty distinct committed test cases that can simply be copied forward as an additive suite. The recoverable historical test modules absent from current `main` were:

- `test_at003_executor_binding.py`
- `test_at003_protected_execution.py`
- `test_at003_consequence_surface.py`

The earlier 60-test figure must therefore remain a historical recorded baseline, not be restated as a presently reproduced 60-test suite.

## Reconciliation lineage

### Run 1 — unchanged historical modules

Workflow run: `32032340560`

Result: **collection failure** because the historical tests referenced the superseded `ProtectedPaymentState` / `execute_protected_payment()` API.

Preserved in:

`HISTORICAL-REGRESSION_PRE_RECONCILIATION.md`

### Run 2 — first semantic translation

Workflow run: `32032469145`

Result:

```text
2 failed, 33 passed, 1 xfailed in 0.57s
```

The two failures occurred because the translation modified fields on integrity-sealed Authority Receipts. The current gateway correctly rejected those altered receipts with `AUTHORITY_RECEIPT_INTEGRITY_INVALID` before the historical expiry/REFUSE assertions could be reached.

Preserved in:

`HISTORICAL-REGRESSION_TRANSLATION_FAILURE.md`

### Run 3 — integrity-preserving semantic translation

The historical proof obligations were then exercised without altering sealed receipts:

- expiry was produced by advancing the execution-attempt time beyond `valid_until`;
- REFUSE was exercised using a natively issued, integrity-valid REFUSE receipt;
- missing authority dependency was tested against the current protected consequence interface;
- the historical v0.9 executor-binding failure remains intentionally preserved as `xfail`.

Workflow run: `32032566537`

Final result:

```text
35 passed, 1 xfailed in 0.45s
```

**0 failed.**

## Interpretation

The current strengthened implementation passes all currently maintained tests plus the recoverable historical AT-003 proof obligations after translating those obligations to the present consequence-boundary API.

The single `xfail` is intentional historical evidence. It preserves the known v0.9 executor-binding failure and is not a current regression failure.

## Claim boundary

This result supports the statement:

> The current public harness passes the current regression suite and the recoverable historical AT-003 proof obligations, with zero failures and one intentionally preserved historical xfail.

It does **not** support the statement that the historical `60 passed` suite has been exactly reproduced, because the public repository history does not expose sixty distinct recoverable committed tests corresponding one-for-one to that historical count.

It also does not include the database-backed API tests that the original AT-004 documentation explicitly excluded because the required PostgreSQL service was unavailable during that historical run.
