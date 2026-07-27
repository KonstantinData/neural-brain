"""Evidence for the fail-closed Article 6 legal-basis evidence intake."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
CONTRACT_PATH = (
    ROOT / "docs" / "architecture" / "contracts" / "article-6-legal-basis-evidence-intake-v1.json"
)


def _contract() -> dict[str, object]:
    loaded: object = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _strings(value: object) -> set[str]:
    assert isinstance(value, list)
    assert all(isinstance(item, str) for item in value)
    return set(value)


def test_template_requires_authenticated_scope_purpose_activity_and_review_evidence() -> None:
    contract = _contract()
    assert contract["contract_id"] == "neural-brain.article-6-legal-basis-evidence-intake"
    assert contract["contract_version"] == "1.0.0"
    assert contract["governing_decisions"] == ["ADR-001", "ADR-005", "ADR-018", "ADR-019"]
    external = contract["authoritative_external_reference"]
    assert isinstance(external, dict)
    assert external["official_url"] == "https://eur-lex.europa.eu/eli/reg/2016/679/oj"
    template = contract["legal_basis_evidence_intake_template"]
    assert isinstance(template, dict)
    required = _strings(template["required_fields"])
    assert {
        "qualified_reviewer_qualification_review_date_and_independence_reference",
        "immutable_authenticated_tenant_area_project_scope_references",
        "immutable_intended_purpose_contract_id_version_and_purpose_reference",
        "immutable_processing_activity_identifier_version_and_activity_reference",
        "article_6_legal_basis_candidate_evidence_references_for_qualified_review_only",
        "necessity_rationale_and_less_intrusive_alternative_evidence_references",
        "proportionality_rationale_scope_duration_data_minimisation_and_safeguard_evidence_references",
        "explicit_non_applicability_unknown_conflict_and_gap_handling",
        "mandatory_reassessment_triggers_and_independent_release_decision_reference",
    } <= required
    scope_binding = _strings(template["scope_binding_requirements"])
    assert any(
        "cannot establish, broaden, or substitute trusted scope" in item for item in scope_binding
    )
    assert any("must not contain raw personal data" in item for item in scope_binding)
    assert any("Unknown, stale, contradictory" in item for item in scope_binding)


def test_review_order_keeps_external_unknown_and_non_applicability_facts_fail_closed() -> None:
    template = _contract()["legal_basis_evidence_intake_template"]
    assert isinstance(template, dict)
    order = template["deterministic_review_order"]
    assert isinstance(order, list)
    assert len(order) == 6
    assert isinstance(order[2], str)
    assert "without selecting, validating, or concluding a legal basis" in order[2]
    assert isinstance(order[3], str)
    assert "necessity, proportionality" in order[3]
    assert isinstance(order[4], str)
    assert "non-applicability" in order[4]
    triggers = _strings(template["mandatory_reassessment_triggers"])
    assert {
        "authenticated_tenant_area_project_scope_purpose_or_activity_change",
        "legal_basis_candidate_necessity_proportionality_compatibility_or_safeguard_change",
        "external_fact_source_currency_authority_or_qualified_review_change",
    } <= triggers


def test_missing_or_unknown_evidence_blocks_without_legal_authority_or_release_outcome() -> None:
    contract = _contract()
    semantics = contract["fail_closed_semantics"]
    assert isinstance(semantics, dict)
    assert all(
        semantics[key]
        == "legal_basis_evidence_intake_incomplete_and_deployment_specific_release_blocked"
        for key in (
            "unknown_or_missing_required_field",
            "stale_scope_mismatched_or_contradictory_evidence",
            "missing_qualified_reviewer_review_date_rationale_evidence_or_reassessment_trigger",
            "unknown_unqualified_stale_or_conflicting_external_fact_or_non_applicability_assertion",
            "unresolved_legal_basis_necessity_proportionality_compatibility_or_alternative_evidence",
        )
    )
    assert (
        semantics["missing_or_nonimmutable_authenticated_scope_purpose_or_activity_reference"]
        == "reject_intake_and_block_deployment_specific_release_decision"
    )
    assert semantics["no_automatic_article_6_legal_basis_or_lawfulness_determination"] is True
    assert semantics["no_runtime_authorization_processing_activation_or_enablement"] is True
    assert semantics["no_automatic_release_or_authority_outcome"] is True
    assert semantics["no_allow_outcome"] is True
    boundary = contract["authority_boundary"]
    assert isinstance(boundary, dict)
    assert {
        "a legal opinion, Article 6 legal-basis determination, or compliance certification",
        "a determination of lawfulness, necessity, proportionality, compatibility, consent validity, legitimate-interest balancing, or a GDPR exemption",
        "a processing, deployment, productive-use, or release approval",
        "a runtime capability enablement or external-effect authorization",
    } <= _strings(boundary["template_is_not"])
