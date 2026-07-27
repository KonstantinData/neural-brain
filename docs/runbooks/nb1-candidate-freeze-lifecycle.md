# NB-1 Candidate Freeze Lifecycle Runbook

## Purpose and stop boundary

Use this only to prepare a future public-only EVAL-01 v4 candidate-freeze
review. Do not create artifacts, keys, signatures, registry entries, hidden
attachments, evaluations, releases, or runtime behavior. Stop if scope, role
independence, custody, retention, registry status, canonicalization, or a
required binding is unknown.

## Preconditions

1. Confirm ADR-018 and EVAL-01 v4 are authoritative and v3 is rejected.
2. Confirm separate authorization for public-only candidate preparation.
3. Obtain external independent-review authority, reviewer/registry-custodian
   identity, conflict/separation evidence, immutable-retention process, and
   registry/revocation process. Repository identities never establish
   organizational independence.

## Procedure

1. In `draft`, enumerate only declared public inputs at deterministic canonical
   relative paths; reject hidden inputs, keys, labels, and outcomes.
2. Confirm clean source commit; complete model/evaluation manifests, receipt,
   and SHA-256 digest map under `nb1-eval-canonical-json-v1` only: UTF-8 without
   byte-order mark, LF, deterministic Unicode code-point ordering, sorted keys,
   compact separators, no `NaN`/`Infinity`, and v4 decimal strings. Before
   hashing, classify each artifact with
   `nb1-independent-evaluation-artifact-manifests-v1.json#/canonicalization/artifact_kind_byte_rules`:
   `canonical_json_object`, `utf8_text`, `binary`, or
   `deterministic_bundle_manifest`. Apply the exact mapped rule; do not
   substitute another canonicalization profile or apply object serialization to
   text, binary, or bundle artifacts.
3. Place public-only bytes in external immutable retention. This runbook does
   not execute storage.
4. Submit immutable bytes and receipt to the independent reviewer. Never alter
   submitted bytes to repair a defect.
5. Reviewer independently recomputes bindings, checks SemVer, supersession,
   registry state, and records accept, reject, or invalidated outcome.
6. If accepted, hand off only receipt ID, bundle digest, registry reference,
   and public verification summary to separately governed review. Do not attach
   hidden material or start evaluation.

## Failure and completion

For tampering, hash mismatch, manifest/version drift, incomplete artifact,
missing/untrusted required signature, mutable registry, unverifiable retention,
or custody breach: record invalidation externally, retain prior record, stop,
and escalate. Do not retry silently or use later scores as repair. A correction
requires a new receipt and fresh review.

Repository preparation is complete when contract, governance, runbook,
traceability, and tests validate. Real freeze remains blocked by `CF-B1` and
`CF-B2`; EVAL-01 remains blocked by its independent external prerequisites.
