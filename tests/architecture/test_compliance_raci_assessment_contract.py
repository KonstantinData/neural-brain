"""Evidence for the fail-closed compliance RACI assessment template."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
CONTRACT_PATH = ROOT / "docs" / "architecture" / "contracts" / "compliance-raci-assessment-v1.json"


def _contract() -> dict[str, object]:
    loaded: object = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _strings(value: object) -> set[str]:
    assert isinstance(value, list)
    assert all(isinstance(item, str) for item in value)
    return set(value)


def test_template_requires_unambiguous_evidence_bound_responsibility_dimensions() -> None:
    contract = _contract()
    assert contract["contract_id"] == "neural-brain.compliance-raci-assessment"
    assert contract["contract_version"] == "1.0.0"
    assert contract["governing_decisions"] == ["ADR-001", "ADR-005", "ADR-018"]
    template = contract["assessment_template"]
    assert isinstance(template, dict)
    assert _strings(template["responsibility_dimensions"]) == {
        "provider",
        "deployer",
        "privacy",
        "security",
        "product",
        "incident",
        "release",
    }
    assert _strings(template["required_assignment_attributes"]) == {
        "accountable_owner",
        "responsible_operator_or_function",
        "consulted_functions",
        "informed_functions",
        "evidence_reference",
        "scope_and_expiry",
    }


def test_approval_cannot_create_authority_or_replace_protected_control_plane_requirements() -> None:
    template = _contract()["assessment_template"]
    assert isinstance(template, dict)
    rules = _strings(template["approval_authority_rules"])
    assert any("pre-existing authenticated authority source" in rule for rule in rules)
    assert any("cannot create missing authority" in rule for rule in rules)
    assert any("requester may not be the sole approver" in rule for rule in rules)
    assert any("policy author may not be the sole policy activator" in rule for rule in rules)
    assert any("Action, Goal, Memory, or Model Promotion Gate" in rule for rule in rules)


def test_independence_and_escalation_preserve_gates_and_indeterminate_effect_handling() -> None:
    template = _contract()["assessment_template"]
    assert isinstance(template, dict)
    boundaries = _strings(template["required_independence_boundaries"])
    assert {
        "requester_vs_approver_for_elevated_risk_operation",
        "policy_author_vs_sole_policy_activator",
        "executor_vs_independent_verifier",
        "automatic_reconciliation_vs_human_incident_resolution",
    } <= boundaries
    rules = _strings(template["escalation_rules"])
    assert any("cannot bypass" in rule for rule in rules)
    assert any(
        "Unknown, unavailable, conflicted, expired, or non-independent" in rule for rule in rules
    )
    assert any("authoritative reconciliation before retry" in rule for rule in rules)


def test_missing_or_bypass_claim_evidence_blocks_without_authority_or_release_outcome() -> None:
    contract = _contract()
    semantics = contract["fail_closed_semantics"]
    assert isinstance(semantics, dict)
    for key in (
        "unknown_or_missing_required_field",
        "stale_scope_mismatched_or_contradictory_evidence",
        "missing_accountable_owner_qualified_reviewer_independence_or_reassessment_trigger",
        "missing_pre_existing_authenticated_authority_or_control_plane_gate_reference",
        "escalation_that_claims_or_attempts_a_bypass",
    ):
        assert semantics[key] == "assessment_incomplete_and_deployment_specific_release_blocked"
    assert semantics["no_automatic_responsibility_or_authority_assignment"] is True
    assert semantics["no_runtime_authorization_or_enablement"] is True
    assert semantics["no_automatic_release_or_approval_outcome"] is True
    assert semantics["no_allow_outcome"] is True


def test_documentation_preserves_product_neutral_evidence_only_boundary() -> None:
    documentation = (ROOT / "docs" / "governance" / "compliance-raci-assessment-v1.md").read_text(
        encoding="utf-8"
    )
    traceability = (ROOT / "docs" / "traceability" / "FND-04.9-compliance-raci.md").read_text(
        encoding="utf-8"
    )
    assert "does not provide legal advice" in documentation
    assert "Approval never creates missing authority" in documentation
    assert "cannot waive," in documentation
    assert "bypass, reorder, or satisfy" in documentation
    assert "no runtime state, authority, policy activation, external" in traceability
    assert "effect, or release decision" in traceability
