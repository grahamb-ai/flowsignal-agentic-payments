# FS-SZ-PAY-001 T20 — preserved RED and remediation contract

## Frozen evidence
GitHub Actions run 44493861540, commit 048b21ebfc6ec6d589cd87a51273a9ce56e48e00:
58 passed, 1 failed. The new T20 test dispatched twice when a second valid permit
was issued for the same represented payment after an unresolved first attempt.
This is a **simulated provider**, not proof of two live bank transfers.

## Root cause
The external adapter sends `transaction_id=permit.signature`. A newly issued
permit has a different signature, so a provider using this key would treat the
new attempt as a different payment. The current `action_binding_hash` hashes
actor, principal, action, target, amount, currency, source account, beneficiary,
purpose and mandate, but **does not identify a unique business payment intent**.
Two legitimately separate payments can have identical fields; consequently
the binding hash must not be used as a permanent uniqueness key.

## Required candidate (NOT IMPLEMENTED)
1. Introduce a caller-supplied, authenticated `payment_intent_id` that remains
   stable across attempts, new permits, executor routes and retries. Include it
   in the protected action binding and in the provider's idempotency identity.
2. Atomically reserve this intent at the **protected execution boundary** in
   shared durable state before provider dispatch. Only a qualified issuer or
   execution authority may release or replace it. Reject or hold a different
   permit while the original outcome is unresolved.
3. Distinguish INTENT_RESERVED, DISPATCH_UNKNOWN, CONFIRMED_COMMITTED,
   AUTHORITATIVELY_NOT_COMMITTED. Never infer NOT_COMMITTED from timeout or
   eventually consistent NOT_FOUND.
4. Reconcile through authenticated provider evidence, matching the intent,
   amount, currency, beneficiary, source account and provider route.
5. Test two genuinely different business intents with identical payment fields:
   they must be allowed separately. Test same intent across two permits, two
   processes and two provider routes: only one effect may form.
6. Test crashes before/after claim, during dispatch, after provider commit and
   before acknowledgement; test recovery after revocation and stale state.
7. Explicitly scope provider cooperation, atomicity and route closure. A local
   SQLite claim alone does not prove cross-host or provider-side enforcement.

## Acceptance
Keep T20 original RED unchanged; implement on a **new candidate branch** and
run original 58 tests plus explicit intent identity and cross-route challenges.
No GREEN claim until evidence is recorded. No production changes.
