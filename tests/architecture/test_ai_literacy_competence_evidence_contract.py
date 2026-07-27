"""Evidence for the fail-closed AI-literacy competence-evidence template."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
CONTRACT_PATH = (
    ROOT / "docs" / "architecture" / "contracts" / "ai-literacy-competence-evidence-v1.json"
)


def _contract() -> dict[str, object]:
    loaded: object = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _strings(value: object) -> set[str]:
    assert isinstance(value, list)
    assert all(isinstance(item, str) for item in value)
    return set(value)


def test_template_covers_all_required_roles_and_shared_safety_topics() -> None:
    contract = _contract()
    assert contract["contract_id"] == "neural-brain.ai-literacy-competence-evidence"
    assert contract["contract_version"] == "1.0.0"
    assert contract["governing_decisions"] == ["ADR-001", "ADR-005", "ADR-018"]
    template = contract["competence_template"]
    assert isinstance(template, dict)
    assert _strings(template["role_categories"]) == {
        "developers",
        "operators",
        "approvers",
        "independent_verifiers",
        "support",
        "affected_staff",
    }
    shared = _strings(template["shared_required_curriculum_topics"])
    assert {
        "two_plane_architecture_and_cognitive_capability_does_not_create_authority",
        "protected_transition_gates_security_floor_and_fail_closed_behavior",
        "audit_evidence_incident_escalation_and_indeterminate_effect_reconciliation",
        "recognition_delivery_stage_and_no_unsupported_capability_claims",
    } <= shared
    role_topics = template["role_specific_required_topics"]
    assert isinstance(role_topics, dict)
    assert set(role_topics) == _strings(template["role_categories"])


def test_evidence_is_deidentified_expiring_and_never_creates_authority() -> None:
    template = _contract()["competence_template"]
    assert isinstance(template, dict)
    fields = _strings(template["required_evidence_fields"])
    assert {
        "de_identified_evidence_record_reference_or_explicit_absence",
        "evidence_timestamp_expiry_and_reassessment_due_or_trigger",
        "linked_release_or_operation_blocker_reference",
    } <= fields
    rules = _strings(template["competence_evidence_rules"])
    assert any("neither proves that a real person is trained" in rule for rule in rules)
    assert any("stores neither HR personal data" in rule for rule in rules)
    assert any("never creates authority" in rule for rule in rules)
    assert any("requester and elevated-risk approver" in rule for rule in rules)
    assert any("Expiry, unknown status" in rule for rule in rules)


def test_refresh_requires_reassessment_and_preserves_all_protected_boundaries() -> None:
    template = _contract()["competence_template"]
    assert isinstance(template, dict)
    refresh = template["refresh_cycle"]
    assert isinstance(refresh, dict)
    assert {
        "evidence_expiry",
        "material_change_trigger_reference",
        "reassessment_owner_and_next_step",
    } <= _strings(refresh["required_fields"])
    order = _strings(refresh["deterministic_order"])
    assert any("separately governed reassessment work item" in rule for rule in order)
    assert any(
        "cannot alter authority, approvals, policy, transition gates" in rule for rule in order
    )
    assert any("not an allow outcome" in rule for rule in order)


def test_incomplete_or_bypass_claim_evidence_fails_closed_without_personnel_or_runtime_effect() -> (
    None
):
    contract = _contract()
    semantics = contract["fail_closed_semantics"]
    assert isinstance(semantics, dict)
    assert semantics["unknown_missing_stale_expired_conflicted_or_scope_mismatched_evidence"] == (
        "competence_evidence_incomplete_and_affected_role_dependent_release_or_operation_blocked"
    )
    assert semantics["attempt_to_use_competence_evidence_as_authority_or_gate_bypass"] == (
        "competence_evidence_invalid_and_affected_role_dependent_release_or_operation_blocked"
    )
    assert semantics["no_real_person_training_or_competence_claim"] is True
    assert semantics["no_hr_personal_data_processing_or_storage"] is True
    assert semantics["no_authority_delegation_or_runtime_authorization"] is True
    assert semantics["no_protected_runtime_state_mutation"] is True
    assert semantics["no_allow_outcome"] is True


def test_documentation_preserves_evidence_only_product_neutral_boundary() -> None:
    documentation = (
        ROOT / "docs" / "governance" / "ai-literacy-competence-evidence-v1.md"
    ).read_text(encoding="utf-8")
    traceability = (
        ROOT / "docs" / "traceability" / "S1-15.2-ai-literacy-competence-evidence.md"
    ).read_text(encoding="utf-8")
    assert "real person was trained or competent" in documentation
    assert "stores no HR personal data" in documentation
    assert "never creates authority" in documentation
    assert "fails closed" in documentation
    assert "no protected runtime state, identity, authority, policy" in traceability
    assert "approval, external effect, release decision, or HR record" in traceability
