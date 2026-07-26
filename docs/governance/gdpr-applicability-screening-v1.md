# GDPR Applicability Screening v1

- Status: Normative Foundation-governance template
- Contract: [`../architecture/contracts/gdpr-applicability-screening-v1.json`](../architecture/contracts/gdpr-applicability-screening-v1.json)
- Governing decisions: ADR-001, ADR-005, and ADR-018
- External reference: [Regulation (EU) 2016/679](https://eur-lex.europa.eu/eli/reg/2016/679/oj)

## Purpose and boundary

This versioned evidence template supports qualified, deployment-specific GDPR
screening. It records Article 2 and 3 applicability facts; Article 9
special-category and Article 10 criminal-data facts; Article 22 profiling and
solely automated individual-decision facts; and Article 35 DPIA risk triggers.
It does not provide legal advice, determine whether GDPR or any Article applies,
determine lawfulness or a DPIA requirement, or authorize processing, release,
authority, or runtime operation.

Repository facts establish no controller, processor, processing operation,
data-subject population, jurisdiction, intended purpose, or deployment. The
Memory Core is a protected subsystem and does not narrow ADR-018's complete
cognitive-system boundary.

## Required screening record

An accountable owner and qualified reviewer must create one immutable record per
artifact digest, proposed deployment and processing operation, intended purpose,
and Tenant/Area/Project scope. The record identifies applicable-article
candidates for qualified review only, risk triggers, required assessments,
release blockers, current rationale, verified evidence references, and the next
review date.

The order is fixed: completeness and provenance first; Article 2 and 3 facts;
Article 9 and 10 data facts; Article 22 profiling/automated-decision facts;
Article 35 DPIA triggers; then any remaining controls, transfer evidence, and
article candidates. A favorable later screen never replaces an unresolved
earlier fact or another security, authority, recognition, or release gate.

## Fail-closed boundary

Any absent, unknown, stale, contradictory, or scope-mismatched input — including
the qualified reviewer, date, rationale, verified evidence reference, or
reassessment trigger — makes the record incomplete and blocks its
deployment-specific release decision. The template has no allow outcome and
cannot override the Security Floor, a Protected Control Plane gate, qualified
privacy review, or independent release governance.
