"""Evidence for the fail-closed data-object catalogue intake contract."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
CONTRACT_PATH = (
    ROOT / "docs" / "architecture" / "contracts" / "data-object-catalogue-intake-v1.json"
)


def _contract() -> dict[str, object]:
    loaded: object = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _strings(value: object) -> set[str]:
    assert isinstance(value, list)
    assert all(isinstance(item, str) for item in value)
    return set(value)


def test_catalogue_requires_every_acceptance_criterion_and_ropa_link() -> None:
    contract = _contract()
    assert contract["contract_id"] == "neural-brain.data-object-catalogue-intake"
    assert contract["contract_version"] == "1.0.0"
    assert contract["governing_decisions"] == ["ADR-001", "ADR-005", "ADR-018", "ADR-019"]
    template = contract["data_object_catalogue_intake_template"]
    assert isinstance(template, dict)
    required = _strings(template["required_fields"])
    assert {
        "technical_owner_and_accountable_governance_owner_evidence",
        "controller_processor_role_evidence_reference",
        "processing_activity_identifier_and_purpose_necessity_evidence",
        "recipient_subprocessor_and_transfer_evidence",
        "storage_location_and_protection_evidence",
        "creation_update_read_export_archive_and_deletion_transition_evidence",
        "retention_legal_hold_recovery_and_deletion_responsibility_evidence",
        "data_subject_rights_and_request-handling_evidence",
        "processing_register_and_ropa_evidence_reference",
    } <= required
    scope = _strings(template["scope_binding_requirements"])
    assert any("cannot establish or expand trusted scope" in item for item in scope)
    assert (
        "project_scope_applicability_and_immutable_authenticated_project_scope_lineage_evidence"
        in required
    )
    assert any("immutable authenticated Project scope evidence" in item for item in scope)
    assert any(
        "cannot establish, infer, or expand Project scope or lineage" in item for item in scope
    )
    assert any("does not create a processing register" in item for item in scope)


def test_catalogue_lifecycle_preserves_gate_and_privacy_invariants() -> None:
    template = _contract()["data_object_catalogue_intake_template"]
    assert isinstance(template, dict)
    lifecycle = _strings(template["lifecycle_requirements"])
    assert any("Memory Transition Gate" in item for item in lifecycle)
    assert any("deletion responsibility" in item for item in lifecycle)
    comparisons = _strings(template["required_comparisons"])
    assert any("processing-register evidence" in item for item in comparisons)
    assert any("Area isolation" in item for item in comparisons)


def test_missing_evidence_and_payloads_fail_closed_without_runtime_authority() -> None:
    semantics = _contract()["fail_closed_semantics"]
    assert isinstance(semantics, dict)
    assert semantics["processing_register_reference_required"] is True
    assert semantics["missing_processing_register_reference"] == (
        "reject_intake_and_block_deployment_specific_release_decision"
    )
    assert semantics["cross_tenant_or_cross_area_evidence_reuse"] == (
        "reject_intake_and_block_deployment_specific_release_decision"
    )
    assert (
        semantics["unknown_or_missing_project_scope_or_lineage_for_project_bound_object"]
        == "reject_intake_and_block_deployment_specific_release_decision"
    )
    assert semantics["cross_tenant_or_cross_area_or_cross_project_evidence_reuse"] == (
        "reject_intake_and_block_deployment_specific_release_decision"
    )
    assert semantics["proposed_personal_data_or_secret_payload"] == (
        "reject_intake_and_record_data_minimization_blocker"
    )
    assert semantics["no_runtime_authorization_processing_activation_or_enablement"] is True
    assert semantics["no_automatic_release_or_authority_outcome"] is True
    assert semantics["no_allow_outcome"] is True


def test_catalogue_cannot_make_legal_processing_or_release_decisions() -> None:
    boundary = _contract()["authority_boundary"]
    assert isinstance(boundary, dict)
    prohibited = _strings(boundary["template_is_not"])
    assert {
        "a repository record containing real personal data, a production processing register, or an active data inventory",
        "an authenticated Tenant, Area, Project, Session, principal, role, authority, or approval context, or Project lineage",
        "a processing, deployment, productive-use, or release approval",
        "a runtime capability enablement, protected-state write, or external-effect authorization",
    } <= prohibited
    release_boundary = boundary["release_boundary"]
    assert isinstance(release_boundary, str)
    assert "never creates a runtime path" in release_boundary
