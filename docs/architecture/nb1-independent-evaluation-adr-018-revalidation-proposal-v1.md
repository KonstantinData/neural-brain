# NB-1 Independent Evaluation Artifact-Manifests ADR-018 Revalidation Proposal v1

- Status: Proposed; not accepted and not runtime authorization
- Date: 2026-07-27
- Parent work package: `EVAL-01`
- Depends on: ADR-018; Architecture Directive v4.0; Recognition Standard;
  EVAL-01 v4 preregistration; `nb1-hidden-evaluation.json`

## Purpose and authority

This proposal defines the decision boundary for a future independent reviewer
to accept a candidate-freeze receipt and its manifest chain. It is a
non-instantiating preparation artifact. It does not create a candidate, data,
seed, key, signature, receipt, registry, evaluation result, authority,
promotion, release, or runtime capability.

ADR-018 requires immutable learning candidates and independent evidence. The
Architecture Directive v4.0 and Recognition Standard require independent,
held-out, non-compensatory evidence. An accepted successor decision must keep
hidden material and protected authority outside the implementation owner and
must deny unknown lineage, version, scope, evaluation, or custody states.

## Proposed decision boundary

The future accepted decision must require canonical manifest and receipt
bindings for the v4-only candidate, source tree, parameters, public training
and development artifacts, model, evaluation protocol, generator, split,
environment, dependencies, resource declarations, reviewer recomputation, and
receipt signature. The exact `nb1-eval-canonical-json-v1` byte profile requires
a UTF-8-without-BOM, NFC-normalized root object with sorted member names, no
outside-string whitespace, fixed escaping, shortest non-negative integer
encoding, lowercase literals, and no trailing bytes. SHA-256 digests bind those
canonical bytes. The same profile maps every bound artifact kind explicitly:
JSON manifests use the exact object profile; UTF-8 text binds its exact valid
stored bytes without normalization; binary binds raw bytes; and a directory or
bundle binds a deterministic canonical manifest of verified regular-file
digests. Undefined artifact kinds and any unspecified normalization,
compression, decoding, metadata transformation, symlink, or path traversal are
rejected. Detached Ed25519
signatures bind only their stated bytes and identity records. They do not prove
organizational independence or pass an evaluation gate.

The contract contains four non-sensitive deterministic test-vector descriptors:
a Unicode JSON object, UTF-8 text, binary bytes, and a Unicode-path bundle
manifest. Each descriptor carries literal encoded input bytes and a fixed
SHA-256 value so any later implementation can recompute the digest without
hidden material, keys, registry access, or an evaluation run. They are protocol
test fixtures only and do not instantiate an artifact or receipt.

The future decision must define external, reviewer-controlled registry and
attestation custody, key acceptance and revocation, immutable storage,
chain-of-custody events, conflict handling, expiry, transfer, quarantine, and
destruction evidence. Until an accepted revalidation explicitly changes this
rule, the independent evaluator alone is the v4 hidden-dataset custodian and
may possess the hidden seed, raw examples, labels, or latent variables. A
separate hidden-dataset provider is prohibited. Neither this repository nor the
implementation owner may hold hidden material, including encrypted or derived
substitutes.

Any source, dependency, parameter, candidate, manifest, generator, split,
protocol, canonicalization, key-status, or custody change after freeze
invalidates the receipt and requires a new independent review. Unknown,
unsigned, revoked, stale, noncanonical, incomplete, or mismatched evidence is
inadmissible and blocks hidden attachment, scoring, gate review, release, and
recognition.

## Exclusions until acceptance

Until a successor decision is accepted and the external operating model is
independently established, this proposal excludes candidate generation,
artifact storage, immutable registry operation, signing-key generation or use,
hidden-data handling, evaluation, scoring, model promotion, stage exit, release
and every runtime or external effect. It cannot amend ADR-018, the EVAL-01 v4
preregistration, or the rejection of v3.

## Required decision owners and acceptance evidence

The architecture decision owner must accept an ADR-018-conformant successor or
record another accepted disposition. The independent-review authority must
approve role separation, reviewer/registry/key custody, and the admissibility
workflow. The implementation owner supplies a public-only freeze package;
the independent reviewer recomputes every declared digest. The independent
evaluator and reviewer must separately attest custody, non-disclosure, conflicts,
execution isolation, and evidence admissibility. Any proposal to add a separate
hidden-dataset provider requires an accepted ADR-018 revalidation before role
assignment or material transfer.

Required pre-implementation review includes manifest completeness, canonical
serialization, digest recomputation, unsigned/revoked-key rejection, version
drift invalidation, hidden-material exclusion, chain-of-custody continuity, and
claim-boundary checks. These are acceptance conditions for a later decision,
not evidence that the conditions now hold.

## Validation boundary

`tests/architecture/test_nb1_independent_evaluation_artifact_manifests_contract.py`
checks that the versioned schema remains v4-only, non-instantiating, canonical,
fail-closed, and non-authorizing. It is not a candidate freeze, signature
verification run, independent evaluation, security certification, release, or
recognition evidence.
