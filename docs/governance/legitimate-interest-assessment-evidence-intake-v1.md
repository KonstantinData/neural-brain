# Legitimate-Interest Assessment Evidence Intake v1

- Status: Normative Foundation documentation preparation; operational task
  unfulfilled and blocked
- Contract: [`../architecture/contracts/legitimate-interest-assessment-evidence-intake-v1.json`](../architecture/contracts/legitimate-interest-assessment-evidence-intake-v1.json)
- Governing decisions: ADR-001, ADR-005, ADR-018, and ADR-019
- External reference: [Regulation (EU) 2016/679](https://eur-lex.europa.eu/eli/reg/2016/679/oj)

## Purpose and boundary

This versioned template defines documentation requirements for evidence that a
future qualified reviewer may need to assess a possible Article 6(1)(f) legitimate-interest
assessment for one proposed processing activity. It is product- and
domain-neutral. It records immutable evidence references for the artifact,
authenticated scope, purpose, activity, review, external facts, and known gaps;
it is not an intake-instance schema or executable validator, does not collect
evidence, and makes no legal conclusion.

The repository establishes no controller, processing activity, personal-data
processing, data-subject population, purpose, jurisdiction, legitimate interest,
necessity, balancing result, safeguard, objection outcome, or lawfulness. The
intake contains no personal data, identifiers, credentials, prompts, memory
payloads, legal advice, or legal conclusion.

## Required evidence

One immutable intake is required for each exact artifact, authenticated Tenant,
Area, and Project scope, purpose, activity, and jurisdiction combination. It
requires qualified reviewer and independence evidence; immutable purpose and
activity references; linked RoPA, GDPR-role, GDPR-applicability, Article 6,
use-case, and reassessment evidence; possible-interest, necessity, alternative,
the Article 6(1)(f) public-authority performance-of-tasks exclusion; balancing
that specifically weights children and other vulnerable persons; safeguard and
Article 21 objection evidence; and Article 21(2)-(3) direct-marketing objection
plus processing-stop evidence; external-fact
provenance and currency; explicit non-applicability, unknown, gap, conflict, and
expiry dispositions; release blockers; and a next review date. The conditional
public-authority and direct-marketing requirements use an exactly-one rule:
candidate evidence XOR a qualified, evidence-backed not-applicable disposition.
Placeholders, both branches, or neither branch keep the preparation incomplete.

Authenticated scope, purpose, and activity evidence are review inputs only. No
label, prompt, payload, observation, model output, memory content, or tool
output can establish trusted context or replace immutable evidence. Missing or
disputed facts are not interpreted in favor of processing.

## Fail-closed boundary

Missing, unknown, stale, contradictory, unqualified, non-immutable, or
scope-mismatched evidence rejects or leaves the intake incomplete and blocks the
deployment-specific release decision. The template has no allow outcome. It
cannot provide legal advice; determine legitimate interest, lawfulness,
necessity, alternatives, balancing, impact, safeguards, or objections; grant
authority; approve processing or release; change policy; activate runtime; or
make capability, maturity, recognition, or production claims.

Automated tests validate only this document's shape and preregistered invariant
constants. They do not validate a future intake instance, perform balancing, or
stop direct-marketing processing. The original S1-14.5 operational acceptance
remains unfulfilled and blocked pending typed instance validation, concrete
evidence, qualified review, and separately authorized operational controls.
