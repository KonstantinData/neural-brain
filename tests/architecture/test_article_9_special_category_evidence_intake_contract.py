"""Evidence for the fail-closed Article 9 special-category evidence intake."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
CONTRACT_PATH = (
    ROOT
    / "docs"
    / "architecture"
    / "contracts"
    / "article-9-special-category-evidence-intake-v1.json"
)


def _contract() -> dict[str, object]:
    loaded: object = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _strings(value: object) -> set[str]:
    assert isinstance(value, list)
    assert all(isinstance(item, str) for item in value)
    return set(value)


def test_template_requires_scope_review_special_category_and_control_evidence() -> None:
    contract = _contract()
    assert contract["contract_id"] == "neural-brain.article-9-special-category-evidence-intake"
    assert contract["contract_version"] == "1.0.0"
    assert contract["status"] == "normative_foundation_documentation_preparation_template"
    assert contract["governing_decisions"] == ["ADR-001", "ADR-005", "ADR-018", "ADR-019"]
    external = contract["authoritative_external_reference"]
    assert isinstance(external, dict)
    assert external["official_url"] == "https://eur-lex.europa.eu/eli/reg/2016/679/oj"
    template = contract["special_category_evidence_intake_template"]
    assert isinstance(template, dict)
    required = _strings(template["required_fields"])
    assert required == {
        "intake_identifier_and_contract_version",
        "intake_timestamp_and_accountable_owner",
        "qualified_reviewer_qualification_review_date_and_independence_reference",
        "immutable_artifact_version_or_digest",
        "deployment_identifier_target_environment_and_jurisdiction_evidence",
        "immutable_authenticated_tenant_area_project_scope_references",
        "immutable_intended_purpose_contract_id_version_and_purpose_reference",
        "immutable_processing_activity_identifier_version_and_activity_reference",
        "linked_ropa_gdpr_role_applicability_article_6_use_case_and_reassessment_evidence_references",
        "personal_data_data_subject_and_special_category_classification_evidence_references",
        "article_9_condition_candidate_and_qualified_safeguard_evidence_or_qualified_not_applicable_disposition_for_qualified_review_only",
        "article_10_official_authority_or_union_member_state_law_authorization_safeguards_and_comprehensive_register_control_evidence_or_qualified_not_applicable_disposition",
        "necessity_data_minimisation_retention_deletion_and_data_subject_rights_evidence_references",
        "recipient_processor_location_and_international_transfer_evidence_references",
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
    assert any("Unknown, stale, contradictory" in item for item in scope_binding)


def test_review_order_requires_article_10_disposition_and_fail_closed_reassessment() -> None:
    template = _contract()["special_category_evidence_intake_template"]
    assert isinstance(template, dict)
    order = template["deterministic_review_order"]
    assert isinstance(order, list)
    assert len(order) == 6
    assert isinstance(order[2], str)
    assert "exactly-one candidate-evidence-or-qualified-not-applicable" in order[2]
    assert isinstance(order[3], str)
    assert "official authority" in order[3]
    assert "Union or Member State law" in order[3]
    assert "comprehensive register" in order[3]
    assert isinstance(order[4], str)
    assert "data minimisation, retention, deletion, data-subject rights" in order[4]
    triggers = _strings(template["mandatory_reassessment_triggers"])
    assert {
        "authenticated_tenant_area_project_scope_purpose_activity_or_jurisdiction_change",
        "data_subject_personal_data_special_category_or_article_10_disposition_change",
        "article_9_condition_candidate_safeguard_minimisation_retention_deletion_or_rights_change",
        "recipient_processor_location_transfer_or_external_fact_change",
    } <= triggers


def test_documentation_boundary_and_xor_semantics_are_explicit() -> None:
    contract = _contract()
    boundary = contract["documentation_preparation_boundary"]
    assert boundary == {
        "machine_validation_scope": "document_shape_and_preregistered_invariant_constants_only",
        "instance_schema_provided": False,
        "operational_task_status": "unfulfilled_and_blocked",
        "non_claim": "This contract does not validate an intake instance, enforce an Article 9 prohibition, authorize Article 10 processing, or satisfy the operational acceptance criteria of S1-14.4.",
    }
    template = contract["special_category_evidence_intake_template"]
    assert isinstance(template, dict)
    xor = template["evidence_or_qualified_not_applicable_semantics"]
    assert isinstance(xor, dict)
    assert "exactly one" in xor["selection_rule"]
    assert "placeholders" in xor["placeholder_rule"]
    assert "Both branches populated" in xor["both_or_neither_rule"]


def test_missing_or_unknown_evidence_blocks_without_legal_authority_runtime_or_release_outcome() -> (
    None
):
    contract = _contract()
    semantics = contract["fail_closed_semantics"]
    assert isinstance(semantics, dict)
    assert all(
        semantics[key]
        == "special_category_evidence_intake_incomplete_and_deployment_specific_release_blocked"
        for key in (
            "unknown_or_missing_required_field",
            "stale_scope_mismatched_or_contradictory_evidence",
            "missing_qualified_reviewer_review_date_rationale_evidence_or_reassessment_trigger",
            "unknown_unqualified_stale_or_conflicting_special_category_article_9_article_10_or_external_fact",
            "missing_article_10_explicit_disposition_or_safeguard_minimisation_retention_rights_or_transfer_evidence",
            "conditional_requirement_missing_both_branches_or_has_placeholder_reference",
        )
    )
    assert (
        semantics[
            "missing_or_nonimmutable_authenticated_scope_purpose_activity_or_artifact_reference"
        ]
        == "reject_intake_and_block_deployment_specific_release_decision"
    )
    assert (
        semantics["proposed_personal_data_or_secret_payload"]
        == "reject_intake_and_record_data_minimization_blocker"
    )
    assert semantics["no_automatic_article_9_condition_or_article_10_determination"] is True
    assert semantics["no_runtime_authorization_processing_activation_or_enablement"] is True
    assert semantics["no_automatic_release_or_authority_outcome"] is True
    assert semantics["no_allow_outcome"] is True
    assert (
        semantics[
            "conditional_requirement_has_both_candidate_evidence_and_not_applicable_disposition"
        ]
        == "reject_intake_and_block_deployment_specific_release_decision"
    )
    boundary = contract["authority_boundary"]
    assert isinstance(boundary, dict)
    assert {
        "a legal opinion, Article 9 condition determination, Article 10 determination, or compliance certification",
        "a processing, deployment, productive-use, or release approval",
        "a runtime capability enablement or external-effect authorization",
        "an implementation, maturity, recognition, safety, product capability, or production-autonomy claim",
    } <= _strings(boundary["template_is_not"])
    template = contract["special_category_evidence_intake_template"]
    assert isinstance(template, dict)
    scope_binding = _strings(template["scope_binding_requirements"])
    assert any(
        all(
            token in item
            for token in (
                "raw personal data",
                "special-category values",
                "criminal-offence data",
                "personal identifiers",
                "credentials",
                "prompts",
                "memory payloads",
                "consent text",
                "contracts",
                "legal advice",
            )
        )
        for item in scope_binding
    )
