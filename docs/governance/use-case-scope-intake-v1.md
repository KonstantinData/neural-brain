# Neural Brain Use-Case and Scope Intake v1

- Status: Normative foundation-governance template
- Contract: [`../architecture/contracts/use-case-scope-intake-v1.json`](../architecture/contracts/use-case-scope-intake-v1.json)
- Governing decisions: ADR-001, ADR-005, and ADR-018
- Current maturity: early Memory Core foundation

## Purpose

This versioned intake makes future productive-use proposals comparable without
introducing a product-domain default, deployment path, or runtime capability.
It covers the complete Neural Brain target: perception, cognition, memory,
models, learning, goals, planning, actions, and effects. The Memory Core stays
a protected subsystem and is not treated as the complete product boundary.

## Required pre-production evidence

Before a separately governed productive-use or deployment-specific release
decision, an accountable owner records every required contract field for one
immutable artifact and one proposed authenticated Tenant, Area, and Project
scope combination. The record must retain the intended-purpose version,
affected people, data and recipients, lifecycle and deletion evidence,
authority and oversight evidence, risks, evaluation evidence, release stops,
and expiry-bound references.

The proposed scope is review evidence only. It never supplies authenticated
runtime identity, broadens a database-bound Tenant, or creates principal,
authority, policy, approval, gate, or kill-switch state. A separately governed
runtime must obtain all trusted context independently.

## Fail-closed boundary

An unknown, missing, stale, scope-mismatched, contradictory, or unqualified
input blocks the relevant productive-use release decision. Each such gap is
recorded with an accountable owner, unblock condition, evidence expiry, and
next review step. A domain-specific extension remains blocked until an accepted
scoped integration decision exists.

This intake is neither legal advice nor a legal, regulatory, compliance,
security, privacy, capability, maturity, recognition, deployment, release, or
authority decision. It has no allow outcome and cannot activate runtime
operation, protected-state transitions, learning promotion, or external
effects. Qualified review, independent release governance, all Protected
Control Plane prerequisites, and non-compensatory recognition evidence remain
separate requirements.
