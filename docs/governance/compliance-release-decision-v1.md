# Compliance Release-Decision Record v1

- Status: Normative Foundation-governance template
- Contract: [`../architecture/contracts/compliance-release-decision-v1.json`](../architecture/contracts/compliance-release-decision-v1.json)
- Governing decisions: ADR-001, ADR-005, and ADR-018

## Purpose and boundary

This versioned record template captures the evidence required for a future,
separately governed and signed compliance-release decision for one concrete
deployment. It does not provide legal advice, determine GDPR or EU AI Act
applicability or compliance, sign or verify a signature, assign authority,
approve release, or enable runtime operation.

The repository has no accepted customer or domain integration, concrete
deployment, qualified finding, signer, authority, or approval. Each is
therefore unknown and blocks productive enablement. The Memory Core remains a
protected subsystem and does not narrow the full cognitive-system boundary of
ADR-018.

## Required immutable record

One immutable record is required for each artifact digest, proposed deployment,
intended purpose, and authenticated Tenant/Area/Project scope. It must bind:

- decision status, effective window, accountable owner, and qualified
  independent reviewer;
- a signer authenticated-identity reference, signature-evidence reference, and
  signing timestamp;
- pre-existing authority snapshot, policy decision, and required approval
  evidence;
- for both GDPR and the EU AI Act, either a qualified approved finding or an
  explicit qualified non-applicability basis with scope, rationale, expiry, and
  reassessment trigger;
- RACI and independence evidence, reassessment-trigger work, release stops,
  evidence freshness, rationale, expiry, and next review date.

Missing, unknown, stale, contradictory, unqualified, or scope-mismatched
evidence makes the record incomplete and blocks productive enablement. Open
reassessment work, a release stop, an ambiguous decision, or an indeterminate
effect also blocks it pending authoritative reconciliation.

## Signed evidence is not authority

The contract only names evidence fields; it does not provide a signing or
signature-verification service. A signer reference does not create authority,
and Approval never creates missing authority. An `approved` record status is
evidence of a separately governed decision attempt, not a runtime allow.

It cannot waive, bypass, reorder, or satisfy a Security Floor prohibition,
Protected Control Plane or transition gate, independent verification,
evaluation or recognition gate, delivery-stage gate, kill switch, sandbox,
budget, resource claim, fence, atomic audit requirement, or release stop.
Each such control remains owned by its designated authority.

## Reassessment and immutability

Any change to the artifact, model supplier, purpose, environment, scope,
jurisdiction, data boundary, findings, non-applicability evidence, signer,
authority, approval, policy, controls, evidence freshness, incident, complaint,
misuse signal, or indeterminate effect requires reassessment. Corrections,
expiry, revocation, and reassessment create a new linked record; they never
rewrite or silently reactivate an existing one.

## Current applicability

The template is deliberately blocked pending concrete, scope-matched,
qualified evidence and separately governed signer, authority, approval, and
release controls. It neither makes a legal or compliance claim nor changes
protected runtime state.
