# SCB-002 Known-Invalid Consequence-Unreachability Challenge

## Status

Frozen before first execution.

## Question

Assume that an authority-issued candidate generation already exists for an
action whose invalidity is knowable from the authoritative mandate.

Within the declared FlowSignal reference-MVP transition surface, can any
supported route convert that candidate or retained artefacts into a protected
consequence?

## Frozen proposition

A known-invalid candidate must have no supported path to protected consequence.
In particular, none of the following may produce an execution permit or form
consequence:

1. ordinary evaluation and gateway validation;
2. direct use of the public permit issuer;
3. transplantation of a valid receipt onto the invalid action;
4. replay of a valid permit against the invalid action binding;
5. an authority-issued successor retaining the invalid binding; or
6. mutation of that successor into a valid-looking but differently bound action.

The liveness control requires a valid candidate to retain an exactly bound,
single-use route to protected consequence.

## Deliberate boundary

SCB-002 does not replace or remediate SCB-001.

SCB-001 asks whether the known-invalid candidate should have been issued at all
and preserves the current failure of that stricter structural non-instantiation
property.

SCB-002 tests the narrower structural-unreachability property after candidate
issuance.  It is bounded to the executable transition surfaces represented in
this public reference MVP; it is not a proof about every possible production
adapter, deployment topology, external side-effect channel, or undisclosed
system.

## Frozen executable test

`harness/tests/test_scb002_known_invalid_consequence_unreachability.py`

No implementation change is authorised before the initial result is recorded.
