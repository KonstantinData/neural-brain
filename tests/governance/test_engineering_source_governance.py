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


def load_registry_schema() -> dict[str, Any]:
    value: object = json.loads(
        (GOVERNANCE_DIR / "engineering-source-registry.schema.json").read_text(encoding="utf-8")
    )
    assert isinstance(value, dict)
    return value


def test_engineering_source_profile_is_repo_scoped_and_not_runtime_scoped() -> None:
    profile = load_profile()

    assert profile["document_type"] == "repository_engineering_source_profile"
    assert profile["repository"] == "KonstantinData/neural-brain"
    assert profile["governed_layer"] == "engineering_knowledge_base"
    assert profile["status"] == "approved"
    assert "development_agents" in profile["applies_to"]
    assert "review_agents" in profile["applies_to"]
    assert "product_runtime" in profile["does_not_apply_to"]
    assert "product_memory" in profile["does_not_apply_to"]
    assert "runtime_rag" in profile["does_not_apply_to"]


def test_governance_hierarchy_has_four_distinct_layers_and_artifacts() -> None:
    profile = load_profile()
    hierarchy = {entry["layer"]: entry["artifact"] for entry in profile["governance_hierarchy"]}

    assert hierarchy == {
        "global_engineering_source_policy": ("docs/governance/engineering-source-governance.md"),
        "repository_engineering_source_profile": (
            "docs/governance/engineering-source-profile.json"
        ),
        "engineering_source_registry": "docs/governance/engineering-source-registry.md",
        "source_governance_audit_records": ("docs/governance/source-governance-audit-records.md"),
    }
    for artifact in hierarchy.values():
        assert (ROOT / artifact).is_file()
    assert len(hierarchy) == 4


def test_runtime_non_effects_block_product_scope_expansion() -> None:
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
        "creates_product_data_source",
        "automatically_changes_product_architecture",
        "automatically_changes_dependencies",
        "automatically_changes_backlog",
        "automatically_changes_adrs",
    ):
        assert denied_effect in non_effects


def test_knowledge_layers_keep_repository_external_and_derived_assessment_separate() -> None:
    layers = {layer["id"]: layer for layer in load_profile()["knowledge_layers"]}

    assert set(layers) == {
        "repository_evidence",
        "external_engineering_evidence",
        "derived_assessment",
        "product_knowledge_and_data",
    }
    assert layers["repository_evidence"]["governed_by_this_profile"] is False
    assert layers["repository_evidence"]["stored_as_external_engineering_source"] is False
    assert layers["external_engineering_evidence"]["governed_by_this_profile"] is True
    assert layers["external_engineering_evidence"]["stored_as_external_engineering_source"] is True
    assert layers["derived_assessment"]["stored_as_external_engineering_source"] is False
    assert layers["product_knowledge_and_data"]["governed_by_this_profile"] is False
    assert layers["repository_evidence"]["authority"] == "proves_repository_current_state"
    assert layers["external_engineering_evidence"]["authority"] == (
        "supports_repository_assessment"
    )


def test_repository_evidence_is_excluded_from_external_source_registry() -> None:
    profile = load_profile()
    boundary = profile["repository_evidence_boundary"]
    excluded = set(boundary["excluded_from_engineering_source_registry"])

    assert {
        "code",
        "tests",
        "migrations",
        "configuration",
        "adrs",
        "contracts",
        "commits",
        "pull_requests",
        "ci_results",
        "release_artifacts",
        "generated_runtime_artifacts",
        "generated_pipeline_artifacts",
    } <= excluded
    assert boundary["internal_model_knowledge_is_evidence"] is False
    flattened_sources = {
        source
        for source_class in profile["source_classes"]
        for source in source_class["allowed_sources"]
    }
    assert not flattened_sources & {
        "active_checkout",
        "git_history",
        "pull_requests",
        "ci_runs",
        "versioned_traceability_records",
        "repository_adrs_and_contracts",
    }


def test_source_records_have_separate_status_dimensions_and_mandatory_metadata() -> None:
    profile = load_profile()

    statuses = profile["source_status_dimensions"]
    assert statuses["external_publication_status"] == [
        "draft",
        "final",
        "superseded",
        "withdrawn",
    ]
    assert statuses["internal_registry_status"] == [
        "proposed",
        "approved",
        "rejected",
        "deprecated",
    ]
    assert statuses["permitted_evidence_use"] == [
        "normative",
        "supporting",
        "watch_only",
        "prohibited",
    ]
    assert statuses["external_publication_status_grants_internal_approval"] is False
    assert statuses["normative_use_requires_internal_approval"] is True
    assert {
        "schema_version",
        "source_identifier",
        "lifecycle_state",
        "title",
        "issuing_organization",
        "canonical_document_reference",
        "source_class",
        "external_publication_status",
        "internal_registry_status",
        "permitted_evidence_use",
        "document_or_specification_version",
        "publication_date",
        "retrieval_date",
        "content_hash",
        "applicable_technology_and_version_range",
        "repository_scope_mapping",
        "claims",
        "source_authority_assessment",
        "freshness_status",
        "conflict_status",
        "validator",
        "approval_status",
        "superseded_and_superseding_sources",
        "next_review_trigger_or_review_date",
    } <= set(profile["source_record_required_fields"])
    assert profile["source_registry_schema"] == (
        "docs/governance/engineering-source-registry.schema.json"
    )
    assert profile["source_registry_schema_version"] == "1.0.0"
    assert profile["search_result_summary_is_source_record"] is False


def test_source_registry_schema_is_deterministic_and_claim_level() -> None:
    schema = load_registry_schema()

    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["additionalProperties"] is False
    assert schema["properties"]["schema_version"]["const"] == "1.0.0"
    assert (
        schema["properties"]["content_hash"]["properties"]["value"]["pattern"] == "^[a-f0-9]{64}$"
    )
    assert schema["properties"]["content_hash"]["properties"]["algorithm"]["const"] == "sha256"
    assert schema["properties"]["retrieval_date"]["format"] == "date-time"
    assert schema["properties"]["publication_date"]["format"] == "date"
    assert schema["properties"]["external_publication_status"]["enum"] == [
        "draft",
        "final",
        "superseded",
        "withdrawn",
    ]
    assert schema["properties"]["internal_registry_status"]["enum"] == [
        "proposed",
        "approved",
        "rejected",
        "deprecated",
    ]
    assert schema["properties"]["permitted_evidence_use"]["enum"] == [
        "normative",
        "supporting",
        "watch_only",
        "prohibited",
    ]
    claim_schema = schema["properties"]["claims"]["items"]
    assert {
        "claim_id",
        "section_or_fragment_reference",
        "summarized_external_statement",
        "applicable_technology_and_version",
        "permitted_evidence_use",
        "known_limitations",
    } <= set(claim_schema["required"])


def test_profile_reference_integrity_blocks_invalid_normative_source_references() -> None:
    integrity = load_profile()["profile_reference_integrity"]

    assert integrity["active_profile_may_reference_unknown_source_ids"] is False
    assert integrity["normative_reference_requires_internal_registry_status"] == "approved"
    assert integrity["normative_reference_requires_permitted_evidence_use"] == "normative"
    assert integrity["normative_reference_allows_external_publication_status"] == ["final"]
    assert integrity["normative_reference_requires_claim_ids"] is True
    assert integrity["forbidden_normative_internal_registry_statuses"] == [
        "proposed",
        "rejected",
        "deprecated",
    ]
    assert integrity["forbidden_normative_permitted_evidence_use"] == [
        "supporting",
        "watch_only",
        "prohibited",
    ]
    assert integrity["forbidden_normative_external_publication_statuses"] == [
        "draft",
        "superseded",
        "withdrawn",
    ]
    assert integrity["invalid_references_fail_validation"] is True


def test_role_baseline_coverage_is_task_filtered_not_profile_mutating() -> None:
    profile = load_profile()
    expected_classes = {source_class["id"] for source_class in profile["source_classes"]}

    for role, required_classes in profile["role_baseline_coverage"].items():
        assert required_classes, role
        assert set(required_classes) <= expected_classes

    task_selection = profile["task_source_selection"]
    assert task_selection["baseline_awareness_required"] is True
    assert task_selection["task_specific_source_use_required"] is True
    assert task_selection["consume_all_role_sources_for_every_task"] is False
    assert task_selection["pull_request_reviews_consume_active_profile"] is True
    assert task_selection["pull_request_reviews_define_or_mutate_profile"] is False
    assert "demonstrable_connection" in task_selection["selection_rule"]


def test_governance_skill_can_propose_but_not_approve_or_mutate_scope() -> None:
    skill = load_profile()["maintenance_skill"]
    permissions = skill["permissions"]

    assert skill["name"] == "engineering-source-governance"
    assert "inspect_repository_declared_engineering_scope" in skill["responsibilities"]
    assert "scheduled_profile_revalidation" in skill["execution_triggers"]
    assert permissions["may_create_proposed_change"] is True
    assert permissions["may_create_auditable_validation_report"] is True
    assert permissions["may_directly_modify_active_normative_profile"] is False
    assert permissions["may_change_code_tests_dependencies_configuration_or_runtime"] is False
    assert permissions["may_create_or_modify_adr"] is False
    assert permissions["may_create_implementation_work_automatically"] is False
    assert permissions["may_expand_product_scope"] is False
    assert permissions["may_treat_external_instructions_as_agent_instructions"] is False
    assert permissions["may_approve_own_normative_changes"] is False
    assert (
        skill["normative_activation_approval"] == "source_governance_approver_or_governance_judge"
    )
    assert skill["proposer_and_sole_approver_may_be_same_autonomous_agent"] is False


def test_profile_change_control_requires_approval_and_complete_change_record() -> None:
    change_control = load_profile()["source_profile_change_control"]

    assert change_control["skill_may_create_proposed_change"] is True
    assert change_control["normative_activation_requires_approval"] is True
    assert change_control["approval_authority"] == [
        "source_governance_approver",
        "governance_judge",
    ]
    assert {
        "reason_for_change",
        "affected_repository_scope",
        "previous_and_proposed_source_records",
        "source_lifecycle_changes",
        "affected_specialist_roles",
        "expected_assessment_impact",
        "security_considerations",
        "unresolved_conflicts",
        "recommendation",
        "proposed_activation_date",
    } <= set(change_control["required_proposed_change_fields"])


def test_audit_log_is_append_only_and_reconstructs_registry_profile_versions() -> None:
    audit = load_profile()["source_audit_log_rules"]

    assert audit["append_only"] is True
    assert audit["existing_records_may_be_edited"] is False
    assert audit["existing_records_may_be_deleted"] is False
    assert audit["corrections_require_new_record"] is True
    assert audit["correction_relationship_fields"] == ["corrects", "supersedes"]
    assert {
        "affected_source_ids",
        "previous_registry_version",
        "proposed_registry_version",
        "previous_profile_version",
        "proposed_profile_version",
        "structured_change_set",
        "decision_rationale",
        "superseded_audit_record",
    } <= set(audit["required_version_references"])
    assert audit["state_reconstruction_required"] is True


def test_external_content_is_untrusted_and_cannot_authorize_repository_actions() -> None:
    boundary = load_profile()["external_content_security_boundary"]

    assert boundary["all_external_content_is_untrusted_input"] is True
    assert boundary["source_authority_grants_execution_authority"] is False
    assert boundary["embedded_instructions_may_be_followed"] is False
    assert set(boundary["external_content_cannot_authorize"]) == {
        "tool_calls",
        "repository_writes",
        "source_profile_activation",
        "issue_or_backlog_creation",
        "adr_changes",
        "credential_use",
        "permission_expansion",
        "communication_with_external_systems",
    }
    assert boundary["high_impact_changes_require_separate_trusted_authorization"] is True


def test_new_knowledge_classification_limits_current_findings_and_future_scope() -> None:
    profile = load_profile()
    stability = profile["state_of_art_stability_principle"]
    classification = profile["new_knowledge_classification"]

    assert stability["state_of_art_scope"] == "specialist_assessment_capability"
    assert stability["continuous_modernization_mandate"] is False
    assert stability["current_production_work_precedence"] is True
    assert "security_vulnerability" in stability["mandatory_concern_requires_evidence_of"]
    assert classification["classes"] == [
        "current_mandatory_concern",
        "future_consideration",
        "not_applicable",
    ]
    assert (
        classification[
            "only_current_mandatory_concern_may_support_current_mandatory_review_finding"
        ]
        is True
    )
    assert classification["future_consideration_target"] == (
        "docs/governance/future-considerations-register.md"
    )
    assert classification["future_considerations_outside_current_pr_findings"] is True
    assert classification["future_considerations_outside_committed_delivery_scope"] is True
    assert "source_describes_only_alternative_approach" in classification["not_applicable_reasons"]


def test_architecture_and_adr_boundary_uses_evolution_register_without_mandate() -> None:
    boundary = load_profile()["architecture_and_adr_boundary"]

    assert boundary["accepted_adrs_remain_binding_until_authorized_supersession"] is True
    assert boundary["new_source_may_automatically_invalidate_adr"] is False
    assert boundary["new_source_may_automatically_create_adr"] is False
    assert boundary["new_source_may_automatically_amend_adr"] is False
    assert boundary["new_source_may_automatically_reopen_completed_architecture_work"] is False
    assert boundary["new_source_may_automatically_create_implementation_work"] is False
    assert boundary["potential_architecture_implication_target"] == (
        "docs/governance/architecture-evolution-register.md"
    )
    assert boundary["architecture_evolution_entry_is_approval"] is False
    assert boundary["architecture_evolution_entry_is_requirement"] is False
    assert boundary["architecture_evolution_entry_is_backlog_commitment"] is False
    assert boundary["architecture_evolution_entry_is_implementation_mandate"] is False
    assert {
        "entry_identifier",
        "created_at",
        "created_by",
        "originating_source_governance_audit_record",
        "last_reviewed_at",
        "next_reassessment_date_or_trigger",
        "new_knowledge_classification_reference",
        "classification_evidence",
        "relevant_sources",
        "affected_components",
        "affected_adrs",
        "assumptions_that_may_no_longer_hold",
        "implementation_and_migration_cost",
        "recommended_reassessment_point",
    } <= set(boundary["required_entry_fields"])
    assert boundary["allowed_statuses"] == [
        "proposed",
        "parked",
        "accepted_for_reassessment",
        "handed_off_for_adr_evaluation",
        "handed_off_for_backlog_triage",
        "rejected",
        "superseded",
        "closed",
    ]
    assert (
        boundary["handoff_statuses_require_target_reference_receiver_and_acceptance_time"] is True
    )
    assert boundary["standard_entry_requires_future_consideration_classification"] is True
    assert (
        boundary["current_mandatory_concern_must_also_use_defect_security_or_review_process"]
        is True
    )


def test_source_conflicts_have_required_record_and_judge_path() -> None:
    conflicts = load_profile()["source_conflict_process"]

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


def test_production_readiness_protection_blocks_continuous_modernization() -> None:
    protection = load_profile()["production_readiness_protection"]

    assert protection["purpose_is_informed_specialists_not_permanent_product_redevelopment"] is True
    assert protection["newer_technology_is_automatically_better"] is False
    assert protection["newer_technology_is_automatically_defect"] is False
    assert protection["newer_technology_is_automatically_release_blocker"] is False
    assert protection["newer_technology_is_automatically_adr_candidate"] is False
    assert protection["newer_technology_is_automatically_backlog_item"] is False
    assert protection["newer_technology_is_automatically_implementation_requirement"] is False
    assert (
        protection[
            "current_production_work_takes_precedence_without_present_mandatory_concern_or_authorized_target_change"
        ]
        is True
    )


def test_governance_docs_publish_policy_profile_registry_audit_and_evolution_boundary() -> None:
    governance = (GOVERNANCE_DIR / "engineering-source-governance.md").read_text(encoding="utf-8")
    normalized_governance = " ".join(governance.split())
    index = (GOVERNANCE_DIR / "README.md").read_text(encoding="utf-8")
    root_readme = (ROOT / "README.md").read_text(encoding="utf-8")
    future_register = (GOVERNANCE_DIR / "future-considerations-register.md").read_text(
        encoding="utf-8"
    )
    source_registry = (GOVERNANCE_DIR / "engineering-source-registry.md").read_text(
        encoding="utf-8"
    )
    audit_records = (GOVERNANCE_DIR / "source-governance-audit-records.md").read_text(
        encoding="utf-8"
    )
    evolution_register = (GOVERNANCE_DIR / "architecture-evolution-register.md").read_text(
        encoding="utf-8"
    )

    assert "Explicitly excluded: Product runtime" in governance
    assert "product memory" in governance
    assert "Global Engineering Source Policy" in governance
    assert "Engineering Source Registry" in governance
    assert "Source Governance Audit Records" in governance
    assert "Internal model knowledge is neither repository evidence" in governance
    assert "A search-result summary is not a source record." in governance
    assert "Future Consideration" in governance
    assert "Architecture Evolution Register entry is not an approval" in normalized_governance
    assert "Engineering source governance" in index
    assert "engineering-source-registry.md" in index
    assert "engineering-source-registry.schema.json" in index
    assert "source-governance-audit-records.md" in index
    assert "architecture-evolution-register.md" in index
    assert "Engineering source governance" in root_readme
    assert "Engineering source registry" in root_readme
    assert "source record schema" in root_readme
    assert "source governance audit records" in root_readme
    assert "architecture evolution register" in root_readme
    assert "It never becomes product work automatically." in future_register
    assert "No individual source records are active yet." in source_registry
    assert "No governance audit events have been recorded yet." in audit_records
    assert "No architecture evolution entries are active." in evolution_register
    assert "External publication status never creates internal approval." in source_registry
    assert "append-only" in audit_records
    assert "handoff accepted at" in evolution_register
