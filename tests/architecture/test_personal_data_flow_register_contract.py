"""Evidence for the fail-closed personal-data flow and recipient register contract."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
CONTRACT_PATH = ROOT / "docs" / "architecture" / "contracts" / "personal-data-flow-register-v1.json"


def _contract() -> dict[str, object]:
    loaded: object = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _strings(value: object) -> set[str]:
    assert isinstance(value, list)
    assert all(isinstance(item, str) for item in value)
    return set(value)


def test_data_flow_register_is_versioned_scope_bound_and_category_only() -> None:
    contract = _contract()
    assert contract["contract_id"] == "neural-brain.personal-data-flow-register"
    assert contract["contract_version"] == "1.0.0"
    assert contract["governing_decisions"] == ["ADR-001", "ADR-005", "ADR-018", "ADR-019"]
    template = contract["personal_data_flow_record_template"]
    assert isinstance(template, dict)
    required = _strings(template["required_fields"])
    assert {
        "source_system_or_origin_category_and_evidence_reference",
        "data_subject_category_and_personal_data_category_evidence",
        "processing_purpose_and_activity_reference",
        "immutable_scope_and_lineage_evidence_reference",
        "recipient_or_subprocessor_category_and_evidence_reference",
        "recipient_location_and_international_transfer_boundary_evidence",
        "retention_deletion_legal_hold_and_recovery_evidence_reference",
        "technical_and_organizational_safeguard_evidence_reference",
        "flow_provenance_mapping_and_evidence_references",
        "known_unknown_or_unverified_deployment_facts",
    } <= required
    requirements = _strings(template["scope_binding_requirements"])
    assert any(
        "cannot establish, expand, replace, or override trusted runtime context" in item
        for item in requirements
    )
    assert any("must not contain raw personal data" in item for item in requirements)
    assert any(
        "may not be reused across Tenant or Area boundaries" in item for item in requirements
    )


def test_missing_or_cross_boundary_data_flow_evidence_fails_closed() -> None:
    semantics = _contract()["fail_closed_semantics"]
    assert isinstance(semantics, dict)
    assert semantics["immutable_authenticated_scope_references_required"] is True
    assert semantics["one_record_per_artifact_scope_source_recipient_and_purpose"] is True
    assert semantics[
        "missing_source_category_purpose_recipient_transfer_retention_safeguard_or_evidence_reference"
    ] == ("reject_record_and_block_deployment_specific_release_decision")
    assert semantics["cross_tenant_or_cross_area_flow_without_authenticated_scoped_evidence"] == (
        "deny_flow_claim_and_block_deployment_specific_release_decision"
    )
    assert semantics["cross_tenant_or_cross_area_evidence_reuse"] == (
        "reject_record_and_block_deployment_specific_release_decision"
    )
    assert semantics["unknown_deployment_fact"] == (
        "record_explicit_blocker_and_block_deployment_specific_release_decision"
    )
    assert semantics["no_runtime_transfer_disclosure_or_processing"] is True
    assert semantics["no_allow_outcome"] is True


def test_data_flow_register_cannot_make_runtime_legal_or_release_decisions() -> None:
    boundary = _contract()["authority_boundary"]
    assert isinstance(boundary, dict)
    prohibited = _strings(boundary["template_is_not"])
    assert {
        "a legal opinion, data-transfer determination, data-protection impact assessment, or compliance certification",
        "a repository record containing real personal data or a production processing or recipient register",
        "a runtime data-flow, processing, transfer, disclosure, storage, or deletion instruction",
        "a processing, deployment, productive-use, or release approval",
        "a runtime capability enablement or external-effect authorization",
    } <= prohibited
    release_boundary = boundary["release_boundary"]
    assert isinstance(release_boundary, str)
    assert "never activates a runtime path" in release_boundary
