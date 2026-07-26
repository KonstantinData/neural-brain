# AI Act Risk-Classification Assessment v1

- Status: Normative Foundation-governance template
- Contract: [`../architecture/contracts/ai-act-risk-classification-assessment-v1.json`](../architecture/contracts/ai-act-risk-classification-assessment-v1.json)
- Governing decisions: ADR-001, ADR-005, and ADR-018
- External reference: [Regulation (EU) 2024/1689](https://eur-lex.europa.eu/eli/reg/2024/1689/oj)

## Purpose and boundary

This is a versioned evidence template for a future, qualified, deployment-specific
EU AI Act risk-classification review. It does not provide legal advice,
classify any real deployment, establish applicability, determine an exemption,
or authorize processing, release, authority, or runtime operation.

Repository facts establish no deployment-specific intended purpose, affected
people, operator, jurisdiction, operational context, Annex I or Annex III fact,
or market availability. The Memory Core is a protected subsystem and does not
narrow ADR-018's complete cognitive-system boundary.

## Required assessment record

An accountable owner and qualified reviewer must create one immutable record per
artifact digest, proposed deployment, intended purpose, and Tenant/Area/Project
scope. It must include the reviewer, review date, current rationale, evidence,
expiry, controls, independent release reference, and every reassessment trigger
defined by the contract.

The review order is fixed: Article 5 prohibition evidence first; Article 6 and
Annex I, then Annex III high-risk evidence; Article 50 transparency evidence;
then any other or minimal-risk candidate. These labels are review-only labels.
They never enable deployment or compensate for missing safety, authority,
recognition, or release evidence.

## Fail-closed boundary

Any absent, unknown, stale, contradictory, or scope-mismatched input — including
the qualified reviewer, date, rationale, or reassessment trigger — makes the
record incomplete and blocks its deployment-specific release decision. A
qualified prohibition conclusion is a non-overridable release stop. A completed
template has no allow outcome and cannot override the Security Floor or any
Protected Control Plane gate.
