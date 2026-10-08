# Architecture

This index separates the current production critical path from implementation
contracts, unaccepted preparation, and archived evidence. A document or passing
documentation test does not establish an implemented capability or passed gate.

## Current target and production gates

Read these in order; ADR-018 and the repository source-precedence rules govern
their interpretation.

1. [Architecture Directive v4.0](architecture-directive-v4.0.md): complete
   cognitive-system target and two-plane authority boundary.
2. [Recognition Standard](neural-brain-recognition-standard.md): all-required
   recognition criteria and independent G8 evidence.
3. [Evaluation Framework](evaluation-framework.md): preregistration, baselines,
   ablations, safety evidence, and the G0–G8 chain.
4. [Delivery Roadmap](delivery-roadmap.md): stage dependencies and exit criteria.
5. [NB-1 work packages](nb1-work-packages.md): the immediate implementation and
   evidence gaps; no NB-1 exit has been accepted.
6. [Threat model](threat-model.md): complete-system security requirements.
7. [Ledger conventions](ledger-conventions-v1.md): protected PostgreSQL
   representation and migration rules.

EVAL-01 v4 is the frozen replacement specification. Versions 1–3 are rejected
history. The merged executable training/evidence chain remains v3-bound; an
accepted executable v4 recipe, compatible candidate/intake, and independently
accepted evidence are still required. Unmerged v4.1 drafts and local candidate
artifacts do not amend the accepted specification.

## Implemented Memory Core contracts and test infrastructure

These documents describe the narrower implemented foundation. They do not
establish complete cognition, protected policy activation, or production use.

| Document | Implemented boundary |
| --- | --- |
| [Security Floor](security-floor-v1.md) | Code-owned scoped ingestion/read constraints |
| [Memory risk outcomes](memory-risk-outcomes-v1.md) | Risk and fail-closed outcome vocabulary |
| [Policy contract](policy-contract-v1.md) | Canonical, expiry-bound intake-policy compiler |
| [Policy decision records](policy-decision-records-v1.md) | Immutable non-authorizing decision evidence |
| [Policy activation](policy-activation-v1.md) | Separated activation-evidence validator |
| [Trust envelopes](trust-envelopes-v1.md) | Untrusted payload and provenance boundary |
| [Deterministic memory test harness](deterministic-memory-test-harness.md) | Effect-free test infrastructure |

## Required preparation awaiting acceptance or implementation

These are prerequisites or decision inputs for later production gates. They
remain here because removing them would hide required control, privacy,
storage, or evaluation work. Their presence grants no runtime authority.

| Document | Required boundary |
| --- | --- |
| [Goal Gate revalidation](goal-gate-adr-018-revalidation-proposal-v1.md) | Session-bound Goal authority |
| [NB-1 planner/verification revalidation](nb1-planner-verification-adr-018-revalidation-proposal-v1.md) | Effect-free internal proposals |
| [NB-1 evaluation manifests revalidation](nb1-independent-evaluation-adr-018-revalidation-proposal-v1.md) | Candidate/evidence admissibility |
| [Action Gate revalidation](action-gate-adr-018-revalidation-proposal-v1.md) | Protected NB-5 execution |
| [Kill-switch revalidation](protected-control-kill-switch-adr-018-revalidation-proposal-v1.md) | Independent shutdown/recovery |
| [Kill-switch scope decision](protected-control-kill-switch-scope-resolution-decision-v1.md) | Unaccepted scope/persistence options |
| [Privacy enforcement ADR proposal](s1-14-4-runtime-privacy-enforcement-adr-proposal-v1.md) | S1-14.4 decision boundary |
| [Special-category runtime enforcement](special-category-data-runtime-enforcement-v1.md) | Future protected-data enforcement |
| [Special-category policy model](special-category-data-policy-model-v1.md) | Proposed policy fields and invariants |
| [Runtime threat/privacy assessment](special-category-data-runtime-threat-and-privacy-assessment-v1.md) | Required negative security/privacy evidence |
| [Privacy ledger migration plan](s1-14-4-privacy-ledger-migration-plan-v1.md) | Future ledger and atomic admission |
| [Controlled storage integration](s1-11-2-controlled-storage-integration-v1.md) | S1-11.2 storage boundary |
| [Enforcement test strategy](s1-14-4-s1-11-2-runtime-enforcement-test-strategy-v1.md) | Future runtime verification |

## Machine-readable authority and evidence

[The contract index](contracts/README.md) distinguishes normative invariants,
implementation boundaries, and preparation-only contracts. JSON files retain
their existing locations and frozen evaluation specifications are unchanged.

The immediate NB-1 evaluation path uses
[the hidden-evaluation boundary](contracts/nb1-hidden-evaluation.json),
[preparation](contracts/nb1-independent-evaluation-preparation-v1.json),
[artifact manifests](contracts/nb1-independent-evaluation-artifact-manifests-v1.json),
[role separation](contracts/nb1-independent-evaluation-organization-v1.json),
and [freeze lifecycle](contracts/nb1-candidate-freeze-lifecycle-v1.json).
These contracts create no external evaluator, accepted receipt, hidden run,
gate result, release, or recognition.

## Archive

[Archive inventory](archive/README.md) contains the superseded v1.1/v2.0/v3.0
directives and deferred optional Relationship Memory preparation. Original
bytes and negative contract tests are preserved. Archived proposals remain
unaccepted and create no authority. Their retention does not add them to the
production critical path.
