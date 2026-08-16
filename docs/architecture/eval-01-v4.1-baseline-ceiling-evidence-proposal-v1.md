# EVAL-01 v4.1 Baseline-Ceiling Public Evidence Proposal v1

- Status: Proposed; not accepted and not effective
- Date: 2026-08-16
- Parent work package: `EVAL-01`
- Depends on: ADR-018, Architecture Directive v4.0, frozen EVAL-01 v4, and the unaccepted v4.1 clarification proposal
- Machine-readable rule: `evaluations/nb1-safe-serial-cognition-v4.1-baseline-ceiling-decision-rule-proposal-v1.json`

## Decision-ready finding

Reject the proposed numerical baseline ceiling `0.750000`. The public record
contains the v4.1 HMAC test vector and textual baseline algorithms, but no
generated v4.1 public train/development artifact, baseline report, fixed seed
panel, uncertainty calculation, sensitivity result, or candidate-feasibility
evidence. The existing development fixture is v3 history and cannot supply
v4.1 evidence because v3 was rejected for an enumerable hidden space.

The equality `0.750000 + 0.050000 = 0.800000` is arithmetic only. It does not
satisfy v4's requirement that the *lower* 95% confidence bound of the lift
over the strongest baseline exceed `0.050000`: at full accuracy `0.800000` and
baseline accuracy `0.750000`, the point lift is already only `0.050000`, so
sampling uncertainty necessarily leaves no positive margin. It therefore
cannot demonstrate a feasible boundary.

## Proposed public-only decision rule

This proposal does not set an operational ceiling. It first requires an
accepted executable successor to generate a public calibration panel of 132
IID, precommitted 256-bit train/development seed pairs. Each pair contains
2,048 train and 1,024 development sequences. There are zero candidate runs,
zero candidate freezes, and zero hidden artifacts in this package.

The eight exact baselines are: majority class, deterministic seeded random,
last observation, uniform pooling, finite state, parameter-matched stateless,
public-generator-family heuristic, and a parameter-matched recurrent
non-neural comparator. The final comparator closes the current omission: it
has a bounded recurrent state but no neural activation or feature gate. Every
parameterized baseline chooses its lexicographically tie-broken tuple only on
the corresponding public train split and is then scored once, unchanged, on
the paired development split.

The calibration produces 1,056 development reports (`132 × 8`). Accuracy is
the exact fraction `correct / 1024`; six-decimal rendering cannot alter a
decision. The panel reports the median, IQR, and maximum for each baseline and
defines `C_panel` as the maximum development accuracy across every baseline and
every seed pair. With IID pairs, the observed maximum covers the 95th
generator quantile of all eight comparators simultaneously with at least
`1 - 8 × 0.95^132 = 0.9908` design-based coverage. SHA-256 of convenient
literal strings alone is reproducible but is not such an IID sampling method.

The Architecture Decision Owner may set a future ceiling only if all fixed
seeds, artifacts, exact reports, digests, and failed attempts are published;
no development result selected parameters; and `C_panel ≤ 0.700000`. Failed
artifacts or high-baseline results invalidate the calibration. They may never
trigger a replacement seed, whole-artifact retry, or baseline-conditioned
rejection sampling.

## Sensitivity and feasibility guard

The inherited minimum full-model accuracy is `0.800000`, and the inherited
lower confidence-bound lift is `0.050000`. The proposed maximum admissible
ceiling of `0.700000` leaves a nominal `0.100000` gap — twice the lift
threshold — before confidence uncertainty. It is a guardrail, not evidence
that a candidate exists or can reach the full-model threshold.

| Ceiling | Gap at full accuracy 0.800000 | Proposed disposition |
| --- | ---: | --- |
| 0.650000 | 0.150000 | Consider only if the complete fixed-seed panel supports it; never force it by filtering artifacts. |
| 0.675000 | 0.125000 | Same panel and power requirements. |
| 0.700000 | 0.100000 | Largest proposed admissible ceiling. |
| 0.725000 | 0.075000 | Not admissible without stronger replacement evidence; family-wise uncertainty can consume the remaining lift. |
| 0.750000 | 0.050000 | Rejected; it equals the required lower confidence-bound lift. |

Before an architecture decision may adopt any ceiling in this band, a separate,
preregistered public paired-bootstrap sensitivity analysis at the minimum
hidden size of 2,048 must demonstrate at least 0.90 power for a full model at
0.800000 against every allowed ceiling over declared paired
discordance/correlation bands. It must use sequence-level paired resampling,
a digest-derived counter RNG, at least 10,000 replicates, a fixed quantile
convention, and a one-sided family-wise 95% lower bound that reselects the
strongest baseline inside every replicate. This prevents a ceiling from making
the inherited accuracy/lift condition statistically incoherent. It cannot,
and does not claim to, prove actual candidate attainability; that remains
`UNKNOWN` until a separately authorized public-only feasibility package.

## Failure criteria and authority boundary

The proposed successor must fail closed for a missing or non-IID seed
provenance record, overlap between any splits, noncanonical artifact,
development-tuned parameter, omitted comparator, malformed/non-finite score,
missing attempt, seed replacement, baseline-conditioned artifact retry,
generator or protocol drift, or an incomplete bootstrap disclosure. A later
hidden run must additionally reject any post-commitment change and score the
strongest baseline with the specified family-wise method.

This package neither modifies v4 nor accepts v4.1. It does not create a
candidate, data artifact, freeze receipt, evaluator, key, signature, hidden
input, score, gate result, release, recognition claim, runtime capability, or
NB-2 authorization. Only the Architecture Decision Owner can accept, reject,
or revise it.
