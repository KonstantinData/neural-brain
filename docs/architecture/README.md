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
- [`goal-gate-adr-018-revalidation-proposal-v1.md`](goal-gate-adr-018-revalidation-proposal-v1.md)
  records the proposed, non-authorizing replacement boundary for historical
  Goal Gate ADRs. It remains blocked pending authorized acceptance.
- [`action-gate-adr-018-revalidation-proposal-v1.md`](action-gate-adr-018-revalidation-proposal-v1.md)
  records the proposed, non-authorizing NB-4/NB-5 boundary for historical
  Action Gate, preparation, dispatch, and reconciliation ADRs. It remains
  blocked pending authorized acceptance together with the Goal Gate boundary.
- [`nb1-planner-verification-adr-018-revalidation-proposal-v1.md`](nb1-planner-verification-adr-018-revalidation-proposal-v1.md)
  records the proposed, non-authorizing prerequisite boundary for the NB-1
  S1-10 planner, verification, and serial-loop packages. It remains blocked
  pending an authorized current contract.
- [`relationship-memory-adr-018-revalidation-proposal-v1.md`](relationship-memory-adr-018-revalidation-proposal-v1.md)
  records preparation-only Positions 1–3; it authorizes neither runtime nor
  retrieval, Planner, or Dreaming use.
- [`s1-14-4-runtime-privacy-enforcement-adr-proposal-v1.md`](s1-14-4-runtime-privacy-enforcement-adr-proposal-v1.md),
  [`special-category-data-runtime-enforcement-v1.md`](special-category-data-runtime-enforcement-v1.md),
  and [`special-category-data-policy-model-v1.md`](special-category-data-policy-model-v1.md)
  define preparation-only S1-14.4/S1-11.2 decision, enforcement, and policy
  boundaries. They are not accepted authority and enable no migration, active
  policy, runtime `ALLOW`, protected storage, or release.
- [`protected-control-kill-switch-adr-018-revalidation-proposal-v1.md`](protected-control-kill-switch-adr-018-revalidation-proposal-v1.md)
  records the proposed, non-authorizing replacement boundary for historical
  Kill-Switch ADR-006. It remains blocked pending an authorized Protected
  Control Plane decision and does not authorize runtime implementation.
- [`nb1-independent-evaluation-adr-018-revalidation-proposal-v1.md`](nb1-independent-evaluation-adr-018-revalidation-proposal-v1.md)
  records a proposed, non-authorizing EVAL-01 v4 artifact, custody, and
  evidence boundary. It remains blocked pending external independent roles and
  evidence and cannot authorize an evaluation, release, or recognition claim.
- [`protected-control-kill-switch-scope-resolution-decision-v1.md`](protected-control-kill-switch-scope-resolution-decision-v1.md)
  records unaccepted scope-resolution options for the future Kill-Switch
  successor. It selects no policy and has no runtime authority.
- [`ledger-conventions-v1.md`](ledger-conventions-v1.md) fixes PostgreSQL
  representation conventions for protected keys, scope, time, exact amounts,
  naming, and structured payloads.
- [`architecture-directive-v3.0.md`](architecture-directive-v3.0.md) is the
  superseded Memory Core baseline retained as historical evidence.
- v2.0 and v1.1 remain earlier superseded baselines.

## Active machine-readable contracts

Relationship Memory preparation is documented in
[`relationship-memory-adr-018-revalidation-proposal-v1.md`](relationship-memory-adr-018-revalidation-proposal-v1.md),
its signal contract, governance matrices, Dreaming boundary, threat plan,
traceability, and runbook. These artifacts create no storage, retrieval,
personal-data processing, Dreaming, Planner, or protected-state runtime.

- `system-boundary.json`: complete-system and two-plane boundary.
- `cognitive-cycle.json`: protected serial perception-to-learning cycle.
- `action-transition-gate-v1.json`: bounded prerequisite contract for a future
  NB-5 Action Transition Gate; it neither authorizes nor implements action,
  dispatch, budget, resource, fence, sandbox, or external-effect behavior.
- `stage-capabilities.json`: NB-0 through NB-8 availability and prohibitions.
- `recognition-gates.json`: mandatory product-recognition gates.
- `evaluation-gates.json`: ordered G0 through G8 evidence chain.
- `release-stops.json`: complete-system non-waivable release stops.
- `memory-release-stops.json`: retained Memory Core-specific release stops.
- `scope-catalog.json`: Brain-to-Session catalog hierarchy; Goals are
  session-bound protected aggregates, not isolation dimensions.
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

[`special-category-data-runtime-threat-and-privacy-assessment-v1.md`](special-category-data-runtime-threat-and-privacy-assessment-v1.md),
[`s1-14-4-privacy-ledger-migration-plan-v1.md`](s1-14-4-privacy-ledger-migration-plan-v1.md),
[`s1-11-2-controlled-storage-integration-v1.md`](s1-11-2-controlled-storage-integration-v1.md),
and [`s1-14-4-s1-11-2-runtime-enforcement-test-strategy-v1.md`](s1-14-4-s1-11-2-runtime-enforcement-test-strategy-v1.md)
record focused preparation and future verification requirements only; no
runtime implementation or production readiness is claimed.
