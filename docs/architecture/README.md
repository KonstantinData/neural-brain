# Architecture

This directory contains versioned normative architecture specifications and
machine-readable contract documentation for Neural Brain.

Documents here describe accepted platform boundaries and invariants. Proposals
that have not been accepted remain outside the normative architecture baseline.

## Normative baseline

- [`architecture-directive-v1.1.md`](architecture-directive-v1.1.md) is the
  consolidated Foundation directive.
- `contracts/` contains machine-readable contracts produced by their owning
  backlog tasks. A contract is not authorized merely because a later-stage
  operation appears in a schema.

Current machine-readable contracts:

- [`contracts/envelopes.json`](contracts/envelopes.json) defines the canonical
  persistent Evidence and Artifact envelope boundary, including immutable
  authenticated scope, actor, and trace context.
- [`contracts/stage-capabilities.json`](contracts/stage-capabilities.json)
  defines cumulative delivery-stage capabilities and fail-closed rejection of
  unavailable operations.
- [`contracts/goal-state-machine.json`](contracts/goal-state-machine.json) and
  [`contracts/action-intent-state-machine.json`](contracts/action-intent-state-machine.json)
  define the protected state graphs and typed transition rules.
- [`contracts/intent-purpose-guards.json`](contracts/intent-purpose-guards.json)
  defines the Goal-state/Intent-purpose matrix and cross-contract guards.
- [`contracts/quiescence.json`](contracts/quiescence.json) and
  [`contracts/ledger-invariants.json`](contracts/ledger-invariants.json) define
  the reusable scoped quiescence predicate, authoritative blocker statuses, and
  transactional ledger invariants.
- [`contracts/inference-provider.json`](contracts/inference-provider.json)
  defines the local Ollama-only, no-cloud-fallback inference boundary.
- [`contracts/release-stops.json`](contracts/release-stops.json) is the
  machine-readable release-stop set.

[`threat-model.md`](threat-model.md) contains the initial Foundation technical
threat model and trust-boundary diagram. Deployment- and use-case-specific
regulatory roles, classifications, prohibited-use determinations,
fundamental-rights assessments, and DPIA evidence remain assigned to FND-04.
