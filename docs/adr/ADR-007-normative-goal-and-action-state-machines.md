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

The canonical Goal states are `proposed`, `active`, `suspended`, `blocked`,
`verifying`, `terminating`, `achieved`, `failed`, and `discarded`. The canonical
Action Intent states are `proposed`, `preparing`, `prepared`, `committed`,
`executing`, `cancel_requested`, `settling`, `indeterminate`, `completed`, and
`aborted`. The only canonical Action Intent purposes are `execution`,
`verification`, `cancellation`, `reconciliation`, and `compensation`.

The normative machine-readable contracts are:

- `docs/architecture/contracts/goal-state-machine.json`;
- `docs/architecture/contracts/action-intent-state-machine.json`;
- `docs/architecture/contracts/intent-purpose-guards.json`; and
- `docs/architecture/contracts/quiescence.json`.

Each declared transition specifies its source and target, request actors,
purpose relationship, authority, policy and approval requirements, guards,
quiescence and evidence requirements, atomic side effects and audit event,
deadline and timeout semantics, cancellation semantics, crash recovery,
reconciliation, and allowed successor states. A transition omitted from the
contract is prohibited.

`blocked_from_state` records the exact resumable state and is cleared only by an
authorized resume transition. `termination_disposition` is required before a
goal enters `terminating` and constrains its terminal successor. An
`indeterminate` action remains nonterminal, retains its claims, and can be
resolved only by evidence-backed `effect_confirmed`, `no_effect_confirmed`, or
`effect_compensated` paths.

## Invariants and Constraints

- Unknown states and transitions are rejected.
- Quiescence is an explicit condition of state-machine behavior.
- Deadlines, cancellation, blocking, termination, and crash recovery are
  represented by the normative contracts rather than informal control flow.
- `blocked_from_state` and `termination_disposition` are explicit state data.
- An `indeterminate` action requires an explicit resolution path.
- Action Intent purpose is immutable after proposal.
- `suspended` and every terminal Goal state require the reusable normative
  quiescence predicate to evaluate true in the authoritative transaction.
- An `indeterminate` action is not quiescent and cannot be retried blindly.

## Consequences

Every transition must name its permitted actors, guards, required evidence,
side effects, audit requirements, timeout behavior, and recovery tests.

## Relationship to the Architecture Directive

This decision specializes the architecture directive's protected Goal and
Action state requirements. The directive defines the system-wide boundary; this
ADR requires the corresponding state behavior to be explicit, versioned, and
default-deny.
