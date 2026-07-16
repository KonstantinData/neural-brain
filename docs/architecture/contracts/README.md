# Machine-readable memory contracts

These contracts implement the active memory-system boundary established by
ADR-015, the hierarchy scope decision in ADR-016, and governed Dreaming in
ADR-017. They define Neural Brain as a governed memory service for authenticated
consumers. Neural Brain does not own consumer goals, plans, tools, action
intents, external effects, or task-success decisions.

The active contract set is:

- [`system-boundary.json`](system-boundary.json): system purpose, consumer
  boundary, non-capabilities, trusted context, and resolved catalog boundary.
- [`scope-catalog.json`](scope-catalog.json): strict Brain-to-Session hierarchy
  lineage and operational-memory scope rules.
- [`envelopes.json`](envelopes.json): strict memory request and record schemas
  with authenticated scope and optional non-authoritative consumer correlations.
- [`memory-lifecycle.json`](memory-lifecycle.json): memory operations, lifecycle
  rules, candidate promotion, deletion, and reconciliation.
- [`ledger-invariants.json`](ledger-invariants.json): PostgreSQL Memory Gate,
  provenance, versioning, audit atomicity, isolation, and recovery invariants.
- [`release-stops.json`](release-stops.json): non-waivable memory-specific release
  stops.
- [`stage-capabilities.json`](stage-capabilities.json): cumulative memory-only
  stage capabilities.
- [`dreaming.json`](dreaming.json): Area-local offline Dreaming guards,
  artifacts, stage behavior, and prohibited effects.
- [`inference-provider.json`](inference-provider.json): local Ollama inference
  restricted to supporting memory functions.

Goal state machines, Action Intent state machines, intent-purpose guards, and
goal quiescence are not Neural Brain contracts. Their historical definitions
remain available through version control only.

All unknown scope, lineage, actor, operation, lifecycle, provenance, freshness,
classification, policy, Dreaming guard, lease, snapshot, or authorization
states fail closed.
