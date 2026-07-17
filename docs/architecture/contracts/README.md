# Machine-readable Neural Brain contracts

These contracts implement the complete cognitive-system target established by
ADR-018 while retaining the governed Memory Core established by ADR-015 through
ADR-017.

## Complete-system contracts

- `system-boundary.json`: Cognitive Plane, Protected Control Plane, scope,
  target capabilities, Memory Core role, and non-claims.
- `cognitive-cycle.json`: typed serial cognitive-cycle order and invariants.
- `nb1-safe-serial-cognition.json`: first implementation-slice boundary for
  recorded or synthetic observations, bounded learned attention, a fixed-version
  recurrent workspace, internal proposals, deterministic checkpoints, and no
  external effects.
- `nb1-hidden-evaluation.json`: label-free candidate boundary, candidate freeze
  receipt, external evaluator custody, and signed evidence intake for EVAL-01 v3.
- `stage-capabilities.json`: cumulative NB-0 through NB-8 delivery contract.
- `recognition-gates.json`: all-required recognition criteria.
- `evaluation-gates.json`: ordered, non-compensatory G0 through G8 evidence.
- `release-stops.json`: non-waivable complete-system release stops.

## Memory Core contracts

- `scope-catalog.json`: strict Brain-to-Goal object lineage; Goal is not an isolation dimension.
- `envelopes.json`: authenticated memory requests and records.
- `memory-lifecycle.json`: Memory Gate operations and lifecycle.
- `memory-stage-capabilities.json`: cumulative, separately namespaced MS-0
  through MS-4 Memory Core maturity contract. These stages are not NB product
  stages and do not advance product maturity by themselves.
- `memory-release-stops.json`: retained non-waivable Memory Core-specific
  release stops under ADR-018.
- `ledger-invariants.json`: PostgreSQL, provenance, audit, isolation, and recovery.
- `dreaming.json`: Area-local offline Dreaming and inactive candidates.
- `inference-provider.json`: bounded local Ollama memory-processing boundary.

Historical Goal, Action Intent, dispatch, intent-purpose, and quiescence
contracts remain in Git history. ADR-018 does not reactivate them automatically;
each must be revalidated or replaced by its delivery task.

Preregistered evaluation specifications live under
`docs/architecture/evaluations/`. Their digest is frozen before the evaluated
runtime or evidence report is accepted.

Unknown scope, actor, authority, state, operation, model version, provenance,
freshness, data class, promotion, evaluation, or authorization state fails
closed. A schema may describe a later operation without authorizing it before
its stage and evidence gates pass.
