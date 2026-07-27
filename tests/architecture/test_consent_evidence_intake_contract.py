"""Evidence for the fail-closed consent evidence intake."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
CONTRACT_PATH = ROOT / "docs" / "architecture" / "contracts" / "consent-evidence-intake-v1.json"


def _contract() -> dict[str, object]:
    loaded: object = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _strings(value: object) -> set[str]:
    assert isinstance(value, list)
    assert all(isinstance(item, str) for item in value)
    return set(value)


def test_related_contract_ids_versions_and_scope_are_consistent() -> None:
    contract_paths = {
        "neural-brain.article-9-special-category-evidence-intake": ROOT
        / "docs"
        / "architecture"
        / "contracts"
        / "article-9-special-category-evidence-intake-v1.json",
        "neural-brain.legitimate-interest-assessment-evidence-intake": ROOT
        / "docs"
        / "architecture"
        / "contracts"
        / "legitimate-interest-assessment-evidence-intake-v1.json",
        "neural-brain.consent-evidence-intake": CONTRACT_PATH,
    }
    for expected_id, path in contract_paths.items():
        loaded: object = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(loaded, dict)
        assert loaded["contract_id"] == expected_id
        assert loaded["contract_version"] == "1.0.0"
        assert loaded["status"] == "normative_foundation_documentation_preparation_template"
        boundary = loaded["documentation_preparation_boundary"]
        assert isinstance(boundary, dict)
        assert boundary["instance_schema_provided"] is False
        assert boundary["operational_task_status"] == "unfulfilled_and_blocked"
        template_key = next(key for key in loaded if key.endswith("evidence_intake_template"))
        template = loaded[template_key]
        assert isinstance(template, dict)
        required = _strings(template["required_fields"])
        assert {
            "immutable_authenticated_tenant_area_project_scope_references",
            "immutable_intended_purpose_contract_id_version_and_purpose_reference",
            "immutable_processing_activity_identifier_version_and_activity_reference",
        } <= required


def test_template_requires_scope_possible_consent_and_qualified_review_evidence() -> None:
    contract = _contract()
    assert contract["contract_id"] == "neural-brain.consent-evidence-intake"
    assert contract["contract_version"] == "1.0.0"
    assert contract["status"] == "normative_foundation_documentation_preparation_template"
    assert contract["governing_decisions"] == ["ADR-001", "ADR-005", "ADR-018", "ADR-019"]
    external = contract["authoritative_external_reference"]
    assert isinstance(external, dict)
    assert external["official_url"] == "https://eur-lex.europa.eu/eli/reg/2016/679/oj"
    template = contract["consent_evidence_intake_template"]
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
        "consent_basis_applicability_predicate_or_qualified_not_applicable_disposition",
        "data_subject_category_and_processing_context_evidence_references",
        "possible_consent_artifact_and_purpose_activity_binding_evidence_references",
        "voluntary_informed_specific_unambiguous_and_granular_evidence_references",
        "article_7_1_controller_demonstrability_evidence_or_qualified_not_applicable_disposition",
        "article_7_2_request_presentation_distinguishable_intelligible_accessible_clear_plain_language_evidence_or_qualified_not_applicable_disposition",
        "article_7_3_withdrawal_notice_accessibility_prior_lawfulness_and_as_easy_as_giving_evidence_or_qualified_not_applicable_disposition",
        "article_7_4_service_conditionality_and_contract_performance_necessity_evidence_or_qualified_not_applicable_disposition",
        "article_8_child_information_society_age_parental_authorization_and_reasonable_verification_evidence_or_qualified_not_applicable_disposition",
        "article_9_2_a_explicit_consent_and_union_or_member_state_law_prohibition_evidence_or_qualified_not_applicable_disposition",
        "language_accessibility_and_information_delivery_evidence_references",
        "record_integrity_provenance_timestamp_version_and_tamper_evidence_references",
        "expiry_refresh_reassessment_and_evidence_currency_references",
        "withdrawal_accessibility_downstream_stop_deletion_and_reconciliation_evidence_references",
        "explicit_non_applicability_unknown_conflict_gap_and_expiry_dispositions",
        "review_rationale_verified_evidence_references_release_blockers_and_next_review_date",
        "mandatory_reassessment_triggers_and_independent_release_decision_reference",
    }
    scope_binding = _strings(template["scope_binding_requirements"])
    assert any(
        "cannot establish, broaden, or substitute trusted scope" in item for item in scope_binding
    )
    assert any("must not contain raw personal data" in item for item in scope_binding)
    assert any("Unknown, stale, contradictory" in item for item in scope_binding)


def test_review_order_and_reassessment_keep_consent_evidence_fail_closed() -> None:
    template = _contract()["consent_evidence_intake_template"]
    assert isinstance(template, dict)
    order = template["deterministic_review_order"]
    assert isinstance(order, list)
    assert len(order) == 7
    assert isinstance(order[2], str)
    assert "Article 7(1)" in order[2]
    assert "Article 7(3)" in order[2]
    assert isinstance(order[3], str)
    assert "Article 8" in order[3]
    assert "Article 9(2)(a)" in order[3]
    assert isinstance(order[4], str)
    assert "withdrawal" in order[4]
    assert "downstream stop" in order[4]
    assert isinstance(order[5], str)
    assert "non-applicability, unknown, conflict, gap, evidence-expiry" in order[5]
    triggers = _strings(template["mandatory_reassessment_triggers"])
    assert {
        "authenticated_tenant_area_project_scope_purpose_activity_context_or_jurisdiction_change",
        "possible_consent_artifact_granularity_information_or_record_integrity_change",
        "expiry_refresh_withdrawal_downstream_stop_deletion_or_reconciliation_change",
        "article_7_demonstrability_request_presentation_withdrawal_or_conditionality_change",
        "article_8_child_age_parental_authorization_or_verification_change",
        "article_9_2_a_explicit_consent_or_union_member_state_law_prohibition_change",
    } <= triggers


def test_documentation_boundary_and_xor_semantics_are_explicit() -> None:
    contract = _contract()
    boundary = contract["documentation_preparation_boundary"]
    assert isinstance(boundary, dict)
    assert boundary["instance_schema_provided"] is False
    assert boundary["operational_task_status"] == "unfulfilled_and_blocked"
    template = contract["consent_evidence_intake_template"]
    assert isinstance(template, dict)
    xor = template["evidence_or_qualified_not_applicable_semantics"]
    assert isinstance(xor, dict)
    assert "exactly one" in xor["selection_rule"]
    assert "placeholders" in xor["placeholder_rule"]
    assert _strings(xor["candidate_evidence_requirements"]) == {
        "immutable_evidence_identifier_and_version_or_digest",
        "official_article_and_condition_addressed",
        "source_provenance_date_currency_and_exact_scope",
        "qualified_reviewer_treatment_and_contradiction_status",
        "reassessment_trigger_and_next_review_date",
    }
    assert _strings(xor["qualified_not_applicable_requirements"]) == {
        "official_article_and_condition_addressed",
        "scope_matched_factual_rationale_and_immutable_evidence_references",
        "qualified_reviewer_identity_qualification_independence_and_review_date",
        "contradiction_unknown_and_evidence_expiry_status",
        "reassessment_trigger_and_next_review_date",
    }
    assert (
        xor["both_or_neither_rule"]
        == "Both branches populated, neither branch populated, or any placeholder reference makes the documentation preparation incomplete and keeps deployment-specific release blocked."
    )


def test_outer_consent_basis_coherence_and_preregistered_branch_matrix() -> None:
    template = _contract()["consent_evidence_intake_template"]
    assert isinstance(template, dict)
    coherence = template["consent_basis_applicability_and_coherence"]
    assert isinstance(coherence, dict)
    assert _strings(coherence["consent_basis_applies_mandatory_candidate_evidence"]) == {
        "possible_consent_artifact_and_purpose_activity_binding_evidence_references",
        "voluntary_informed_specific_unambiguous_and_granular_evidence_references",
        "article_7_1_controller_demonstrability_candidate_evidence",
        "article_7_3_withdrawal_notice_accessibility_prior_lawfulness_and_as_easy_as_giving_candidate_evidence",
        "record_integrity_provenance_timestamp_version_and_tamper_evidence_references",
        "withdrawal_accessibility_downstream_stop_deletion_and_reconciliation_evidence_references",
    }
    assert _strings(coherence["qualified_consent_basis_not_applicable_requirements"]) == {
        "official_article_and_consent_basis_addressed",
        "scope_matched_factual_rationale_and_immutable_evidence_references",
        "qualified_reviewer_identity_qualification_independence_and_review_date",
        "all_consent_specific_candidate_evidence_absent",
        "all_consent_specific_conditional_fields_absent_or_qualified_not_applicable",
        "contradiction_unknown_and_evidence_expiry_status",
        "reassessment_trigger_and_next_review_date",
    }
    assert coherence["conditional_predicates"] == {
        "article_7_2": "consent_request_is_presented_in_a_written_declaration_that_also_concerns_other_matters",
        "article_7_4": "service_or_contract_performance_is_conditioned_on_consent_to_processing_not_necessary_for_performance",
        "article_8": "information_society_service_is_offered_directly_to_a_child_and_consent_is_relied_on",
        "article_9_2_a": "explicit_consent_is_relied_on_for_special_category_processing",
    }
    assert (
        coherence["inconsistent_combination_rule"]
        == "Reject consent_basis_applies without Article 7(1) and Article 7(3) candidate evidence; reject qualified_consent_basis_not_applicable with any consent-specific candidate evidence; reject both or neither outer branches; reject any conditional predicate/evidence mismatch."
    )
    matrix = coherence["preregistered_branch_matrix"]
    assert matrix == [
        {
            "branch": "consent_basis_applies_coherent",
            "preconditions": [
                "consent_basis_applies_predicate_evidence_present",
                "article_7_1_candidate_evidence_present",
                "article_7_3_candidate_evidence_present",
                "every_conditional_predicate_resolved_with_matching_candidate_or_qualified_not_applicable_branch",
            ],
            "documentation_outcome": "documentation_preparation_complete_for_qualified_review_only",
            "runtime_or_release_outcome": "none",
        },
        {
            "branch": "consent_basis_applies_missing_mandatory_evidence",
            "preconditions": [
                "consent_basis_applies_predicate_evidence_present",
                "article_7_1_or_article_7_3_candidate_evidence_missing",
            ],
            "documentation_outcome": "documentation_preparation_incomplete",
            "runtime_or_release_outcome": "deployment_specific_release_blocked",
        },
        {
            "branch": "consent_basis_not_applicable_coherent",
            "preconditions": [
                "qualified_consent_basis_not_applicable_disposition_complete",
                "all_consent_specific_candidate_evidence_absent",
                "all_conditional_fields_absent_or_qualified_not_applicable",
            ],
            "documentation_outcome": "documentation_not_applicable_candidate_for_qualified_review_only",
            "runtime_or_release_outcome": "none",
        },
        {
            "branch": "consent_basis_not_applicable_inconsistent",
            "preconditions": [
                "qualified_consent_basis_not_applicable_disposition_present",
                "any_consent_specific_candidate_evidence_present",
            ],
            "documentation_outcome": "reject_incoherent_documentation",
            "runtime_or_release_outcome": "deployment_specific_release_blocked",
        },
        {
            "branch": "outer_or_conditional_branch_unresolved_or_inconsistent",
            "preconditions": [
                "both_or_neither_outer_branches_or_any_unknown_placeholder_or_predicate_evidence_mismatch"
            ],
            "documentation_outcome": "reject_or_keep_documentation_preparation_incomplete",
            "runtime_or_release_outcome": "deployment_specific_release_blocked",
        },
    ]


def test_missing_evidence_blocks_without_legal_authority_runtime_or_release_claim() -> None:
    contract = _contract()
    semantics = contract["fail_closed_semantics"]
    assert isinstance(semantics, dict)
    assert all(
        semantics[key]
        == "consent_evidence_intake_incomplete_and_deployment_specific_release_blocked"
        for key in (
            "unknown_or_missing_required_field",
            "stale_scope_mismatched_or_contradictory_evidence",
            "missing_qualified_reviewer_independence_review_date_rationale_evidence_or_reassessment_trigger",
            "unknown_unqualified_stale_or_conflicting_consent_condition_external_fact_or_non_applicability_assertion",
            "unresolved_voluntary_informed_specific_unambiguous_granular_language_accessibility_or_record_integrity_evidence",
            "unresolved_expiry_refresh_withdrawal_downstream_stop_deletion_or_reconciliation_evidence",
            "conditional_requirement_missing_both_branches_or_has_placeholder_reference",
        )
    )
    assert (
        semantics["missing_or_nonimmutable_authenticated_scope_purpose_or_activity_reference"]
        == "reject_intake_and_block_deployment_specific_release_decision"
    )
    assert (
        semantics[
            "cross_boundary_or_changed_artifact_purpose_activity_context_or_jurisdiction_evidence_reuse"
        ]
        == "reject_intake_and_block_deployment_specific_release_decision"
    )
    assert (
        semantics["proposed_personal_data_or_secret_payload"]
        == "reject_intake_and_record_data_minimization_blocker"
    )
    assert semantics["no_automatic_legal_or_regulatory_conclusion"] is True
    assert semantics["no_automatic_consent_validity_or_lawfulness_determination"] is True
    assert semantics["no_runtime_authorization_processing_activation_or_enablement"] is True
    assert semantics["no_automatic_release_or_authority_outcome"] is True
    assert semantics["no_allow_outcome"] is True
    assert (
        semantics[
            "conditional_requirement_has_both_candidate_evidence_and_not_applicable_disposition"
        ]
        == "reject_intake_and_block_deployment_specific_release_decision"
    )
    assert (
        semantics["consent_basis_applies_without_article_7_1_or_article_7_3_candidate_evidence"]
        == "consent_evidence_intake_incomplete_and_deployment_specific_release_blocked"
    )
    assert all(
        semantics[key] == "reject_intake_and_block_deployment_specific_release_decision"
        for key in (
            "consent_basis_not_applicable_with_any_consent_specific_candidate_evidence",
            "outer_consent_basis_both_or_neither_branch",
            "conditional_predicate_and_evidence_branch_mismatch",
        )
    )
    boundary = contract["authority_boundary"]
    assert isinstance(boundary, dict)
    assert {
        "a legal opinion, consent-validity determination, or compliance certification",
        "a processing, deployment, productive-use, or release approval",
        "a runtime capability enablement or external-effect authorization",
        "an implementation, maturity, recognition, safety, or production-autonomy claim",
    } <= _strings(boundary["template_is_not"])
