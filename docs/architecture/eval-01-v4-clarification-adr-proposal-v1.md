# EVAL-01 v4 Clarification ADR Proposal v1

- Status: Proposed; not accepted and not effective
- Date: 2026-08-16
- Parent work package: `EVAL-01`
- Governing sources: ADR-018 and Architecture Directive v4.0
- Proposed amendment: `evaluations/nb1-safe-serial-cognition-v4-clarification-amendment-v1.json`

## Decision request

The Architecture Decision Owner is asked to accept, reject, or revise the
proposed EVAL-01 v4.1 clarification. It preserves the frozen v4.0
preregistration as immutable history and does not train a candidate, create or
access hidden material, appoint an independent party, or pass any gate.

The current v4 source set lacks a numerical and algorithmic baseline ceiling,
literal public train/development seeds, and a fully executable HMAC mapping.
It also conflicts with the legacy hidden-evidence runner, which requires
separate provider and evaluator organizations although frozen v4 assigns the
logical provider duty to the evaluator alone. These omissions make a v4 public
candidate/freeze recipe inadmissible under the existing fail-closed rules.

## Proposed decision

If accepted, create `EVAL-01.NB-1.safe-serial-cognition.v4.1` from the exact
versioned amendment. The successor must retain the v4.0 identifier, digest,
and rejected-v3 history as immutable provenance; it must not mutate or
retroactively reinterpret either earlier specification.

The proposal fixes the following points precisely:

- Public train and development each receive a 32-byte, literal public seed,
  deterministic derivation input, split identifier, and artifact size.
- The HMAC-SHA-256 input grammar, rejection sampling, domains, byte-to-world,
  scenario, feature/noise/state, constraint, and canonical serialization rules
  are complete and language-independent.
- Every named baseline has a fixed algorithm, public-train selection/tie rule,
  exact pre-scoring ceiling of `0.750000`, and required validation-report
  fields. The candidate must still exceed the strongest baseline by the
  separately preregistered confidence-bound threshold; the ceiling does not
  weaken that threshold.
- A future v4.1 candidate-freeze receipt binds the amendment, both public seed
  commitments, implementation, constraint, baseline-ceiling, and existing
  public artifact/manifests. Unknown, missing, changed, or
  non-recomputable bindings invalidate it.
- For v4.1 only, the independent evaluator is the sole hidden-material
  custodian and performs the logical provider duty. The legacy separate
  provider/evaluator runner, schema, and tests are explicitly superseded for
  v4.1 and remain only immutable, inadmissible historical evidence.

## Authority and non-authorization

This proposal is not an amendment to ADR-018 or Directive v4.0. It is a
proposed preregistration successor. Acceptance does not itself authorize
candidate training, a candidate receipt, a registry entry, hidden-data
creation/access, evaluator appointment, key/signature use, hidden evaluation,
gate review, stage exit, release, recognition, runtime activation, or NB-2.
Every unknown scope, lineage, algorithm, custody, key, or evaluation state
remains denied.

## Acceptance criteria

- [ ] The Architecture Decision Owner explicitly accepts a v4.1 successor and
  records the disposition of this proposal.
- [ ] The accepted successor copies the amendment without changing its public
  seed commitments, HMAC mapping, baseline ceiling, or receipt delta.
- [ ] Review confirms that `0.750000` is compatible with the existing `0.8`
  full-mechanism threshold and `0.05` lower-confidence-bound lift, without
  substituting a ceiling check for either requirement.
- [ ] A post-acceptance, public-only implementation package updates the
  generator/specification, receipt contracts, traceability, and tests.
- [ ] That package replaces or marks the legacy provider/evaluator code,
  runbook, and tests as legacy-only for v4.1 before any hidden handoff.
- [ ] Independent review validates the public-only recipe and receipt chain;
  external appointment, registry, key custody, and hidden evaluation remain
  separately required.

## Review questions

1. Is the proposed `0.750000` ceiling appropriate for every listed baseline,
   given the existing full-model and confidence-bound thresholds?
2. Does the HMAC grammar and integer-only mapping provide enough
   cross-language determinism, including every rounding, rejection, and
   serialization edge case?
3. Should v4.1 retain evaluator-only hidden custody, or is there an accepted
   reason to design a different custody model before any implementation starts?
4. Are the additional receipt bindings sufficient for an independent reviewer
   to reproduce public train/development generation and baseline validation?
5. Does the legacy supersession list cover every operational provider/evaluator
   assumption before a v4.1 hidden handoff is considered?

## Migration and compatibility

No database migration, runtime migration, or protected-state migration is
authorized. The change is a future, repository-versioned evaluation-contract
successor only. v3 remains rejected; v4.0 remains frozen but insufficient for
candidate generation; legacy provider/evaluator code and records remain
historical and cannot be relabelled as v4.1. Existing candidate exports stay
blocked until a separate public-only package is accepted and independently
reviewed.

## Minimal authorized next package after acceptance

`EVAL-01 v4.1 public recipe and freeze-contract preparation` is the only
authorized next repository package. It may add the accepted v4.1 generator and
specification, deterministic public artifact generator, receipt/schema delta,
legacy-only guards, traceability, and the listed contract tests. It may not
train a candidate, create a receipt, operate storage/registry, appoint roles,
create keys/signatures, create or access hidden material, run evaluation,
claim a gate/stage/release, or begin NB-2.
