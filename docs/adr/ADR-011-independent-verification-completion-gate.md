# ADR-011: Independent Verification Completion Gate

- Status: Accepted
- Date: 2026-07-15
- Notion source: https://app.notion.com/p/39d1c1ac5ec0817b97d2dacdbedbd1d9
- Notion page ID: `39d1c1ac-5ec0-817b-97d2-dacdbedbd1d9`

## Context

Executor or planner success is not sufficient evidence that a goal has been
achieved.

## Decision

Only the Goal Transition Gate may write `Achieved`. It may do so only from a
separate verifier decision, complete evidence, and quiescence. Verification
intents have their own purpose and state guard. When blocked verification can
resume, it returns to `Verifying`.

## Invariants and Constraints

- Planner or executor success cannot write or imply `Achieved`.
- The verifier decision is separate from execution.
- Complete evidence and quiescence are mandatory completion conditions.
- Verification intents are purpose-bound and state-guarded.
- Resumed blocked verification returns to `Verifying`.

## Consequences

Goal completion has an independent, evidence-based gate. Verification blockage
does not bypass that gate or convert execution success into goal success.

## Relationship to the Architecture Directive

This decision specializes the architecture directive's separation of executor,
verifier, and Goal Transition Gate responsibilities. It defines the only
authorized completion path without merging those runtime roles.
