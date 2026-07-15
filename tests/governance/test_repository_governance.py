from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = ROOT / "docs" / "governance" / "repository-policy.json"


def load_policy() -> dict[str, Any]:
    value: object = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_task_branch_contract_accepts_only_declared_examples() -> None:
    policy = load_policy()
    branches = policy["branches"]
    pattern = re.compile(branches["task_branch_pattern"])

    assert all(pattern.fullmatch(name) for name in branches["examples_allowed"])
    assert not any(pattern.fullmatch(name) for name in branches["examples_denied"])
    assert not pattern.fullmatch(policy["default_branch"])


def test_conventional_commit_contract_is_fail_closed() -> None:
    pattern = re.compile(load_policy()["commits"]["conventional_commit_pattern"])
    allowed = (
        "feat(memory): add guarded checkpoint resume",
        "fix: reject stale source assessment",
        "docs(adr): record policy boundary",
        "ci!: require governance evidence",
    )
    denied = (
        "Add a feature",
        "feature(runtime): add a feature",
        "fix(runtime) missing separator",
        "fix(runtime): Uppercase description",
        "Merge pull request #1",
    )

    assert all(pattern.fullmatch(header) for header in allowed)
    assert not any(pattern.fullmatch(header) for header in denied)


def test_main_policy_requires_review_and_has_no_bypass() -> None:
    policy = load_policy()
    principles = policy["principles"]
    pull_requests = policy["pull_requests"]

    assert policy["default_branch"] == "main"
    assert principles["reviewed_delivery_only"] is True
    assert principles["direct_push_to_default_branch"] is False
    assert principles["administrator_bypass"] is False
    assert pull_requests["required"] is True
    assert pull_requests["minimum_approvals"] >= 1
    assert pull_requests["dismiss_stale_approvals"] is True
    assert pull_requests["require_approval_after_latest_push"] is True
    assert pull_requests["require_code_owner_review"] is True
    assert pull_requests["require_conversation_resolution"] is True
    assert pull_requests["author_may_approve_own_change"] is False
    assert pull_requests["last_pusher_may_satisfy_required_approval"] is False
    assert pull_requests["force_push"] is False
    assert pull_requests["branch_deletion"] is False


def test_required_checks_are_unique_and_blocking() -> None:
    checks = load_policy()["required_checks"]
    ids = [check["id"] for check in checks]
    contexts = [check["expected_context"] for check in checks]

    assert len(ids) == len(set(ids))
    assert len(contexts) == len(set(contexts))
    assert all(check["blocking"] is True for check in checks)
    assert ids == [
        "quality",
        "migration-validation",
        "secret-history",
        "dependency-license-workflow-policy",
        "release-evidence",
    ]
    assert contexts == [
        "quality",
        "PostgreSQL 18 forward migrations",
        "Secret history scan",
        "Dependency, license, and workflow policy",
        "Build deterministic release evidence",
    ]
    assert {
        "format",
        "lint",
        "typecheck",
        "type_exception_audit",
        "tests",
        "dependency_lock",
        "governance",
    } == set(checks[0]["aggregated_gates"])
    assert all((ROOT / check["workflow"]).is_file() for check in checks)


def test_required_quality_context_matches_workflow_contract() -> None:
    check = load_policy()["required_checks"][0]
    workflow = (ROOT / check["workflow"]).read_text(encoding="utf-8")

    assert "name: Quality" in workflow
    assert "pull_request:" in workflow
    assert "branches:\n      - main" in workflow
    assert "  quality:\n    name: quality" in workflow
    assert "uv run --locked --all-groups python tools/quality.py --locked" in workflow


def test_sensitive_review_requires_independent_evidence() -> None:
    sensitive = load_policy()["sensitive_review"]

    assert sensitive["minimum_approvals"] >= 1
    assert "docs/architecture/**" in sensitive["path_patterns"]
    assert "docs/governance/**" in sensitive["path_patterns"]
    assert ".github/**" in sensitive["path_patterns"]
    assert "src/**/ingestion/**" in sensitive["path_patterns"]
    assert "src/**/retrieval/**" in sensitive["path_patterns"]
    assert "src/**/consolidation/**" in sensitive["path_patterns"]
    assert "src/**/executor/**" not in sensitive["path_patterns"]
    assert len(sensitive["runtime_boundaries"]) == 6
    assert sensitive["runtime_boundaries"] == [
        "memory_producer_vs_transition_gate",
        "retrieval_consumer_vs_source_policy_assessor",
        "requester_vs_approver_for_elevated_risk_memory_operation",
        "policy_author_vs_sole_policy_activator",
        "automatic_memory_reconciliation_vs_human_incident_resolution",
        "memory_candidate_producer_vs_sensitive_candidate_promoter",
    ]
    properties = " ".join(sensitive["required_reviewer_properties"])
    assert "CODEOWNER" in properties
    assert "distinct from the change author" in properties
    assert "did not implement the evidence" in properties
    assert "not approved solely by the policy author" in properties


def test_repository_narrative_defines_memory_system_consumer_boundary() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    contributing = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
    project = (ROOT / "pyproject.toml").read_text(encoding="utf-8")

    assert "Neural Brain is not an agent" in readme
    assert "memory system" in readme
    assert "consumer_goal_ref" in readme
    assert "non-authoritative" in readme
    assert "The persistent Tenant-root representation" in readme
    assert "remains an open architecture decision" in readme
    assert "Neural Brain itself is not an agent" in agents
    assert "Memory Transition Gate is the only writer" in agents
    assert "External agents may consume it" in contributing
    assert "provenance-preserving memory system" in project


def test_repository_artifacts_expose_required_review_contract() -> None:
    codeowners = (ROOT / ".github" / "CODEOWNERS").read_text(encoding="utf-8")
    template = (ROOT / ".github" / "pull_request_template.md").read_text(encoding="utf-8")
    contributing = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")

    assert "* @KonstantinData @KonstantinCondata" in codeowners
    sensitive_patterns = (
        "/docs/architecture/**",
        "/docs/adr/**",
        "/docs/governance/**",
        "/migrations/**",
        "/src/**",
        "/tools/**",
        "/.github/**",
    )
    for pattern in sensitive_patterns:
        assert f"{pattern} @KonstantinData @KonstantinCondata" in codeowners
    governance = (ROOT / "docs" / "governance" / "README.md").read_text(encoding="utf-8")
    assert "pending invitation" in governance
    assert "read-only access" in governance
    for heading in load_policy()["pull_requests"]["required_template_sections"]:
        assert f"## {heading}" in template
    assert "codex/" in contributing
    assert "Conventional Commit" in contributing
    assert "Never push directly to `main`" in contributing


def test_external_github_enforcement_has_sanitized_live_evidence() -> None:
    external = load_policy()["external_enforcement"]
    evidence = (ROOT / "docs" / "governance" / "github-settings-evidence.md").read_text(
        encoding="utf-8"
    )

    assert external["mutation_authorized_by_this_contract"] is False
    assert external["status"] == "live_verified"
    assert len(external["sanitized_evidence_sha256"]) == 64
    assert len(external["evidence_required_before_fnd_03_completion"]) >= 5
    assert any("sensitive-review" in setting for setting in external["required_settings"])
    assert "Live configuration verified: **Yes**" in evidence
    assert external["sanitized_evidence_sha256"] in evidence
    assert "mergeStateStatus=BLOCKED" in evidence
