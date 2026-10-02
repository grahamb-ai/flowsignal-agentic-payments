# SCB-002 Known-Invalid Consequence-Unreachability Result

## Frozen object

- Branch: `challenge/scb-002-known-invalid-consequence-unreachability`
- Frozen-test commit: `a50f53b`
- Test: `harness/tests/test_scb002_known_invalid_consequence_unreachability.py`
- Challenge: `evidence/SCB-002/SCB-002_CHALLENGE.md`

No FlowSignal implementation code was changed for this result.

## Initial execution

```text
..                                                                       [100%]
2 passed in 0.05s
```

## Observed route results

The authority-issued `DELETE_ACCOUNT` candidate was already invalid under the
authoritative payment mandate.  Within the declared reference-MVP surface:

1. ordinary evaluation returned `REFUSE` and gateway validation returned
   `BLOCKED` without an execution permit;
2. direct use of the public permit issuer without its private gateway capability
   returned no permit, and protected consequence returned
   `DENIED_NO_EXECUTION_PERMIT`;
3. transplantation of a genuine valid-action ALLOW receipt onto
   `DELETE_ACCOUNT` returned `BLOCKED / ACTION_BINDING_MISMATCH`;
4. presentation of a genuine valid-action permit against the invalid action
   hash returned `DENIED_ACTION_BINDING_MISMATCH`;
5. an authority-issued successor retaining the invalid action binding again
   returned `REFUSE` and no execution permit; and
6. mutation of that successor into the valid action changed its binding, so its
   existing candidate identity was not authority-issued for the new action and
   again returned `REFUSE` with no execution permit.

The positive liveness control obtained an exactly bound permit, formed one
protected consequence, and rejected reuse as
`DENIED_EXECUTION_PERMIT_REPLAY`.

## Regression execution

Candidate lifecycle, consequence boundary and gateway non-bypass regressions:

```text
........                                                                 [100%]
8 passed in 0.26s
```

External route-capability closure regression:

```text
.                                                                        [100%]
1 passed in 0.13s
```

An earlier regression invocation from the repository root produced seven passes
and one `FileNotFoundError` because CBP-001 expects its relative fixture path to
be launched from the `harness` directory.  The same unchanged test was rerun
from that declared working directory and passed.  This was an invocation-path
error, not a behavioural test failure.

## Finding

**STRUCTURAL UNREACHABILITY DEMONSTRATED WITHIN THE DECLARED REFERENCE-MVP
TRANSITION SURFACE — KNOWN-INVALID ACTION DID NOT REACH PROTECTED CONSEQUENCE**

## Critical qualification

This result does not close SCB-001.

FlowSignal still issued an authority-owned candidate generation for an action
whose invalidity was already knowable from the authoritative mandate.  SCB-001
therefore remains correctly classified:

**STRUCTURAL CLOSURE NOT ESTABLISHED — KNOWN-INVALID INITIAL GENERATION WAS
ISSUED**

Accordingly, the combined evidence is:

- structural non-instantiation: **NOT ESTABLISHED**;
- bounded structural unreachability after issuance: **DEMONSTRATED**;
- valid exactly bound consequence liveness: **DEMONSTRATED**;
- one-shot consequence route / replay closure: **DEMONSTRATED**.

No claim is made about undisclosed systems, every possible production adapter,
all deployment topologies, or external channels outside the tested boundary.
