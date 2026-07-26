"""Evidence for the fail-closed reassessment-trigger intake template."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
CONTRACT_PATH = ROOT / "docs" / "architecture" / "contracts" / "reassessment-trigger-intake-v1.json"


def _contract() -> dict[str, object]:
    loaded: object = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _strings(value: object) -> set[str]:
    assert isinstance(value, list)
    assert all(isinstance(item, str) for item in value)
    return set(value)


def test_template_covers_every_required_change_category_and_tracked_work() -> None:
    contract = _contract()
    assert contract["contract_id"] == "neural-brain.reassessment-trigger-intake"
    assert contract["contract_version"] == "1.0.0"
    assert contract["governing_decisions"] == ["ADR-001", "ADR-005", "ADR-018"]
    template = contract["trigger_intake_template"]
    assert isinstance(template, dict)
    trigger_types = _strings(template["mandatory_trigger_types"])
    assert {
        "legal_or_regulatory_source_change",
        "qualified_guidance_or_review_standard_change",
        "model_artifact_model_version_or_model_behavior_change",
        "supplier_supplier_terms_or_supplier_assurance_change",
        "intended_purpose_enabled_operation_or_reasonably_foreseeable_misuse_change",
        "data_subject_category_data_class_data_source_recipient_location_or_transfer_boundary_change",
        "deployment_environment_jurisdiction_operator_affected_people_or_external_effect_boundary_change",
    } == trigger_types
    required = _strings(template["required_event_fields"])
    assert {
        "trigger_source_and_immutable_evidence_reference",
        "assessment_owner_and_accountable_owner",
        "tracked_reassessment_work_item_identifier",
        "tracked_reassessment_work_item_owner_status_next_step_and_due_date",
    } <= required


def test_intake_requires_open_owned_work_and_preserves_non_bypass_boundary() -> None:
    template = _contract()["trigger_intake_template"]
    assert isinstance(template, dict)
    order = _strings(template["deterministic_intake_order"])
    assert any(
        "Create or link exactly one tracked reassessment work item" in rule for rule in order
    )
    assert any("cannot amend, expire, supersede, or reactivate" in rule for rule in order)
    attributes = _strings(template["tracked_work_item_required_attributes"])
    assert {
        "accountable_owner",
        "concrete_next_step",
        "due_date_or_explicit_review_trigger",
        "release_blocker_and_non_bypass_boundary",
    } <= attributes


def test_unknown_or_incomplete_trigger_fails_closed_without_polling_or_runtime_effect() -> None:
    contract = _contract()
    semantics = contract["fail_closed_semantics"]
    assert isinstance(semantics, dict)
    for key in (
        "unknown_or_missing_required_event_or_work_item_field",
        "stale_scope_mismatched_or_contradictory_trigger_evidence",
        "missing_owner_next_step_due_or_review_trigger_or_tracked_work_item",
        "attempted_bypass_or_closure_without_separately_governed_qualified_evidence",
    ):
        assert (
            semantics[key]
            == "reassessment_incomplete_and_affected_deployment_specific_release_blocked"
        )
    assert semantics["unrecognized_ambiguous_or_compound_change_event"] == (
        "unknown_and_escalate_reassessment_incomplete_and_affected_deployment_specific_release_blocked"
    )
    assert semantics["no_background_polling_or_external_fact_claim"] is True
    assert semantics["no_runtime_authorization_or_enablement"] is True
    assert semantics["no_protected_runtime_state_mutation"] is True
    assert semantics["no_allow_outcome"] is True


def test_documentation_preserves_reported_change_and_separate_governance_boundary() -> None:
    documentation = (ROOT / "docs" / "governance" / "reassessment-trigger-intake-v1.md").read_text(
        encoding="utf-8"
    )
    traceability = (
        ROOT / "docs" / "traceability" / "FND-04.10-reassessment-triggers.md"
    ).read_text(encoding="utf-8")
    assert "does not poll external" in documentation
    assert "neither determines law" in documentation
    assert "cannot waive, compensate for, reorder," in documentation
    assert "no runtime state, authority, policy activation, external" in traceability
    assert "effect, release decision, or background job" in traceability
