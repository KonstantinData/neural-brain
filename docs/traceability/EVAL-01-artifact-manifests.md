# EVAL-01 Artifact-Manifests Preparation Traceability

## Objective

Version the minimum non-instantiating schema for a future EVAL-01 v4 candidate
freeze receipt, model/evaluation/dataset manifests, canonical digest and
signature references, and chain-of-custody evidence. No candidate, dataset,
hidden material, key, receipt, signature, registry record, evaluation, release,
or recognition claim is created.

## Normative sources

- ADR-018 and Architecture Directive v4.0: protected two-plane boundary,
  immutable candidate provenance, independent evidence, and deny-by-default.
- `docs/architecture/neural-brain-recognition-standard.md`: independent held-out
  evidence and non-compensatory recognition requirements.
- `docs/architecture/evaluations/nb1-safe-serial-cognition-v4.json`: frozen v4
  preregistration and candidate-freeze prerequisite.
- `docs/architecture/contracts/nb1-hidden-evaluation.json`: candidate/evaluator
  separation and signed-evidence boundary.
- `docs/architecture/contracts/nb1-independent-evaluation-preparation-v1.json`:
  repository-side preparation and B1–B3 external blockers.

## Requirement-to-artifact mapping

| Requirement | Versioned artifact | Automated evidence | External evidence still required |
| --- | --- | --- | --- |
| V4-only freeze receipt and model lineage | Artifact-manifests contract: `candidate_freeze_receipt_schema`, `model_manifest_schema` | `test_v4_only_non_instantiating_claim_boundary_and_receipt_fields` | Public-only candidate, canonical receipt and independent reviewer recomputation |
| Evaluation, dataset, generator and split bindings | Contract: `evaluation_manifest_schema`, `dataset_and_generator_manifest_schema` | `test_manifest_schemas_bind_public_and_hidden_custody_without_disclosure` | Independent-evaluator sole-custody and split-isolation attestations; a separate provider remains prohibited pending accepted revalidation |
| Exact canonical SHA-256 / Ed25519 rules for JSON, text, binary and bundles | Contract: `canonicalization`, `artifact_reference_schema`, `registry_and_attestation_schema` | `test_canonical_digest_signature_and_registry_rules_fail_closed`, `test_artifact_kind_rules_cross_contract_bindings_are_consistent` | Reviewer-controlled trusted key registry, key status and detached signatures |
| Chain of custody and role attestations | Contract: `chain_of_custody_schema`, `registry_and_attestation_schema` | `test_chain_of_custody_and_attestation_requirements_are_complete` | Independent role, conflict, custody and transfer evidence |
| No false operational claim | Claim boundary, ADR-018 revalidation proposal and external blockers | `test_version_drift_unsigned_and_hidden_repository_states_are_denied` | Accepted ADR disposition and all external B1–B3 evidence |

## Acceptance criteria

- [x] Manifest, receipt, custody, canonicalization, attestation, registry and
  chain-of-custody schemas are versioned without instantiating their subjects.
- [x] The exact `nb1-eval-canonical-json-v1` byte profile and the schema fail
  closed for absent, unsigned, revoked, noncanonical,
  mismatched, drifted, or hidden-material-contaminated evidence.
- [x] The profile maps JSON, UTF-8 text, binary, and deterministic bundle
  artifacts to exact digest inputs and rejects every undefined transformation.
- [x] Four literal, non-sensitive vectors bind Unicode JSON, UTF-8 text, binary,
  and a Unicode-path bundle to recomputable SHA-256 values without creating an
  evaluation artifact, key, receipt, or hidden material.
- [x] The proposed ADR-018 decision boundary is explicit and non-authorizing.
- [ ] Independent evaluator sole-custody appointment, immutable storage, registry/key custody,
  candidate freeze, hidden commitment, evaluation, and admissibility review are
  external prerequisites, not repository facts.

## Verification record

The controller must run the focused contract test, JSON validation, and the
combined repository quality gates after integration. A passing documentation
test verifies only schema completeness and exclusion boundaries.
