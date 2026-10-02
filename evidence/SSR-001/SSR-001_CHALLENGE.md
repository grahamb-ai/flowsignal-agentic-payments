# SSR-001 Structural-Law / Current-Fact Resolution Challenge

## Status

Frozen before first execution.

## Origin

This challenge tests the proposed split:

- structure predetermines the authority meaning and consequence reachability rules;
- runtime resolves materially current facts against that fixed structure; and
- the protected consequence path is present only while those facts satisfy the
  structural law.

## Frozen propositions

1. A candidate already known to violate the fixed authoritative mandate has no
   enabled path to protected consequence.
2. A candidate that is not known invalid may obtain a path only after current
   facts resolve and bind to the fixed structural requirements.
3. A later authority-state change removes the historical path without changing
   the structural meaning or rewriting the historical receipt.
4. Re-resolution under the new current state may create a new, separately bound
   path for the same business action.
5. Expiry and consumption remove path availability according to the already
   declared structural rules; runtime does not redefine those rules.

## Liveness and non-vacuity controls

A current, exactly bound candidate must still be able to form one protected
consequence.  The proof fails if all paths are disabled.

## Declared boundary

The result is bounded to the public Python reference-MVP transition surface. It
does not establish distributed production enforcement, universal structural
standing, or absence of routes outside the tested surface.

## Frozen executable test

`harness/tests/test_ssr001_structural_law_current_fact_resolution.py`

No implementation change is authorised before the initial result is recorded.
