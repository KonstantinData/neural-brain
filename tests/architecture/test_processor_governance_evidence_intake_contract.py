"""Evidence for the fail-closed processor-governance evidence intake."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
CONTRACT_PATH = (
    ROOT / "docs" / "architecture" / "contracts" / "processor-governance-evidence-intake-v1.json"
)


def _contract() -> dict[str, object]:
    loaded: object = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _strings(value: object) -> set[str]:
    assert isinstance(value, list)
    assert all(isinstance(item, str) for item in value)
    return set(value)


def test_template_requires_scope_review_relationship_and_article_28_evidence() -> None:
    contract = _contract()
    assert contract["contract_id"] == "neural-brain.processor-governance-evidence-intake"
    assert contract["contract_version"] == "1.0.0"
    assert contract["governing_decisions"] == ["ADR-001", "ADR-005", "ADR-018", "ADR-019"]
    external = contract["authoritative_external_reference"]
    assert isinstance(external, dict)
    assert external["official_url"] == "https://eur-lex.europa.eu/eli/reg/2016/679/oj"
    template = contract["processor_governance_evidence_intake_template"]
    assert isinstance(template, dict)
    required = _strings(template["required_fields"])
    assert required == {
        "intake_identifier_and_contract_version",
        "intake_timestamp_accountable_owner_and_qualified_reviewer_qualification_review_date_and_independence_reference",
        "immutable_artifact_version_or_digest",
        "deployment_identifier_target_environment_and_jurisdiction_evidence",
        "immutable_authenticated_tenant_area_project_scope_references",
        "immutable_intended_purpose_contract_id_version_and_purpose_reference",
        "immutable_processing_activity_identifier_version_and_activity_reference",
        "linked_ropa_gdpr_role_applicability_use_case_article_6_and_reassessment_evidence_references",
        "proposed_party_and_processor_or_subprocessor_role_scope_and_controller_relationship_evidence_references",
        "documented_instruction_evidence_references_for_qualified_review_only",
        "security_and_confidentiality_evidence_references_for_qualified_review_only",
        "subprocessor_due_diligence_change_and_authorization_evidence_references_for_qualified_review_only",
        "audit_assistance_and_evidence_access_references_for_qualified_review_only",
        "international_transfer_location_and_safeguard_evidence_references_for_qualified_review_only",
        "deletion_or_return_and_termination_evidence_references_for_qualified_review_only",
        "external_facts_source_provenance_date_currency_and_scope_evidence_references",
        "explicit_non_applicability_unknown_conflict_gap_and_blocker_handling",
        "review_rationale_verified_evidence_references_release_blockers_and_next_review_date",
        "mandatory_reassessment_triggers_and_independent_release_decision_reference",
    }
    scope_binding = _strings(template["scope_binding_requirements"])
    assert any(
        "cannot establish, broaden, or substitute trusted scope" in item for item in scope_binding
    )
    assert any("must not contain raw personal data" in item for item in scope_binding)
    assert any("contract terms" in item for item in scope_binding)


def test_review_order_requires_article_28_evidence_without_contract_or_appointment() -> None:
    template = _contract()["processor_governance_evidence_intake_template"]
    assert isinstance(template, dict)
    order = template["deterministic_review_order"]
    assert isinstance(order, list)
    assert len(order) == 6
    assert isinstance(order[2], str)
    assert "without selecting a role, appointing a party" in order[2]
    assert isinstance(order[3], str)
    assert all(
        token in order[3]
        for token in (
            "security",
            "confidentiality",
            "subprocessor",
            "audit",
            "transfer",
            "deletion/return",
            "termination",
        )
    )
    triggers = _strings(template["mandatory_reassessment_triggers"])
    assert {
        "authenticated_tenant_area_project_scope_purpose_activity_relationship_or_jurisdiction_change",
        "party_processor_or_subprocessor_role_scope_controller_relationship_or_instruction_change",
        "security_confidentiality_subprocessor_audit_assistance_or_evidence_access_change",
        "location_transfer_safeguard_deletion_return_change_or_termination_change",
    } <= triggers


def test_missing_or_unknown_evidence_blocks_without_legal_contract_authority_runtime_or_release_outcome() -> (
    None
):
    contract = _contract()
    semantics = contract["fail_closed_semantics"]
    assert isinstance(semantics, dict)
    assert all(
        semantics[key]
        == "processor_governance_evidence_intake_incomplete_and_deployment_specific_release_blocked"
        for key in (
            "unknown_or_missing_required_field",
            "stale_scope_mismatched_or_contradictory_evidence",
            "missing_qualified_reviewer_review_date_rationale_evidence_or_reassessment_trigger",
            "unknown_unqualified_stale_or_conflicting_processor_subprocessor_article_28_or_external_fact",
            "missing_instruction_security_confidentiality_subprocessor_audit_transfer_deletion_return_change_or_termination_evidence",
            "unknown_downstream_processor_or_subprocessor",
        )
    )
    assert (
        semantics[
            "missing_or_nonimmutable_authenticated_scope_purpose_activity_relationship_or_artifact_reference"
        ]
        == "reject_intake_and_block_deployment_specific_release_decision"
    )
    assert (
        semantics["proposed_personal_data_or_secret_payload"]
        == "reject_intake_and_record_data_minimization_blocker"
    )
    assert (
        semantics["no_automatic_article_28_applicability_sufficiency_or_processor_appointment"]
        is True
    )
    assert semantics["no_runtime_authorization_processing_activation_or_enablement"] is True
    assert semantics["no_automatic_release_or_authority_outcome"] is True
    assert semantics["no_allow_outcome"] is True
    boundary = contract["authority_boundary"]
    assert isinstance(boundary, dict)
    assert {
        "a legal opinion, Article 28 applicability or sufficiency determination, or compliance certification",
        "a data-processing agreement, contract terms, controller-processor instruction, processor or subprocessor appointment, authorization, or approval",
        "a processing, deployment, productive-use, or release approval",
        "a runtime capability enablement or external-effect authorization",
        "an implementation, maturity, recognition, safety, product capability, or production-autonomy claim",
    } <= _strings(boundary["template_is_not"])
