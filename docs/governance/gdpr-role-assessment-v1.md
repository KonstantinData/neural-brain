# GDPR Role Assessment v1

- Status: Normative foundation-governance template
- Contract: [`../architecture/contracts/gdpr-role-assessment-v1.json`](../architecture/contracts/gdpr-role-assessment-v1.json)
- Governing decisions: ADR-001 and ADR-018
- Current maturity: early Memory Core foundation; no customer or production deployment

## Purpose

This versioned template records the evidence inputs needed to assess each deployment-specific GDPR processing relationship. It keeps the possible role vocabulary explicit: controller, joint controller, processor, subprocessor, and recipient. It does not select any role for Neural Brain, a repository maintainer, a Tenant, a customer, or another party.

The complete Neural Brain target remains product- and domain-neutral. The Memory Core is a protected subsystem, not the product boundary. Assessment content cannot create authenticated scope, authority, policy, approval, protected-state permission, processing activation, or an external effect.

## Required future record

Before a deployment-specific release decision, the deployment accountable owner must create one immutable record for every processing relationship using all required fields in the machine-readable contract. Each record must identify the proposed deployment, exact artifact, parties, proposed role, processing and data-flow facts, evidence, gaps, and qualified applicable-law review reference.

Unknown, missing, stale, scope-mismatched, or contradictory input rejects the assessment or creates a release stop. An unknown downstream processor or subprocessor is a release stop; it is not an implicit approval.

## Current blocker

No concrete customer, deployment, processing relationship, party facts, or qualified review are present in this repository. Therefore no role conclusion can be made here.

- Owner: future deployment accountable owner.
- Unblock condition: complete relationship-specific assessment inputs and a qualified applicable-law review reference are available for separate governance and release evaluation.
- Next step: create one immutable assessment record per relationship before any deployment-specific release decision.

## Deliberate limits

This artifact is neither a legal opinion nor a GDPR role determination. It is not a finding of lawfulness, data-processing agreement, controller instruction, compliance certification, release approval, authority grant, policy decision, or runtime enablement. It introduces no personal-data processing, deployment, or new product capability.

Only separately applicable qualified legal review, accepted governance, and Protected Control Plane release mechanisms may make a deployment-specific decision after all mandatory evidence gates pass.
