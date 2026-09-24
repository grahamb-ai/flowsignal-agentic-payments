# FS-RAI R2 Authority Resolution Architecture

**Status:** ARCHITECTURE DESIGN — POST HOSTILE-SURFACE FREEZE  
**Date:** 24 September 2026

## 1. Objective

Replace the current field-by-field R2 remediation with a coherent authority-resolution architecture capable of representing the frozen hostile failure surface without moving Runtime Authority Infrastructure upstream into policy creation or downstream into consequence control.

The architecture answers one question:

> Does a valid, current and coherent chain of institutionally grounded authority reach this exact protected operation at the authority-relevant commitment point?

## 2. Architectural overview

```text
INSTITUTIONAL TRUST / AUTHORITY ROOTS
                 |
                 v
        AUTHORITY SEMANTICS
                 |
                 v
      REQUIRED PROPOSITION SET
                 |
                 v
 AUTHORITY PROPOSITION EVIDENCE
                 |
                 v
       AUTHORITY DERIVATION
                 |
                 v
    AUTHORITY RESOLUTION CONTEXT
                 |
                 v
        EFFECTIVE AUTHORITY
                 |
          +------+------+
          |             |
          v             v
   AUTHORITY USAGE   EXECUTION
      STATE          CORRESPONDENCE
          |             |
          +------+------+
                 v
          DETERMINATION
                 |
                 v
   AUTHORISED EXECUTION CONSTRAINT
                 |
                 v
     FINAL BIND REVALIDATION
                 |
                 v
 AUTHORITY-RELEVANT COMMITMENT
```

Institutional roots and governing policy originate outside RAI. RAI resolves their current applicability and correspondence to the protected operation.

## 3. Primitive A — Authority Semantics

First-class object: `AuthoritySemanticsSet`.

Minimum conceptual content:

```text
semantics_set_id
version
authoritative_source_id
source_competence_id
valid_from / valid_until
supersession / applicability state
protected_operation_class
required_proposition_schema
derivation_rule_set_id
delegation_semantics_id
approval_semantics_id
parameterisation_semantics_id
usage_semantics_id
topology_semantics_id
revalidation_semantics_id
```

Purpose:
- identify what rules govern;
- establish required propositions;
- define composition/derivation;
- define approval, parameter, usage and revalidation meaning;
- prevent semantic downgrade, equivocation and policy rollback.

A semantics document being authentic does not establish that it is applicable.

## 4. Primitive B — Authority Proposition Evidence

First-class object: `AuthorityPropositionEvidence`.

```text
evidence_id
proposition_id
semantic_definition_id
subject_binding
purpose_context_binding
observed_value
authoritative_source_id
source_competence_id
source_version
observed_at
valid_from / valid_until
supersession_marker / watermark
finality_state where applicable
usage/replay semantics where applicable
provenance/integrity material
```

Every authority-material premise must be grounded either in a coherent source cut or in independently authoritative evidence whose compatibility can be established.

Request-side assertions are not authoritative merely because they are supplied.

## 5. Primitive C — Authority Derivation

First-class objects:
- `AuthorityDerivationGraph`
- `EffectiveAuthorityScope`

Graph nodes may represent roots, grants, restrictions, propositions, roles, approvals and derived scopes.

Edges bind the applicable derivation rule.

Required properties include:
- no circular manufacture of normative authority;
- child authority cannot exceed parent authority;
- restrictions accumulate according to governing semantics;
- parallel grants cannot be spliced unless composition semantics permit it;
- derivation rules themselves have identity, provenance and applicability;
- dependency closure is preserved for derived propositions;
- equal visible values do not make evidence inputs authority-equivalent.

## 6. Primitive D — Authority Resolution Context

First-class object: `AuthorityResolutionContext`.

This is NOT required to be one physical database transaction.

```text
context_id
semantics_set_id
authority_subject
protected_operation_class
authority_epoch
authority_scope_owner_id
authority_scope_ownership_epoch
source_topology_generation
evidence_member_ids
derivation_graph_id
source_version_vector / compatible cut
watermarks / fences
resolved_at
validity horizon
compatibility_rule_id
```

Purpose:
establish that individually valid authority material belongs to one compatible authority decision.

It represents NOW as a multidimensional authority state rather than merely a wall-clock timestamp.

Final bind revalidation checks whether the context remains applicable to the proposed operation.

## 7. Primitive E — Authority Usage

First-class objects:
- `AuthorityUsagePolicy`
- `AuthorityUsageReservation`
- `AuthorityUsageDisposition`

```text
usage_policy_id
authority_scope_id
mode: single / bounded / aggregate / renewable / windowed / other
scope_key
window_id
capacity
reservation_id
authority_exercise_id
execution_attempt_id
reserved_amount_or_units
state
disposition_rule_id
```

R2 defines the meaning of usage semantics.

R4 implements atomic reservation, consumption, release, quarantine and aggregate enforcement.

Disposition may depend on protected-execution or consequence evidence without collapsing those evidence layers into authority evidence.

UNRESOLVED outcome must not automatically mean non-formation.

## 8. Primitive F — Execution Correspondence

First-class objects:
- `ProtectedOperation`
- `AuthorityOperationBinding`
- `AuthorisedExecutionConstraint`

The binding covers every authority-material property required by the applicable semantics, including where relevant:

```text
principal
actor/mechanism
action
target
source account
beneficiary identity/account
amount
currency
purpose
mandate
parameter envelope
final instantiated parameters
route/executor
approval binding
authority exercise
execution attempt
instruction identity
```

A valid authority graph is insufficient unless it reaches the concrete operation crossing the commitment boundary.

## 9. Determination object

`AuthorityDetermination` references rather than duplicates the six primitives:

```text
determination_id
resolution_context_id
effective_authority_scope_id
usage_policy/reservation reference
protected_operation_id
authority_operation_binding_id
decision
reason_codes
resolved_at
valid_until
integrity material
```

Product labels may remain ALLOW / ESCALATE / REFUSE. They are not architectural primitives.

## 10. Final bind

The final protected boundary verifies:

1. determination integrity;
2. exact protected-operation correspondence;
3. current resolution-context applicability;
4. current semantics/topology/ownership generation as required;
5. authority-subject and derivation standing as required by semantics;
6. usage reservation/current availability where consumptive;
7. approval/parameter-instantiation correspondence where applicable;
8. route/executor correspondence;
9. attempt/exercise lineage;
10. expiry and replay state.

Only then may the authorised execution constraint permit authority-relevant commitment.

## 11. Reconciliation and re-entry

After RAI END, downstream evidence may establish:
- commitment formed;
- commitment demonstrably did not form;
- outcome remains unresolved;
- later reconciliation/finality.

Where usage semantics depend on this evidence, a competent reconciliation source may update Authority Usage state according to the governing disposition rule.

That update is evidence/state for a later authority exercise. It does not retroactively move the original RAI END.

## 12. Remediation implementation slices

Implement in this order:

### A. Core model
Create the six first-class domain structures and canonical identities.

### B. Authoritative adapters
Move request-side mutable premises behind explicit authoritative evidence adapters. Unknown/unavailable authoritative state fails closed where required.

### C. Resolution engine
Build required-proposition completeness, evidence compatibility and derivation evaluation into one Authority Resolution Context.

### D. Determination + constraint
Issue a determination referencing the frozen context and exact protected operation; bind it into the execution constraint.

### E. Final-bind revalidation
Revalidate the authority-relevant context and exact operation at commitment.

### F. R5 lineage
Introduce explicit authority_exercise_id and execution_attempt_id.

### G. R3 approval
Implement approval as authority proposition/derivation semantics, not a boolean.

### H. R4 usage
Implement atomic reservation/consumption/release/quarantine and aggregate semantics.

## 13. Anti-patterns prohibited

Do not remediate by:
- adding one receipt field per Frankie failure;
- trusting request-side booleans as authority facts;
- treating one global version integer as coherent authority state;
- treating signatures as proof of applicability;
- treating source identity as source competence;
- treating freshness as currentness;
- treating a new timestamp/signature as revalidation;
- treating approval count as authority;
- treating envelope compliance as authority to instantiate;
- treating missing success evidence as non-formation;
- using one global leader/fence where authority is legitimately scoped;
- requiring one giant physical distributed transaction where compatible evidence cuts suffice.

## 14. Verification rule

No frozen R2 failure is closed by this document.

Closure requires implementation plus executable evidence. The historical first failures remain preserved.

**End of R2 Authority Resolution Architecture.**
