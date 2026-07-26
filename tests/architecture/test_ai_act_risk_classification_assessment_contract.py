"""Evidence for the fail-closed AI Act risk-classification assessment template."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
CONTRACT_PATH = (
    ROOT / "docs" / "architecture" / "contracts" / "ai-act-risk-classification-assessment-v1.json"
)


def _contract() -> dict[str, object]:
    loaded: object = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _strings(value: object) -> set[str]:
    assert isinstance(value, list)
    assert all(isinstance(item, str) for item in value)
    return set(value)


def test_template_requires_versioned_deployment_specific_classification_evidence() -> None:
    contract = _contract()
    assert contract["contract_id"] == "neural-brain.ai-act-risk-classification-assessment"
    assert contract["contract_version"] == "1.0.0"
    assert contract["governing_decisions"] == ["ADR-001", "ADR-005", "ADR-018"]
    external = contract["authoritative_external_reference"]
    assert isinstance(external, dict)
    assert external["official_url"] == "https://eur-lex.europa.eu/eli/reg/2024/1689/oj"
    template = contract["assessment_template"]
    assert isinstance(template, dict)
    required = _strings(template["required_fields"])
    assert {
        "qualified_reviewer_and_review_date",
        "classification_rationale_and_evidence_references",
        "reassessment_triggers_and_next_review_date",
        "article_5_prohibition_review_evidence",
        "article_6_and_annex_i_high_risk_review_evidence",
        "annex_iii_high_risk_review_evidence",
        "article_50_transparency_review_evidence",
        "other_or_minimal_risk_review_evidence",
    } <= required
    assert _strings(template["candidate_classification_labels_for_review_only"]) == {
        "prohibited_candidate",
        "high_risk_candidate",
        "transparency_obligation_candidate",
        "minimal_or_other_risk_candidate",
        "not_assessed",
    }


def test_review_order_is_deterministic_and_prohibition_precedes_other_labels() -> None:
    template = _contract()["assessment_template"]
    assert isinstance(template, dict)
    order = template["deterministic_review_order"]
    assert isinstance(order, list)
    assert len(order) == 5
    assert isinstance(order[1], str)
    assert "Article 5" in order[1]
    assert isinstance(order[2], str)
    assert "Article 6 and Annex I, then Annex III" in order[2]
    triggers = _strings(template["mandatory_reassessment_triggers"])
    assert {
        "immutable_artifact_or_model_supplier_change",
        "intended_purpose_or_enabled_operation_change",
        "deployment_context_jurisdiction_or_affected_people_change",
        "legal_or_regulatory_change",
        "incident_complaint_or_material_misuse_signal",
    } <= triggers


def test_unknown_or_unqualified_evidence_blocks_without_a_legal_or_release_outcome() -> None:
    contract = _contract()
    semantics = contract["fail_closed_semantics"]
    assert isinstance(semantics, dict)
    assert {
        "unknown_or_missing_required_field",
        "stale_scope_mismatched_or_contradictory_evidence",
        "missing_qualified_reviewer_date_rationale_or_reassessment_trigger",
        "unverified_prohibition_or_high_risk_fact",
    } <= set(semantics)
    assert all(
        semantics[key] == "assessment_incomplete_and_deployment_specific_release_blocked"
        for key in (
            "unknown_or_missing_required_field",
            "stale_scope_mismatched_or_contradictory_evidence",
            "missing_qualified_reviewer_date_rationale_or_reassessment_trigger",
            "unverified_prohibition_or_high_risk_fact",
        )
    )
    assert semantics["qualified_prohibition_conclusion"] == "non_overridable_release_stop"
    assert semantics["no_automatic_risk_classification"] is True
    assert semantics["no_automatic_release_or_authority_outcome"] is True
    assert semantics["no_allow_outcome"] is True
    boundary = contract["authority_boundary"]
    assert isinstance(boundary, dict)
    assert {
        "a legal opinion, applicability determination, or compliance certification",
        "a classification of a real deployment or system",
        "a deployment, productive-use, or release approval",
        "an authority grant, policy decision, human approval, or Security Floor override",
        "a protected-state transition request, gate decision, or runtime capability enablement",
    } <= _strings(boundary["template_is_not"])
