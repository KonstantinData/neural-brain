# ADR-008: Atomic Action Preparation and Commit

- Status: Accepted
- Date: 2026-07-15
- Notion source: https://app.notion.com/p/39d1c1ac5ec081f89fb1c846ca5f942d
- Notion page ID: `39d1c1ac-5ec0-81f8-9fb1-c846ca5f942d`

## Context

Authority, approval, budget reservations, and resource claims must remain
consistent and atomic when an action is prepared and committed.

## Decision

Action preparation uses two phases. Prepare validates authority, approval,
budget availability, and resource claims. Commit revalidates those conditions
and commits all resulting claims and reservations atomically, or rolls all of
them back.

## Invariants and Constraints

- Prepare validates authority, approval, budget, and resource claims together.
- Commit revalidates the conditions established during prepare.
- Commit either persists all required claims and reservations or persists none
  of them.
- Partial claims and unaccounted reservations are forbidden.

## Consequences

Failure-injection evidence must prove that no failure boundary can leave
partial claims or unaccounted reservations.

## Relationship to the Architecture Directive

This decision specializes the architecture directive's authorization, approval,
budget, and resource prerequisites for external effects. It makes their
prepare-and-commit relationship atomic without weakening any prerequisite.
