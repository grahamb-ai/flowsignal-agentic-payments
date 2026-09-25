# R6 All-Low-Level-Capabilities — First Failure

## Status

Preserved RED. No remediation is recorded in this document.

## Preceding checkpoint

The immediately preceding R6 provenance-binding checkpoint was fully GREEN:

- 113 passed.
- Final-bind provenance was bound to the exact execution permit signature.
- Cross-permit reuse and tested cross-chain provenance transplant routes were rejected.

## Challenge

The next-order case asks whether possession of every relevant in-process reference capability can substitute for the successful integrated final-bind path.

The test directly reaches:

- execution-permit mint capability;
- usage-policy registration capability;
- final-bind provenance issuance capability;
- RAI execution-binding registration capability.

It constructs mutually matching permit, usage reservation, provenance and RAI registry state without traversing `final_bind_payment(...)` / successful `revalidate_at_final_bind(...)`.

## Observed first failure

Full suite:

```
1 failed, 113 passed
```

The protected consequence returned:

```
CONSEQUENCE_FORMED
```

The failing case is:

`test_r6_all_low_level_capabilities_cannot_substitute_for_successful_final_bind`

## Root-cause trace

The current reference implementation uses module-level object identities as possession capabilities.

`establish_final_bind_provenance(...)` accepts caller-supplied lineage/action/usage/permit fields and establishes provenance when the caller presents `_FINAL_BIND_PROVENANCE_ISSUANCE_CAPABILITY`.

It does not independently consume or verify a result emitted by `revalidate_at_final_bind(...)`.

The integrated mint path does call `final_bind_payment(...)` and requires `FinalBindResult.status == "PERMITTED"` before minting. However, the low-level provenance helper is independently reachable and its capability object is importable in the reference process.

Consequently, a caller holding all of the low-level reference capabilities can construct internally consistent records that satisfy the protected consequence verifier even though the integrated successful final-bind path was not traversed.

## Boundary implication

The present reference capability objects provide call-site gating, but the complete set does not prove causal traversal of final-bind.

This is distinct from the earlier permit-signature provenance reuse finding. Exact permit binding remains necessary, but it is not sufficient when provenance itself can be established independently of successful final-bind.

## Remediation requirement

Do not solve this by adding another caller-supplied flag or another freely importable possession token.

A valid remediation must make successful final-bind causally necessary for provenance establishment, so that directly composing the low-level mint/usage/provenance/registry helpers cannot manufacture equivalent executable state.

The preserved RED should remain unchanged until that property is implemented and demonstrated.


## Remediation verification

The preserved first failure was remediated by making successful final-bind emit a one-shot causal grant bound to the protected operation, authority exercise and execution attempt. Final-bind provenance establishment now requires and consumes that grant.

The hostile case itself was not weakened: direct possession of the low-level mint, usage-policy registration, provenance-issuance and RAI-registration capabilities remains insufficient because no successful final-bind causal grant exists.

The pre-existing cross-chain provenance case was aligned with the strengthened contract by obtaining chain A provenance through the genuine successful final-bind/mint path before attempting transplantation.

Final full regression:

```
114 passed in 0.43s
```

This closes the demonstrated all-low-level-capabilities causal-substitution route within the bounded reference implementation. It does not establish global closure for production IAM/process isolation, persistence, concurrency, rollback of all state, distributed execution or infrastructure compromise.
