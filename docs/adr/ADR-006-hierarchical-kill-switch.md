# ADR-006: Hierarchical Kill Switch

- Status: Accepted
- Date: 2026-07-15
- Notion source: https://app.notion.com/p/39d1c1ac5ec081aa8bcad2746d30fac2
- Notion page ID: `39d1c1ac-5ec0-81aa-8bca-d2746d30fac2`

## Context

Autonomous execution requires a cheap, race-safe stop mechanism.

## Decision

Kill switches exist at global, tool, and goal scope. Each switch has the states
`enabled`, `drain`, and `disabled`. The runtime checks applicable switches at
prepare, commit, and dispatch.

## Consequences

Settlement and reconciliation continue during drain. Agents cannot re-enable a
kill switch.

## Invariants and Constraints

- Applicable global, tool, and goal kill switches are checked at prepare,
  commit, and dispatch.
- Settlement and reconciliation continue during drain.
- Agents cannot re-enable a kill switch.
- Kill-switch enforcement is race-safe.

## Relationship to the Architecture Directive

This decision supplies the stop-control contract for the architecture
directive's external-effect authorization, runtime checks, guardian behavior,
settlement, and reconciliation requirements.
