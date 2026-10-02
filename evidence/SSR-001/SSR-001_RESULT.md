# SSR-001 Structural-Law / Current-Fact Resolution Result

## Frozen object

- Branch: `challenge/ssr-001-structural-law-current-fact-resolution`
- Frozen-test commit: `215fb26ab42e7d0890851eda52c9d28297791eb4`
- Test: `harness/tests/test_ssr001_structural_law_current_fact_resolution.py`
- Challenge: `evidence/SSR-001/SSR-001_CHALLENGE.md`

No FlowSignal implementation code was changed for this result.

## Initial execution

The repository's copied virtual environment initially lacked its `python`
symlink.  That invocation did not start pytest and is not a behavioural result.
After repairing the local, untracked virtual-environment launcher, the unchanged
frozen test produced:

```text
...                                                                      [100%]
3 passed in 0.08s
```

## Observed results

1. The fixed authoritative mandate admitted only its declared payment action.
   A candidate bound to `DELETE_ACCOUNT` resolved `REFUSE`, failed the
   `action_permitted` structural requirement, and obtained no execution permit.
2. A valid current candidate resolved `ALLOW`, obtained an exactly bound permit,
   and formed the protected consequence, establishing non-vacuous liveness.
3. After the authority-state version advanced, the formerly valid permit
   returned `DENIED_AUTHORITY_STATE_STALE`; its consequence receipt preserved
   the historical authority receipt and recorded non-formation.
4. A fresh resolution of the same business action under the new state obtained
   a new receipt and permit bound to the current authority version.  The fresh
   path formed consequence while the historical path remained stale.
5. A candidate evaluated one microsecond after mandate expiry resolved
   `REFUSE`, failed `mandate_not_expired`, and obtained no permit.
6. A current permit formed exactly one consequence; its second use returned
   `DENIED_EXECUTION_PERMIT_REPLAY`.
7. None of those runtime resolutions mutated the declared authoritative mandate
   object used as the fixed structural law in this bounded test.

## Related regression execution

The focused test was rerun with known-invalid unreachability, consequence
boundary, context freshness, delayed expiry, durable replay, concurrent
revocation, boundary expiry, terminal invalid-generation and unauthorised
successor-generation tests:

```text
................                                                         [100%]
16 passed in 0.72s
```

## Full reference-harness execution

The complete harness retained the deliberately preserved SCB-001 failure:

```text
596 passed, 1 failed in 2.56s

FAILED
tests/test_scb001_known_invalid_path_nonexistence.py::
test_known_invalid_action_has_no_authority_issued_consequential_path
```

The failure is expected evidence, not a regression introduced by SSR-001.  It
shows that the stronger non-instantiation proposition remains unsatisfied:
FlowSignal prevents the known-invalid candidate from reaching consequence but
does not yet prevent authority-owned issuance of that candidate identity.

## Finding

**BOUNDED STRUCTURAL-LAW / CURRENT-FACT SEPARATION DEMONSTRATED WITHIN THE
DECLARED REFERENCE-MVP SURFACE**

Within this tested surface:

```text
KNOWN INVALID
-> NO ENABLED CONSEQUENCE PATH

NOT KNOWN INVALID
-> RESOLVE CURRENT FACTS
-> BIND TO FIXED STRUCTURAL REQUIREMENTS
-> PATH PRESENT / PATH ABSENT
```

Runtime resolved current facts and path availability.  It did not redefine the
meaning of authority, expiry, revocation or consumption.

## Critical qualifications

- This is a bounded executable result, not a proof of universal structural
  standing or a new computational category.
- It does not establish distributed atomicity across independently owned
  production systems.
- It does not close SCB-001: the reference MVP can still issue an
  authority-owned candidate identity for an action whose invalidity was already
  knowable.  The stricter structural non-instantiation property remains not
  established.
- The test demonstrates the declared separation through observable behaviour;
  it does not establish that the terminology itself denotes a unique
  architecture.
