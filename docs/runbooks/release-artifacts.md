# Release Artifacts and Provenance

## Purpose

Every Neural Brain release candidate is represented by a deterministic evidence
bundle. The bundle identifies the exact source commit, complete `uv.lock`
dependency graph, SPDX 2.3 SBOM, validated migration plan, resulting PostgreSQL
schema digest, and the versioned policy, architecture-contract, and ADR inputs.
It does not authorize or package a Stage 1 runtime before that stage is accepted.

## Pull-request validation

The `Release evidence` workflow checks pull requests with a read-only GitHub
token. It reproduces the frozen environment, revalidates the FND-03.3 security
workflow policy, runs the release tests, validates migrations against disposable
PostgreSQL 18 databases, and uploads a versioned validation artifact. Pull
requests do not receive OIDC or attestation write permission and cannot create a
release attestation.

## Tag and release attestation

Tags matching `v*` and published GitHub releases run the same validation. A
separate job then downloads the exact validated artifact and invokes the pinned
GitHub Artifact Attestation action. GitHub OIDC supplies the short-lived signing
identity; no signing key, API key, or repository secret is stored. The job has
only `contents: read`, `id-token: write`, and `attestations: write` permissions.

All external Actions use reviewed, dereferenced commit SHAs. Checkout always
sets `persist-credentials: false`. The workflow does not publish packages,
modify releases, or write repository contents.

## Evidence contents

For candidate `<version>`, the uploaded artifact contains:

- `neural-brain-<version>.release-manifest.json`;
- `neural-brain-<version>.build-metadata.json`;
- `neural-brain-<version>.locked-dependencies.json`;
- `neural-brain-<version>.sbom.spdx.json`; and
- `neural-brain-<version>.checksums.sha256`.

The manifest records the repository, full commit SHA, commit timestamp,
migration and schema digests, every migration file, and file digests plus
versions or statuses for policies, contracts, and ADRs. The checksum file binds
every other uploaded evidence file.

## Local deterministic build

Obtain the migration-plan and schema digests from a successful guarded
`tools/validate_migrations.py` run. Then run:

```text
python tools/build_release_evidence.py \
  --root . \
  --output-dir release-evidence \
  --artifact-version <version> \
  --source-commit <40-character-commit> \
  --source-timestamp <commit-ISO-8601-timestamp> \
  --repository <owner/name> \
  --migration-plan-sha256 <migration-plan-sha256> \
  --schema-sha256 <validated-schema-sha256> \
  --verify-git-head
```

The output directory must be absent or empty. A migration digest mismatch,
unknown document shape, invalid identity, stale output, or source/checkout
mismatch fails closed. Rebuilding from identical inputs produces byte-identical
files.

## Verification

For GitHub-hosted evidence, verify the attestation with GitHub CLI against this
repository and then verify the checksum file inside the downloaded artifact.
The attestation subject must match the candidate files and source workflow. A
missing or unverifiable attestation blocks a tag or release from being treated
as accepted release evidence.
