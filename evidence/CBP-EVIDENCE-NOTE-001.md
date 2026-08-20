# FlowSignal™ Consequence-Boundary Evidence Note

**Document:** CBP-EVIDENCE-NOTE-001  
**Evidence covered:** CBP-001 → CBP-003  
**Status:** Consolidated evidence note  
**Date:** 20 August 2026  

> **Execute with Authority. Defend with Evidence.**

## 1. Purpose

FlowSignal addresses a narrow but important execution question:

**Immediately before a consequential action is formed, does the authority required for that exact action still exist and remain exercisable?**

The CBP sequence was built to test progressively stronger versions of that proposition rather than relying on architectural description alone.

This note consolidates the evidence earned by CBP-001, CBP-002 and CBP-003. It is written for buyers, architects, legal/risk teams and investors who need to understand both what has been demonstrated and where the present evidence boundary stops.

It is not a production certification, security accreditation or claim that every possible execution environment has been proven non-bypassable.

---

## 2. The execution problem

A workflow, agent or automated process may have been approved earlier and may still possess an instruction, token, permit or decision saying that an action can proceed.

That does not necessarily mean the institution still has authority to create the consequence when execution actually occurs.

Between approval and consequence formation, relevant conditions can change: authority can expire or be withdrawn, the requested action can be substituted, evidence can become stale, or the execution context can cease to match the conditions under which permission was granted.

The FlowSignal reference architecture therefore separates **prior permission** from **current execution authority**.

The evidence question is not simply whether FlowSignal can return ALLOW, ESCALATE or REFUSE. It is whether the mechanism at the execution boundary can make a consequential operation depend on current, exact-action authority and produce evidence of what happened.

---

## 3. Evidence method

Each CBP qualification follows the same discipline:

`freeze proposition → implement/expose mechanism → execute qualification → preserve result → state only the claim earned`

The proposition is frozen before its executable result is known. The first executable result is preserved whether it passes or fails. Passing test counts are not treated as proof by themselves; the evidence claim is bounded to the mechanism and observations actually exercised.

The qualifications were executed in GitHub Actions against their recorded pull-request states. GitHub Actions execution is **not described as independent verification**.

---

## 4. Evidence ladder

### CBP-001 — Represented consequence boundary

**Classification:** PASS  
**Boundary:** FlowSignal reference harness represented protected consequence

CBP-001 tested whether a previously valid exact-action execution permit could still form the represented protected consequence after authoritative runtime state changed.

The qualification established a fresh-authority positive control, then changed authority state after issuance of a second valid permit. Direct presentation of that historical permit to the protected-consequence boundary was denied as `DENIED_AUTHORITY_STATE_STALE`. The represented consequence did not form and a signed consequence receipt recorded non-formation.

The qualification also exercised beneficiary/amount action substitution, current-authority reacquisition, historical-permit replay after reacquisition and a fresh-current positive control.

**What CBP-001 earned:** within the reference harness, prior permission alone is insufficient to form the represented consequence after the authority state changes. Current authority and exact-action binding are checked at the protected consequence boundary.

**What it did not earn:** evidence that an independently observable external system was unchanged, or universal closure of external routes.

---

### CBP-002 — Independently observable external consequence

**Classification:** **CBP-002 — EXTERNAL CONSEQUENCE BOUNDARY: PASS (BOUNDED TO NAMED EXTERNAL TARGET AND INTEGRATION)**

CBP-002 moved the qualification beyond FlowSignal's internal represented consequence.

A separate HTTP consequence service ran as a separate operating-system process and owned its own ledger state. Its balances and transfers were queried through the service itself, so FlowSignal's internal `CONSEQUENCE_FORMED` record was no longer the sole observation.

A fresh current permit formed the intended external transfer as the positive control. A permit that became stale after authoritative state changed was then presented through the same protected external integration. FlowSignal denied the attempt and the external service's independently queried state remained unchanged.

Material action substitution was also refused, historical authority remained unusable after current authority was reacquired, and a fresh current permit formed exactly the intended external transfer.

**What CBP-002 earned:** for the named integration, a previously valid exact-action FlowSignal permit did not cause the independently observable external consequence after its underlying authority state changed.

**What it did not earn:** universal alternate-route closure. The sandbox retained an administrative reset capability outside the protected route.

---

### CBP-003 — Protected external route/capability closure

**Classification:** **CBP-003 — PROTECTED EXTERNAL ROUTE/CAPABILITY CLOSURE: PASS (BOUNDED TO NAMED TARGET, CAPABILITY AND INTEGRATION)**

CBP-003 addressed the next question: could the ordinary caller bypass the FlowSignal adapter and invoke the tested external consequence directly?

The external target was changed so its protected payment operation required a distinct target-issued, one-time consequence capability. A FlowSignal execution permit itself was not accepted as the external payment credential.

The target released the capability only after the protected execution path had established the required execution state for the exact action. Direct payment without the target capability failed. Direct capability release from a valid FlowSignal permit that had not passed through the protected execution interval also failed.

After authority changed, the historical permit was denied before capability release. A materially substituted action was denied before capability release. Reacquiring current authority did not rehabilitate the historical permit. Fresh current exact-action authority released a capability and formed the intended external consequence. Replaying the used one-time capability did not form a duplicate consequence.

**What CBP-003 earned:** within the named target/capability integration, the ordinary caller cannot form the tested protected external consequence merely by possessing or replaying a FlowSignal permit or by invoking the protected payment endpoint without the separately released consequence capability.

**What it did not earn:** closure against privileged administrators, operating-system owners, cloud providers, code replacement, credential-store compromise or other production infrastructure powers.

---

## 5. What changed across the three qualifications

| Evidence question | CBP-001 | CBP-002 | CBP-003 |
|---|---|---|---|
| Current authority checked before consequence formation | Demonstrated | Demonstrated | Demonstrated |
| Exact action binding exercised | Demonstrated | Demonstrated | Demonstrated |
| Stale historical permit refused | Demonstrated | Demonstrated | Demonstrated |
| Fresh-current positive control | Demonstrated | Demonstrated | Demonstrated |
| Consequence state observed outside FlowSignal internal consequence store | Not claimed | Demonstrated | Demonstrated |
| External state unchanged after stale attempt | Not claimed | Demonstrated | Demonstrated |
| Direct external protected operation requires separate consequence capability | Not claimed | Not claimed | Demonstrated for named route |
| Permit alone insufficient to obtain external consequence capability | Not claimed | Not claimed | Demonstrated for named route |
| One-time external capability replay cannot duplicate consequence | Not claimed | Not claimed | Demonstrated for named route |
| Universal privileged/admin route closure | Not claimed | Not claimed | Not claimed |
| Production bank/payment-rail control | Not claimed | Not claimed | Not claimed |

The progression matters. CBP-001 did not become stronger merely because more tests were added. CBP-002 changed what could be observed. CBP-003 changed the consequence architecture by making the named external payment operation dependent on a distinct capability released through the protected execution path.

---

## 6. What the evidence supports today

The strongest defensible consolidated statement is:

> **In the FlowSignal reference implementation and the named CBP external integrations, executable evidence demonstrates a consequence boundary at which current exact-action authority is re-established before the tested consequence can form. The evidence progresses from a represented consequence, to independently observable external state, to a bounded external route in which the consequence-forming capability is not available to the ordinary caller unless the protected execution path releases it.**

That statement is intentionally narrower than saying FlowSignal has proven universal non-bypassability or production control of every consequence route.

### For a buyer

The evidence demonstrates an implementable control pattern rather than only a governance concept: prior approval can be made insufficient for execution, current authority can be checked at the consequence boundary, and evidence can record why formation was permitted or refused.

A buyer would still need deployment-specific evidence showing how the pattern is integrated into the actual consequential system and how privileged routes are controlled.

### For an architect

The evidence demonstrates increasing claim/mechanism correspondence across three boundaries: local protected consequence, external observable consequence, and capability-gated external consequence.

The next architectural proof burden is deployment-specific: identity and credential isolation, privilege boundaries, failure modes, distributed transaction semantics, infrastructure trust and the actual external system's enforcement properties.

### For legal, risk and assurance teams

The evidence is designed to make a narrow proposition inspectable: what authority was relied upon, what exact action was attempted, whether relevant state changed, whether the consequence formed, and what evidence was retained.

It does not determine by itself what legal authority ought to exist. Policy, mandate and legal interpretation remain inputs to the authority model. The engineering question addressed here is whether the resulting authority condition can remain relevant at execution time rather than only at an earlier approval point.

### For an investor

The sequence provides evidence that the FlowSignal proposition can be expressed as executable infrastructure rather than only as a conceptual governance layer. Each qualification deliberately moved the enforcement boundary outward.

Commercial and production viability remain separate questions. The CBP evidence should therefore be read as technical de-risking of the core execution-boundary proposition, not as proof of market adoption or production readiness.

---

## 7. Current evidence boundary — deliberately not demonstrated

The CBP sequence does **not currently establish**:

- universal production non-bypassability;
- control of a real bank settlement or payment rail;
- absence of root, administrator, cloud-provider or equivalent privileged override;
- production IAM/process isolation;
- HSM/KMS-backed key isolation;
- resistance to compromise of the capability issuer or trusted execution-state stores;
- cross-provider distributed atomicity;
- production high availability, disaster recovery or operational resilience;
- production performance at enterprise scale;
- regulatory certification or legal approval;
- fitness for every workflow, system or deployment architecture.

These are not hidden qualifications. They identify the propositions that would require deployment-specific or future evidence if FlowSignal were integrated into a production consequence path.

---

## 8. Why stop the CBP sequence here for now

CBP-001 to CBP-003 now form a coherent evidence ladder. Automatically creating another laboratory qualification would risk increasing test volume without materially increasing the standing of the claim.

The more useful next step is external scrutiny and deployment discovery: expose this evidence ladder to buyers, system architects, legal/risk practitioners and technical reviewers, identify which remaining proposition matters in a real integration, and freeze the next qualification around that actual requirement.

Future evidence should therefore be driven by a specific deployment or falsifiable architectural gap — not by a desire to accumulate another passing test.

---

## 9. Canonical evidence record

### CBP-001

- Result: `evidence/CBP-001/CBP-001_RESULT.md`
- Frozen challenge: `evidence/CBP-001/CBP-001_CHALLENGE.md`
- Executable qualification: `harness/tests/test_cbp001_consequence_boundary_proof.py`
- GitHub Actions run: `32275844799`
- Merge commit: `1ef1852512defaeed0c2efbd305efaa9628a98ff`

### CBP-002

- Result: `evidence/CBP-002/CBP-002_RESULT.md`
- Frozen challenge: `evidence/CBP-002/CBP-002_CHALLENGE.md`
- Executable qualification: `harness/tests/test_cbp002_external_consequence_boundary.py`
- GitHub Actions first run: `32337280354`
- Merge commit: `cb89c5c4ae1edba4c3c38931ae53e94421d0732d`

### CBP-003

- Result: `evidence/CBP-003/CBP-003_RESULT.md`
- Frozen challenge: `evidence/CBP-003/CBP-003_CHALLENGE.md`
- Executable qualification: `harness/tests/test_cbp003_route_capability_closure.py`
- GitHub Actions first run: `32339656708`
- PR: `#18`
- Merge commit: `9d561b6c18704432d68b2f696a68fcf4f5fabf0e`

---

## 10. Review question

The useful review question is not whether FlowSignal has proven every possible execution environment.

It is:

> **Does the mechanism exercised by CBP-001 through CBP-003 earn the bounded consequence-boundary propositions stated here; and, for a real deployment, what is the next material proposition that should be frozen and tested?**

That keeps future scrutiny tied to falsifiable claim/mechanism correspondence.

---

**FlowSignal™**  
**Execute with Authority. Defend with Evidence.**
