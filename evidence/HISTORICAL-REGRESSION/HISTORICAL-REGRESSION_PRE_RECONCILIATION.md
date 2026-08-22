# Historical Regression Reconciliation — Pre-Reconciliation Result

**Date:** 17 August 2026

## Purpose

Recover the historical AT-003 regression modules from the preserved `adversarial-testing-v0.10` branch and execute them, unchanged in their original architectural assumptions, against the current EC-001-strengthened implementation.

## Historical provenance

The AT-004 documentation recorded a **60 passed** non-database regression baseline on 13 August 2026. The preserved `adversarial-testing-v0.10` branch contains three AT-003 modules that are no longer present on current `main`:

- `test_at003_executor_binding.py`
- `test_at003_protected_execution.py`
- `test_at003_consequence_surface.py`

## First reconciliation run

GitHub Actions workflow: **EC-001 and Regression Tests**

Workflow run: `32032340560`

Result: **FAIL DURING TEST COLLECTION**

Observed errors:

```text
ImportError: cannot import name 'ProtectedPaymentState' from 'app.engines.execution_gateway'
```

The collection failure occurred in:

- `test_at003_consequence_surface.py`
- `test_at003_protected_execution.py`

Pytest stopped during collection with:

```text
2 errors in 0.54s
```

## Interpretation

This is an **API compatibility failure**, not an observed failure of the current Runtime Authority invariant.

The historical AT-003 tests targeted the earlier `ProtectedPaymentState` / `execute_protected_payment()` execution API. The current implementation replaced that represented execution surface with the `ExecutionGateway` + `ExecutionPermit` + `execute_protected_consequence()` boundary introduced and strengthened during later assurance work.

Accordingly, the unchanged historical modules cannot execute against the current implementation without translation to the current consequence-boundary API.

## Preservation rule

This failure is preserved before translation. The historical source remains recoverable from `adversarial-testing-v0.10`; any translated regression tests must preserve the original proof obligations rather than silently rewriting them into easier assertions.
