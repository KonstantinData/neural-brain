"""Evidence for the fail-closed compliance release-decision record template."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
CONTRACT_PATH = ROOT / "docs" / "architecture" / "contracts" / "compliance-release-decision-v1.json"


def _contract() -> dict[str, object]:
    loaded: object = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _strings(value: object) -> set[str]:
    assert isinstance(value, list)
    assert all(isinstance(item, str) for item in value)
    return set(value)


def test_record_requires_scoped_signed_evidence_and_both_regulatory_paths() -> None:
    contract = _contract()
    assert contract["contract_id"] == "neural-brain.compliance-release-decision-record"
    assert contract["contract_version"] == "1.0.0"
    assert contract["governing_decisions"] == ["ADR-001", "ADR-005", "ADR-018"]
    template = contract["release_decision_record_template"]
    assert isinstance(template, dict)
    fields = _strings(template["required_fields"])
    assert {
        "authenticated_tenant_area_project_scope_model",
        "signer_authenticated_identity_reference_signature_evidence_and_signing_timestamp",
        "pre_existing_authority_snapshot_reference_policy_decision_reference_and_required_approval_evidence",
        "gdpr_qualified_approved_finding_reference_or_explicit_qualified_non_applicability_basis",
        "ai_act_qualified_approved_finding_reference_or_explicit_qualified_non_applicability_basis",
        "reassessment_trigger_intake_references_open_work_and_current_evidence_freshness",
        "decision_status_and_effective_window",
    } <= fields
    assert _strings(template["permitted_decision_statuses"]) == {
        "approved",
        "blocked",
        "rejected",
        "expired",
        "revoked",
        "indeterminate",
    }


def test_approved_requires_two_qualified_paths_and_cannot_authorize_runtime() -> None:
    template = _contract()["release_decision_record_template"]
    assert isinstance(template, dict)
    rules = _strings(template["decision_rules"])
    assert any("both the GDPR and EU AI Act requirement" in rule for rule in rules)
    assert any("explicit qualified non-applicability basis" in rule for rule in rules)
    assert any("cannot create missing authority" in rule for rule in rules)
    assert any("Action, Goal, Memory, or Model Promotion transition" in rule for rule in rules)


def test_missing_ambiguous_or_unresolved_evidence_fails_closed() -> None:
    contract = _contract()
    semantics = contract["fail_closed_semantics"]
    assert isinstance(semantics, dict)
    for key in (
        "unknown_or_missing_required_field",
        "stale_scope_mismatched_or_contradictory_evidence",
        "missing_or_unverifiable_signer_identity_signature_authority_policy_or_approval_evidence",
        "missing_gdpr_or_ai_act_approved_finding_and_explicit_qualified_non_applicability_basis",
        "open_or_unresolved_reassessment_release_stop_or_non_bypass_exception",
    ):
        assert semantics[key] == "release_decision_incomplete_and_productive_enablement_blocked"
    assert semantics["indeterminate_or_ambiguous_decision_or_effect"] == (
        "indeterminate_and_productive_enablement_blocked_pending_authoritative_reconciliation"
    )
    assert semantics["no_runtime_authorization_or_enablement"] is True
    assert semantics["no_protected_state_mutation"] is True
    assert semantics["no_allow_outcome"] is True


def test_documentation_preserves_signed_evidence_and_non_authorization_boundary() -> None:
    documentation = (ROOT / "docs" / "governance" / "compliance-release-decision-v1.md").read_text(
        encoding="utf-8"
    )
    traceability = (
        ROOT / "docs" / "traceability" / "FND-04.11-compliance-release-decision.md"
    ).read_text(encoding="utf-8")
    assert "does not provide legal advice" in documentation
    assert "does not provide a signing or" in documentation
    assert "Approval never creates missing authority" in documentation
    assert "cannot waive, bypass, reorder, or satisfy" in documentation
    assert "no protected state, authority, policy activation, external" in traceability
    assert "effect, or product runtime" in traceability
