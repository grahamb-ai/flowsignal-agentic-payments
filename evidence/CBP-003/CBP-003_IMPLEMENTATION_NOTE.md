# CBP-003 — Protected External Route/Capability Closure Implementation Note

## Status

**IMPLEMENTATION ASSEMBLED — FIRST EXECUTABLE RESULT NOT YET CLASSIFIED**

## Frozen challenge

`CBP-003_CHALLENGE.md` was committed before implementation at:

`693aa230268142169b8b150757f7191d04fab867`

Frozen base commit:

`cb89c5c4ae1edba4c3c38931ae53e94421d0732d`

The frozen proposition has not been edited after implementation began.

## Named target and capability mechanism

External target:

`harness/external_targets/cbp003_capability_service.py`

The target runs as a separate OS process and owns independently queryable external ledger state.

The protected payment endpoint requires a one-time bearer capability. A FlowSignal execution permit is **not** accepted by the payment endpoint as the payment credential.

Capability release is provided by the target's `/capabilities/release` endpoint. Release succeeds only when the target can observe, in the explicitly named FlowSignal execution-state stores, both:

- durable consumption of the presented permit signature; and
- an unresolved consequence outcome bound to the same action-binding hash.

Those records are established by the existing protected consequence mechanism only after permit integrity, exact action binding, expiry, current authority-state version, rollback anchor and one-time permit consumption checks have succeeded.

The target binds the released capability to source account, beneficiary, amount, currency and purpose, and marks the capability used when the external consequence forms.

## Protected adapter

`harness/app/engines/capability_external_adapter.py`

The ordinary caller supplies the FlowSignal execution permit and attempted action, not an external payment capability.

Inside the existing protected consequence formation interval, the adapter:

1. requests a capability for the exact attempted action;
2. receives a one-time target-issued capability only if the target observes the required protected execution state; and
3. presents that capability to the target payment endpoint.

If the existing protected boundary refuses stale authority or action-binding mismatch, the capability-release hook is never reached.

## Executable qualification

`harness/tests/test_cbp003_route_capability_closure.py`

The qualification exercises:

- independently observable initial external state;
- direct payment without capability rejected;
- direct capability release using a valid but not-yet-consumed FlowSignal permit rejected;
- current-authority positive control through the protected capability route;
- authority-state change after historical permit issuance;
- stale permit refused before capability release;
- material action substitution refused before capability release;
- direct payment bypass without capability rejected;
- direct capability release using the stale historical permit rejected;
- current authority reacquisition;
- historical permit replay after reacquisition still refused;
- fresh current permit forming one external consequence through the same route; and
- replay of the used external capability rejected without a duplicate external effect.

## Dedicated workflow

`.github/workflows/cbp003-route-capability.yml`

Exact qualification command:

```text
pytest -q tests/test_cbp003_route_capability_closure.py
```

## Bounded closure statement

The intended qualification is deliberately narrower than universal non-bypassability.

The external test service still contains an administrative reset route, and a sufficiently privileged administrator can replace code, alter stores, change operating-system permissions or otherwise act outside the ordinary caller route. Those powers are outside the frozen CBP-003 closure proposition.

The proposition under test is whether the **named ordinary protected consequence route** requires a target-issued one-time capability whose release depends on successful entry into the current exact-action FlowSignal protected execution interval, and whether bypass/replay/substitution attempts fail without producing external effect.

No result classification is recorded in this note before the first executable run.
