# Article 9 Special-Category Evidence Intake v1

- Status: Normative Foundation documentation preparation; operational task
  unfulfilled and blocked
- Contract: [`../architecture/contracts/article-9-special-category-evidence-intake-v1.json`](../architecture/contracts/article-9-special-category-evidence-intake-v1.json)
- Governing decisions: ADR-001, ADR-005, ADR-018, and ADR-019
- External reference: [Regulation (EU) 2016/679](https://eur-lex.europa.eu/eli/reg/2016/679/oj)

## Purpose and boundary

This versioned template defines documentation requirements for evidence that a
future qualified reviewer may need to assess potential Article 9 special-category condition
candidates, related safeguards, and an explicit Article 10 criminal-offence
data disposition for one proposed processing activity. It is product- and
domain-neutral. It records immutable evidence references for the artifact,
authenticated scope, purpose, activity, jurisdiction, review, external facts,
and known gaps. It is not an intake-instance schema or executable validator,
does not collect evidence, and makes no legal conclusion.

The repository establishes no controller, processing activity, personal-data
processing, data-subject population, data category, special-category
classification, Article 9 condition, Article 10 disposition, purpose,
jurisdiction, safeguard, retention period, rights process, transfer fact, or
lawfulness. The Memory Core is a protected subsystem, not the product boundary.
The intake contains no personal data, special-category values, criminal-offence
data, identifiers, credentials, prompts, memory payloads, contract text,
consent text, or legal advice.

## Required evidence

One immutable intake is required for each exact artifact, authenticated Tenant,
Area, and Project scope, purpose, activity, and jurisdiction combination. It
requires qualified reviewer and independence evidence; immutable purpose and
activity references; linked RoPA, GDPR-role, GDPR-applicability, Article 6,
use-case, and reassessment evidence; special-category and Article 9 candidate
evidence or a qualified, evidence-backed not-applicable disposition. Article 10
candidate evidence must address official-authority control or authorization by
Union or Member State law, appropriate safeguards, and comprehensive-register
control under official authority where applicable. The template also requires necessity,
minimisation, retention, deletion, data-subject-rights, recipient, processor,
location, and transfer evidence; external-fact provenance and currency;
explicit non-applicability, unknown, conflict, gap, and blocker dispositions;
release blockers; and a next review date. Each conditional requirement uses an
exactly-one rule: candidate evidence XOR a qualified not-applicable
disposition. Blank, TODO, TBD, pending, unknown-as-not-applicable,
illustrative, unresolved, and non-resolving references satisfy neither branch;
both or neither branches keep the preparation incomplete.

Authenticated scope, purpose, and activity evidence are review inputs only. No
label, prompt, payload, observation, model output, memory content, or tool
output can establish trusted context or replace immutable evidence. Unknown,
stale, contradictory, unqualified, or scope-mismatched condition, safeguard,
Article 10, or external facts are explicit blockers and are never silently
interpreted in favor of processing.

## Fail-closed boundary

Missing, unknown, stale, contradictory, unqualified, non-immutable, or
scope-mismatched evidence rejects or leaves the intake incomplete and blocks
the deployment-specific release decision. A favorable later statement never
compensates for an unresolved earlier scope, purpose, activity, jurisdiction,
reviewer, Article 9, Article 10, safeguard, minimisation, retention, rights,
transfer, external-fact, or control gap.

Automated tests validate only this document's shape and preregistered invariant
constants. They do not validate a future intake instance or prove a qualified
review. The original S1-14.4 operational acceptance remains unfulfilled and
blocked pending typed instance validation, concrete evidence, qualified review,
and separately authorized runtime enforcement.

The template has no allow outcome. It cannot provide legal advice, select or
validate an Article 9 condition, decide an Article 10 disposition, determine
lawfulness or special-category classification, grant authority, approve
processing or release, change policy, activate a runtime path, or replace any
Protected Control Plane, transition-gate, evaluation, recognition, or
independent-release evidence. It creates no Article 10 register or
official-authority control and makes no implementation, product-capability,
maturity, recognition, safety, or production-autonomy claim.
