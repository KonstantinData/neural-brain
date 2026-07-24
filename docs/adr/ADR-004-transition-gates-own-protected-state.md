# ADR-004: Transition Gates Own Protected State

- Status: Superseded by ADR-015
- Date: 2026-07-15
- Notion source: https://app.notion.com/p/39d1c1ac5ec081679210dcd3e65beadd
- Notion page ID: `39d1c1ac-5ec0-8167-9210-dcd3e65beadd`
- Authority: historical
- Theme: protected_control
- Applies to stages: none
- Supersedes: none
- Superseded by: ADR-015
- Amends: none
- Amended by: none

## Supersession

ADR-015 removes Goal and Action state from the Neural Brain boundary. External
consumers own those state machines. Memory state still requires an owning typed
mutation boundary, but this three-gate agent-runtime decision is historical and
is not implementation authority.

## Context

Distributed responsibilities create bypasses around protected state changes.

## Decision

The Goal, Action, and Memory Transition Gates are the only writers of their
protected state. Planners, executors, verifiers, guardians, and models submit
typed requests to those gates.

## Consequences

APIs and database privileges must make direct mutation of protected state
technically impossible.

## Invariants and Constraints

- Only the owning transition gate writes protected Goal, Action, or Memory
  state.
- Planners, executors, verifiers, guardians, and models cannot write protected
  state directly.
- Calls into a transition gate use typed requests.
- API and database boundaries enforce the same writer restriction.

## Relationship to the Architecture Directive

This decision establishes the writer-ownership rule used throughout the
architecture directive for state machines, runtime separation of duties, and
protected-state mutation.
