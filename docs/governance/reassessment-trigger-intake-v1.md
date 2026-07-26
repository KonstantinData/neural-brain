# Reassessment Trigger Intake v1

- Status: Normative Foundation-governance template
- Contract: [`../architecture/contracts/reassessment-trigger-intake-v1.json`](../architecture/contracts/reassessment-trigger-intake-v1.json)
- Governing decisions: ADR-001, ADR-005, and ADR-018

## Purpose and boundary

This is a versioned evidence intake for a reported change that requires a
separately governed deployment-specific reassessment. It does not poll external
sources, perform legal research, claim that a change has occurred, or provide
legal advice. It neither determines law, risk, applicability, policy, authority,
approval, release, nor runtime operation.

The repository has no concrete deployment, jurisdiction, operating entity,
legal source, qualified guidance, supplier, model, data flow, or release
decision. The Memory Core is a protected subsystem and does not narrow
ADR-018's complete cognitive-system boundary.

## Deterministic trigger intake

Each reported event creates one immutable evidence record and one linked tracked
reassessment work item for the exact artifact digest, deployment, intended
purpose, and authenticated Tenant/Area/Project scope. The record must preserve
the source evidence, before/after comparison (or explicit unknown), owner,
qualified reviewer or escalation recipient, due date or review trigger, prior
assessment references, and an open work item with a concrete next step.

The mandatory trigger vocabulary covers changes to legal or regulatory sources,
qualified guidance or review standards, model artifacts or behavior, suppliers
or supplier terms, intended purpose or enabled operations, data categories,
sources, recipients, locations or transfer boundaries, and deployment context,
jurisdiction, operator, affected people, or external-effect boundary.

An ambiguous, compound, unrecognized, or incompletely evidenced event remains
`unknown_and_escalate`. It cannot be silently ignored, deduplicated away, or
converted to an allow outcome.

## Tracked reassessment work

The linked item must name its accountable owner, qualified reviewer or
escalation recipient, `open`, `pending_qualified_reassessment`, or `blocked`
status, next step, due date or explicit review trigger, affected scope and
artifact, immutable evidence, and its release-blocker/non-bypass boundary.
Closing it requires separate qualified reassessment evidence and, where needed,
a separate release decision. Closure does not mutate protected runtime state or
grant authority.

## Fail-closed boundary

Missing, unknown, stale, contradictory, scope-mismatched, or unlinked trigger
and work-item evidence blocks a deployment-specific release decision that would
rely on the affected evidence. The record cannot waive, compensate for, reorder,
or satisfy Security Floor prohibitions, Protected Control Plane gates,
transition gates, independent verification, delivery-stage or recognition gates,
or release stops. It has no polling, authorization, release, or runtime path.
