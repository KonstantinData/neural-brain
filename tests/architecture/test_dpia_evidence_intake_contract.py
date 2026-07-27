"""Evidence for the fail-closed DPIA evidence intake contract."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
CONTRACT_PATH = ROOT / "docs" / "architecture" / "contracts" / "dpia-evidence-intake-v1.json"


def _contract() -> dict[str, object]:
    loaded: object = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _strings(value: object) -> set[str]:
    assert isinstance(value, list)
    assert all(isinstance(item, str) for item in value)
    return set(value)


def test_template_requires_scope_owner_reviewer_and_dpia_evidence() -> None:
    contract = _contract()
    assert contract["contract_id"] == "neural-brain.dpia-evidence-intake"
    assert contract["contract_version"] == "1.0.0"
    assert contract["governing_decisions"] == ["ADR-001", "ADR-005", "ADR-018", "ADR-019"]
    external = contract["authoritative_external_reference"]
    assert isinstance(external, dict)
    assert external["official_url"] == "https://eur-lex.europa.eu/eli/reg/2016/679/oj"
    template = contract["dpia_evidence_intake_template"]
    assert isinstance(template, dict)
    required = _strings(template["required_fields"])
    assert {
        "intake_timestamp_and_accountable_owner_reference",
        "qualified_independent_reviewer_qualification_review_date_and_independence_reference",
        "immutable_artifact_version_or_digest",
        "deployment_identifier_target_environment_and_jurisdiction_evidence_references",
        "immutable_authenticated_tenant_area_project_scope_references",
        "immutable_intended_purpose_contract_id_version_and_purpose_reference",
        "immutable_processing_activity_identifier_version_and_activity_reference",
        "dpia_assessment_method_scope_and_necessity_proportionality_evidence_references_for_qualified_review_only",
        "risk_scenario_likelihood_impact_and_risk_register_evidence_references_for_qualified_review_only",
        "mitigation_control_owner_due_date_and_effectiveness_evidence_references_for_qualified_review_only",
        "residual_risk_assessment_and_unresolved_high_residual_risk_evidence_references_for_qualified_review_only",
        "approval_review_status_and_reviewer_or_approver_evidence_references_for_qualified_review_only",
        "article_36_prior_consultation_trigger_disposition_and_evidence_references_for_qualified_review_only",
    } <= required
    scope_binding = _strings(template["scope_binding_requirements"])
    assert any(
        "cannot establish, broaden, or substitute trusted scope" in item for item in scope_binding
    )
    assert any("must not contain raw personal data" in item for item in scope_binding)
    assert any("Unknown, stale, contradictory" in item for item in scope_binding)


def test_review_order_and_reassessment_are_deterministic_and_fail_closed() -> None:
    template = _contract()["dpia_evidence_intake_template"]
    assert isinstance(template, dict)
    order = template["deterministic_review_order"]
    assert isinstance(order, list)
    assert len(order) == 6
    assert isinstance(order[2], str)
    assert "without determining whether a DPIA is required or whether any risk is high" in order[2]
    assert isinstance(order[3], str)
    assert (
        "without determining adequacy, effectiveness, residual risk, approval validity" in order[3]
    )
    assert isinstance(order[4], str)
    assert "prior consultation is legally required" in order[4]
    triggers = _strings(template["mandatory_reassessment_triggers"])
    assert {
        "authenticated_tenant_area_project_scope_purpose_activity_or_jurisdiction_change",
        "dpia_assessment_method_risk_scenario_likelihood_impact_mitigation_control_or_residual_risk_evidence_change",
        "article_36_prior_consultation_trigger_disposition_change",
    } <= triggers


def test_unknown_or_unresolved_high_risk_evidence_blocks_without_determinations() -> None:
    contract = _contract()
    semantics = contract["fail_closed_semantics"]
    assert isinstance(semantics, dict)
    blocked = "dpia_evidence_intake_incomplete_and_deployment_specific_release_blocked"
    assert all(
        semantics[key] == blocked
        for key in (
            "unknown_or_missing_required_field",
            "stale_scope_mismatched_or_contradictory_evidence",
            "missing_accountable_owner_qualified_independent_reviewer_review_date_evidence_or_reassessment_trigger",
            "unknown_unqualified_stale_or_conflicting_assessment_risk_mitigation_residual_risk_approval_review_or_prior_consultation_trigger_evidence",
            "unresolved_high_residual_risk_or_prior_consultation_trigger_disposition",
        )
    )
    assert (
        semantics[
            "missing_or_nonimmutable_authenticated_scope_artifact_purpose_activity_or_jurisdiction_reference"
        ]
        == "reject_intake_and_block_deployment_specific_release_decision"
    )
    assert (
        semantics["proposed_personal_data_or_secret_payload"]
        == "reject_intake_and_record_data_minimization_blocker"
    )
    assert (
        semantics[
            "no_automatic_dpia_requirement_risk_residual_risk_approval_or_prior_consultation_determination"
        ]
        is True
    )
    assert semantics["no_runtime_authorization_processing_activation_or_enablement"] is True
    assert semantics["no_automatic_release_or_authority_outcome"] is True
    assert semantics["no_allow_outcome"] is True


def test_template_cannot_be_an_approved_dpia_or_runtime_or_release_decision() -> None:
    boundary = _contract()["authority_boundary"]
    assert isinstance(boundary, dict)
    prohibited = _strings(boundary["template_is_not"])
    assert {
        "a legal opinion, data-protection impact assessment determination, prior-consultation determination, or compliance certification",
        "a determination that a DPIA is required, a risk is high, residual risk is acceptable, a mitigation is effective, an approval is valid, or prior consultation is legally required",
        "a processing, deployment, productive-use, or release approval",
        "a runtime capability enablement or external-effect authorization",
        "an implementation, maturity, recognition, safety, product capability, or production-autonomy claim",
    } <= prohibited
    release_boundary = boundary["release_boundary"]
    assert isinstance(release_boundary, str)
    assert "never activates a runtime path" in release_boundary
