# GPAI Provider-Obligation Applicability Assessment v1

- Status: Normative Foundation-governance template
- Contract: [`../architecture/contracts/gpai-provider-obligation-applicability-v1.json`](../architecture/contracts/gpai-provider-obligation-applicability-v1.json)
- Governing decisions: ADR-018, Architecture Directive v4.0, and the Neural Brain Recognition Standard
- External review reference: [Regulation (EU) 2024/1689](https://eur-lex.europa.eu/eli/reg/2024/1689/oj), Articles 3(63) and 53

## Purpose and boundary

This is a product- and domain-neutral, fail-closed evidence template for a
qualified, deployment-specific review of whether concrete distribution,
modification, branding, or fine-tuning facts require GPAI-provider-obligation
assessment. It is not legal advice. It cannot assign a GPAI-provider status,
determine whether an obligation applies, interpret licence terms, find
compliance, approve a deployment, grant authority, activate a model, or enable
runtime behavior.

The cited Regulation is a qualified-review reference only. Articles 3(63) and
53 must be considered against current, scope-matched facts by a qualified
reviewer; this repository does not assert their applicability or interpretation
for any entity, model, artifact, distribution, branding, modification, or
fine-tuning event.

## Required immutable evidence record

Create one record for each immutable model or GPAI-boundary artifact and each
concrete distribution and operating context. The record must link the exact
model-inference inventory record and capture all fields in
`assessment_template.required_fields`: accountable owner and qualified reviewer;
supplier/producer/downstream chain; verifiable availability, modification,
fine-tuning, brand, entity, terms, model-card, purpose, scope, jurisdiction,
and recipient facts; qualified-review evidence; open gaps; expiry; reassessment
work; and the separately governed compliance-release decision reference.

Repository visibility, a package, a branch, a repository name, a public URL, a
brand-like string, or an agent self-report do not prove distribution,
market-placement, putting into service, a legal entity, a GPAI model, provider
status, or an obligation. Mutable model tags are insufficient; immutable model
or artifact digests are mandatory.

## Fail-closed and reassessment behavior

Unknown, absent, stale, contradictory, scope-mismatched, or unverified
evidence blocks the affected deployment-specific release decision. The template
has no allow state. Any model, supplier, distribution, modification,
fine-tuning, branding, purpose, jurisdiction, or legal-source change must be
recorded through the separately governed reassessment-trigger intake with one
owned tracked work item before the affected deployment-specific release can
proceed.

This contract neither creates trusted runtime scope nor changes protected
state. It cannot bypass the Protected Control Plane, Security Floor, delivery
stages, evaluation gates, recognition gates, or independent release governance.
