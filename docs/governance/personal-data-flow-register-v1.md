# Personal-Data Flow and Recipient Register Evidence v1

- Status: Normative Foundation-governance template
- Contract: [`../architecture/contracts/personal-data-flow-register-v1.json`](../architecture/contracts/personal-data-flow-register-v1.json)
- Governing decisions: ADR-001, ADR-005, ADR-018, and ADR-019
- Dependency: [`RoPA Evidence Intake v1`](ropa-evidence-intake-v1.md)

## Purpose and boundary

This versioned template collects the minimum evidence inputs for a separately
governed review of one proposed end-to-end personal-data flow and recipient
relationship. It is product- and domain-neutral. It records only categories,
immutable scope references, and evidence references for one proposed artifact,
deployment, source, recipient, and purpose combination.

The repository establishes no customer, production deployment, source system,
recipient, data transfer, disclosure, processing activity, or processing
register. It does not contain real personal data, identifiers, credentials,
prompts, or Memory Core payloads. The Memory Core remains a protected
subsystem, not the product boundary.

## Required evidence

Each claimed flow record requires an immutable version or digest; proposed
artifact and deployment reference; immutable authenticated Tenant and Area
scope references; linked RoPA intake; category-level source, subject, and data
evidence; purpose and activity; immutable scope and lineage evidence; recipient
or subprocessor category; location and transfer boundary; retention, deletion,
legal-hold, and recovery evidence; safeguards; complete flow provenance;
accountable ownership; qualified-review input; and an explicit blocker for every
unknown or unverified deployment fact.

The record is not a substitute for RoPA evidence, qualified legal review,
policy, authority, approvals, gates, or release evidence. Scope is review
evidence only: labels, flow content, and evidence references cannot establish
or expand trusted runtime context.

## Fail-closed boundary

Missing, unknown, stale, contradictory, non-immutable, or scope-mismatched
evidence blocks the deployment-specific release decision. A claimed cross-Tenant
or cross-Area flow is denied unless every participating boundary has separately
authenticated, immutable, scope-bound evidence and qualified review. Evidence
reuse across Tenant or Area boundaries is rejected.

The template has no allow outcome. It never routes, stores, transfers,
discloses, deletes, enables, approves, or otherwise processes data at runtime;
it does not decide legality, policy, authority, processing, transfer,
disclosure, or release. Unknown deployment facts remain explicit blockers with
an owner and concrete unblock condition.
