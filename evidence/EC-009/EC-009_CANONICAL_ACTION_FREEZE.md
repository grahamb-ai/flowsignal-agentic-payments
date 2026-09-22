# EC-009 Canonical Action Freeze

This freeze defines the one action that may be used by the bounded FlowSignal ×
SafeAgent × Stripe Test Mode EC-009 fixture.

- Action: `payment.collect`
- Stripe environment: Test Mode only
- Stripe operation: `payment_intent.create`
- Stripe account / beneficiary: `acct_1U06JYL6P3JlguFB`
- Source payment method: `pm_card_visa`
- Amount: USD 1.00, represented canonically as 100 minor units
- Customer: none
- Canonical SHA-256: `bb7dbb55025471a21a216f5e08eea74f72a5a6e1bd0513e127d2f84abcc8de93`

`EC-009_CANONICAL_ACTION.json` is the authority-bearing action object. FlowSignal,
the SafeAgent adapter, the Stripe projection and the semantic evidence verifier
must compute the same canonical SHA-256 over that object. Metadata correlation is
not a substitute for equality with this object.

For this v1 schema, canonical bytes are UTF-8 JSON with object keys sorted,
no insignificant whitespace, and no ASCII escaping. The hash is over those
canonical bytes, not over the pretty-printed repository file. The `.sha256`
sidecar records that digest directly.

The SafeAgent/downstream capability must directly verify the upstream FlowSignal
permit and must not expire later than the upstream permit. A Stripe execution is
not supported by this freeze if any authority-bearing field differs.

The frozen object does not establish production settlement, route closure,
deployment-wide non-bypassability, distributed atomicity or certification.
