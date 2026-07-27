# EVAL-01 Independent Evaluation Preparation Traceability

## Objective

Prepare the repository-side, fail-closed contract and handoff evidence for a future independent EVAL-01 v4 hidden evaluation without producing a candidate, hidden data, evaluation result, signature, runtime behavior, release, or recognition claim.

## Normative sources

- ADR-018: complete protected cognitive-system boundary and non-compensatory evidence requirement.
- `docs/architecture/architecture-directive-v4.0.md`, sections 10, 12–14: immutable candidates, independent evidence, NB-1 effect-free boundary, and release stops.
- `docs/architecture/neural-brain-recognition-standard.md`: independent, held-out, causal evidence and non-compensatory recognition gates.
- `docs/architecture/evaluations/nb1-safe-serial-cognition-v4.json`: frozen EVAL-01 v4 preregistration.
- `docs/architecture/evaluations/nb1-serial-context-generator-v4.json`: hidden split, non-enumerability, and custody rules.
- `docs/architecture/contracts/nb1-hidden-evaluation.json`: existing candidate/evaluator and signed-evidence boundary.

## Requirement-to-artifact mapping

| Requirement | Versioned artifact | Automated evidence | External evidence still required |
| --- | --- | --- | --- |
| v4-only candidate freeze and reproducible digest bindings | `docs/architecture/contracts/nb1-independent-evaluation-preparation-v1.json` `candidate_freeze`, including separate public train/development, dataset/split, and generator-contract digests plus model/evaluation manifest fields | `tests/architecture/test_nb1_independent_evaluation_preparation_contract.py` | Reviewer recomputation and accepted freeze receipt |
| Hidden seed/data custody and separation | Contract `custody_and_separation` | Architecture test prohibits disclosure and self-certification | Provider/evaluator/reviewer identity, conflict, custody, and separation attestations |
| Registry, key, signature, and evidence-ledger requirements | Contract `registry_and_evidence_requirements` | Architecture test asserts registry/ledger/signature requirements | Reviewer-controlled registry, trusted key records, external ledger, detached signature |
| Review workflow and fail-closed response | Contract `review_workflow` and `fail_closed`; governance/runbook | Architecture test asserts no evaluation/release/recognition claim | Independent reviewer admissibility and gate review |
| Exact external blockers | Contract `external_blockers`; governance/runbook | Architecture test asserts owner/evidence/unblocker fields | Human/external completion of B1–B3 |

## Acceptance criteria

- [x] Repository-side candidate freeze, reproducibility, custody, registry, ledger, attestation, signature, role, review, and test-plan requirements are versioned without creating protected or external artifacts.
- [x] The contract fails closed for unknown or unverifiable inputs and preserves the EVAL-01 v4 / v3-rejection boundaries.
- [x] The external owners, evidence, approvals, impacts, and concrete unblockers are explicit.
- [x] Architecture tests verify the preparation contract and no runtime, release, or recognition authority is introduced.
- [ ] External independent roles, registries, candidate freeze, hidden commitment, scoring, evidence, and admissibility review exist. These are deliberately outside this repository task.

## Verification record

The controller records integrated commands, results, commit, and Notion coordination evidence. This slice must remain marked as preparation only until the external blockers are independently resolved.
