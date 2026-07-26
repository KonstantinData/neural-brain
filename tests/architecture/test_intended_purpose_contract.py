import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
CONTRACT_PATH = ROOT / "docs" / "architecture" / "contracts" / "intended-purpose.json"


def _contract() -> dict[str, object]:
    loaded: object = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _strings(value: object) -> set[str]:
    assert isinstance(value, list)
    assert all(isinstance(item, str) for item in value)
    return set(value)


def test_intended_purpose_is_versioned_product_neutral_and_honest_about_maturity() -> None:
    contract = _contract()
    assert contract["contract_id"] == "neural-brain.intended-purpose"
    assert contract["contract_version"] == "1.0.0"
    assert contract["governing_decisions"] == ["ADR-001", "ADR-018"]
    purpose = contract["stable_intended_purpose"]
    assert isinstance(purpose, dict)
    assert "product- and domain-neutral" in purpose["statement"]
    assert purpose["current_maturity"] == "memory_core_foundation"
    assert "does not establish" in purpose["current_implementation_boundary"]
    assert (
        purpose["product_boundary"]
        == "The Memory Core is a protected internal subsystem, not the product boundary."
    )
    assert {
        "consciousness",
        "production autonomy",
        "legal, regulatory, certification, or compliance determination",
    } <= _strings(purpose["non_claims"])


def test_every_deployment_assessment_requires_stable_purpose_and_protected_control_comparisons() -> (
    None
):
    template = _contract()["deployment_assessment_template"]
    assert isinstance(template, dict)
    assert {
        "deployment_identifier",
        "artifact_version_or_digest",
        "intended_purpose_contract_id",
        "intended_purpose_contract_version",
        "proposed_use_description",
        "enabled_operations",
        "evidence_references",
        "identified_gaps_and_release_stops",
    } <= _strings(template["required_fields"])
    comparisons = _strings(template["required_comparisons"])
    assert any("product- and domain-neutral" in comparison for comparison in comparisons)
    assert any("Protected Control Plane" in comparison for comparison in comparisons)
    assert any("Memory Core" in comparison for comparison in comparisons)
    assert (
        template["unknown_or_missing_input"]
        == "assessment_incomplete_and_deployment_specific_release_decision_blocked"
    )


def test_assessment_template_never_becomes_legal_or_release_authority() -> None:
    contract = _contract()
    boundary = contract["authority_boundary"]
    assert isinstance(boundary, dict)
    assert boundary["template_is"] == "a versioned assessment input and traceability anchor"
    assert {
        "a legal opinion",
        "a regulatory classification",
        "a compliance certification",
        "a deployment approval",
        "a release authorization",
        "an authority grant",
        "a policy decision",
        "an implementation or maturity claim",
    } <= _strings(boundary["template_is_not"])
    semantics = contract["validation_semantics"]
    assert isinstance(semantics, dict)
    assert semantics["assessment_contract_version_must_match"] is True
    assert semantics["unknown_or_missing_required_field"] == "reject_assessment"
    assert semantics["unaccepted_domain_specific_extension"] == "reject_assessment"
    assert (
        semantics["unproven_capability_or_evidence_gate"] == "deployment_specific_release_blocked"
    )
    assert semantics["no_automatic_legal_or_compliance_conclusion"] is True
