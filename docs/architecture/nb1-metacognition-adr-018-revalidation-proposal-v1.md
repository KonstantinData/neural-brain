# NB-1 Metacognition ADR-018 Revalidation Proposal v1

- Status: Proposed prerequisite; not accepted and not runtime authorization
- Task: NB1-EVIDENCE-20260816
- Governing target: ADR-018 and Architecture Directive v4.0
- Delivery boundary: NB-1 internal, effect-free proposal boundary only

## Purpose and authority

NB-1 work packages request internal `continue`, `ask`, `defer`, and `stop`
proposals, while the executable NB-1 slice contract currently implements only
`continue` and `ask` and explicitly reserves `defer` and `stop`. This proposal
records that authority gap. It does not amend the contract, enable a runtime
decision, define an uncertainty threshold, or alter EVAL-01 v4.

The existing activation-ambiguity value is an uncalibrated internal heuristic.
It is not a probability, confidence guarantee, competence estimate, risk
estimate, calibration result, evaluation result, or gate outcome. The
calibrated uncertainty, risk-coverage, OOD, and error-awareness evidence that
would support a calibration claim remains an NB-6 prerequisite.

## Required accepted disposition

Before `defer` or `stop` can be implemented, an Architecture Decision Owner
must accept, replace, or reject an ADR-018-aligned contract amendment. The
accepted amendment must specify, without delegating authority to untrusted
content:

1. typed input provenance and the distinction between activation ambiguity,
   epistemic uncertainty, aleatoric uncertainty, and any later calibration;
2. the deterministic, bounded selection and tie semantics for each internal
   decision, including the default when information is missing, conflicting,
   stale, or out of scope;
3. whether an internal `defer` or `stop` proposal is checkpointed, its required
   audit envelope, expiry, recovery, and idempotent replay semantics;
4. the boundary that keeps every decision an internal proposal, never an Action
   Intent, Goal transition, authority, approval, policy decision, tool call,
   external effect, model mutation, or evaluation-gate result; and
5. a separately preregistered calibration evaluation design, including held-out
   data provenance, metric, threshold, failure rule, contamination control,
   recovery tests, and the delivery stage to which it belongs.

No numeric cutoff, metric, threshold, calibration claim, candidate criterion,
or evaluator rule is defined by this proposal. Those values remain absent until
the required accepted decision and preregistration exist.

## Existing NB-1 evidence that may proceed

The current NB-1 slice can retain its bounded `continue` and `ask` heuristic as
an explicitly uncalibrated internal proposal. It may add effect-free tests for
authenticated scope isolation, Memory Transition Gate ownership, input-field
rejection, durable-commit recovery, deterministic development replay, and the
already preregistered ablation declarations. Such tests cannot create an
evaluation pass, a v4 candidate, a freeze receipt, hidden material, an
independent evaluator, or stage-exit evidence.

## EVAL-01 v4 and reproducibility boundary

EVAL-01 v4 already fixes its own baseline and ablation declarations. Its public
candidate/freeze path remains blocked because the current frozen generator does
not supply an accepted executable public seed commitment, complete HMAC pipeline
mapping, or baseline ceiling. This proposal neither supplies those missing
criteria nor permits reuse or relabelling of rejected v3 artifacts. A separate
accepted EVAL-01 v4 clarification is required before public v4 candidate work.

## Non-claims

This proposal creates no runtime implementation authority, migration, protected
state transition, external effect, online training, active-model mutation,
candidate, freeze receipt, hidden dataset, evaluator identity, independent
review, evaluation result, gate pass, NB-1 exit, NB-2 activation, recognition,
or production claim.

## Validation

`tests/architecture/test_nb1_metacognition_adr_018_revalidation_proposal.py`
validates the proposal's non-authorizing, non-calibration, and fail-closed
boundary only. It is not behavioral, independent, evaluation, or release
evidence.
