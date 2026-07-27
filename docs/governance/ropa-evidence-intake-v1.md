# RoPA Evidence Intake v1

- Status: Normative Foundation-governance template
- Contract: [`../architecture/contracts/ropa-evidence-intake-v1.json`](../architecture/contracts/ropa-evidence-intake-v1.json)
- Governing decisions: ADR-001, ADR-005, ADR-018, and ADR-019

## Purpose and boundary

This versioned template collects the deployment-specific evidence that an
accountable party may need for a separately governed record-of-processing-
activities review.  It is product- and domain-neutral.  It records category-
level facts and evidence references for one proposed artifact, authenticated
Tenant and Area scope, processing activity, and purpose combination.

The repository establishes no customer, production deployment, processing
activity, controller, processor, data-subject population, or record of
processing activities. The template does not contain real personal data,
identifiers, credentials, prompts, or memory payloads. The Memory Core remains
a protected subsystem, not the product boundary.

## Required evidence

The immutable intake requires the artifact and deployment reference; immutable
authenticated Tenant and Area scope references; purpose and activity; owner;
controller/processor evidence; categories of subjects and personal data;
recipients and subprocessors; transfers and locations; retention, deletion,
legal hold, and recovery; safeguards; data sources and flows; linked GDPR role,
applicability, and use-case evidence; qualified review; and every gap, expiry,
release stop, and next review date.

Scope is review evidence only. Neither a deployment label nor any intake
content can establish or broaden trusted runtime context. A record is required
for each proposed artifact, authenticated Tenant and Area scope, activity, and
purpose; evidence cannot cross a Tenant or Area boundary without a separately
scope-bound record and qualified review.

## Fail-closed boundary

Missing, unknown, stale, contradictory, scope-mismatched, non-immutable, or
cross-boundary evidence rejects or leaves the intake incomplete and blocks the
deployment-specific release decision. A personal-data or secret payload is
rejected and recorded as a data-minimization blocker. The intake has no allow
outcome and cannot provide legal advice, determine lawfulness, role,
applicability, transfer, or retention legality, grant authority, decide policy,
approve a release, activate processing, or enable any runtime capability.

The required evidence remains additive and non-compensatory: a favorable later
review never replaces a missing scope reference, processing fact, qualified
review, Protected Control Plane gate, or recognition and release evidence.
