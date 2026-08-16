# NB-2 Perception, Attention, and World Model Work Packages

- Status: Prerequisite-ready package; blocked on NB-1 exit
- Governing decision: ADR-018
- Parent milestone: NB-2 / Notion NB-247

## Boundary

NB-2 cannot begin runtime implementation until NB-1 has an independently
accepted stage exit. The current NB-1 development slice, local tests, a frozen
evaluation specification, a candidate freeze, or an evaluator self-attestation
does not satisfy that condition by itself.

This package defines future contracts and evaluation acceptance only. It does
not enable a perception runtime, model, memory write, tool or action surface,
model activation, external effect, or NB-2 maturity claim.

## Ordered work packages

| ID | Objective | Hard dependency | Affected components | Acceptance before next package |
| --- | --- | --- | --- | --- |
| NB-2.0 | Hold the stage until the NB-1 exit is independently accepted | NB-1 complete exit evidence and gate review | All NB-2 runtime surfaces | Independent exit reference is recorded; unknown remains blocked |
| NB-2.1 | Freeze typed perception, provenance, temporal-binding, and bounded-attention contracts | NB-2.0 | Cognitive Plane contracts only | Static contract tests prove record separation, immutable authenticated scope reference, non-language temporal stream, missingness, contradiction, and non-suppressible channels |
| NB-2.2 | Freeze the simulation-only world-model evaluation preregistration | NB-2.0 | Evaluation artifacts only | Static tests prove baselines, ablations, budgets, contamination controls, thresholds, and failure criteria are explicit |
| NB-2.3 | Implement temporal perception, binding, calibrated attention, and world model in simulation | NB-2.1, NB-2.2 | New NB-2-owned runtime files | Runtime remains simulation-only; no protected-state writer, tool, executor, or activation surface exists |
| NB-2.4 | Perform independent held-out evaluation and gate review | NB-2.3 | Isolated evaluation harness and evidence ledger | Prediction, uncertainty, OOD, contradiction, attention, and planning-usefulness gates all pass non-compensatorily |

## Required exit evidence

NB-2 requires held-out multi-step action-conditioned prediction, calibrated
uncertainty under dynamics shift, OOD behavior, contradiction and missing-input
handling, bounded-attention evidence, and simulated planning lift against
model-free and shuffled-action baselines. Each component requires a
preregistered baseline, effect threshold, confidence bound, resource budget,
ablation, safety boundary, and failure criterion.

Predictions remain distinct from observations. Simulation action tokens never
commit an Action Intent, invoke a tool, or create authority. Any unknown or
failed prerequisite, evidence, authority, privacy, security, or evaluation gate
is a non-compensatory release stop.
