# ADR-000: Short Decision Title

- Status: Proposed
- Date: YYYY-MM-DD
- Notion source: https://app.notion.com/p/...
- Notion page ID: `00000000-0000-0000-0000-000000000000`
- Authority: current | retained_subsystem | historical
- Theme: product_boundary | scope_and_isolation | protected_control | ledger_and_evidence | memory_lifecycle | runtime_and_inference
- Applies to stages: NB-0
- Supersedes: none
- Superseded by: none
- Amends: none
- Amended by: none

## Context

Describe the concrete problem, affected system boundary, current evidence,
accepted ADRs, rejected assumptions, and why a new decision is needed.

## Decision

State the decision in imperative, implementation-ready language. Distinguish
current implementation authority from target architecture and subsystem-only
authority.

## Consequences

List the required implementation, testing, documentation, migration, operation,
security, privacy, and release-gate effects.

## Invariants and Constraints

- Unknown identity, scope, authority, state, policy, operation, model version,
  data class, or evaluation state fails closed.
- Cognitive capability never creates protected-control-plane authority.
- Product maturity claims must not exceed versioned evidence.

## Relationship to Earlier Decisions

Name every ADR this record supersedes, amends, narrows, widens, or depends on.
If a historical ADR is reused, state the exact revalidated subset.

## Validation

Record required tests, contract updates, migration checks, release evidence,
and Notion lifecycle updates.
