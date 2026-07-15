"""Tests for deterministic release evidence generation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from tools.build_release_evidence import ReleaseEvidenceInputs, build_release_evidence
from tools.validate_migrations import discover_migrations, migration_plan_digest


def _write_repository(root: Path) -> None:
    (root / ".github").mkdir(parents=True)
    (root / "docs" / "architecture" / "contracts").mkdir(parents=True)
    (root / "docs" / "adr").mkdir(parents=True)
    (root / "migrations").mkdir(parents=True)
    (root / ".github" / "security-policy.json").write_text(
        '{"policy_version":1}\n', encoding="utf-8"
    )
    (root / "docs" / "architecture" / "contracts" / "example.json").write_text(
        '{"contract_id":"example","contract_version":"1.0.0","status":"normative"}\n',
        encoding="utf-8",
    )
    (root / "docs" / "adr" / "ADR-001-example.md").write_text(
        "# ADR-001: Example\n\n- Status: Accepted\n", encoding="utf-8"
    )
    (root / "uv.lock").write_text(
        """version = 1
revision = 3
requires-python = "==3.14.*"

[[package]]
name = "alpha"
version = "1.2.3"
source = { registry = "https://pypi.org/simple" }
wheels = [
  { url = "https://example.invalid/alpha.whl", hash = "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", size = 1 },
]

[[package]]
name = "beta"
version = "2.0.0"
source = { registry = "https://pypi.org/simple" }
dependencies = [{ name = "alpha" }]
""",
        encoding="utf-8",
    )


def _inputs(root: Path) -> ReleaseEvidenceInputs:
    migrations = discover_migrations(root / "migrations", allow_empty=True)
    return ReleaseEvidenceInputs(
        artifact_version="v1.2.3",
        source_commit="1" * 40,
        source_timestamp="2026-07-15T09:30:00+02:00",
        repository="example/neural-brain",
        migration_plan_sha256=migration_plan_digest(migrations),
        schema_sha256="2" * 64,
    )


def _directory_digest(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(path.iterdir()):
        digest.update(item.name.encode())
        digest.update(item.read_bytes())
    return digest.hexdigest()


def test_build_is_deterministic_and_traceable(tmp_path: Path) -> None:
    root = tmp_path / "repository"
    root.mkdir()
    _write_repository(root)

    first = tmp_path / "first"
    second = tmp_path / "second"
    first_manifest = build_release_evidence(root, first, _inputs(root))
    build_release_evidence(root, second, _inputs(root))

    assert _directory_digest(first) == _directory_digest(second)
    manifest = json.loads(first_manifest.read_text(encoding="utf-8"))
    assert manifest["artifact_version"] == "v1.2.3"
    assert manifest["source"]["commit"] == "1" * 40
    assert manifest["source"]["timestamp"] == "2026-07-15T07:30:00Z"
    assert manifest["migration"]["plan_sha256"] == _inputs(root).migration_plan_sha256
    assert manifest["migration"]["schema_sha256"] == "2" * 64
    assert manifest["versions"]["policies"][0]["policy_version"] == 1
    assert manifest["versions"]["contracts"][0]["contract_version"] == "1.0.0"
    assert manifest["versions"]["adrs"][0]["status"] == "Accepted"

    dependencies = json.loads(
        next(first.glob("*.locked-dependencies.json")).read_text(encoding="utf-8")
    )
    assert dependencies["package_count"] == 2
    assert {package["name"] for package in dependencies["uv_lock"]["package"]} == {
        "alpha",
        "beta",
    }
    sbom = json.loads(next(first.glob("*.sbom.spdx.json")).read_text(encoding="utf-8"))
    assert sbom["spdxVersion"] == "SPDX-2.3"
    assert {package["name"] for package in sbom["packages"]} == {"alpha", "beta"}
    assert any(
        relationship["relationshipType"] == "DEPENDS_ON" for relationship in sbom["relationships"]
    )


def test_rejects_migration_digest_mismatch(tmp_path: Path) -> None:
    root = tmp_path / "repository"
    root.mkdir()
    _write_repository(root)
    inputs = _inputs(root)
    mismatched = ReleaseEvidenceInputs(
        artifact_version=inputs.artifact_version,
        source_commit=inputs.source_commit,
        source_timestamp=inputs.source_timestamp,
        repository=inputs.repository,
        migration_plan_sha256="3" * 64,
        schema_sha256=inputs.schema_sha256,
    )

    with pytest.raises(ValueError, match="migration plan digest"):
        build_release_evidence(root, tmp_path / "output", mismatched)


def test_rejects_nonempty_output_directory(tmp_path: Path) -> None:
    root = tmp_path / "repository"
    root.mkdir()
    _write_repository(root)
    output = tmp_path / "output"
    output.mkdir()
    (output / "stale.txt").write_text("stale", encoding="utf-8")

    with pytest.raises(ValueError, match="absent or empty"):
        build_release_evidence(root, output, _inputs(root))


@pytest.mark.parametrize(
    ("artifact_version", "source_commit"),
    [("bad/version", "1" * 40), ("v1", "ABC")],
)
def test_rejects_invalid_candidate_identity(
    tmp_path: Path, artifact_version: str, source_commit: str
) -> None:
    root = tmp_path / "repository"
    root.mkdir()
    _write_repository(root)
    inputs = _inputs(root)
    invalid = ReleaseEvidenceInputs(
        artifact_version=artifact_version,
        source_commit=source_commit,
        source_timestamp=inputs.source_timestamp,
        repository=inputs.repository,
        migration_plan_sha256=inputs.migration_plan_sha256,
        schema_sha256=inputs.schema_sha256,
    )

    with pytest.raises(ValueError):
        build_release_evidence(root, tmp_path / "output", invalid)
