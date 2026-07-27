# Consent Evidence Intake v1

- Status: Normative Foundation documentation preparation; operational task
  unfulfilled and blocked
- Contract: [`../architecture/contracts/consent-evidence-intake-v1.json`](../architecture/contracts/consent-evidence-intake-v1.json)
- Governing decisions: ADR-001, ADR-005, ADR-018, and ADR-019
- External reference: [Regulation (EU) 2016/679](https://eur-lex.europa.eu/eli/reg/2016/679/oj)

## Purpose and boundary

This versioned template defines documentation requirements for evidence that a
future qualified reviewer may need to assess a possible consent when consent is used for one proposed
processing activity. It is product- and domain-neutral. It records immutable
evidence references for artifact, authenticated scope, purpose, activity,
data-subject category, processing context, reviewer, evidence currency, and
known gaps. It is not an intake-instance schema or executable validator, does
not collect consent evidence, and makes no legal conclusion.

The repository establishes no controller, processing activity, consent
interaction, data-subject population, jurisdiction, consent condition, or
lawfulness. The intake contains no personal data, identifiers, consent text or
records, credentials, prompts, memory payloads, contract text, or legal advice.
The Memory Core is a protected subsystem, not the product boundary.

## Required evidence

One immutable intake is required for each exact artifact, authenticated Tenant,
Area, and Project scope, purpose, activity, processing context, and jurisdiction
combination. It requires qualified reviewer and independence evidence; immutable
purpose and activity references; linked RoPA, GDPR-role, GDPR-applicability,
Article 6, use-case, and reassessment evidence; possible consent-artifact and
purpose/activity binding evidence; data-subject and context evidence; voluntary,
informed, specific, unambiguous, granular, language, accessibility, and
record-integrity evidence; Article 7(1) controller demonstrability; Article
7(2) distinguishable, intelligible, easily accessible, clear and plain-language
request presentation; Article 7(3) withdrawal notice, accessibility,
prior-lawfulness and as-easy-as-giving evidence; Article 7(4) service
conditionality and contract-performance necessity; Article 8 child
information-society age, parental authorization and reasonable verification;
Article 9(2)(a) explicit consent and any Union or Member State law prohibition;
expiry/refresh evidence; withdrawal accessibility and
downstream stop, deletion, and reconciliation evidence; explicit
non-applicability, unknown, conflict, gap, and expiry dispositions; release
blockers; and a next review date. Each conditional requirement uses an
exactly-one rule: candidate evidence XOR a qualified, evidence-backed
not-applicable disposition. Placeholders, both branches, or neither branch keep
the preparation incomplete.

The outer consent-basis branch is resolved first. When consent applies,
Article 7(1) demonstrability and Article 7(3) withdrawal evidence are mandatory
candidate evidence and cannot be replaced by N/A. When consent is qualified not
applicable, every consent-specific candidate-evidence field must be absent and
every conditional field must be absent or carry a consistent qualified N/A
disposition. Article 7(2), Article 7(4), Article 8, and Article 9(2)(a) are
evaluated only inside the consent-applies branch against explicit predicates:
true requires candidate evidence, false requires qualified N/A, and unknown,
both, neither, placeholder, or predicate/evidence mismatch blocks release.

The contract preregisters five documentation branches: coherent
consent-applies; consent-applies missing mandatory Article 7 evidence; coherent
consent-N/A; inconsistent consent-N/A with candidate evidence; and an unresolved
or inconsistent outer/conditional branch. These are documentation outcomes
only and never legal, runtime, or release decisions.

Authenticated scope, purpose, and activity evidence are review inputs only. No
label, prompt, payload, observation, model output, memory content, or tool
output can establish trusted context or replace immutable evidence. Missing or
disputed facts are not silently interpreted in favor of processing.

## Fail-closed boundary

Missing, unknown, stale, contradictory, unqualified, non-immutable, or
scope-mismatched evidence rejects or leaves the intake incomplete and blocks the
deployment-specific release decision. This also applies to unresolved possible
consent-condition, language/accessibility, integrity, expiry/refresh,
withdrawal, downstream stop, deletion, and reconciliation evidence. A favorable
later statement never compensates for an unresolved earlier fact.

Consent-applies without Article 7(1) or Article 7(3) candidate evidence is
incomplete. Consent-N/A with any consent-specific candidate evidence, both or
neither outer branches, and any conditional predicate/evidence mismatch are
rejected as incoherent.

The template has no allow outcome. It cannot provide legal advice, validate
consent, determine lawfulness or a legal basis, grant authority, approve
processing or release, change policy, activate a runtime path, trigger a
withdrawal workflow, stop processing, delete data, or enable any external
effect. All such outcomes require separately governed qualified review and the
applicable Protected Control Plane, transition-gate, evaluation, recognition,
and release evidence.

Automated tests validate only this document's shape and preregistered invariant
constants. They do not validate a future intake instance, prove consent, execute
withdrawal, or stop downstream processing. The original S1-14.6 operational
acceptance remains unfulfilled and blocked pending typed instance validation,
concrete evidence, qualified review, and separately authorized runtime controls.
