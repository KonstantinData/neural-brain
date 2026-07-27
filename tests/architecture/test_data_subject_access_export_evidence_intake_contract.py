"""Evidence for the fail-closed data-subject access and export evidence intake."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
CONTRACT_PATH = (
    ROOT
    / "docs"
    / "architecture"
    / "contracts"
    / "data-subject-access-export-evidence-intake-v1.json"
)


def _contract() -> dict[str, object]:
    loaded: object = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _strings(value: object) -> set[str]:
    assert isinstance(value, list)
    assert all(isinstance(item, str) for item in value)
    return set(value)


def test_template_requires_scope_inventory_coverage_and_qualified_review_evidence() -> None:
    contract = _contract()
    assert contract["contract_id"] == "neural-brain.data-subject-access-export-evidence-intake"
    assert contract["contract_version"] == "1.0.0"
    assert contract["governing_decisions"] == ["ADR-001", "ADR-005", "ADR-018", "ADR-019"]
    external = contract["authoritative_external_reference"]
    assert isinstance(external, dict)
    assert external["official_url"] == "https://eur-lex.europa.eu/eli/reg/2016/679/oj"
    template = contract["data_subject_access_export_evidence_intake_template"]
    assert isinstance(template, dict)
    required = _strings(template["required_fields"])
    assert required == {
        "intake_identifier_and_contract_version",
        "intake_timestamp_and_accountable_owner_reference",
        "qualified_independent_privacy_reviewer_qualification_review_date_and_independence_reference",
        "immutable_artifact_version_or_digest",
        "deployment_identifier_target_environment_and_jurisdiction_evidence_references",
        "immutable_authenticated_tenant_area_project_scope_references",
        "immutable_intended_purpose_contract_id_version_and_purpose_reference",
        "immutable_processing_activity_identifier_version_and_activity_reference",
        "linked_data_object_catalogue_ropa_data_flow_data_subject_request_and_reassessment_evidence_references",
        "case_tracking_request_category_identity_and_representative_authorization_evidence_references_for_qualified_review_only",
        "category_only_primary_data_memory_evidence_log_cache_derivative_backup_and_archive_inventory_references",
        "category_only_discovery_coverage_method_boundary_gap_and_currency_evidence_references_for_qualified_review_only",
        "data_source_owner_location_recipient_subprocessor_transfer_retention_legal_hold_and_deletion_linkage_evidence_references",
        "access_copy_portability_recipient_information_format_delivery_security_and_export_evidence_references_for_qualified_review_only",
        "third_party_rights_redaction_data_minimisation_access_control_and_audit_evidence_references_for_qualified_review_only",
        "cache_derivative_backup_archive_recovery_and_deletion_propagation_evidence_references_for_qualified_review_only",
        "explicit_non_applicability_unknown_gap_conflict_expiry_and_unavailable_source_dispositions",
        "mandatory_reassessment_triggers_next_review_date_and_independent_release_decision_reference",
    }
    scope_binding = _strings(template["scope_binding_requirements"])
    assert any(
        "cannot establish, broaden, or substitute trusted scope" in item for item in scope_binding
    )
    assert any("must not contain raw personal data" in item for item in scope_binding)
    assert any("Unknown, stale, contradictory" in item for item in scope_binding)


def test_review_order_and_reassessment_keep_discovery_and_export_evidence_fail_closed() -> None:
    template = _contract()["data_subject_access_export_evidence_intake_template"]
    assert isinstance(template, dict)
    order = template["deterministic_review_order"]
    assert isinstance(order, list)
    assert len(order) == 6
    assert isinstance(order[2], str)
    assert "without discovering, reading, enumerating, or copying a data store" in order[2]
    assert isinstance(order[3], str)
    assert "without determining a right, obligation, completeness" in order[3]
    assert isinstance(order[4], str)
    assert "third-party-rights, redaction, data minimisation" in order[4]
    triggers = _strings(template["mandatory_reassessment_triggers"])
    assert {
        "authenticated_tenant_area_project_scope_purpose_activity_jurisdiction_or_case_reference_change",
        "discovery_coverage_method_boundary_gap_currency_or_unavailable_source_disposition_change",
        "access_export_format_delivery_security_third_party_right_redaction_audit_cache_derivative_backup_archive_or_recovery_evidence_change",
    } <= triggers


def test_missing_evidence_blocks_without_discovery_export_or_runtime_claim() -> None:
    contract = _contract()
    semantics = contract["fail_closed_semantics"]
    assert isinstance(semantics, dict)
    blocked = "data_subject_access_export_evidence_intake_incomplete_and_deployment_specific_release_blocked"
    assert all(
        semantics[key] == blocked
        for key in (
            "unknown_or_missing_required_field",
            "stale_scope_mismatched_or_contradictory_evidence",
            "missing_accountable_owner_qualified_independent_privacy_reviewer_review_date_inventory_coverage_or_reassessment_trigger",
            "unknown_unqualified_stale_conflicting_or_unavailable_inventory_discovery_export_redaction_third_party_cache_derivative_or_deletion_linkage_evidence",
            "unresolved_coverage_gap_unavailable_source_third_party_right_redaction_or_export_evidence",
        )
    )
    assert semantics["no_automatic_legal_or_regulatory_conclusion"] is True
    assert (
        semantics[
            "no_automatic_data_subject_right_identity_deadline_completeness_or_obligation_determination"
        ]
        is True
    )
    assert semantics["no_data_discovery_store_access_export_delivery_or_disclosure"] is True
    assert semantics["no_runtime_authorization_processing_activation_or_enablement"] is True
    assert semantics["no_automatic_release_or_authority_outcome"] is True
    assert semantics["no_allow_outcome"] is True
    boundary = contract["authority_boundary"]
    assert isinstance(boundary, dict)
    assert {
        "a data discovery, inventory enumeration, data-store access, data collection, record lookup, export generation, export delivery, or disclosure workflow",
        "a processing, deployment, productive-use, data-subject-request handling, or release approval",
        "a runtime capability enablement, personal-data operation, protected-state write, or external-effect authorization",
        "an implementation, capability, maturity, recognition, safety, or production-autonomy claim",
    } <= _strings(boundary["template_is_not"])
