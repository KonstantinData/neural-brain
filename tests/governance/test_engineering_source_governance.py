from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
GOVERNANCE_DIR = ROOT / "docs" / "governance"
PROFILE_PATH = GOVERNANCE_DIR / "engineering-source-profile.json"


def load_profile() -> dict[str, Any]:
    value: object = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_engineering_source_profile_is_repo_scoped_and_not_runtime_scoped() -> None:
    profile = load_profile()

    assert profile["document_type"] == "engineering_source_profile"
    assert profile["repository"] == "KonstantinData/neural-brain"
    assert profile["governed_layer"] == "engineering_knowledge_base"
    assert "development_agents" in profile["applies_to"]
    assert "review_agents" in profile["applies_to"]
    assert "product_runtime" in profile["does_not_apply_to"]
    assert "runtime_rag" in profile["does_not_apply_to"]


def test_engineering_source_profile_has_no_product_runtime_effects() -> None:
    non_effects = load_profile()["runtime_non_effects"]

    assert non_effects
    assert all(value is False for value in non_effects.values())
    for denied_effect in (
        "creates_product_web_search",
        "creates_product_source_crawler",
        "creates_product_rag",
        "creates_product_knowledge_store",
        "allows_runtime_external_research",
        "allows_engineering_sources_to_be_ingested_into_product_memory",
        "automatically_changes_product_behavior",
        "automatically_changes_adrs",
    ):
        assert denied_effect in non_effects


def test_knowledge_layers_keep_repository_engineering_and_product_separate() -> None:
    layers = {layer["id"]: layer for layer in load_profile()["knowledge_layers"]}

    assert set(layers) == {
        "repository_evidence",
        "engineering_knowledge_base",
        "product_knowledge_and_data",
    }
    assert layers["repository_evidence"]["governed_by_this_profile"] is False
    assert layers["engineering_knowledge_base"]["governed_by_this_profile"] is True
    assert layers["product_knowledge_and_data"]["governed_by_this_profile"] is False
    assert layers["repository_evidence"]["authority"] == "durable_technical_source_of_truth"
    assert layers["engineering_knowledge_base"]["authority"] == "engineering_review_input"


def test_source_profile_contains_only_external_engineering_source_categories() -> None:
    profile = load_profile()
    categories = {category["id"]: category for category in profile["external_source_categories"]}

    expected_categories = {
        "language_and_runtime",
        "dependencies_and_frameworks",
        "security_and_privacy",
        "ci_cd_and_operations",
        "architecture_and_cognitive_evaluation",
    }
    assert set(categories) == expected_categories
    assert all(category["allowed_sources"] for category in categories.values())
    assert all(category["quality_rules"] for category in categories.values())
    assert "source_categories" not in profile

    excluded = set(
        profile["repository_evidence_boundary"]["excluded_from_engineering_source_profile"]
    )
    assert {"code", "tests", "adrs", "git_history", "pull_requests", "ci_runs"} <= excluded
    flattened_sources = {
        source for category in categories.values() for source in category["allowed_sources"]
    }
    assert not flattened_sources & {
        "active_checkout",
        "git_history",
        "pull_requests",
        "ci_runs",
        "versioned_traceability_records",
        "repository_adrs_and_contracts",
    }


def test_role_baseline_coverage_is_task_filtered_not_forced_full_consumption() -> None:
    profile = load_profile()
    expected_categories = {category["id"] for category in profile["external_source_categories"]}

    for role, required_categories in profile["role_baseline_coverage"].items():
        assert required_categories, role
        assert set(required_categories) <= expected_categories

    task_selection = profile["task_source_selection"]
    assert task_selection["baseline_awareness_required"] is True
    assert task_selection["task_specific_source_use_required"] is True
    assert task_selection["consume_all_role_sources_for_every_task"] is False
    assert "demonstrable_connection" in task_selection["selection_rule"]


def test_new_external_insights_do_not_become_findings_without_current_risk() -> None:
    profile = load_profile()
    stability = profile["state_of_art_stability_principle"]
    classification = profile["new_insight_classification"]

    assert stability["state_of_art_scope"] == "specialist_assessment_ability"
    assert stability["continuous_modernization_mandate"] is False
    assert stability["newer_approach_is_finding_without_current_risk"] is False
    assert "security_risk" in stability["finding_requires_repository_evidence_of"]
    assert classification["required_before_routing"] is True
    assert classification["pr_finding_allowed_only_for"] == ["current_defect_or_risk"]
    assert classification["future_option_target"] == "future-considerations-register.md"
    assert classification["backlog_or_adr_requires_separate_repository_decision"] is True
    assert classification["modernization_only_creates_pr_finding"] is False


def test_profile_change_control_and_maintenance_skill_are_bounded() -> None:
    profile = load_profile()
    skill = profile["maintenance_skill"]
    workflow = profile["profile_change_workflow"]

    assert skill["name"] == "Engineering Source Governance Skill"
    assert "inspect_profile_coverage" in skill["responsibilities"]
    assert "scheduled_periodic_review" in skill["execution_triggers"]
    assert skill["periodic_review_interval"] == "quarterly_or_before_release_gate"
    assert skill["permissions"]["may_propose_profile_changes"] is True
    assert skill["permissions"]["may_activate_normative_profile_changes"] is False
    assert skill["permissions"]["may_change_product_runtime"] is False
    assert skill["permissions"]["may_change_adrs"] is False
    assert skill["approval_authority"] == "repository_governance_workflow_with_codeowner_review"

    assert workflow["allowed_states"] == [
        "proposed",
        "reviewed",
        "approved",
        "deprecated",
        "rejected",
    ]
    assert workflow["skill_may_only_propose"] is True
    assert workflow["normative_activation_requires_approval"] is True
    assert {
        "rationale",
        "affected_roles",
        "previous_source_state",
        "proposed_source_state",
        "approver",
        "activation_date",
        "audit_artifact",
    } <= set(workflow["required_change_record_fields"])


def test_sources_require_freshness_metadata_and_revalidation_triggers() -> None:
    profile = load_profile()

    assert {
        "source_id",
        "source_category",
        "authority_level",
        "version_or_applicability_scope",
        "last_validated_at",
        "validation_status",
        "revalidation_triggers",
    } <= set(profile["source_record_required_fields"])
    assert "current" in profile["source_validation_statuses"]
    assert "stale" in profile["source_validation_statuses"]
    assert "version_mismatch" in profile["source_validation_statuses"]
    assert "security_advisory" in profile["revalidation_triggers"]
    assert "end_of_life_notice" in profile["revalidation_triggers"]
    assert "authoritative_source_conflict" in profile["revalidation_triggers"]


def test_external_content_is_untrusted_and_conflicts_have_judge_path() -> None:
    profile = load_profile()
    trust = profile["external_content_trust"]
    conflicts = profile["source_conflict_process"]

    assert trust["classification"] == "untrusted_evidence"
    assert trust["embedded_instructions_are_authority"] is False
    assert trust["may_change_agent_roles"] is False
    assert trust["may_change_governance"] is False
    assert trust["may_authorize_repository_actions"] is False
    assert trust["may_authorize_profile_changes"] is False
    assert trust["may_authorize_adr_changes"] is False
    assert trust["may_authorize_tool_calls"] is False

    assert {
        "competing_statements",
        "source_identity_and_authority",
        "version_and_applicability_scope",
        "prioritization_decision",
        "remaining_uncertainty",
    } <= set(conflicts["required_record_fields"])
    assert conflicts["priority_order"] == [
        "authority",
        "exact_version_match",
        "publication_or_validation_date",
        "support_status",
        "repository_applicability",
    ]
    assert conflicts["unresolved_conflicts_escalate_to"] == "governance_judge"


def test_governance_docs_publish_the_boundary_and_profile() -> None:
    governance = (GOVERNANCE_DIR / "engineering-source-governance.md").read_text(encoding="utf-8")
    normalized_governance = " ".join(governance.split())
    index = (GOVERNANCE_DIR / "README.md").read_text(encoding="utf-8")
    root_readme = (ROOT / "README.md").read_text(encoding="utf-8")
    future_register = (GOVERNANCE_DIR / "future-considerations-register.md").read_text(
        encoding="utf-8"
    )

    assert "Out of scope: Product runtime" in governance
    assert "product RAG system" in governance
    assert "engineering-source-profile.json" in governance
    assert "Future Considerations Register" in governance
    assert "A newer alternative alone is not a review finding." in normalized_governance
    assert "Engineering source governance" in index
    assert "future-considerations-register.md" in index
    assert "Engineering source governance" in root_readme
    assert "It never becomes product work automatically." in future_register
