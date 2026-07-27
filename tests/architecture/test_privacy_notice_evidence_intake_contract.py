"""Evidence for the fail-closed privacy-notice evidence intake."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
CONTRACT_PATH = (
    ROOT / "docs" / "architecture" / "contracts" / "privacy-notice-evidence-intake-v1.json"
)


def _contract() -> dict[str, object]:
    loaded: object = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _strings(value: object) -> set[str]:
    assert isinstance(value, list)
    assert all(isinstance(item, str) for item in value)
    return set(value)


def test_template_requires_collection_paths_notice_elements_and_qualified_review() -> None:
    contract = _contract()
    assert contract["contract_id"] == "neural-brain.privacy-notice-evidence-intake"
    assert contract["contract_version"] == "1.0.0"
    assert contract["governing_decisions"] == ["ADR-001", "ADR-005", "ADR-018", "ADR-019"]
    external = contract["authoritative_external_reference"]
    assert isinstance(external, dict)
    assert external["official_url"] == "https://eur-lex.europa.eu/eli/reg/2016/679/oj"
    template = contract["privacy_notice_evidence_intake_template"]
    assert isinstance(template, dict)
    required = _strings(template["required_fields"])
    assert {
        "qualified_reviewer_qualification_review_date_and_independence_reference",
        "immutable_authenticated_tenant_area_project_scope_references",
        "immutable_intended_purpose_contract_id_version_and_purpose_reference",
        "immutable_processing_activity_identifier_version_and_activity_reference",
        "collection_path_direct_or_indirect_and_collection_event_evidence_references",
        "controller_representative_and_dpo_contact_evidence_references",
        "purpose_basis_personal_data_category_and_data_subject_category_evidence_references",
        "indirect_collection_source_category_and_source_information_evidence_references",
        "recipient_processor_location_and_transfer_boundary_evidence_references",
        "retention_deletion_and_reassessment_evidence_references",
        "data_subject_rights_complaint_and_contact_route_evidence_references",
        "article_22_automated_decision_and_profiling_disposition_evidence_references",
        "notice_delivery_timing_language_accessibility_and_version_integrity_evidence_references",
        "explicit_non_applicability_unknown_conflict_gap_and_expiry_dispositions",
    } <= required
    scope_binding = _strings(template["scope_binding_requirements"])
    assert any(
        "cannot establish, broaden, or substitute trusted scope" in item for item in scope_binding
    )
    assert any("must not contain raw personal data" in item for item in scope_binding)
    assert any("Unknown, stale, contradictory" in item for item in scope_binding)


def test_review_order_and_reassessment_keep_notice_evidence_fail_closed() -> None:
    template = _contract()["privacy_notice_evidence_intake_template"]
    assert isinstance(template, dict)
    order = template["deterministic_review_order"]
    assert isinstance(order, list)
    assert len(order) == 6
    assert isinstance(order[2], str)
    assert "without selecting, validating, or concluding any notice requirement" in order[2]
    assert isinstance(order[3], str)
    assert "Article 22 automated-decision or profiling disposition" in order[3]
    assert isinstance(order[4], str)
    assert "non-applicability, unknown, conflict, gap, and evidence-expiry" in order[4]
    triggers = _strings(template["mandatory_reassessment_triggers"])
    assert {
        "authenticated_tenant_area_project_scope_purpose_activity_jurisdiction_or_collection_path_change",
        "notice_delivery_timing_language_accessibility_version_integrity_or_currency_change",
        "retention_deletion_rights_complaint_contact_or_article_22_disposition_change",
    } <= triggers


def test_missing_evidence_blocks_without_legal_authority_runtime_or_release_claim() -> None:
    contract = _contract()
    semantics = contract["fail_closed_semantics"]
    assert isinstance(semantics, dict)
    assert all(
        semantics[key]
        == "privacy_notice_evidence_intake_incomplete_and_deployment_specific_release_blocked"
        for key in (
            "unknown_or_missing_required_field",
            "stale_scope_mismatched_or_contradictory_evidence",
            "missing_qualified_reviewer_independence_review_date_rationale_evidence_or_reassessment_trigger",
            "unknown_unqualified_stale_or_conflicting_notice_element_external_fact_or_non_applicability_assertion",
            "unresolved_collection_path_contact_purpose_category_source_recipient_transfer_retention_rights_article_22_delivery_accessibility_or_version_evidence",
        )
    )
    assert (
        semantics[
            "missing_or_nonimmutable_authenticated_scope_purpose_activity_jurisdiction_or_collection_path_reference"
        ]
        == "reject_intake_and_block_deployment_specific_release_decision"
    )
    assert (
        semantics[
            "cross_boundary_or_changed_artifact_purpose_activity_jurisdiction_collection_path_or_notice_version_evidence_reuse"
        ]
        == "reject_intake_and_block_deployment_specific_release_decision"
    )
    assert (
        semantics["proposed_personal_data_or_secret_payload"]
        == "reject_intake_and_record_data_minimization_blocker"
    )
    assert semantics["no_automatic_legal_or_regulatory_conclusion"] is True
    assert semantics["no_automatic_privacy_notice_sufficiency_or_lawfulness_determination"] is True
    assert (
        semantics["no_runtime_authorization_collection_processing_activation_or_enablement"] is True
    )
    assert semantics["no_automatic_release_or_authority_outcome"] is True
    assert semantics["no_allow_outcome"] is True
    boundary = contract["authority_boundary"]
    assert isinstance(boundary, dict)
    assert {
        "a legal opinion, privacy-notice sufficiency determination, or compliance certification",
        "a collection, processing, disclosure, transfer, deployment, productive-use, or release approval",
        "a runtime capability enablement or external-effect authorization",
        "an implementation, maturity, recognition, safety, or production-autonomy claim",
    } <= _strings(boundary["template_is_not"])
