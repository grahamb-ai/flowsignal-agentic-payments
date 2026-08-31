# Historical Regression Reconciliation — Translation Run Failure

**Date:** 17 August 2026

## Context

After the preserved historical AT-003 modules failed collection because the earlier `ProtectedPaymentState` / `execute_protected_payment()` API no longer exists, the historical proof obligations were translated to the current `ExecutionGateway` + `ExecutionPermit` + protected consequence boundary.

## Translation run

GitHub Actions workflow: **EC-001 and Regression Tests**

Workflow run: `32032469145`

Result:

```text
2 failed, 33 passed, 1 xfailed in 0.57s
```

The two failures were:

- historical expired-ALLOW assertion expected `AUTHORITY_DETERMINATION_EXPIRED`;
- historical REFUSE assertion expected `NO_APPLICABLE_ALLOW`.

Both translated tests had altered fields on an already integrity-sealed Authority Receipt using `dataclasses.replace()`.

The current gateway correctly rejected both altered receipts earlier in the validation chain with:

```text
AUTHORITY_RECEIPT_INTEGRITY_INVALID
```

## Interpretation

This is not evidence that expired or REFUSE determinations can execute. It shows that the later AT-004 receipt-integrity strengthening changed the valid way to exercise those historical proof obligations: an integrity-protected receipt must not be modified after sealing merely to construct the test condition.

The next translation therefore preserves receipt integrity:

- expiry is tested by moving the **execution attempt time** beyond the valid receipt's `valid_until`, rather than altering the receipt;
- REFUSE is tested using a scenario that natively produces a signed REFUSE receipt, rather than converting an ALLOW receipt after sealing.

This failed translation run is preserved so that the final green result does not hide the interaction between historical tests and the stronger receipt-integrity boundary.
