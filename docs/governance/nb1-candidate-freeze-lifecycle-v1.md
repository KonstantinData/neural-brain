# NB-1 Candidate Freeze Lifecycle Governance v1

## Status and purpose

This is a preparation-only lifecycle for a future public-only candidate freeze
under `EVAL-01.NB-1.safe-serial-cognition.v4`. It does not create a candidate,
store an artifact, establish a registry, sign anything, attach hidden material,
run an evaluation, pass a gate, authorize release, or enable runtime behavior.

The machine-readable contract is
[`../architecture/contracts/nb1-candidate-freeze-lifecycle-v1.json`](../architecture/contracts/nb1-candidate-freeze-lifecycle-v1.json).
ADR-018, Architecture Directive v4.0, the Recognition Standard, and the
existing hidden-evaluation boundary remain authoritative.

## Lifecycle and authority boundary

`draft -> submitted -> accepted` is an admissibility workflow only. Any
unknown or changed condition moves the receipt to `invalidated`. A later
receipt may be `superseded` only with immutable prior-record reference and new
independent acceptance; no record may be overwritten or deleted.

The implementation owner may prepare a public-only package. The independent
reviewer alone may accept reproducibility evidence subject to externally
designated role, custody, conflict, and registry process. Neither actor may
infer a gate pass, stage exit, release, recognition, model quality, or
hidden-data isolation merely from lifecycle state.

## Package, receipt, manifests, and versioning

The package binds a clean committed source tree, candidate bundle, model and
evaluation manifests, parameter/training/code/specification/generator/
dependency-lock digests, separate public train/development artifacts, and
dataset/split digests using only `nb1-eval-canonical-json-v1`: UTF-8 without a
byte-order mark, LF line endings, deterministic Unicode code-point ordering,
sorted object keys, compact JSON separators, no `NaN` or `Infinity`, and
v4-defined decimal values represented as strings. The lifecycle binds the
artifact-kind mapping in
`nb1-independent-evaluation-artifact-manifests-v1.json#/canonicalization/artifact_kind_byte_rules`:
`canonical_json_object`, `utf8_text`, `binary`, and
`deterministic_bundle_manifest`. Every artifact must use its exact mapped rule;
no alternative profile is admissible. Hidden seeds, examples, labels, latent
metadata, private keys, tokens, scores, and raw outcomes are prohibited; their
presence is a custody breach.

The receipt names immutable IDs, SemVer candidate version, bundle/manifest
digest map, registry reference, preparation time, and a limited claim boundary.
Every byte, field, digest, version, source, dependency, parameter, protocol,
threshold, generator, or canonicalization-profile change invalidates it. Silent
rebuilds, mutable tags, receipt reuse, backdating, registry overwrites, and v3
use are prohibited.

## Verification and handoff

The independent reviewer obtains the public-only bundle from external immutable
retention, recomputes all bindings, checks scope, version, supersession, and
registry status, then records an immutable outcome. Any future signature must
be externally detached Ed25519, registry-bound, independently checked, and
never substitutes for recomputation or independence.

After acceptance, only receipt ID, bundle digest, registry reference, and
public verification summary may go to a separate hidden-attachment review. It
cannot attach hidden material or start EVAL-01.

## Failure, rollback, and external decisions

Digest mismatch, drift, incomplete record, untrusted key status, registry
revocation, custody breach, or unreproducible canonicalization invalidates the
receipt. Rollback records an immutable reason and blocks downstream use; it
does not delete or repair the receipt. A replacement needs a new ID and review.

`CF-B1` requires a separately authorized public-only v4 candidate package.
`CF-B2` requires external appointment and attestation of independent reviewer,
registry custody, immutable storage, conflict handling, and revocation process.
Unknown identity, status, custody, or scope must be escalated to the designated
independent-review authority and blocks the workflow.
