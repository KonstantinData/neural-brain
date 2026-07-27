# NB-1 Independent Evaluation Preparation Runbook

## Purpose and stop boundary

Use this runbook only to prepare an external independent hidden evaluation under EVAL-01 v4. It does not authorize candidate training, candidate export, hidden-data generation or attachment, external scoring, key creation, signing, runtime behavior, release, or recognition. Stop immediately if any required external role, accepted registry record, v4-bound freeze receipt, or scope of this preparation is unknown.

## Inputs and custody

Required public repository inputs:

- `docs/architecture/evaluations/nb1-safe-serial-cognition-v4.json`;
- `docs/architecture/evaluations/nb1-serial-context-generator-v4.json`;
- `docs/architecture/contracts/nb1-hidden-evaluation.json`;
- `docs/architecture/contracts/nb1-independent-evaluation-preparation-v1.json`.

External inputs are required but must not be copied into the repository: role identity and separation attestations; reviewer-controlled registry records; public keys; private-key custody evidence; hidden commitment; hidden seed, examples, labels, and latent metadata; evaluator ledger; aggregate evidence; and detached signature.

## Preparation checklist

1. Confirm that EVAL-01 v4 is frozen and EVAL-01 v3 is rejected. Confirm that this preparation has no gate, release, or recognition result.
2. Ask the designated independent-review authority to appoint and attest implementation owner, hidden-artifact provider, evaluator, reviewer, and registry custodian. Record conflicts, qualifications, reporting-line separation, key revocation process, and reviewer authority outside the repository.
3. Establish reviewer-controlled registries for specification digest, candidate freeze receipt digest, hidden commitment digest, role attestations, trusted Ed25519 public keys/status, and evaluation protocol digest. Reject self-supplied or stale entries.
4. Prepare a public-only v4 candidate-freeze task only after approval. Require a clean committed tree and bind every freeze-receipt digest, including separate public train/development artifact and dataset/split digests plus the generator-contract digest. Require the declared model- and evaluation-manifest field sets. Do not attach a hidden artifact.
5. Before any hidden scoring, require reviewer acceptance of the v4 freeze receipt and provider pre-run commitment. Verify that the commitment is sealed from the implementation owner.
6. Require evaluator process plans for fresh read-only network-disabled candidate execution, evaluator-owned baselines and ablations, bounded resources, append-only attempt finalization, and aggregate-only disclosure.
7. Require reviewer test evidence for revoked keys, invalid signatures, missing ledger entries, post-freeze changes, duplicate/replaced attempts, contamination, and claim-boundary violations.

## Evidence intake handoff

The evaluator may hand off only aggregate, signed evidence permitted by the existing hidden-evaluation contract. The reviewer independently verifies registry bindings, signature validity, ledger completeness, contamination report, hard-failure report, resource bounds, and the non-claim boundary. Detailed examples, labels, hidden seed, private keys, raw per-sequence outcomes, and provider-private generator details must never be handed to the implementation owner.

## Failure handling

Treat every unknown, missing, stale, revoked, mismatched, unsigned, self-signed, leaked, post-freeze, duplicate, incomplete, crashed, aborted, or undisclosed item as a fail-closed stop. Do not retry silently, recreate a ledger entry, alter a candidate after hidden attachment, substitute a local agent for independence, or infer a pass from a signature or score.

## Completion condition for preparation

Preparation is complete only when the versioned preparation contract, governance record, traceability record, and repository tests exist and the remaining external decisions are explicit. It is not completion of EVAL-01. EVAL-01 remains blocked until the external roles, registries, v4 candidate freeze, hidden commitment, independent evaluation, and independent admissibility review exist.
