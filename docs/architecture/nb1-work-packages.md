# NB-1 Safe Serial Neural Cognition Work Packages

- Status: Implementation plan
- Governing decision: ADR-018
- Parent milestone: NB-1
- Evaluation specification: `EVAL-01.NB-1.safe-serial-cognition.v2`

## Boundary

NB-1 implements one internal serial cognitive cycle over recorded or synthetic
observations. It has no Action Intent, tool, executor, external-effect, online
training, or active-model mutation surface. It is an implementation slice, not
NB-1 stage release evidence or authorization to use `Neural Brain Candidate`.

## Ordered work packages

| ID | Objective | Dependencies | Primary evidence |
| --- | --- | --- | --- |
| NB-1.1 | Freeze cognitive-cycle and evaluation contracts | NB-0, EVAL-01 | Contract validation and frozen digest |
| NB-1.2 | Implement fixed-version trainable recurrent workspace and learned bounded attention | NB-1.1 | Baseline lift and causal ablations |
| NB-1.3 | Implement authenticated session state and deterministic compare-and-set checkpoints | NB-1.1, MS-1 checkpoint boundary | Scope, stale-version, recovery, and atomicity tests |
| NB-1.4 | Emit internal goal, executive-control, and plan proposals | NB-1.2, NB-1.3 | Typed-output and no-effect-surface tests |
| NB-1.5 | Add metacognitive continue, ask, defer, and stop behavior | NB-1.3, NB-1.4 | Calibration-boundary and recovery tests |
| NB-1.6 | Execute the frozen baseline, ablation, recovery, scope, and bypass evaluation | NB-1.1 through NB-1.5 | Immutable evaluation report |

## Current slice status

| Work package | Current evidence | Remaining before package completion |
| --- | --- | --- |
| NB-1.1 | v2 contract and evaluation digest frozen | Independent acceptance of the complete stage harness |
| NB-1.2 | One-unit recurrent mechanism and bounded trainable feature gate implemented; development ablations execute | Offline training artifact plus independent hidden-test evidence |
| NB-1.3 | Session-scoped serial state commits through the existing Memory Transition Gate with CAS, idempotency, checkpoint, and audit tests | PostgreSQL integration and crash-recovery evidence for this cognition path |
| NB-1.4 | Internal Goal and Plan proposals implemented without an action or effect surface | Separate causal executive-control evidence |
| NB-1.5 | `continue` and `ask` activation-ambiguity proposals implemented | Calibrated uncertainty plus reachable `defer`, `stop`, and recovery behavior |
| NB-1.6 | Six baselines, three ablations, confidence intervals, and deterministic development evaluation implemented | Independent hidden artifact, contamination report, environment hashes, and gate review |

## Acceptance rule

The implementation may be described as the first NB-1 vertical slice only
when all six work packages have repository evidence. NB-1 itself remains
incomplete until every stage contract and independent release gate passes.
