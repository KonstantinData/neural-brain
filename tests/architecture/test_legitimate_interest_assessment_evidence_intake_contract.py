"""Evidence for the fail-closed legitimate-interest assessment evidence intake."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
CONTRACT_PATH = (
    ROOT
    / "docs"
    / "architecture"
    / "contracts"
    / "legitimate-interest-assessment-evidence-intake-v1.json"
)


def _contract() -> dict[str, object]:
    loaded: object = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _strings(value: object) -> set[str]:
    assert isinstance(value, list)
    assert all(isinstance(item, str) for item in value)
    return set(value)


def test_template_requires_scope_review_and_legitimate_interest_evidence() -> None:
    contract = _contract()
    assert contract["contract_id"] == "neural-brain.legitimate-interest-assessment-evidence-intake"
    assert contract["contract_version"] == "1.0.0"
    assert contract["status"] == "normative_foundation_documentation_preparation_template"
    assert contract["governing_decisions"] == ["ADR-001", "ADR-005", "ADR-018", "ADR-019"]
    external = contract["authoritative_external_reference"]
    assert isinstance(external, dict)
    assert external["official_url"] == "https://eur-lex.europa.eu/eli/reg/2016/679/oj"
    template = contract["legitimate_interest_assessment_evidence_intake_template"]
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
        "possible_legitimate_interest_artifact_and_purpose_evidence_references_for_qualified_review_only",
        "article_6_1_f_public_authority_performance_of_tasks_exclusion_evidence_or_qualified_not_applicable_disposition",
        "necessity_rationale_processing_activity_and_less_intrusive_alternative_evidence_references",
        "balancing_data_subject_impact_reasonable_expectation_child_and_vulnerable_person_weighting_and_rights_freedoms_evidence_references",
        "safeguard_data_minimisation_retention_security_transparency_and_accountability_evidence_references",
        "article_21_objection_and_downstream_review_evidence_references",
        "article_21_2_3_direct_marketing_objection_and_processing_stop_evidence_or_qualified_not_applicable_disposition",
        "external_facts_source_provenance_date_currency_and_scope_evidence_references",
        "explicit_non_applicability_unknown_gap_conflict_and_expiry_dispositions",
        "review_rationale_verified_evidence_references_release_blockers_and_next_review_date",
        "mandatory_reassessment_triggers_and_independent_release_decision_reference",
    }
    scope_binding = _strings(template["scope_binding_requirements"])
    assert any(
        "cannot establish, broaden, or substitute trusted scope" in item for item in scope_binding
    )
    assert any("must not contain raw personal data" in item for item in scope_binding)
    assert any("Unknown, stale, contradictory" in item for item in scope_binding)


def test_review_order_requires_explicit_dispositions_and_reassessment() -> None:
    template = _contract()["legitimate_interest_assessment_evidence_intake_template"]
    assert isinstance(template, dict)
    order = template["deterministic_review_order"]
    assert isinstance(order, list)
    assert len(order) == 6
    assert isinstance(order[2], str)
    assert "public-authority performance-of-tasks exclusion" in order[2]
    assert isinstance(order[3], str)
    assert "necessity" in order[3]
    assert "balancing" in order[3]
    assert "children and other vulnerable persons" in order[3]
    assert "direct marketing" in order[3]
    assert "processing for those purposes stops" in order[3]
    assert isinstance(order[4], str)
    assert "non-applicability, unknown, gap, conflict, expiry" in order[4]
    triggers = _strings(template["mandatory_reassessment_triggers"])
    assert {
        "authenticated_tenant_area_project_scope_purpose_activity_or_jurisdiction_change",
        "possible_legitimate_interest_necessity_alternative_balancing_impact_or_safeguard_change",
        "data_subject_category_data_class_source_recipient_transfer_retention_or_objection_change",
        "public_authority_task_child_vulnerability_direct_marketing_or_processing_stop_change",
    } <= triggers


def test_documentation_boundary_and_xor_semantics_are_explicit() -> None:
    contract = _contract()
    boundary = contract["documentation_preparation_boundary"]
    assert isinstance(boundary, dict)
    assert boundary["instance_schema_provided"] is False
    assert boundary["operational_task_status"] == "unfulfilled_and_blocked"
    template = contract["legitimate_interest_assessment_evidence_intake_template"]
    assert isinstance(template, dict)
    xor = template["evidence_or_qualified_not_applicable_semantics"]
    assert isinstance(xor, dict)
    assert "exactly one" in xor["selection_rule"]
    assert "placeholders" in xor["placeholder_rule"]


def test_missing_or_unknown_evidence_blocks_without_legal_authority_runtime_or_release_claim() -> (
    None
):
    contract = _contract()
    semantics = contract["fail_closed_semantics"]
    assert isinstance(semantics, dict)
    blocked = "legitimate_interest_assessment_evidence_intake_incomplete_and_deployment_specific_release_blocked"
    assert all(
        semantics[key] == blocked
        for key in (
            "unknown_or_missing_required_field",
            "stale_scope_mismatched_or_contradictory_evidence",
            "missing_qualified_reviewer_independence_review_date_rationale_evidence_or_reassessment_trigger",
            "unknown_unqualified_stale_or_conflicting_external_fact_or_disposition",
            "unresolved_possible_legitimate_interest_necessity_alternative_balancing_impact_safeguard_or_objection_evidence",
            "conditional_requirement_missing_both_branches_or_has_placeholder_reference",
        )
    )
    assert (
        semantics["missing_or_nonimmutable_authenticated_scope_purpose_or_activity_reference"]
        == "reject_intake_and_block_deployment_specific_release_decision"
    )
    assert (
        semantics[
            "cross_boundary_or_changed_artifact_purpose_activity_or_jurisdiction_evidence_reuse"
        ]
        == "reject_intake_and_block_deployment_specific_release_decision"
    )
    assert (
        semantics["proposed_personal_data_or_secret_payload"]
        == "reject_intake_and_record_data_minimization_blocker"
    )
    assert semantics["no_automatic_legal_or_regulatory_conclusion"] is True
    assert semantics["no_automatic_legitimate_interest_or_lawfulness_determination"] is True
    assert semantics["no_runtime_authorization_processing_activation_or_enablement"] is True
    assert semantics["no_automatic_release_or_authority_outcome"] is True
    assert semantics["no_capability_maturity_or_recognition_claim"] is True
    assert semantics["no_allow_outcome"] is True
    assert (
        semantics[
            "conditional_requirement_has_both_candidate_evidence_and_not_applicable_disposition"
        ]
        == "reject_intake_and_block_deployment_specific_release_decision"
    )
    boundary = contract["authority_boundary"]
    assert isinstance(boundary, dict)
    prohibited = _strings(boundary["template_is_not"])
    assert any("legal opinion" in item for item in prohibited)
    assert any("legitimate interest" in item for item in prohibited)
    assert any("authority" in item for item in prohibited)
    assert any("release approval" in item for item in prohibited)
    assert any("runtime capability enablement" in item for item in prohibited)
    assert any("recognition" in item for item in prohibited)
