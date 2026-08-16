# EVAL-01 External Operating Package Proposal Traceability

## Objective

Define the exact proposed-only operating sequence for future external EVAL-01
v4 work without creating external actors, evidence, keys, hidden data,
evaluation, gate passage, stage exit, release, runtime, or NB-2 activation.

## Requirement mapping

| Requirement | Versioned artifact | Automated evidence | External evidence still required |
| --- | --- | --- | --- |
| Architecture clarification precedes any v4 operation | Operating-package proposal `OP-B1`, `OP-01` | `test_nb1_eval01_v4_external_operating_package_proposal.py` | Accepted ADR-018/v4 clarification or an explicit rejected disposition; the proposal defines no evaluation criterion or value |
| External appointment and organizational separation | `OP-B2`, `OP-02` | Structural non-appointment and fail-closed checks | Externally attested identities, organizations, reporting lines, mandates, qualifications, conflicts, validity, deputies, and handoffs |
| Sole evaluator v4 hidden custody and pre-run commitment | Reconciliation proposal, `OP-05` | V4 sole-custody and legacy-route rejection checks | Sealed external artifact, sole-custody attestation, and non-disclosing commitment |
| Registry, signing key, validity, revocation | `OP-03`, `OP-07`, `OP-08` | Unknown/revoked/self-supplied evidence requirements | Reviewer-controlled registry, trusted Ed25519 public key, custody, status, and revocation records |
| Freeze, isolated execution, complete ledger, aggregate evidence | `OP-04` through `OP-07` | Ordered owner/action and claim-boundary checks | Reviewer-recomputed receipt; fresh network-disabled records; append-only complete ledger; aggregate signed evidence |
| Independent admissibility and gate review | `OP-08`, `OP-09` | No automatic gate/stage/release/runtime/NB-2 claim | Independent reviewer recommendation and separately authorized gate-review disposition |
| Legacy separate-provider reconciliation | Reconciliation proposal | Explicit proposed-only legacy treatment | Accepted successor decision before inherited generator/runbook/evidence schema can be used for v4 |

## Fail-closed test plan

- `tests/architecture/test_nb1_eval01_v4_external_operating_package_proposal.py`
  verifies the proposal is non-authorizing, requires OP-B1 to OP-B3, keeps
  v4 sole evaluator custody, preserves the ordered owner/action workflow, and
  denies automatic gate, stage, release, runtime, or NB-2 claims.
- The existing independent-evaluation preparation, organization,
  artifact-manifest, candidate-freeze lifecycle, and hidden-evaluation
  contract tests remain required structural evidence.
- After an accepted clarification, add successor tests that reject all use of
  inherited separate-provider execution surfaces for v4 until their schema and
  runbook are explicitly revalidated. Do not alter frozen v4 retroactively.

## Acceptance and non-claims

- [x] Proposed owner/action sequence, records, separation, custody, registry,
  key/revocation, commitment, isolated execution, aggregate-signature, and
  gate-review boundaries are traceable.
- [x] Legacy provider/evaluator expectations are identified as a proposed
  replacement pending an accepted clarification.
- [x] Repository regression coverage rejects a false authorization claim.
- [ ] No external appointment, attestation, registry, key, candidate, hidden
  artifact, commitment, evaluation, signature, independent review, gate result,
  stage exit, release, runtime activation, or NB-2 activation exists.
