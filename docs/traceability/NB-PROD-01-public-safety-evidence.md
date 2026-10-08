# NB-PROD-01 Public NB-1 Safety Evidence

## Scope and provenance

Task: [NB-PROD-01](https://app.notion.com/p/3f31c1ac5ec0817fbfa0f2c38cced8d8),
subtask NB-PR-01E. Work area: Neural Brain.
Accepted base: `cc78c48c5c401fec64133aa7bd5113600639cce1`.
Branch: `codex/nb1-public-safety-evidence-20261008`.

The test changes selectively recover existing public evidence from
`98c1da43fb64f1c6fa8a060ea09f187c9f5c5144`, with stronger assertions and
accurate claim boundaries. No unaccepted metacognition/evaluation amendment,
later-stage package, migration, product implementation, or frozen specification
is imported. Commit and PR evidence are recorded in the linked coordination task.

## Requirement mapping

| Requirement | Executed evidence | Limit |
| --- | --- | --- |
| Tenant/Area/Project/Session checkpoint isolation | `test_authenticated_scope_dimension_matrix_denies_foreign_checkpoint_reads` varies each trusted dimension, denies before neural inference, proves unchanged observations/working state/checkpoints/receipts/audit, and permits a legitimate initial cycle in the new scope. | Unit-level authenticated-scope behavior; live Tenant boundaries are covered separately by the existing database suite. |
| Request cannot select scope, principal, authority, approval, or model | `test_cycle_request_rejects_scope_authority_model_and_gate_bypass_fields` requires exact `extra_forbidden` error locations for twelve fields. Existing nested observation rejection cases remain. | Schema exclusion, not a proof of every possible internal bypass. |
| Durable commit survives lost caller acknowledgement without duplicate writes | `test_lost_caller_acknowledgement_after_commit_replays_and_recovers_exactly` reads committed state through a new adapter, replays the same cycle, proves full checkpoint equality, and retains exact checkpoint/evidence/receipt/audit counts. | Models caller acknowledgement loss after adapter return; does not kill a process, restart PostgreSQL, or inject a transport failure. |
| Immutable parameters and bounded public API | Existing immutable-parameter test retains explicit absent execution/mutation method names. | API regression guard, not complete effect-surface certification. |

Relevant authority: ADR-018, Architecture Directive v4.0,
`docs/architecture/contracts/nb1-safe-serial-cognition.json`, and the existing
Memory Transition Gate contracts. All authenticated and protected-state
boundaries are unchanged.

## Verification

On 2026-10-08, CPython 3.14.6, locked uv 0.11.28 dependencies and PostgreSQL 18.4:

- `uv run --locked --all-groups python tools/quality.py --locked`:
  formatting, lint, strict MyPy (183 files), type-exception audit (zero findings),
  and **915 tests passed, no skips**, in 673.46 seconds.
- After adding the final full-checkpoint replay equality assertion:
  `uv run --locked --all-groups python -m pytest -q tests/unit/test_cognition_service.py tests/database/test_postgres_cognitive_repository.py`:
  **38 passed**, in 5.13 seconds.
- Final focused formatting, lint and strict typing passed for both test files.
- Separate read-only reviews assessed scope/bypass assertions and database
  claim/isolation boundaries. Review corrections were incorporated.

Live tests used newly initialized, dedicated loopback PostgreSQL clusters,
SCRAM authentication and ephemeral test credentials. Fixtures created only
guarded disposable test databases and runtime roles inside those clusters.
Both clusters were stopped after verification; the existing PostgreSQL service
was not used or modified. No credential or live personal data is recorded here.

## Remaining gates

This record adds public safety evidence; it does not complete NB-1, establish
a conforming v4 candidate, approve a scientific threshold, appoint an evaluator,
supply hidden data, pass recognition/G8, activate a runtime, or deploy a system.
The v4 generator clarification, compatible v4 evaluation implementation,
independent custody/registry/candidate acceptance, external evaluation, and
eligible repository review remain separate requirements.
