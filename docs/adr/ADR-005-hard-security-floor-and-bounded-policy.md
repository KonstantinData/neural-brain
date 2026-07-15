# ADR-005: Hard Security Floor and Bounded Policy

- Status: Accepted
- Date: 2026-07-15
- Notion source: https://app.notion.com/p/39d1c1ac5ec0810fbb65c3ca4fea2686
- Notion page ID: `39d1c1ac-5ec0-810f-bb65-c3ca4fea2686`

## Amendment by ADR-015

The hard security floor governs memory identity and scope, provenance, access,
classification, retention, deletion, promotion, quarantine, and cross-area
transfer. Agent action authorization and emergency execution controls belong to
external consumers.

## Context

Approval and configurable policy cannot override prohibitions, authority,
isolation, or emergency controls.

## Decision

Hard security rules are implemented in code. Configurable policy parameters are
versioned, schema-validated, and bound to digests and expiry.

## Consequences

Policy changes require regression tests and cannot authorize a prohibited
memory operation.

## Invariants and Constraints

- Configurable policy cannot override the hard security floor.
- Approval cannot create missing authority or permit a prohibited action.
- Policy parameters are versioned and schema-validated.
- A policy decision is bound to its policy digest and expiry.
- Policy changes require regression evidence.

## Relationship to the Architecture Directive

This decision defines the security-floor boundary for the architecture
directive's policy engine, authority, approval, isolation, and emergency-control
requirements.
