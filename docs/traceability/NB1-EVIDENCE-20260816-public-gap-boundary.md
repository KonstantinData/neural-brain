# NB1-EVIDENCE-20260816: Public Internal Evidence-Gap Boundary

## Scope and authority

This bounded package uses ADR-018, Architecture Directive v4.0, the NB-1
contract, and the NB-1 work packages to add only internal, effect-free
evidence. It does not change EVAL-01 v4 criteria, create hidden data, claim an
independent party, or change the blocked NB-1 milestone status.

| Evidence package | Repository evidence | Boundary preserved |
| --- | --- | --- |
| Authenticated scope matrix | `tests/unit/test_cognition_service.py::test_authenticated_scope_dimension_matrix_denies_foreign_checkpoint_reads` independently varies Tenant, Area, Project, and Session. | Scope remains runtime-authenticated; request payload cannot supply a scope field. |
| NB-1 bypass surface | `tests/unit/test_cognition_service.py::test_cycle_request_rejects_scope_authority_model_and_gate_bypass_fields` rejects all trusted scope, authority, approval, and model-selection fields; `test_parameters_are_immutable_and_no_effect_surface_is_exposed` keeps direct mutation/effect methods absent. | No Goal/Action Gate, tool, executor, or external effect is introduced. |
| Durable-commit recovery | `tests/database/test_postgres_cognitive_repository.py::test_crash_after_durable_commit_replays_and_recovers_exactly` discards the client acknowledgement only after the transaction has committed, then proves restart/readback and idempotent replay. | It verifies the existing Memory Transition Gate ledger only; it does not treat an unknown external effect as retryable. |
| Metacognition and calibration | `docs/architecture/nb1-metacognition-adr-018-revalidation-proposal-v1.md` and its deterministic documentation test identify the missing decision authority. | `defer`, `stop`, calibrated uncertainty, and all new evaluation criteria remain unimplemented and unclaimed. |
| Reproducibility and ablations | EVAL-01 v4 remains frozen with its own baseline/ablation declarations; its public candidate path remains blocked on the accepted v4 clarification. | No v3 artifact is relabelled, and no candidate, freeze, hidden run, score, or gate result is created. |

## Explicit blockers

1. An Architecture Decision Owner must accept, replace, or reject the proposed
   NB-1 metacognition contract before `defer` or `stop` becomes executable.
2. Calibration requires its own accepted, preregistered NB-6 evaluation design;
   EVAL-01 v4 has no metacognitive calibration metric or threshold.
3. Public EVAL-01 v4 candidate and reproducibility work remains blocked on an
   accepted clarification for seeds, full generator mapping, and baseline
   ceiling. External custody, independent evaluator/reviewer attestations, and
   hidden evaluation remain separate external blockers.

None of these blockers is resolved by the tests in this package.
