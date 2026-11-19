# Consolidated integration contract — unresolved authority and intent identity

## Evidence baseline
CI run 44501801976: 13/13 focused PASS; full 81 PASS, 1 historical T23 FAIL. Original RED remains preserved.

## Source-level mismatch (verified)
- `ExecutionAttempt.mandate_id` identifies the institution's mandate; `ExecutionPermit.authority_state_version` is a **FlowSignal process-local authority-store version**, not a provider-owned per-mandate epoch.
- `external_consequence_adapter._external_payload` sends `transaction_id=permit.signature`, amount, beneficiary, source, currency, purpose; **does not send mandate_id or authority_epoch**.
- Configured `ExternalLedger.transfer` now requires `mandate_id` and `authority_epoch` to match its configured provider values. Thus existing FlowSignal adapter cannot successfully invoke this configured provider without a contract change.
- A newly issued permit changes its signature even for the same business payment. Thus the provider's unique `transaction_id` does not yet guarantee stable business-intent idempotency across permits.
- T22's atomic permit/intent claim is a separate local component and is **not** wired to the external payment adapter.

## Required coherent contract (not yet implemented)
1. Authority source defines a **per-mandate provider epoch**, including its issuance, freshness, revocation and trusted delivery semantics. Do not substitute FlowSignal's global `authority_state_version` as though it were that epoch.
2. Institution supplies a stable business payment-intent ID. Authenticate and bind it to mandate, amount, currency, source account, beneficiary, action and target *before* issuing a permit.
3. FlowSignal's permit must bind the exact intent and authoritative epoch; provider must verify that binding independently of caller-controlled request fields.
4. Provider's one atomic operation must validate standing, prevent duplicate business intent, and form the simulated transfer. Retries after ambiguous acknowledgement must reconcile the same intent, not mint a new identity.
5. All declared payment routes must use this same operation. Historical `--legacy-test-mode` remains explicitly outside the protected boundary and must not be reachable by protected credentials.
6. Re-run original T20 duplicate-new-permit challenge, T23 unfenced-provider counterexample (historical RED), T26 empty-response challenge, HTTP/mandate and concurrency tests.

## Decision
**DO NOT** silently set `authority_epoch=permit.authority_state_version` or `payment_intent_id=permit.signature`. Both would make tests appear integrated without satisfying the original safety property. Next implementation requires explicit signed/bound business intent and provider epoch contract. No production/main change.
