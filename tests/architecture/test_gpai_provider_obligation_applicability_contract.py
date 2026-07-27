"""Evidence for the fail-closed GPAI provider-obligation applicability template."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
CONTRACT_PATH = ROOT / "docs" / "architecture" / "contracts" / "gpai-provider-obligation-applicability-v1.json"


def _contract() -> dict[str, object]:
    loaded: object = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _strings(value: object) -> set[str]:
    assert isinstance(value, list)
    assert all(isinstance(item, str) for item in value)
    return set(value)


def test_assessment_requires_immutable_distribution_and_change_evidence() -> None:
    contract = _contract()
    assert contract["contract_id"] == "neural-brain.gpai-provider-obligation-applicability-assessment"
    assert contract["contract_version"] == "1.0.0"
    assert contract["governing_decisions"] == [
        "ADR-018",
        "architecture-directive-v4.0",
        "neural-brain-recognition-standard",
    ]
    external = contract["authoritative_external_reference"]
    assert isinstance(external, dict)
    assert external["instrument"] == "Regulation (EU) 2024/1689"
    assert external["official_url"] == "https://eur-lex.europa.eu/eli/reg/2024/1689/oj"
    template = contract["assessment_template"]
    assert isinstance(template, dict)
    required = _strings(template["required_fields"])
    assert {
        "immutable_model_or_artifact_digest_and_model_inventory_reference",
        "concrete_distribution_availability_market_placement_or_putting_into_service_evidence",
        "modification_fine_tuning_adapter_or_training_change_evidence",
        "brand_trademark_and_entity_under_which_availability_is_claimed_evidence",
        "article_3_63_and_article_53_qualified_review_evidence",
        "linked_reassessment_trigger_and_tracked_work_item_reference",
        "independent_compliance_release_decision_reference",
    } <= required
    assert _strings(template["review_states_for_evidence_routing_only"]) == {
        "not_assessed",
        "qualified_review_required",
        "evidence_incomplete_or_stale",
        "reassessment_open",
    }


def test_repository_facts_do_not_invent_provider_or_obligation_status() -> None:
    facts = _contract()["repository_facts_at_template_creation"]
    assert isinstance(facts, dict)
    unknown = _strings(facts["unknown_facts_not_inferred"])
    assert {
        "whether any entity is a GPAI provider for a concrete model or deployment",
        "whether a concrete distribution, modification, branding, fine-tuning, or downstream release creates a legal obligation",
        "whether any Article 53 obligation applies, is met, or is exempted",
        "whether any deployment, release, model activation, authority, or external effect is authorized",
    } <= unknown
    verified = _strings(facts["verified_facts"])
    assert any("no approved productive model deployment" in item for item in verified)
    assert any("No repository artifact currently establishes" in item for item in verified)


def test_unknown_or_changed_evidence_fails_closed_without_authority_or_runtime_effect() -> None:
    contract = _contract()
    semantics = contract["fail_closed_semantics"]
    assert isinstance(semantics, dict)
    for key in (
        "unknown_or_missing_required_field",
        "unverified_distribution_modification_branding_or_fine_tuning_fact",
        "stale_scope_mismatched_or_contradictory_evidence",
        "missing_qualified_review_or_linked_reassessment_work",
    ):
        assert semantics[key] == "assessment_incomplete_and_affected_deployment_specific_release_blocked"
    assert semantics["no_automatic_provider_status_or_obligation_conclusion"] is True
    assert semantics["no_automatic_legal_applicability_or_compliance_conclusion"] is True
    assert semantics["no_automatic_deployment_release_or_authority_outcome"] is True
    assert semantics["no_runtime_activation_or_protected_state_mutation"] is True
    assert semantics["public_repository_or_branding_metadata_is_insufficient"] is True
    assert semantics["no_allow_outcome"] is True


def test_authority_boundary_prohibits_legal_provider_and_enablement_claims() -> None:
    boundary = _contract()["authority_boundary"]
    assert isinstance(boundary, dict)
    forbidden = _strings(boundary["template_is_not"])
    assert {
        "a GPAI-provider status assignment",
        "an Article 53 applicability or obligation conclusion",
        "a compliance certification",
        "a deployment or release approval",
        "an authority grant",
        "a model activation or promotion",
        "a runtime capability enablement",
    } <= forbidden
    docs = (ROOT / "docs" / "governance" / "gpai-provider-obligation-applicability-v1.md").read_text(encoding="utf-8")
    assert "not legal advice" in docs
    assert "does not assert their applicability or interpretation" in docs
    assert "has no allow state" in docs
