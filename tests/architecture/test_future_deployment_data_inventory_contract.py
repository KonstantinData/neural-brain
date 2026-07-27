"""Evidence for the future deployment data-inventory readiness template."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
CONTRACT_PATH = (
    ROOT / "docs" / "architecture" / "contracts" / "future-deployment-data-inventory-v1.json"
)


def _contract() -> dict[str, object]:
    loaded: object = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _strings(value: object) -> set[str]:
    assert isinstance(value, list)
    assert all(isinstance(item, str) for item in value)
    return set(value)


def test_inventory_requires_all_category_only_data_classes_and_scope_review() -> None:
    contract = _contract()
    assert contract["contract_id"] == "neural-brain.future-deployment-data-inventory"
    assert contract["governing_decisions"] == ["ADR-001", "ADR-005", "ADR-018", "ADR-019"]
    template = contract["future_deployment_inventory_template"]
    assert isinstance(template, dict)
    assert _strings(template["required_data_class_categories"]) == {
        "primary_data",
        "memory",
        "working_memory",
        "episodic_memory",
        "semantic_memory",
        "procedural_memory",
        "evidence",
        "logs",
        "cache",
        "embeddings",
        "attachments",
        "artefacts",
        "backups",
        "archives",
        "derivatives",
        "indexes",
        "recovery",
        "retention",
    }
    required = _strings(template["required_fields"])
    assert required == {
        "inventory_record_identifier_and_contract_version",
        "intake_timestamp_accountable_owner_and_qualified_independent_privacy_reviewer_references",
        "immutable_artifact_version_or_digest_and_proposed_deployment_identifier",
        "immutable_authenticated_tenant_area_project_scope_references",
        "immutable_intended_purpose_processing_activity_and_jurisdiction_references",
        "linked_ropa_data_object_catalogue_data_flow_data_subject_request_and_export_evidence_intake_references",
        "data_class_category_lifecycle_surface_and_category_only_description",
        "primary_data_memory_working_memory_episodic_memory_semantic_memory_and_procedural_memory_classification_evidence",
        "evidence_logs_cache_embeddings_attachments_artefacts_backups_archives_derivatives_indexes_recovery_and_retention_classification_evidence",
        "category_only_source_owner_location_store_boundary_and_lineage_evidence",
        "export_coverage_matrix_row_and_coverage_gap_evidence",
        "redaction_and_third_party_rights_matrix_row_and_qualified_review_evidence",
        "legal_basis_controller_processor_and_tenant_scope_matrix_rows_and_evidence",
        "retention_legal_hold_backup_archive_recovery_and_deletion_propagation_evidence",
        "export_readiness_checklist_review_workflow_audit_workflow_and_reassessment_evidence",
        "explicit_unknown_non_applicability_conflict_expiry_unavailable_source_and_release_stop_dispositions",
    }
    binding = _strings(template["scope_binding_requirements"])
    assert any(
        "cannot establish, broaden, substitute, or override trusted scope" in item
        for item in binding
    )
    assert any("must not contain personal data" in item for item in binding)


def test_all_readiness_matrices_have_required_evidence_fields() -> None:
    template = _contract()["future_deployment_inventory_template"]
    assert isinstance(template, dict)
    matrices = template["required_matrix_templates"]
    assert isinstance(matrices, dict)
    assert set(matrices) == {
        "export_coverage_matrix",
        "redaction_matrix",
        "third_party_rights_matrix",
        "legal_basis_matrix",
        "controller_matrix",
        "processor_matrix",
        "tenant_scope_matrix",
    }
    assert "gap_or_unavailable_source_disposition" in _strings(matrices["export_coverage_matrix"])
    assert "qualified_review_reference" in _strings(matrices["redaction_matrix"])
    assert "unresolved_disposition" in _strings(matrices["third_party_rights_matrix"])
    assert "legal_basis_evidence_intake_reference" in _strings(matrices["legal_basis_matrix"])
    assert "controller_role_evidence_reference" in _strings(matrices["controller_matrix"])
    assert "processor_or_subprocessor_evidence_reference" in _strings(matrices["processor_matrix"])
    assert "immutable_authenticated_tenant_area_project_scope_references" in _strings(
        matrices["tenant_scope_matrix"]
    )


def test_inventory_is_fail_closed_and_creates_no_operational_path() -> None:
    contract = _contract()
    semantics = contract["fail_closed_semantics"]
    assert isinstance(semantics, dict)
    blocked = "future_deployment_data_inventory_incomplete_and_deployment_specific_release_blocked"
    assert semantics["unknown_or_missing_required_field"] == blocked
    assert semantics["missing_required_data_class_or_matrix_row"] == blocked
    assert (
        semantics["stale_scope_mismatched_contradictory_unqualified_or_unavailable_evidence"]
        == blocked
    )
    assert (
        semantics["no_data_discovery_store_access_processing_export_delivery_or_disclosure"] is True
    )
    assert semantics["no_runtime_authorization_processing_activation_or_enablement"] is True
    assert semantics["no_automatic_release_or_authority_outcome"] is True
    assert semantics["no_allow_outcome"] is True
    boundary = contract["authority_boundary"]
    assert isinstance(boundary, dict)
    prohibited = _strings(boundary["template_is_not"])
    assert {
        "a real data inventory, data discovery, store enumeration, record lookup, data collection, processing, or export workflow",
        "a processing, deployment, productive-use, disclosure, recovery, retention, or release approval",
        "a runtime capability enablement, protected-state write, external-effect authorization, maturity claim, recognition claim, or production-autonomy claim",
    } <= prohibited
