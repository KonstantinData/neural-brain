# ADR-007: Normative Goal and Action State Machines

- Status: Accepted
- Date: 2026-07-15
- Notion source: https://app.notion.com/p/39d1c1ac5ec08172af9bebb3791c34cf
- Notion page ID: `39d1c1ac-5ec0-8172-af9b-ebb3791c34cf`

## Context

Informal state logic cannot safely cover termination, verification,
cancellation, blocking, and crash recovery.

## Decision

Goal and Action state machines are versioned normative contracts. Unknown
states and transitions are denied by default. The contracts explicitly cover
quiescence, deadlines, `blocked_from_state`, `termination_disposition`, and the
resolution of `indeterminate` actions.

## Invariants and Constraints

- Unknown states and transitions are rejected.
- Quiescence is an explicit condition of state-machine behavior.
- Deadlines, cancellation, blocking, termination, and crash recovery are
  represented by the normative contracts rather than informal control flow.
- `blocked_from_state` and `termination_disposition` are explicit state data.
- An `indeterminate` action requires an explicit resolution path.

## Consequences

Every transition must name its permitted actors, guards, required evidence,
side effects, audit requirements, timeout behavior, and recovery tests.

## Relationship to the Architecture Directive

This decision specializes the architecture directive's protected Goal and
Action state requirements. The directive defines the system-wide boundary; this
ADR requires the corresponding state behavior to be explicit, versioned, and
default-deny.
