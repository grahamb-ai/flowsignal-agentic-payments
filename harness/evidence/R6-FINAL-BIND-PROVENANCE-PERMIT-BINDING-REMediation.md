# R6 Final-Bind Provenance / Permit Binding — Failure-First Evidence

## Scope

This record freezes the R6 provenance-binding finding and remediation on `fs-rai-v1-remediation`. It does not claim R6 is globally closed beyond the tested routes.

## Preserved baseline

Before the next-order provenance challenges, the full suite was GREEN:

- 111 passed.
- No production change was required to align the earlier R6 hostile cases with the strengthened final-bind provenance contract.

## First meaningful RED

The fourth-order case `test_r6_valid_final_bind_provenance_cannot_be_reused_for_a_second_permit_signature` began with a genuinely successful integrated final-bind/mint chain.

A second, separately signed permit was then minted with the same legitimate RAI lineage and registered against the first permit's genuine final-bind provenance.

Observed result before remediation:

- `CONSEQUENCE_FORMED`
- Full suite at that point: 2 failed, 111 passed.
- The second failure was test setup: aggregate authority capacity was exceeded before its intended boundary was reached.

The demonstrated weakness was therefore specific: final-bind provenance was bound to the authority lineage and usage reservation, but not to the exact permit signature created from that final-bind/mint event.

## Root cause

`FinalBindProvenance` recorded:

- determination ID
- constraint ID
- protected operation ID
- authority exercise ID
- execution attempt ID
- action binding hash
- usage reservation ID

It did not record the permit signature.

The RAI execution registry was keyed by permit signature, but final-bind provenance verification did not establish that the provenance belonged to the permit presented at the protected consequence boundary.

## Narrow remediation

The remediation binds final-bind provenance to the exact permit signature:

1. `FinalBindProvenance` now records `permit_signature`.
2. The successful integrated mint path establishes provenance for the exact permit it minted.
3. The protected consequence boundary supplies the presented permit signature when verifying final-bind provenance.
4. Verification requires equality with the provenance-bound permit signature.

No special-case executor bypass or test weakening was introduced.

## Verification

After remediation, the original second-permit reuse case no longer formed a consequence.

The next-order cross-chain case was then corrected so it could reach its intended boundary without exceeding aggregate authority capacity and without attempting to overwrite an immutable existing registry row.

Final full regression:

```
........................................................................ [ 63%]
.........................................                                [100%]
113 passed in 0.61s
```

The tested properties now demonstrate:

- forged/self-registered RAI-looking state is insufficient;
- possession of low-level registry capability does not manufacture valid provenance;
- forged usage state does not complete the causal provenance chain;
- genuine provenance from one mint cannot be reused for a second permit signature;
- genuine provenance from one prepared chain cannot be transplanted into another chain and form a protected consequence.

## Evidence lineage

- Baseline GREEN: 111/111.
- Preserved fourth-order RED: genuine provenance reused by a separately signed permit reached `CONSEQUENCE_FORMED`.
- Root cause: final-bind provenance lacked exact permit-signature binding.
- Remediation: provenance-to-permit binding at establishment and verification.
- Final checkpoint: 113/113 GREEN on branch `fs-rai-v1-remediation`.

## Boundary statement

This evidence supports closure of the specific R6 provenance-reuse and provenance-transplant routes exercised by these tests. It is not a claim that every possible provenance, minting, persistence, concurrency, rollback, or distributed execution route is closed.
