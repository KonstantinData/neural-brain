"""Evidence for the fail-closed data-subject-request evidence intake."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
CONTRACT_PATH = (
    ROOT / "docs" / "architecture" / "contracts" / "data-subject-request-evidence-intake-v1.json"
)


def _contract() -> dict[str, object]:
    loaded: object = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _strings(value: object) -> set[str]:
    assert isinstance(value, list)
    assert all(isinstance(item, str) for item in value)
    return set(value)


def test_template_requires_scope_request_case_and_qualified_privacy_review_evidence() -> None:
    contract = _contract()
    assert contract["contract_id"] == "neural-brain.data-subject-request-evidence-intake"
    assert contract["contract_version"] == "1.0.0"
    assert contract["governing_decisions"] == ["ADR-001", "ADR-005", "ADR-018", "ADR-019"]
    external = contract["authoritative_external_reference"]
    assert isinstance(external, dict)
    assert external["official_url"] == "https://eur-lex.europa.eu/eli/reg/2016/679/oj"
    template = contract["data_subject_request_evidence_intake_template"]
    assert isinstance(template, dict)
    required = _strings(template["required_fields"])
    assert {
        "qualified_privacy_reviewer_qualification_review_date_and_independence_reference",
        "immutable_authenticated_tenant_area_project_scope_references",
        "immutable_intended_purpose_contract_id_version_and_purpose_reference",
        "immutable_processing_activity_identifier_version_and_activity_reference",
        "request_category_candidate_and_request_scope_evidence_references_for_qualified_review_only",
        "identity_verification_and_representative_authorization_evidence_references_for_qualified_review_only",
        "deadline_timing_extension_and_communication_evidence_references_for_qualified_review_only",
        "case_tracking_identifier_lifecycle_provenance_and_immutability_evidence_references",
        "audit_redaction_data_minimisation_and_access_control_evidence_references",
        "escalation_exception_conflict_and_downstream_coordination_evidence_references",
    } <= required
    scope_binding = _strings(template["scope_binding_requirements"])
    assert any(
        "cannot establish, broaden, or substitute trusted scope" in item for item in scope_binding
    )
    assert any("must not contain raw personal data" in item for item in scope_binding)
    assert any("Unknown, stale, contradictory" in item for item in scope_binding)


def test_review_order_and_reassessment_keep_request_evidence_fail_closed() -> None:
    template = _contract()["data_subject_request_evidence_intake_template"]
    assert isinstance(template, dict)
    order = template["deterministic_review_order"]
    assert isinstance(order, list)
    assert len(order) == 6
    assert isinstance(order[2], str)
    assert "without classifying, validating, selecting, or concluding a request" in order[2]
    assert isinstance(order[3], str)
    assert "audit, redaction, data minimisation, access-control, escalation" in order[3]
    assert isinstance(order[4], str)
    assert "non-applicability, unknown, gap, conflict, expiry, and escalation" in order[4]
    triggers = _strings(template["mandatory_reassessment_triggers"])
    assert {
        "authenticated_tenant_area_project_scope_purpose_activity_request_category_or_jurisdiction_change",
        "identity_verification_representative_authorization_deadline_timing_or_communication_evidence_change",
        "case_tracking_audit_redaction_data_minimisation_access_control_or_escalation_change",
    } <= triggers


def test_missing_evidence_blocks_without_legal_runtime_or_request_execution_claim() -> None:
    contract = _contract()
    semantics = contract["fail_closed_semantics"]
    assert isinstance(semantics, dict)
    assert all(
        semantics[key]
        == "data_subject_request_evidence_intake_incomplete_and_deployment_specific_release_blocked"
        for key in (
            "unknown_or_missing_required_field",
            "stale_scope_mismatched_or_contradictory_evidence",
            "missing_qualified_privacy_reviewer_independence_review_date_rationale_evidence_or_reassessment_trigger",
            "unknown_unqualified_stale_or_conflicting_request_identity_deadline_case_audit_redaction_escalation_or_external_fact",
            "unresolved_request_category_identity_verification_representative_authorization_deadline_case_tracking_audit_redaction_or_escalation_evidence",
        )
    )
    assert (
        semantics[
            "missing_or_nonimmutable_authenticated_scope_purpose_activity_or_artifact_reference"
        ]
        == "reject_intake_and_block_deployment_specific_release_decision"
    )
    assert (
        semantics[
            "cross_boundary_or_changed_artifact_purpose_activity_request_category_case_or_jurisdiction_evidence_reuse"
        ]
        == "reject_intake_and_block_deployment_specific_release_decision"
    )
    assert (
        semantics["proposed_personal_data_or_secret_payload"]
        == "reject_intake_and_record_data_minimization_blocker"
    )
    assert semantics["no_automatic_legal_or_regulatory_conclusion"] is True
    assert semantics["no_automatic_request_identity_deadline_or_obligation_determination"] is True
    assert semantics["no_runtime_authorization_processing_activation_or_enablement"] is True
    assert semantics["no_automatic_release_or_authority_outcome"] is True
    assert semantics["no_request_handling_or_data_subject_right_execution"] is True
    assert semantics["no_allow_outcome"] is True
    boundary = contract["authority_boundary"]
    assert isinstance(boundary, dict)
    assert {
        "a legal opinion, data-subject request determination, identity-verification determination, deadline determination, or compliance certification",
        "a processing, deployment, productive-use, request-handling, or release approval",
        "a runtime capability enablement, personal-data operation, or external-effect authorization",
        "an implementation, capability, maturity, recognition, safety, or production-autonomy claim",
    } <= _strings(boundary["template_is_not"])
