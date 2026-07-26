"""Evidence for the non-authorizing, deployment-specific GDPR role template."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
CONTRACT_PATH = ROOT / "docs" / "architecture" / "contracts" / "gdpr-role-assessment-v1.json"


def _contract() -> dict[str, object]:
    loaded: object = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _strings(value: object) -> set[str]:
    assert isinstance(value, list)
    assert all(isinstance(item, str) for item in value)
    return set(value)


def test_role_assessment_is_versioned_deployment_input_not_a_role_conclusion() -> None:
    contract = _contract()
    assert contract["contract_id"] == "neural-brain.gdpr-role-assessment"
    assert contract["contract_version"] == "1.0.0"
    assert contract["governing_decisions"] == ["ADR-001", "ADR-018"]
    purpose = contract["purpose"]
    assert isinstance(purpose, str)
    assert "does not determine a role" in purpose
    scope = contract["scope"]
    assert isinstance(scope, dict)
    assert scope["current_repository_state"] == (
        "No customer, production deployment, or deployment-specific processing relationship "
        "is established by this repository."
    )
    assert scope["product_boundary"] == (
        "The Memory Core is a protected internal subsystem, not the product boundary."
    )


def test_each_processing_relationship_requires_all_role_evidence_inputs() -> None:
    template = _contract()["deployment_role_assessment_template"]
    assert isinstance(template, dict)
    assert {
        "deployment_identifier",
        "artifact_version_or_digest",
        "processing_relationship_identifier",
        "assessed_organization_or_person_identifier",
        "other_parties_and_relationships",
        "processing_purposes",
        "personal_data_categories",
        "data_flow_and_locations",
        "proposed_role",
        "role_rationale_and_evidence_references",
        "applicable_law_and_qualified_review_reference",
        "contractual_and_subprocessor_evidence_references",
        "retention_and_deletion_evidence_references",
        "international_transfer_evidence_references",
        "identified_gaps_and_release_stops",
        "assessment_owner",
        "assessment_timestamp",
    } <= _strings(template["required_fields"])
    assert _strings(template["permitted_proposed_roles"]) == {
        "controller",
        "joint_controller",
        "processor",
        "subprocessor",
        "recipient",
    }
    relationships = _strings(template["role_relationship_requirements"])
    assert any("cannot decide a role" in requirement for requirement in relationships)
    assert any("unknown status as a release stop" in requirement for requirement in relationships)
    assert (
        template["unknown_or_missing_input"]
        == "gdpr_role_assessment_incomplete_and_deployment_specific_release_decision_blocked"
    )


def test_unknown_or_unqualified_role_evidence_fails_closed_without_authorization() -> None:
    contract = _contract()
    semantics = contract["validation_semantics"]
    assert isinstance(semantics, dict)
    assert semantics["assessment_contract_version_must_match"] is True
    assert semantics["one_assessment_per_processing_relationship"] is True
    assert semantics["unknown_or_missing_required_field"] == (
        "reject_assessment_and_block_deployment_specific_release_decision"
    )
    assert semantics["unknown_or_missing_role_relationship"] == "release_stop"
    assert semantics["stale_or_scope_mismatched_evidence"] == "release_stop"
    assert semantics["contradictory_party_or_role_evidence"] == "release_stop"
    assert semantics["no_automatic_legal_or_compliance_conclusion"] is True
    assert semantics["no_runtime_authorization_or_processing_activation"] is True
    boundary = contract["authority_boundary"]
    assert isinstance(boundary, dict)
    assert boundary["template_is"] == (
        "a versioned deployment-specific assessment input and traceability anchor"
    )
    assert {
        "a legal opinion",
        "a GDPR role determination",
        "a finding of lawfulness",
        "a deployment approval",
        "a release authorization",
        "an authority grant",
        "a runtime capability enablement",
    } <= _strings(boundary["template_is_not"])


def test_current_absence_of_deployment_facts_is_a_named_blocker() -> None:
    blocker = _contract()["current_blocker"]
    assert isinstance(blocker, dict)
    assert blocker == {
        "status": "blocked_pending_concrete_deployment_facts_and_qualified_review",
        "owner": "future deployment accountable owner",
        "unblock_condition": (
            "A concrete proposed deployment supplies every required field, relationship-specific "
            "evidence, and a qualified applicable-law review reference for separate governance "
            "and release evaluation."
        ),
        "next_step": (
            "Create one immutable assessment record per proposed processing relationship before "
            "any deployment-specific release decision."
        ),
    }
