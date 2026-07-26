"""Evidence for the non-authorizing, fail-closed use-case and scope intake."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
CONTRACT_PATH = ROOT / "docs" / "architecture" / "contracts" / "use-case-scope-intake-v1.json"


def _contract() -> dict[str, object]:
    loaded: object = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _strings(value: object) -> set[str]:
    assert isinstance(value, list)
    assert all(isinstance(item, str) for item in value)
    return set(value)


def test_intake_is_versioned_product_neutral_and_covers_the_complete_target() -> None:
    contract = _contract()
    assert contract["contract_id"] == "neural-brain.use-case-scope-intake"
    assert contract["contract_version"] == "1.0.0"
    assert contract["governing_decisions"] == ["ADR-001", "ADR-005", "ADR-018"]
    purpose = contract["purpose"]
    assert isinstance(purpose, str)
    assert "product- and domain-neutral" in purpose
    assert "cannot determine applicable law" in purpose
    scope = contract["scope"]
    assert isinstance(scope, dict)
    assert scope["product_boundary"] == (
        "The Memory Core is a protected internal subsystem, not the product boundary."
    )
    assert scope["activation_precondition"].endswith("it has no allow outcome.")


def test_intake_requires_complete_use_case_scope_control_and_evidence_inputs() -> None:
    template = _contract()["use_case_scope_intake_template"]
    assert isinstance(template, dict)
    required = _strings(template["required_fields"])
    assert {
        "immutable_artifact_version_or_digest",
        "intended_purpose_contract_id_and_version",
        "authenticated_tenant_area_project_scope_model",
        "affected_people_and_impact_assessment",
        "perception_and_observation_boundary",
        "cognition_and_attention_boundary",
        "memory_types_and_lifecycle_boundary",
        "world_self_value_and_model_boundary",
        "learning_consolidation_and_model_promotion_boundary",
        "goals_planning_action_selection_and_external_effect_boundary",
        "data_classes_sources_recipients_and_cross_boundary_flows",
        "retention_legal_hold_deletion_and_recovery_evidence",
        "principal_authority_policy_approvals_and_separation_of_duties_evidence",
        "human_oversight_kill_switch_incident_and_escalation_evidence",
        "risk_assessment_and_security_privacy_release_stops",
        "evaluation_evidence_and_capability_stage_claims",
        "independent_release_decision_reference",
        "evidence_references_and_expiry",
    } <= required
    comparisons = _strings(template["required_comparisons"])
    assert any("intended-purpose contract version" in item for item in comparisons)
    assert any("transition gate" in item for item in comparisons)
    assert any("Memory Core" in item for item in comparisons)
    requirements = _strings(template["recording_requirements"])
    assert any("must not become authenticated runtime context" in item for item in requirements)
    assert any("one favorable input cannot compensate" in item for item in requirements)


def test_missing_or_unqualified_intake_evidence_fails_closed_without_enablement() -> None:
    contract = _contract()
    semantics = contract["fail_closed_semantics"]
    assert isinstance(semantics, dict)
    assert semantics["assessment_contract_version_must_match"] is True
    assert semantics["unknown_or_missing_required_field"] == (
        "intake_incomplete_and_productive_use_release_decision_blocked"
    )
    assert semantics["stale_scope_mismatched_or_contradictory_evidence"] == (
        "intake_incomplete_and_productive_use_release_decision_blocked"
    )
    assert semantics["unaccepted_domain_specific_extension"] == (
        "reject_intake_and_block_productive_use_release_decision"
    )
    assert (
        semantics["unproven_capability_or_recognition_gate"]
        == "productivity_or_capability_claim_blocked"
    )
    assert semantics["unqualified_legal_or_regulatory_input"] == (
        "deployment_specific_release_decision_blocked"
    )
    assert semantics["no_automatic_legal_or_compliance_conclusion"] is True
    assert semantics["no_runtime_authorization_or_enablement"] is True
    assert semantics["no_automatic_release_or_authority_outcome"] is True
    assert semantics["no_allow_outcome"] is True


def test_intake_does_not_become_trusted_context_or_a_runtime_decision() -> None:
    boundary = _contract()["authority_boundary"]
    assert isinstance(boundary, dict)
    assert boundary["template_is"] == (
        "a versioned pre-production governance and traceability input for separately governed review"
    )
    assert {
        "a legal opinion or applicability determination",
        "a deployment, productive-use, or release approval",
        "an authority grant or approval",
        "an authenticated scope, Tenant, Area, Project, Session, or principal context",
        "a protected-state transition request or gate decision",
        "a runtime capability enablement",
    } <= _strings(boundary["template_is_not"])
    assert boundary["release_boundary"].endswith("This template never activates a runtime path.")


def test_current_absence_of_deployment_facts_remains_a_named_blocker() -> None:
    blocker = _contract()["current_blocker"]
    assert isinstance(blocker, dict)
    assert blocker["status"] == "blocked_pending_concrete_use_case_scope_and_qualified_review"
    assert blocker["owner"] == "future deployment accountable owner"
    assert "every required field" in blocker["unblock_condition"]
    assert blocker["next_step"].startswith("Create one immutable intake record")
