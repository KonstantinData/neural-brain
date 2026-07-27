# Article 6 Legal-Basis Evidence Intake v1

- Status: Normative Foundation-governance template
- Contract: [`../architecture/contracts/article-6-legal-basis-evidence-intake-v1.json`](../architecture/contracts/article-6-legal-basis-evidence-intake-v1.json)
- Governing decisions: ADR-001, ADR-005, ADR-018, and ADR-019
- External reference: [Regulation (EU) 2016/679](https://eur-lex.europa.eu/eli/reg/2016/679/oj)

## Purpose and boundary

This versioned template collects deployment-specific evidence that a qualified
reviewer may need to assess Article 6 legal-basis candidates and the related
necessity and proportionality facts for one proposed processing activity. It is
product- and domain-neutral. It records immutable evidence references for the
artifact, authenticated scope, purpose, activity, review, external facts, and
known gaps; it does not make any legal conclusion.

The repository establishes no controller, processing activity, personal-data
processing, data-subject population, purpose, jurisdiction, legal basis, or
lawfulness. The Memory Core is a protected subsystem, not the product boundary.
The intake contains no personal data, identifiers, credentials, prompts, memory
payloads, contract text, consent text, or legal advice.

## Required evidence

One immutable intake is required for each exact artifact, authenticated Tenant,
Area, and Project scope, purpose, activity, and jurisdiction combination. It
requires qualified reviewer and independence evidence; immutable purpose and
activity references; linked RoPA, GDPR-role, GDPR-applicability, use-case, and
reassessment evidence; Article 6 candidate evidence; necessity,
proportionality, alternatives, compatibility, minimisation, duration, and
safeguard rationale; external-fact provenance and currency; explicit
non-applicability, unknown, conflict, and gap dispositions; release blockers;
and a next review date.

Authenticated scope, purpose, and activity evidence are review inputs only. No
label, prompt, payload, observation, model output, memory content, or tool
output can establish trusted context or replace immutable evidence. External
facts and non-applicability assertions must remain explicit, sourced,
scope-bound, dated, qualified-review inputs; missing or disputed facts are not
silently interpreted in favor of processing.

## Fail-closed boundary

Missing, unknown, stale, contradictory, unqualified, non-immutable, or
scope-mismatched evidence rejects or leaves the intake incomplete and blocks
the deployment-specific release decision. A favorable later statement never
compensates for an unresolved earlier scope, purpose, activity, reviewer,
legal-basis, necessity, proportionality, external-fact, or control gap.

The template has no allow outcome. It cannot provide legal advice, choose or
validate a legal basis, determine lawfulness, necessity, proportionality,
compatibility, consent, or legitimate interests; it cannot grant authority,
approve processing or release, change policy, activate a runtime path, or
replace any Protected Control Plane, transition-gate, evaluation, recognition,
or independent-release evidence.
