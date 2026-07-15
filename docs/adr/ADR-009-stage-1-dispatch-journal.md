# ADR-009: Stage 1 Dispatch Journal and External-Effect Reconciliation

- Status: Accepted
- Date: 2026-07-15
- Notion source: https://app.notion.com/p/39d1c1ac5ec08190bb81ed5337cd1eba
- Notion page ID: `39d1c1ac-5ec0-8190-bb81-ed5337cd1eba`

## Context

An external effect cannot be made exactly atomic with a database transaction.
Stage 1 uses a serial executor and therefore does not require distributed
dispatch ownership.

## Decision

Before an adapter is invoked, the system persists a committed action intent, a
minimal local dispatch-journal record, an execution grant, and an execution
attempt. Each operation has a reconciliation strategy. Ambiguous external
effects become `indeterminate`.

Stage 1 does not introduce a generalized distributed outbox. Multi-consumer
ownership, replication, and generalized distributed dispatch belong to Stage 4.

## Invariants and Constraints

- No adapter dispatch occurs before the committed intent, dispatch evidence,
  execution grant, and execution attempt exist.
- Execution attempts are monotonic and durably evidenced.
- An ambiguous effect is recorded as `indeterminate` and is not blindly retried.
- Non-reconcilable effects require human oversight.
- Stage 1 dispatch remains minimal, local, and serial.
- Generalized outbox behavior, multi-consumer ownership, and replication are
  excluded from Stage 1 and reserved for Stage 4.

## Consequences

Dispatch and attempt evidence is durable. Ambiguous outcomes cannot be hidden by
automatic retry, and operations without an automatic reconciliation path remain
subject to human oversight. Distributed dispatch capabilities are deferred to
Stage 4.

## Relationship to the Architecture Directive

This decision specializes the architecture directive's external-effect and
stage-boundary requirements. It provides only the persistent dispatch evidence
needed by the Stage 1 serial executor while preserving the Stage 4 boundary for
distributed execution ownership.
