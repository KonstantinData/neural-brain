"""Contract tests for least-privilege release evidence CI."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")


def test_every_external_action_is_pinned_to_a_dereferenced_commit() -> None:
    references = re.findall(r"^\s*uses:\s*([^@\s]+)@([^\s#]+)", WORKFLOW, re.MULTILINE)
    assert references
    assert all(re.fullmatch(r"[0-9a-f]{40}", revision) for _, revision in references)
    assert dict(references) == {
        "actions/attest-build-provenance": "977bb373ede98d70efdf65b84cb5f73e068dcc2a",
        "actions/checkout": "df4cb1c069e1874edd31b4311f1884172cec0e10",
        "actions/download-artifact": "018cc2cf5baa6db3ef3c5f8a56943fffe632ef53",
        "actions/upload-artifact": "ea165f8d65b6e75b540449e92b4886f43607fa02",
        "astral-sh/setup-uv": "37802adc94f370d6bfd71619e3f0bf239e1f3b78",
    }


def test_checkout_never_persists_credentials() -> None:
    assert WORKFLOW.count("actions/checkout@") == WORKFLOW.count("persist-credentials: false")
    assert "${{ secrets." not in WORKFLOW


def test_pr_validation_has_no_write_permission_and_cannot_attest() -> None:
    validate_job, attest_job = WORKFLOW.split("\n  attest:\n", maxsplit=1)
    assert "id-token: write" not in validate_job
    assert "attestations: write" not in validate_job
    assert "actions/attest-build-provenance@" not in validate_job
    assert "if: github.event_name == 'push' || github.event_name == 'release'" in attest_job


def test_attestation_uses_only_oidc_and_attestation_write_permissions() -> None:
    attest_job = WORKFLOW.split("\n  attest:\n", maxsplit=1)[1]
    assert "contents: read" in attest_job
    assert "id-token: write" in attest_job
    assert "attestations: write" in attest_job
    assert "contents: write" not in attest_job
    assert "packages: write" not in attest_job


def test_workflow_builds_versioned_traceable_evidence() -> None:
    required = [
        "uv lock --check",
        "uv sync --frozen --all-groups --no-editable",
        "tools/security_policy.py workflow",
        "tools/validate_migrations.py",
        "tools/build_release_evidence.py",
        "--migration-plan-sha256",
        "--schema-sha256",
        "actions/upload-artifact@",
        "actions/attest-build-provenance@",
    ]
    assert all(fragment in WORKFLOW for fragment in required)
