"""Tests for fail-closed dependency and workflow security policy."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.security_policy import (
    SecurityPolicyError,
    validate_license_inventory,
    validate_workflow,
)

ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT / ".github" / "security-policy.json"
WORKFLOW = ROOT / ".github" / "workflows" / "security.yml"


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value), encoding="utf-8")


def test_repository_security_workflow_satisfies_policy() -> None:
    validate_workflow(WORKFLOW, POLICY)


def test_license_policy_accepts_reviewed_license(tmp_path: Path) -> None:
    inventory = tmp_path / "licenses.json"
    _write_json(
        inventory,
        [{"Name": "example", "Version": "1.0.0", "License": "Apache-2.0"}],
    )

    validate_license_inventory(inventory, POLICY)


def test_license_policy_does_not_misclassify_reviewed_lgpl(tmp_path: Path) -> None:
    inventory = tmp_path / "licenses.json"
    _write_json(
        inventory,
        [{"Name": "linked-library", "Version": "1.0.0", "License": "LGPL-3.0-only"}],
    )

    validate_license_inventory(inventory, POLICY)


@pytest.mark.parametrize("license_name", ["MIT-0", "Apache-2.0 OR BSD-3-Clause"])
def test_license_policy_accepts_exact_reviewed_dependency_expressions(
    tmp_path: Path, license_name: str
) -> None:
    inventory = tmp_path / "licenses.json"
    inventory.write_text(
        json.dumps([{"Name": "reviewed", "Version": "1.0", "License": license_name}]),
        encoding="utf-8",
    )

    validate_license_inventory(inventory, POLICY)


@pytest.mark.parametrize("license_name", ["MIT-0 OR Unknown", "Apache-2.0 OR BSD-3-Clause+"])
def test_license_policy_rejects_unreviewed_nearby_expressions(
    tmp_path: Path, license_name: str
) -> None:
    inventory = tmp_path / "licenses.json"
    inventory.write_text(
        json.dumps([{"Name": "unreviewed", "Version": "1.0", "License": license_name}]),
        encoding="utf-8",
    )

    with pytest.raises(SecurityPolicyError, match="license policy violations"):
        validate_license_inventory(inventory, POLICY)


@pytest.mark.parametrize("license_name", ["UNKNOWN", "AGPL-3.0-only", "unlicensed"])
def test_license_policy_rejects_unknown_or_prohibited_license(
    tmp_path: Path, license_name: str
) -> None:
    inventory = tmp_path / "licenses.json"
    _write_json(
        inventory,
        [{"Name": "unsafe", "Version": "1.0.0", "License": license_name}],
    )

    with pytest.raises(SecurityPolicyError, match="license policy violations"):
        validate_license_inventory(inventory, POLICY)


def test_workflow_policy_rejects_mutable_action_reference(tmp_path: Path) -> None:
    workflow = tmp_path / "security.yml"
    workflow.write_text(
        WORKFLOW.read_text(encoding="utf-8").replace(
            "actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10",
            "actions/checkout@v6",
            1,
        ),
        encoding="utf-8",
    )

    with pytest.raises(SecurityPolicyError, match="full commit"):
        validate_workflow(workflow, POLICY)


def test_workflow_policy_rejects_write_permission(tmp_path: Path) -> None:
    workflow = tmp_path / "security.yml"
    workflow.write_text(
        WORKFLOW.read_text(encoding="utf-8").replace("contents: read", "contents: write", 1),
        encoding="utf-8",
    )

    with pytest.raises(SecurityPolicyError, match="write-scoped"):
        validate_workflow(workflow, POLICY)


def test_workflow_policy_rejects_secret_context(tmp_path: Path) -> None:
    workflow = tmp_path / "security.yml"
    workflow.write_text(
        WORKFLOW.read_text(encoding="utf-8") + "\n# ${{ secrets.UNAPPROVED }}\n",
        encoding="utf-8",
    )

    with pytest.raises(SecurityPolicyError, match="secrets are denied"):
        validate_workflow(workflow, POLICY)
