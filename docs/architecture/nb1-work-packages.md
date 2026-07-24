# NB-1 Safe Serial Neural Cognition Work Packages

- Status: Implementation plan
- Governing decision: ADR-018
- Parent milestone: NB-1
- Evaluation specification: `EVAL-01.NB-1.safe-serial-cognition.v4`

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
| NB-1.1 | v1-v3 are immutable evaluation history; v3 was rejected before hidden attachment after its generator was proven enumerable; v4 replacement specification and generator contract are preregistered | Independently accept the v4 specification/generator and complete stage harness before hidden attachment |
| NB-1.2 | One-unit recurrent mechanism, bounded trainable feature gate, deterministic train-only grid search, self-verifying offline bundle, label-free candidate boundary, candidate freeze receipt, and signed external-evidence intake implemented for the rejected v3 candidate | Generate public v4 train/development artifacts, train and freeze a v4-bound candidate, then obtain an external hidden artifact, independent run, contamination report, threshold review, and accepted evidence |
| NB-1.3 | Dedicated PostgreSQL cognition adapter and migration keep checkpoint, transition envelope, trusted training/model evidence, receipt, and audit inside one Memory Transition Gate transaction; PostgreSQL 18 evidence covers CAS, replay, scope, corruption, restart, and rollback | Complete through merged PR #8; broader NB-1 release remains gated |
| NB-1.4 | Internal Goal and Plan proposals implemented without an action or effect surface | Separate causal executive-control evidence |
| NB-1.5 | `continue` and `ask` activation-ambiguity proposals implemented | Calibrated uncertainty plus reachable `defer`, `stop`, and recovery behavior |
| NB-1.6 | Six baselines, three ablations, confidence intervals, deterministic development evaluation, training/environment hashes, label-free candidate output, signed evidence intake, and v4 replacement preregistration implemented | v4-bound candidate freeze, independent hidden artifact and run, contamination report, complete safety results, and gate review |

## Acceptance rule

The implementation may be described as the first NB-1 vertical slice only
when all six work packages have repository evidence. NB-1 itself remains
incomplete until every stage contract and independent release gate passes.
