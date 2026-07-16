# Architecture

This directory contains versioned normative architecture specifications and
machine-readable contract documentation for Neural Brain.

Documents here describe accepted platform boundaries and invariants. Proposals
that have not been accepted remain outside the normative architecture baseline.

## Normative baseline

- [`architecture-directive-v3.0.md`](architecture-directive-v3.0.md) is the
  current normative memory-system directive governed by ADR-015, ADR-016, and
  ADR-017.
- [`architecture-directive-v2.0.md`](architecture-directive-v2.0.md) is the
  superseded memory-system baseline retained as historical evidence.
- [`architecture-directive-v1.1.md`](architecture-directive-v1.1.md) is the
  superseded agent-system baseline retained as historical evidence.
- `contracts/` contains machine-readable contracts produced by their owning
  backlog tasks. A contract is not authorized merely because a later-stage
  operation appears in a schema.

Current machine-readable contracts:

- [`contracts/system-boundary.json`](contracts/system-boundary.json) defines
  Neural Brain's memory-only capability boundary and excludes agent-runtime
  responsibilities.
- [`contracts/scope-catalog.json`](contracts/scope-catalog.json) defines typed
  Brain-to-Session catalog lineage without descendant or sentinel scope.
- [`contracts/envelopes.json`](contracts/envelopes.json) defines validated,
  provenance-bearing memory request and result envelopes with immutable
  authenticated scope.
- [`contracts/memory-lifecycle.json`](contracts/memory-lifecycle.json) defines
  protected memory lifecycle transitions and their fail-closed guards.
- [`contracts/stage-capabilities.json`](contracts/stage-capabilities.json)
  defines cumulative memory delivery-stage capabilities and rejects unavailable
  or agent-runtime operations.
- [`contracts/ledger-invariants.json`](contracts/ledger-invariants.json) defines
  transactional memory, provenance, audit, retention, and deletion invariants.
- [`contracts/inference-provider.json`](contracts/inference-provider.json)
  defines the bounded local Ollama-only, no-cloud-fallback memory-processing
  boundary.
- [`contracts/release-stops.json`](contracts/release-stops.json) is the
  machine-readable memory-system release-stop set.
- [`contracts/dreaming.json`](contracts/dreaming.json) defines Area-local
  offline Dreaming, stage limits, artifacts, guards, and prohibited effects.

The superseded Goal, Action Intent, intent-purpose, and quiescence contracts
were removed from the active tree. Their Git history and superseded ADRs remain
historical evidence; they are not implementation authority.

[`threat-model.md`](threat-model.md) contains the initial Foundation technical
threat model and trust-boundary diagram. Deployment- and use-case-specific
regulatory roles, classifications, prohibited-use determinations,
fundamental-rights assessments, and DPIA evidence remain assigned to FND-04.
