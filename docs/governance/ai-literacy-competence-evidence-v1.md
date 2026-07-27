# AI Literacy and Competence Evidence v1

- Status: Normative Foundation-governance template
- Contract: [`../architecture/contracts/ai-literacy-competence-evidence-v1.json`](../architecture/contracts/ai-literacy-competence-evidence-v1.json)
- Governing decisions: ADR-001, ADR-005, and ADR-018

## Purpose and boundary

This versioned, product- and domain-neutral template defines curriculum and
de-identified competence-evidence inputs for future people affected by a
Neural Brain deployment. It covers developers, operators, approvers,
independent verifiers, support, and affected staff. It does not claim that any
real person was trained or competent, store HR personal data, make an
employment or legal decision, grant authority, approve a deployment, or enable
a runtime operation.

The current repository contains neither a concrete deployment nor an employer,
learner population, training provider, qualification record, or applicable
legal duty. The protected Memory Core remains an internal subsystem and cannot
narrow ADR-018's complete cognitive-system product boundary.

## Curriculum and evidence record

Every role category receives the shared curriculum: maturity and scope limits,
the two-plane boundary, authenticated scope, protected gates and fail-closed
behavior, audit and indeterminate-effect reconciliation, human oversight,
privacy, and recognition/delivery-stage limits. Role-specific material covers
secure changes for developers, incident and kill-switch handling for operators,
pre-existing authority for approvers, outcome evidence and independence for
verifiers, safe escalation for support, and intended-use limits for affected
staff.

An immutable record binds one curriculum version, role category, intended
purpose, proposed deployment, authenticated Tenant/Area/Project scope, and
de-identified evidence reference (or explicit absence). Required evidence also
records assessment method, expiry, next review or trigger, gaps, owner, next
step, and a linked release/operation blocker. It is evidence only: a curriculum
or record does not prove that a real person is trained, competent, authorized,
available, or supervised.

Personnel identity and performance records belong only in an independently
governed system. This repository stores no HR personal data. A competence
record never creates authority, delegation, approval, policy activation,
authenticated identity, scope, Gate ownership, or runtime access.

## Separation and refresh

Competence evidence cannot collapse protected separation: requester versus
elevated-risk approver, executor versus independent verifier, policy author
versus sole policy activator, and Brain runtime versus kill-switch authority
remain separate. A completed learning activity does not remove those controls.

Expiry and material changes require a new, separately governed reassessment
work item. Changes include intended purpose, enabled operation, artifact/model,
supplier, data boundary, policy, Security Floor, incidents, responsibility,
deployment scope, and qualified-review requirements. The refresh record
preserves prior evidence and cannot alter authority, approvals, policy, Gates,
security controls, identity, scope, runtime permission, protected state, or
release state.

Missing, unknown, stale, expired, contradictory, scope-mismatched, or
non-independent evidence fails closed and blocks the affected role-dependent
release or operation decision. The template has no allow outcome and cannot
waive, compensate for, reorder, or satisfy a Security Floor prohibition,
Protected Control Plane gate, transition gate, independent verification,
delivery-stage gate, recognition gate, release stop, or separately required
approval.
