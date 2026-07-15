"""Build deterministic, attestable release evidence from repository inputs."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from datetime import UTC, date, datetime, time
from pathlib import Path
from typing import Final

ROOT: Final = Path(__file__).resolve().parents[1]
SHA256_PATTERN: Final = re.compile(r"^[0-9a-f]{64}$")
COMMIT_PATTERN: Final = re.compile(r"^[0-9a-f]{40}$")
VERSION_PATTERN: Final = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
REPOSITORY_PATTERN: Final = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
ADR_PATTERN: Final = re.compile(r"^ADR-(?P<number>[0-9]{3})-.+\.md$")
MIGRATION_PATTERN: Final = re.compile(r"^(?P<sequence>[0-9]{4})_[a-z0-9]+(?:_[a-z0-9]+)*\.sql$")


@dataclass(frozen=True, slots=True)
class ReleaseEvidenceInputs:
    """Validated inputs that identify one release candidate."""

    artifact_version: str
    source_commit: str
    source_timestamp: str
    repository: str
    migration_plan_sha256: str
    schema_sha256: str


@dataclass(frozen=True, slots=True)
class MigrationEvidence:
    """Normalized migration input included in release evidence."""

    sequence: int
    name: str
    content_sha256: str


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest of one file."""

    return _sha256_bytes(path.read_bytes())


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def _discover_migrations(directory: Path) -> tuple[MigrationEvidence, ...]:
    migrations: list[MigrationEvidence] = []
    for expected_sequence, path in enumerate(sorted(directory.glob("*.sql")), start=1):
        match = MIGRATION_PATTERN.fullmatch(path.name)
        if match is None or int(match.group("sequence")) != expected_sequence:
            raise ValueError("migration filenames must be contiguous from 0001")
        normalized = path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
        if not normalized.strip():
            raise ValueError(f"migration is empty: {path.name}")
        migrations.append(
            MigrationEvidence(
                sequence=expected_sequence,
                name=path.name,
                content_sha256=_sha256_bytes(normalized.encode("utf-8")),
            )
        )
    return tuple(migrations)


def _migration_plan_digest(migrations: tuple[MigrationEvidence, ...]) -> str:
    payload = [
        {"name": migration.name, "sequence": migration.sequence, "sha256": migration.content_sha256}
        for migration in migrations
    ]
    return _sha256_bytes(_canonical_json(payload).rstrip(b"\n"))


def _write_json(path: Path, value: object) -> None:
    path.write_bytes(_canonical_json(value))


def _normalize_toml(value: object) -> object:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()
    if isinstance(value, list):
        return [_normalize_toml(item) for item in value]
    if isinstance(value, dict):
        normalized: dict[str, object] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("TOML mapping keys must be strings")
            normalized[key] = _normalize_toml(item)
        return normalized
    raise ValueError(f"Unsupported TOML value type: {type(value).__name__}")


def _object_mapping(value: object, *, field: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError(f"{field} must be an object")
    result: dict[str, object] = {}
    for key, item in value.items():
        if not isinstance(key, str):
            raise ValueError(f"{field} keys must be strings")
        result[key] = item
    return result


def _object_list(value: object, *, field: str) -> list[object]:
    if not isinstance(value, list):
        raise ValueError(f"{field} must be an array")
    return list(value)


def _required_string(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field} must be a non-empty string")
    return value


def _normalized_timestamp(value: str) -> str:
    candidate = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError as error:
        raise ValueError("source timestamp must be ISO-8601") from error
    if parsed.tzinfo is None:
        raise ValueError("source timestamp must include an offset")
    return parsed.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _validate_inputs(inputs: ReleaseEvidenceInputs) -> ReleaseEvidenceInputs:
    if VERSION_PATTERN.fullmatch(inputs.artifact_version) is None:
        raise ValueError("artifact version contains unsupported characters")
    if COMMIT_PATTERN.fullmatch(inputs.source_commit) is None:
        raise ValueError("source commit must be a lowercase 40-character Git SHA")
    if REPOSITORY_PATTERN.fullmatch(inputs.repository) is None:
        raise ValueError("repository must use owner/name form")
    for label, digest in (
        ("migration plan", inputs.migration_plan_sha256),
        ("schema", inputs.schema_sha256),
    ):
        if SHA256_PATTERN.fullmatch(digest) is None:
            raise ValueError(f"{label} digest must be a lowercase SHA-256 value")
    return ReleaseEvidenceInputs(
        artifact_version=inputs.artifact_version,
        source_commit=inputs.source_commit,
        source_timestamp=_normalized_timestamp(inputs.source_timestamp),
        repository=inputs.repository,
        migration_plan_sha256=inputs.migration_plan_sha256,
        schema_sha256=inputs.schema_sha256,
    )


def _read_lock(root: Path) -> tuple[dict[str, object], list[dict[str, object]]]:
    lock_path = root / "uv.lock"
    raw_object: object = tomllib.loads(lock_path.read_text(encoding="utf-8"))
    raw = _object_mapping(_normalize_toml(raw_object), field="uv.lock")
    package_values = _object_list(raw.get("package"), field="uv.lock.package")
    packages = [_object_mapping(item, field="uv.lock.package[]") for item in package_values]
    packages.sort(
        key=lambda package: (
            _required_string(package.get("name"), field="package.name"),
            _required_string(package.get("version"), field="package.version"),
        )
    )
    return raw, packages


def _spdx_id(name: str, version: str, index: int) -> str:
    safe = re.sub(r"[^A-Za-z0-9.-]", "-", f"{name}-{version}")
    return f"SPDXRef-Package-{index:04d}-{safe}"


def _build_spdx(
    inputs: ReleaseEvidenceInputs, packages: list[dict[str, object]]
) -> dict[str, object]:
    spdx_packages: list[dict[str, object]] = []
    relationships: list[dict[str, str]] = []
    package_ids_by_name: dict[str, list[str]] = {}
    for index, package in enumerate(packages, start=1):
        name = _required_string(package.get("name"), field="package.name")
        version = _required_string(package.get("version"), field="package.version")
        package_id = _spdx_id(name, version, index)
        package_ids_by_name.setdefault(name, []).append(package_id)
        spdx_packages.append(
            {
                "SPDXID": package_id,
                "downloadLocation": "NOASSERTION",
                "externalRefs": [
                    {
                        "referenceCategory": "PACKAGE-MANAGER",
                        "referenceLocator": f"pkg:pypi/{name}@{version}",
                        "referenceType": "purl",
                    }
                ],
                "filesAnalyzed": False,
                "licenseConcluded": "NOASSERTION",
                "licenseDeclared": "NOASSERTION",
                "name": name,
                "versionInfo": version,
            }
        )
        relationships.append(
            {
                "relatedSpdxElement": package_id,
                "relationshipType": "DESCRIBES",
                "spdxElementId": "SPDXRef-DOCUMENT",
            }
        )
    for index, package in enumerate(packages, start=1):
        source_id = _spdx_id(
            _required_string(package.get("name"), field="package.name"),
            _required_string(package.get("version"), field="package.version"),
            index,
        )
        dependencies = package.get("dependencies", [])
        for dependency_value in _object_list(dependencies, field="package.dependencies"):
            dependency = _object_mapping(dependency_value, field="package.dependencies[]")
            dependency_name = _required_string(
                dependency.get("name"), field="package.dependencies[].name"
            )
            target_ids = package_ids_by_name.get(dependency_name)
            if target_ids is None:
                raise ValueError(f"locked dependency is missing package entry: {dependency_name}")
            relationships.extend(
                {
                    "relatedSpdxElement": target_id,
                    "relationshipType": "DEPENDS_ON",
                    "spdxElementId": source_id,
                }
                for target_id in target_ids
            )
    return {
        "SPDXID": "SPDXRef-DOCUMENT",
        "creationInfo": {
            "created": inputs.source_timestamp,
            "creators": ["Tool: neural-brain-release-evidence/1.0"],
        },
        "dataLicense": "CC0-1.0",
        "documentNamespace": (
            f"https://github.com/{inputs.repository}/sbom/"
            f"{inputs.source_commit}/{inputs.artifact_version}"
        ),
        "name": f"neural-brain-{inputs.artifact_version}-locked-dependencies",
        "packages": spdx_packages,
        "relationships": relationships,
        "spdxVersion": "SPDX-2.3",
    }


def _document_entry(root: Path, path: Path, *, kind: str) -> dict[str, object]:
    relative = path.relative_to(root).as_posix()
    entry: dict[str, object] = {"kind": kind, "path": relative, "sha256": sha256_file(path)}
    if path.suffix == ".json":
        parsed: object = json.loads(path.read_text(encoding="utf-8"))
        document = _object_mapping(parsed, field=relative)
        for field in (
            "contract_id",
            "contract_version",
            "document_type",
            "policy_version",
            "status",
        ):
            value = document.get(field)
            if isinstance(value, (str, int)):
                entry[field] = value
    else:
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        if lines:
            entry["title"] = lines[0].removeprefix("# ")
        status = re.search(r"(?m)^- Status: (.+)$", text)
        if status is not None:
            entry["status"] = status.group(1)
    return entry


def _versioned_documents(root: Path) -> dict[str, list[dict[str, object]]]:
    policy_paths = sorted(
        {
            *root.glob(".github/*.json"),
            *root.glob("docs/governance/*.json"),
        }
    )
    contract_paths = sorted((root / "docs" / "architecture" / "contracts").glob("*.json"))
    adr_paths = sorted(
        path
        for path in (root / "docs" / "adr").glob("ADR-*.md")
        if ADR_PATTERN.fullmatch(path.name)
    )
    return {
        "adrs": [_document_entry(root, path, kind="adr") for path in adr_paths],
        "contracts": [_document_entry(root, path, kind="contract") for path in contract_paths],
        "policies": [_document_entry(root, path, kind="policy") for path in policy_paths],
    }


def _document_set_digest(documents: dict[str, list[dict[str, object]]]) -> str:
    return _sha256_bytes(_canonical_json(documents))


def _verify_git_head(root: Path, expected_commit: str) -> None:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    if completed.stdout.strip() != expected_commit:
        raise ValueError("source commit does not match the checked-out Git HEAD")


def build_release_evidence(
    root: Path,
    output_dir: Path,
    inputs: ReleaseEvidenceInputs,
    *,
    verify_git_head: bool = False,
) -> Path:
    """Create a deterministic release-evidence bundle and return its manifest path."""

    validated = _validate_inputs(inputs)
    root = root.resolve()
    if verify_git_head:
        _verify_git_head(root, validated.source_commit)
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ValueError("output directory must be absent or empty")
    output_dir.mkdir(parents=True, exist_ok=True)

    migrations = _discover_migrations(root / "migrations")
    calculated_plan_digest = _migration_plan_digest(migrations)
    if calculated_plan_digest != validated.migration_plan_sha256:
        raise ValueError("migration plan digest does not match repository migrations")

    lock, packages = _read_lock(root)
    documents = _versioned_documents(root)
    prefix = f"neural-brain-{validated.artifact_version}"
    dependencies_path = output_dir / f"{prefix}.locked-dependencies.json"
    sbom_path = output_dir / f"{prefix}.sbom.spdx.json"
    metadata_path = output_dir / f"{prefix}.build-metadata.json"
    manifest_path = output_dir / f"{prefix}.release-manifest.json"
    checksums_path = output_dir / f"{prefix}.checksums.sha256"

    _write_json(
        dependencies_path,
        {
            "document_type": "complete_locked_dependency_graph",
            "lock_sha256": sha256_file(root / "uv.lock"),
            "package_count": len(packages),
            "uv_lock": lock,
        },
    )
    _write_json(sbom_path, _build_spdx(validated, packages))
    metadata = {
        "artifact_version": validated.artifact_version,
        "attestation": {
            "issuer": "GitHub Actions OIDC",
            "mode": "artifact-attestation",
            "required_for": ["tag", "release"],
            "stored_signing_secret": False,
        },
        "document_type": "release_build_metadata",
        "migration_plan_sha256": validated.migration_plan_sha256,
        "repository": validated.repository,
        "schema_sha256": validated.schema_sha256,
        "source_commit": validated.source_commit,
        "source_timestamp": validated.source_timestamp,
        "uv_lock_sha256": sha256_file(root / "uv.lock"),
        "versioned_document_set_sha256": _document_set_digest(documents),
    }
    _write_json(metadata_path, metadata)

    components = [dependencies_path, sbom_path, metadata_path]
    manifest = {
        "artifact_version": validated.artifact_version,
        "components": [
            {"path": path.name, "sha256": sha256_file(path)} for path in sorted(components)
        ],
        "document_type": "neural_brain_release_evidence_manifest",
        "manifest_version": 1,
        "migration": {
            "count": len(migrations),
            "files": [
                {"name": migration.name, "sha256": migration.content_sha256}
                for migration in migrations
            ],
            "plan_sha256": validated.migration_plan_sha256,
            "schema_sha256": validated.schema_sha256,
        },
        "repository": validated.repository,
        "source": {
            "commit": validated.source_commit,
            "timestamp": validated.source_timestamp,
        },
        "versions": documents,
    }
    _write_json(manifest_path, manifest)
    checksum_targets = sorted([*components, manifest_path])
    checksums_path.write_text(
        "".join(f"{sha256_file(path)}  {path.name}\n" for path in checksum_targets),
        encoding="utf-8",
        newline="\n",
    )
    return manifest_path


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--artifact-version", required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--source-timestamp", required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--migration-plan-sha256", required=True)
    parser.add_argument("--schema-sha256", required=True)
    parser.add_argument("--verify-git-head", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Build release evidence from CLI arguments."""

    arguments = _parser().parse_args(argv)
    inputs = ReleaseEvidenceInputs(
        artifact_version=arguments.artifact_version,
        source_commit=arguments.source_commit,
        source_timestamp=arguments.source_timestamp,
        repository=arguments.repository,
        migration_plan_sha256=arguments.migration_plan_sha256,
        schema_sha256=arguments.schema_sha256,
    )
    try:
        manifest = build_release_evidence(
            arguments.root,
            arguments.output_dir,
            inputs,
            verify_git_head=arguments.verify_git_head,
        )
    except (OSError, ValueError, subprocess.CalledProcessError, tomllib.TOMLDecodeError) as error:
        print(f"release evidence failed: {error}", file=sys.stderr)
        return 1
    print(f"release evidence manifest: {manifest}")
    print(f"release evidence manifest sha256: {sha256_file(manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
