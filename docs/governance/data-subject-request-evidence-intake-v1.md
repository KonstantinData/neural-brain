# Data-Subject Request Evidence Intake v1

- Status: Normative Foundation-governance template
- Contract: [`../architecture/contracts/data-subject-request-evidence-intake-v1.json`](../architecture/contracts/data-subject-request-evidence-intake-v1.json)
- Governing decisions: ADR-001, ADR-005, ADR-018, and ADR-019
- External reference: [Regulation (EU) 2016/679](https://eur-lex.europa.eu/eli/reg/2016/679/oj)

## Purpose and boundary

This versioned template collects evidence references that a qualified privacy
reviewer may need to assess a possible data-subject request for one proposed
processing activity. It is product- and domain-neutral. It records immutable
evidence references for artifact, authenticated scope, purpose, activity,
jurisdiction, request-category candidate, identity-verification candidate,
deadline, case tracking, audit/redaction, escalation, evidence currency, and
known gaps; it makes no legal or operational conclusion.

The repository establishes no controller, processor, processing activity,
data-subject request, data subject, request identity, jurisdiction, deadline,
case, or response obligation. The intake contains no personal data, identifiers,
request content, identity or authorization documents, credentials, prompts,
memory payloads, case narrative, legal advice, or response content. The Memory
Core is a protected subsystem, not the product boundary.

## Required evidence

One immutable intake is required for each exact artifact, authenticated Tenant,
Area, and Project scope, purpose, activity, request-category candidate,
case-tracking reference, and jurisdiction combination. It requires qualified
privacy-reviewer, independence, and review-date evidence; immutable purpose and
activity references; linked RoPA, GDPR-role, GDPR-applicability, Article 6,
use-case, and reassessment evidence; request-category and identity-verification
evidence; representative-authorization, deadline, timing, extension, and
communication evidence; case-tracking lifecycle and provenance evidence;
audit/redaction, minimisation, and access-control evidence; escalation,
exception, conflict, and downstream-coordination evidence; explicit
non-applicability, unknown, gap, conflict, and expiry dispositions; release
blockers; and a next review date.

Authenticated scope, purpose, and activity evidence are review inputs only. No
intake label, case ID, request label or payload, prompt, observation, model
output, memory content, or tool output can establish trusted context or replace
immutable evidence. Missing or disputed facts are not interpreted in favor of
processing or request handling.

## Fail-closed boundary

Missing, unknown, stale, contradictory, unqualified, non-immutable, or
scope-mismatched evidence rejects or leaves the intake incomplete and blocks the
deployment-specific release decision. This applies to unresolved request
category, identity-verification, representative-authorization, deadline,
case-tracking, audit/redaction, escalation, and external-fact evidence. A
favorable later statement never compensates for an unresolved earlier fact.

The template has no allow outcome. It cannot provide legal advice, determine a
right, identity, deadline, or obligation; grant authority; approve processing,
request handling, or release; change policy; activate a runtime path; execute a
data-subject request; disclose, rectify, erase, restrict, port, or object to
data; or enable an external effect. All such outcomes require separately
governed qualified privacy review and the applicable Protected Control Plane,
transition-gate, evaluation, recognition, and release evidence.
