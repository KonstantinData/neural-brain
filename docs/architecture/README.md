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

The exact Goal and Action transitions, intent-purpose guards, quiescence
statuses, threat model, and unresolved regulatory schemas remain unavailable
until their recorded dependencies and architecture decisions are resolved.
