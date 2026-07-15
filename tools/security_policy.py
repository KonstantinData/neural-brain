"""Fail-closed policy checks for security CI inputs and configuration."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ACTION_PATTERN = re.compile(
    r"^\s*uses:\s*([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)@([^\s#]+)(?:\s+#.*)?$",
    re.MULTILINE,
)
FULL_COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")
WRITE_PERMISSION_PATTERN = re.compile(r"^\s+[A-Za-z0-9_-]+:\s*write\s*$", re.MULTILINE)


class SecurityPolicyError(ValueError):
    """Raised when security configuration violates the fail-closed policy."""


def _load_json_object(path: Path) -> dict[str, Any]:
    try:
        value: Any = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SecurityPolicyError(f"cannot read valid JSON from {path}: {error}") from error
    if not isinstance(value, dict):
        raise SecurityPolicyError(f"expected a JSON object in {path}")
    return value


def _string_mapping(value: object, *, field: str) -> dict[str, str]:
    if not isinstance(value, dict):
        raise SecurityPolicyError(f"{field} must be an object")
    result: dict[str, str] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not isinstance(item, str):
            raise SecurityPolicyError(f"{field} must contain only string keys and values")
        result[key] = item
    return result


def _string_set(value: object, *, field: str) -> set[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise SecurityPolicyError(f"{field} must be an array of strings")
    return set(value)


def validate_license_inventory(inventory_path: Path, policy_path: Path) -> None:
    """Reject unknown, unreviewed, or explicitly prohibited package licenses."""

    policy = _load_json_object(policy_path)
    license_policy = policy.get("licenses")
    if not isinstance(license_policy, dict):
        raise SecurityPolicyError("licenses policy must be an object")
    allowed = _string_set(license_policy.get("allowed_exact"), field="licenses.allowed_exact")
    denied_markers = _string_set(
        license_policy.get("denied_markers"), field="licenses.denied_markers"
    )

    try:
        inventory: Any = json.loads(inventory_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SecurityPolicyError(f"cannot read license inventory: {error}") from error
    if not isinstance(inventory, list):
        raise SecurityPolicyError("license inventory must be a JSON array")

    violations: list[str] = []
    for entry in inventory:
        if not isinstance(entry, dict):
            violations.append("malformed inventory entry")
            continue
        name = entry.get("Name")
        version = entry.get("Version")
        license_name = entry.get("License")
        if not all(
            isinstance(value, str) and value.strip() for value in (name, version, license_name)
        ):
            violations.append("inventory entry has missing name, version, or license")
            continue
        assert isinstance(name, str)
        assert isinstance(version, str)
        assert isinstance(license_name, str)
        matched_denials = sorted(marker for marker in denied_markers if marker in license_name)
        if license_name in allowed:
            continue
        if matched_denials:
            violations.append(
                f"{name} {version}: prohibited license marker(s) {', '.join(matched_denials)}"
            )
        else:
            violations.append(f"{name} {version}: unreviewed license {license_name!r}")

    if violations:
        details = "\n".join(f"- {violation}" for violation in violations)
        raise SecurityPolicyError(f"license policy violations:\n{details}")


def validate_workflow(workflow_path: Path, policy_path: Path) -> None:
    """Enforce immutable external references and least-privilege workflow settings."""

    policy = _load_json_object(policy_path)
    approved_actions = _string_mapping(policy.get("actions"), field="actions")
    tools = _string_mapping(policy.get("tools"), field="tools")
    try:
        workflow = workflow_path.read_text(encoding="utf-8")
    except OSError as error:
        raise SecurityPolicyError(f"cannot read workflow: {error}") from error

    if "pull_request_target:" in workflow or "workflow_run:" in workflow:
        raise SecurityPolicyError("privileged indirect workflow triggers are denied")
    if "${{ secrets." in workflow:
        raise SecurityPolicyError("repository or organization secrets are denied in security CI")
    if WRITE_PERMISSION_PATTERN.search(workflow):
        raise SecurityPolicyError("write-scoped GitHub token permissions are denied")
    if not re.search(r"^permissions:\s*\n\s+contents:\s*read\s*$", workflow, re.MULTILINE):
        raise SecurityPolicyError("workflow must declare top-level contents: read permission")

    references = ACTION_PATTERN.findall(workflow)
    if not references:
        raise SecurityPolicyError("workflow contains no external Action references")
    checkout_count = 0
    for action, revision in references:
        expected_revision = approved_actions.get(action)
        if expected_revision is None:
            raise SecurityPolicyError(f"unapproved GitHub Action: {action}")
        if not FULL_COMMIT_PATTERN.fullmatch(revision):
            raise SecurityPolicyError(f"GitHub Action is not pinned to a full commit: {action}")
        if revision != expected_revision:
            raise SecurityPolicyError(
                f"GitHub Action revision is not approved: {action}@{revision}"
            )
        if action == "actions/checkout":
            checkout_count += 1

    if set(action for action, _ in references) != set(approved_actions):
        raise SecurityPolicyError("approved Action policy and workflow references differ")
    if workflow.count("persist-credentials: false") != checkout_count:
        raise SecurityPolicyError("every checkout must explicitly disable credential persistence")

    required_fragments = [
        f"zricethezav/gitleaks/v8@{tools['gitleaks_revision']}",
        f"pip-audit=={tools['pip_audit_version']}",
        f"pip-licenses=={tools['pip_licenses_version']}",
        f'version: "{tools["uv_version"]}"',
        "uv lock --check",
        "uv sync --frozen",
        "--require-hashes",
        "--strict",
        "--exit-code 1",
    ]
    missing_fragments = [fragment for fragment in required_fragments if fragment not in workflow]
    if missing_fragments:
        raise SecurityPolicyError(
            "workflow is missing required security controls: " + ", ".join(missing_fragments)
        )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    licenses = subparsers.add_parser("licenses", help="validate a pip-licenses inventory")
    licenses.add_argument("--inventory", type=Path, required=True)
    licenses.add_argument("--policy", type=Path, required=True)

    workflow = subparsers.add_parser("workflow", help="validate the security workflow policy")
    workflow.add_argument("--workflow", type=Path, required=True)
    workflow.add_argument("--policy", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the selected fail-closed policy check."""

    args = _parser().parse_args(argv)
    try:
        if args.command == "licenses":
            validate_license_inventory(args.inventory, args.policy)
        elif args.command == "workflow":
            validate_workflow(args.workflow, args.policy)
        else:
            raise SecurityPolicyError(f"unsupported command: {args.command}")
    except SecurityPolicyError as error:
        print(f"security policy failed: {error}", file=sys.stderr)
        return 1
    print(f"security policy passed: {args.command}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
