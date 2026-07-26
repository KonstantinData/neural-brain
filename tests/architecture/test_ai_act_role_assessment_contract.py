"""Evidence for the fail-closed AI Act role-assessment template."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
CONTRACT_PATH = ROOT / "docs" / "architecture" / "contracts" / "ai-act-role-assessment-v1.json"


def _contract() -> dict[str, object]:
    loaded: object = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _strings(value: object) -> set[str]:
    assert isinstance(value, list)
    assert all(isinstance(item, str) for item in value)
    return set(value)


def test_role_assessment_requires_deployment_specific_evidence() -> None:
    contract = _contract()
    assert contract["contract_id"] == "neural-brain.ai-act-role-assessment"
    assert contract["contract_version"] == "1.0.0"
    assert contract["governing_decisions"] == ["ADR-001", "ADR-005", "ADR-018"]
    external = contract["authoritative_external_reference"]
    assert isinstance(external, dict)
    assert external["instrument"] == "Regulation (EU) 2024/1689"
    assert external["official_url"] == "https://eur-lex.europa.eu/eli/reg/2024/1689/oj"
    template = contract["assessment_template"]
    assert isinstance(template, dict)
    assert {
        "immutable_artifact_version_or_digest",
        "operating_legal_entity_and_contact",
        "brand_or_trademark_used_for_availability",
        "availability_or_putting_into_service_evidence",
        "authority_over_operation_and_use_evidence",
        "eu_output_or_market_nexus_evidence",
        "applicable_law_review_evidence",
        "role_analysis_evidence",
        "independent_release_decision_reference",
    } <= _strings(template["required_fields"])
    assert _strings(template["candidate_role_labels_for_review_only"]) == {
        "provider",
        "deployer",
        "other_or_combined_role",
        "not_assessed",
    }


def test_repository_facts_do_not_invent_a_deployment_or_role() -> None:
    facts = _contract()["repository_facts_at_template_creation"]
    assert isinstance(facts, dict)
    unknown = _strings(facts["unknown_facts_not_inferred"])
    assert {
        "whether a specific deployment exists",
        "artifact distribution, market placement, or putting into service",
        "operating or accountable legal entity",
        "name or trademark under which a system is made available",
        "applicable AI Act scope, risk classification, exemption, or operator role",
    } <= unknown
    verified = _strings(facts["verified_facts"])
    assert any(
        "no stable service API or production deployment is claimed" in item for item in verified
    )
    assert any("not evidence of a deployed artifact" in item for item in verified)


def test_unknown_or_unverified_facts_fail_closed_without_legal_or_release_outcome() -> None:
    contract = _contract()
    semantics = contract["fail_closed_semantics"]
    assert isinstance(semantics, dict)
    assert {
        "unknown_or_missing_required_field",
        "stale_or_scope_mismatched_evidence",
        "unverified_deployment_or_operator_fact",
    } <= set(semantics)
    assert all(
        semantics[key] == "assessment_incomplete_and_deployment_specific_release_blocked"
        for key in (
            "unknown_or_missing_required_field",
            "stale_or_scope_mismatched_evidence",
            "unverified_deployment_or_operator_fact",
        )
    )
    assert semantics["no_automatic_role_assignment"] is True
    assert semantics["no_automatic_ai_act_applicability_conclusion"] is True
    assert semantics["no_automatic_lawfulness_or_compliance_conclusion"] is True
    assert semantics["no_automatic_release_or_authority_outcome"] is True
    assert semantics["public_repository_or_branding_metadata_is_insufficient"] is True
    boundary = contract["authority_boundary"]
    assert isinstance(boundary, dict)
    assert {
        "a provider or deployer assignment",
        "an AI Act applicability conclusion",
        "a deployment or release approval",
        "an authority grant",
        "a runtime capability enablement",
    } <= _strings(boundary["template_is_not"])
