"""Evidence for the fail-closed RoPA intake contract."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
CONTRACT_PATH = ROOT / "docs" / "architecture" / "contracts" / "ropa-evidence-intake-v1.json"


def _contract() -> dict[str, object]:
    loaded: object = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _strings(value: object) -> set[str]:
    assert isinstance(value, list)
    assert all(isinstance(item, str) for item in value)
    return set(value)


def test_template_is_versioned_scope_bound_and_category_only() -> None:
    contract = _contract()
    assert contract["contract_id"] == "neural-brain.ropa-evidence-intake"
    assert contract["contract_version"] == "1.0.0"
    assert contract["governing_decisions"] == ["ADR-001", "ADR-005", "ADR-018", "ADR-019"]
    template = contract["ropa_evidence_intake_template"]
    assert isinstance(template, dict)
    required = _strings(template["required_fields"])
    assert {
        "immutable_authenticated_tenant_scope_reference",
        "immutable_authenticated_area_scope_reference",
        "processing_activity_identifier_and_description",
        "processing_purpose_and_necessity_rationale",
        "data_subject_category_evidence",
        "personal_data_category_evidence",
        "recipient_and_subprocessor_evidence",
        "international_transfer_and_location_evidence",
        "retention_deletion_legal_hold_and_recovery_evidence",
        "technical_and_organizational_safeguard_evidence",
        "intake_timestamp_and_accountable_owner",
    } <= required
    scope_requirements = _strings(template["scope_binding_requirements"])
    assert any("cannot establish or expand trusted scope" in item for item in scope_requirements)
    assert any("must not contain raw personal data" in item for item in scope_requirements)
    assert any(
        "may not be reused across Tenant or Area boundaries" in item for item in scope_requirements
    )


def test_missing_scope_or_cross_boundary_evidence_fails_closed() -> None:
    semantics = _contract()["fail_closed_semantics"]
    assert isinstance(semantics, dict)
    assert semantics["immutable_authenticated_scope_references_required"] is True
    assert semantics["one_record_per_artifact_scope_activity_and_purpose"] is True
    assert semantics["missing_or_nonimmutable_authenticated_scope_reference"] == (
        "reject_intake_and_block_deployment_specific_release_decision"
    )
    assert semantics["cross_tenant_or_cross_area_evidence_reuse"] == (
        "reject_intake_and_block_deployment_specific_release_decision"
    )
    assert semantics["proposed_personal_data_or_secret_payload"] == (
        "reject_intake_and_record_data_minimization_blocker"
    )
    assert semantics["no_runtime_authorization_processing_activation_or_enablement"] is True
    assert semantics["no_automatic_release_or_authority_outcome"] is True
    assert semantics["no_allow_outcome"] is True


def test_template_cannot_make_legal_runtime_or_release_decisions() -> None:
    boundary = _contract()["authority_boundary"]
    assert isinstance(boundary, dict)
    prohibited = _strings(boundary["template_is_not"])
    assert {
        "a legal opinion, record-of-processing legal determination, or compliance certification",
        "a repository record containing real personal data or a production processing register",
        "an authenticated Tenant, Area, Project, Session, principal, role, authority, or approval context",
        "a processing, deployment, productive-use, or release approval",
        "a runtime capability enablement or external-effect authorization",
    } <= prohibited
    release_boundary = boundary["release_boundary"]
    assert isinstance(release_boundary, str)
    assert "never activates a runtime path" in release_boundary
