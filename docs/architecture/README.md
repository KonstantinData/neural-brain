# Architecture

This directory contains versioned normative architecture, recognition,
evaluation, threat, and machine-readable contract documentation for Neural
Brain. Target architecture and implemented maturity must remain explicitly
distinct.

## Normative baseline

- [`architecture-directive-v4.0.md`](architecture-directive-v4.0.md) is the
  complete cognitive-system target governed by ADR-018.
- [`neural-brain-recognition-standard.md`](neural-brain-recognition-standard.md)
  defines the non-compensatory criteria for the product name.
- [`evaluation-framework.md`](evaluation-framework.md) defines ordered evidence
  gates, baselines, ablations, transfer, robustness, and safety evaluation.
- [`delivery-roadmap.md`](delivery-roadmap.md) defines NB-0 through NB-8 and
  their hard dependencies.
- [`architecture-directive-v3.0.md`](architecture-directive-v3.0.md) is the
  superseded Memory Core baseline retained as historical evidence.
- v2.0 and v1.1 remain earlier superseded baselines.

## Active machine-readable contracts

- `system-boundary.json`: complete-system and two-plane boundary.
- `cognitive-cycle.json`: protected serial perception-to-learning cycle.
- `stage-capabilities.json`: NB-0 through NB-8 availability and prohibitions.
- `recognition-gates.json`: mandatory product-recognition gates.
- `evaluation-gates.json`: ordered G0 through G8 evidence chain.
- `release-stops.json`: complete-system non-waivable release stops.
- `memory-release-stops.json`: retained Memory Core-specific release stops.
- `scope-catalog.json`: Brain-to-Goal protected-object hierarchy with isolation ending at Session.
- `envelopes.json`: authenticated, provenance-bearing memory envelopes.
- `memory-lifecycle.json`: protected Memory Core lifecycle.
- `ledger-invariants.json`: transactional state, audit, provenance, and recovery.
- `dreaming.json`: Area-local offline Dreaming constraints.
- `inference-provider.json`: bounded local inference for Memory Core operations.

Memory-specific contracts remain subsystem authority under ADR-015 through
ADR-017. They do not define the complete product boundary. Goal, Action,
execution, verification, cognitive inference, world-model, and model-promotion
contracts must be added by their owning delivery tasks before implementation.

[`threat-model.md`](threat-model.md) defines the Foundation threat model.
Deployment-specific legal classification, DPIA, fundamental-rights assessment,
and production authorization remain separate evidence.
