# NB-1 Independent Evaluation Preparation v1

## Status and purpose

This is a preparation-only governance artifact for `EVAL-01.NB-1.safe-serial-cognition.v4`. It makes the external custody, reproducibility, registry, review, and evidence expectations explicit before a hidden evaluation is contemplated. It does not create a candidate, hidden artifact, key, signature, attestation, evaluator, approval, evaluation result, gate result, release, recognition claim, runtime capability, or external effect.

The governing architecture remains ADR-018 and Architecture Directive v4.0. EVAL-01 v4 is frozen preregistration that can contribute only to G0/G1 evidence when independently executed and accepted. EVAL-01 v3 remains rejected history and is never eligible for hidden attachment or evidence intake.

The machine-readable authority for this preparation is [`../architecture/contracts/nb1-independent-evaluation-preparation-v1.json`](../architecture/contracts/nb1-independent-evaluation-preparation-v1.json). Existing candidate-boundary and signed-evidence intake behavior remains governed by [`../architecture/contracts/nb1-hidden-evaluation.json`](../architecture/contracts/nb1-hidden-evaluation.json).

## Non-negotiable boundaries

- Only a clean, committed, public-only, v4-bound candidate package with the complete freeze receipt may be submitted for review. The receipt binds the public train and development artifacts, their dataset/split digests, and the generator-contract digest separately from the training artifact. Its model manifest must identify model version/architecture, code, parameters, training, public splits, specification, generator, and resource bounds; its evaluation manifest must bind protocol/specification, candidate, baselines/ablations, thresholds/failure criteria, confidence method, budgets, environment, and evaluator executable. A changed source tree, dependency lock, parameter, model manifest, generator, protocol, threshold, or candidate code invalidates the freeze.
- The hidden seed, examples, labels, latent metadata, provider implementation details, and per-sequence correctness stay outside the implementation trust domain. Frozen EVAL-01 v4 binds the Hidden Dataset Provider duty to `independent_evaluator_only`; a separate provider/evaluator organization is prohibited until an accepted v4 revalidation. These materials must not enter this repository, a candidate process, logs, bundles, or reports returned to the implementation owner.
- Candidate code receives only permitted opaque identifiers and unlabeled observations; it cannot receive scores, thresholds, baselines, ablations, correctness, gate decisions, or recognition decisions.
- The candidate process is fresh, read-only, network-disabled, bounded, and effect-free. Scoring, baseline and ablation execution, attempt accounting, and aggregate reporting belong to the independent evaluator.
- A subagent, branch, worktree, repository permission, process label, or `independent:*` identifier does not establish organizational separation.
- A signature has only the limited cryptographic meaning stated in the contract. It cannot prove independence or pass a gate by itself.

## Required external roles and separation evidence

| Role | Owns | Must be independent from | Evidence required before use |
| --- | --- | --- | --- |
| Implementation owner | Public source and candidate preparation | Provider, evaluator, reviewer registry decisions | Named responsibility and conflict disclosure |
| Hidden artifact provider | Logical duty: hidden seed, artifact, labels, pre-run commitment | Separate provider organization is prohibited by frozen v4 | Independent evaluator custody and commitment attestations |
| Independent evaluator | Scoring executable, baselines, ablations, append-only ledger, aggregate report, signing-key custody, and frozen-v4 provider duty | Implementation owner and reviewer | Identity, organization, process isolation, custody, key custody, and separation attestations |
| Independent reviewer | Candidate admissibility, registry custody, identity/key acceptance, evidence admissibility recommendation | Implementation owner, provider, evaluator | Identity, qualification, registry custody, conflict, and separation attestations |

The designated independent-review authority must approve the identities, organizational separation, qualifications, conflicts, registry custodian, and admissibility workflow outside this repository. This governance text does not appoint those persons or organizations.

## Required external records

The reviewer-controlled external registry must bind the accepted v4 specification, complete candidate freeze receipt, pre-run hidden commitment, role attestations, trusted Ed25519 public key/status, and accepted evaluation-protocol digest. It must reject unknown, stale, revoked, mismatched, self-supplied, or unverifiable records.

The evaluator-owned ledger is append-only and includes every completed, failed, aborted, crashed, duplicate, and missing-output attempt. Each entry binds the previous entry digest, candidate and hidden-artifact digests, inputs and prediction batch digests, executable and environment digests, timestamps, status, and failure digest when applicable. Omission or retry replacement makes the evidence inadmissible.

All signed aggregate evidence uses canonical JSON, SHA-256, and detached Ed25519 signatures. Private keys, secrets, hidden material, and raw outcome data remain external. Signed evidence must state a claim boundary that excludes a gate pass, stage exit, release, production status, and Neural Brain Candidate recognition.

## Review sequence

1. The independent reviewer accepts the v4 preregistration, protocol digest, role evidence, separation evidence, and external registry custody.
2. The implementation owner submits the public-only v4 candidate freeze package. The reviewer recomputes its declared digests and rejects any incomplete or changed binding.
3. The independent evaluator performing the frozen-v4 provider duty records a pre-run commitment; the reviewer checks commitment completeness and split-isolation/search-space attestations without receiving or exposing the hidden artifact.
4. The evaluator runs the accepted frozen bundle and evaluator-owned comparison modes in fresh network-disabled processes, finalizing each attempt in the ledger.
5. The evaluator returns only permitted aggregate evidence and detached signature. The reviewer performs the admissibility review.
6. A separately authorized evaluation-gate reviewer may assess the admissible evidence. No prior step passes a gate automatically.

## Remaining blockers

| Blocker | Owner | Required decision/evidence | Concrete next action |
| --- | --- | --- | --- |
| No v4 candidate freeze receipt | Implementation owner and independent reviewer | Complete public-only v4 candidate plus reviewer-recomputed receipt | Run a separately authorized public-only candidate-freeze task; do not attach hidden material. |
| No independent actors or registries | Designated independent-review authority | Appointment, qualifications, conflict/separation, registry/key custody, and revocation process | Establish and attest the four roles outside the implementation trust domain. |
| No hidden commitment or independent evidence | Provider, evaluator, then reviewer | Pre-run commitment, sealed custody, complete ledger, aggregate report, contamination/failure evidence, detached signature | Perform only after the preceding two blockers have been accepted. |

Unknown, missing, stale, contradictory, self-certified, scope-mismatched, unsigned, revoked, leaked, repeated, post-freeze, or incompletely disclosed evidence blocks the next step. It is never repaired by an aggregate score or a later favorable result.
