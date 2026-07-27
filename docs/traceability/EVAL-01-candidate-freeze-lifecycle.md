# EVAL-01 Candidate Freeze Lifecycle Traceability

## Objective

Define a preparation-only, public-only candidate-freeze lifecycle before a
future independent EVAL-01 v4 hidden-attachment review, without candidate,
registry, immutable store, signature, hidden artifact, evaluation, gate,
release, or runtime authority.

## Source mapping

| Source | Lifecycle mapping | Boundary |
| --- | --- | --- |
| ADR-018 and Architecture Directive v4.0 | Non-authorization, state transitions, fail-closed rules | No lifecycle state creates authority or effects. |
| Recognition Standard | Independent reviewer acceptance and no recognition claim | Independent held-out evidence remains external. |
| `nb1-hidden-evaluation.json` | v4 binding, public-only inputs, hidden-material exclusion | No hidden attachment/evaluation occurs. |
| `nb1-independent-evaluation-preparation-v1.json` | Receipt, custody, registry, signature, and review details | EVAL-01 B1–B3 remain unresolved. |

## Requirement mapping

| Requirement | Versioned artifact | Automated evidence | External evidence |
| --- | --- | --- | --- |
| Immutable receipt and canonical SHA-256 workflow | Lifecycle contract `canonicalization_and_hashing` requires `nb1-eval-canonical-json-v1` and exact `artifact_kind_byte_rules` mapping, `required_receipt` | Candidate-freeze contract test | Bundle and independent recomputation with the mapped JSON/text/binary/bundle rule. |
| Manifests and SemVer/supersession | Contract `required_manifests`, `versioning_and_supersession` | Drift test coverage | Reviewer acceptance and immutable registry. |
| Immutable registry/storage and handoff | Contract `registry_and_immutable_storage`, `verification_and_handoff` | Contract test | External custodian, retention, access audit, revocation. |
| Tamper/hash/manifest/version/completeness/signature rejection | Contract `preregistered_negative_tests`, `invalidation_and_rollback` | Contract test | Independent review execution. |
| Remaining decisions | Contract `external_blockers` | Required blocker fields test | CF-B1 public package; CF-B2 custody/approval. |

## Acceptance and non-claims

- [x] Lifecycle, receipt, digest, manifests, versioning, registry reference,
  verification, handoff, invalidation, rollback, and negative-test definitions
  are versioned.
- [x] Unknown and changed conditions fail closed without overwriting evidence.
- [x] External owners and exact unblocking actions are explicit.
- [x] No candidate, storage, key, signature, evaluation, gate, release,
  recognition, runtime, or external effect is implemented or claimed.
- [ ] Real public-only candidate, independent registry/storage, reviewer
  acceptance, hidden attachment, and EVAL-01 evidence are external follow-ons.
