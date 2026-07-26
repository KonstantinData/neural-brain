# Compliance RACI and Approval-Authority Assessment v1

- Status: Normative Foundation-governance template
- Contract: [`../architecture/contracts/compliance-raci-assessment-v1.json`](../architecture/contracts/compliance-raci-assessment-v1.json)
- Governing decisions: ADR-001, ADR-005, and ADR-018

## Purpose and boundary

This is a versioned evidence template for a future qualified,
deployment-specific responsibility, approval-authority, independence, and
escalation review. It does not provide legal advice, assign any real person or
organization, determine a provider or deployer, grant authority, approve a
deployment, or enable a runtime operation.

Repository facts establish no concrete provider, deployer, privacy, security,
product, incident, release authority, operating entity, deployment, or
delegation. The Memory Core is a protected subsystem and does not narrow
ADR-018's complete cognitive-system boundary.

## Required assessment record

An accountable owner and qualified governance reviewer must create one
immutable record per artifact digest, proposed deployment, intended purpose,
authenticated Tenant/Area/Project scope, and responsibility-assignment version.
For each of these dimensions the record names an accountable owner, responsible
function, consulted and informed functions, evidence reference, scope, and
expiry:

- provider;
- deployer;
- privacy;
- security;
- product;
- incident; and
- release.

Every proposed approval additionally cites its pre-existing authenticated
authority source, immutable scope, operation, policy decision, approval type,
expiry, and independent evidence. The record proves neither authority nor an
approval outcome; it exposes absent or conflicting evidence as a release
blocker.

## Independence and escalation

The assessment records evidence for requester/approver and policy-author/sole-
policy-activator separation, plus the executor/independent-verifier,
learning-candidate-producer/model-promoter, Brain/safety-supervisor,
Brain/kill-switch, planner/executor, and reconciliation/human-incident-
resolution boundaries.

Escalation is a documented concern and next-review path only. It cannot waive,
bypass, reorder, or satisfy a Security Floor prohibition, a Protected Control
Plane gate, independent review, a delivery-stage or recognition gate, or a
release stop. An indeterminate external effect remains subject to authoritative
reconciliation before retry or resource release.

## Fail-closed boundary

Missing, unknown, stale, contradictory, scope-mismatched, expired, unavailable,
or non-independent responsibility, authority, approval, or escalation evidence
makes the assessment incomplete and blocks the deployment-specific release
decision. Approval never creates missing authority. A completed template has no
allow path and cannot override gates, policy, qualified review, or the Security
Floor.

Only separately authorized release governance and all applicable Protected
Control Plane, transition-gate, evaluation, recognition, and evidence
requirements may decide a concrete deployment. This template cannot activate a
runtime path.
