"""Evidence for the fail-closed GDPR applicability screening template."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
CONTRACT_PATH = (
    ROOT / "docs" / "architecture" / "contracts" / "gdpr-applicability-screening-v1.json"
)


def _contract() -> dict[str, object]:
    loaded: object = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _strings(value: object) -> set[str]:
    assert isinstance(value, list)
    assert all(isinstance(item, str) for item in value)
    return set(value)


def test_template_requires_versioned_deployment_specific_gdpr_screening_evidence() -> None:
    contract = _contract()
    assert contract["contract_id"] == "neural-brain.gdpr-applicability-screening"
    assert contract["contract_version"] == "1.0.0"
    assert contract["governing_decisions"] == ["ADR-001", "ADR-005", "ADR-018"]
    external = contract["authoritative_external_reference"]
    assert isinstance(external, dict)
    assert external["official_url"] == "https://eur-lex.europa.eu/eli/reg/2016/679/oj"
    template = contract["screening_template"]
    assert isinstance(template, dict)
    required = _strings(template["required_fields"])
    assert {
        "qualified_reviewer_and_review_date",
        "screening_rationale_and_verified_evidence_references",
        "reassessment_triggers_and_next_review_date",
        "applicable_articles_for_qualified_review_only",
        "risk_triggers_required_assessments_and_release_blockers",
        "article_9_special_category_and_article_10_criminal_data_screening_evidence",
        "article_22_automated_individual_decision_and_profiling_screening_evidence",
        "article_35_dpia_risk_trigger_and_required_assessment_evidence",
    } <= required


def test_screening_order_and_reassessment_are_deterministic() -> None:
    template = _contract()["screening_template"]
    assert isinstance(template, dict)
    order = template["deterministic_screening_order"]
    assert isinstance(order, list)
    assert len(order) == 6
    assert isinstance(order[1], str)
    assert "Article 2 and Article 3" in order[1]
    assert isinstance(order[2], str)
    assert "Articles 9 and 10" in order[2]
    assert isinstance(order[3], str)
    assert "Article 22" in order[3]
    assert isinstance(order[4], str)
    assert "Article 35 DPIA" in order[4]
    triggers = _strings(template["mandatory_reassessment_triggers"])
    assert {
        "immutable_artifact_or_model_supplier_change",
        "data_subject_category_data_class_source_recipient_or_location_change",
        "special_category_criminal_data_profiling_or_automated_decision_change",
        "legal_regulatory_or_qualified_review_change",
    } <= triggers


def test_missing_or_unresolved_evidence_blocks_without_a_legal_or_release_outcome() -> None:
    contract = _contract()
    semantics = contract["fail_closed_semantics"]
    assert isinstance(semantics, dict)
    assert all(
        semantics[key] == "screening_incomplete_and_deployment_specific_release_blocked"
        for key in (
            "unknown_or_missing_required_field",
            "stale_scope_mismatched_or_contradictory_evidence",
            "missing_qualified_reviewer_date_rationale_verified_evidence_or_reassessment_trigger",
            "unresolved_applicability_special_category_automated_decision_or_dpia_risk_trigger",
            "missing_required_assessment_or_release_blocker_disposition",
        )
    )
    assert semantics["no_automatic_gdpr_applicability_or_dpia_determination"] is True
    assert semantics["no_runtime_authorization_processing_activation_or_enablement"] is True
    assert semantics["no_automatic_release_or_authority_outcome"] is True
    assert semantics["no_allow_outcome"] is True
    boundary = contract["authority_boundary"]
    assert isinstance(boundary, dict)
    assert {
        "a legal opinion, GDPR applicability determination, or compliance certification",
        "a determination of lawfulness, Article 6 legal basis, Article 9 condition, Article 10 condition, Article 22 outcome, or DPIA necessity",
        "a deployment, processing, productive-use, or release approval",
        "an authority grant, policy decision, human approval, or Security Floor override",
        "a protected-state transition request, gate decision, or runtime capability enablement",
    } <= _strings(boundary["template_is_not"])
