"""Evidence for the non-authorizing prohibited and unsupported-use contract."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
CONTRACT_PATH = ROOT / "docs" / "architecture" / "contracts" / "prohibited-unsupported-use-v1.json"


def _contract() -> dict[str, object]:
    loaded: object = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _strings(value: object) -> set[str]:
    assert isinstance(value, list)
    assert all(isinstance(item, str) for item in value)
    return set(value)


def _records(value: object) -> list[dict[str, object]]:
    assert isinstance(value, list)
    assert all(isinstance(item, dict) for item in value)
    return value


def test_prohibitions_are_immutable_and_precede_policy_or_approval() -> None:
    contract = _contract()
    assert contract["contract_id"] == "neural-brain.prohibited-unsupported-use"
    assert contract["contract_version"] == "1.0.0"
    assert contract["governing_decisions"] == ["ADR-001", "ADR-005", "ADR-018"]
    outcomes = contract["classification_outcomes"]
    assert isinstance(outcomes, dict)
    prohibited = outcomes["prohibited"]
    assert isinstance(prohibited, dict)
    assert prohibited["decision"] == "deny_unconditionally"
    assert prohibited["activation"] == "never_authorized_by_policy_or_approval"
    ordered_rules = contract["deterministic_classification_order"]
    assert isinstance(ordered_rules, list)
    assert isinstance(ordered_rules[0], str)
    assert ordered_rules[0].startswith("If a proposed use matches any immutable_prohibition")
    assert _contract()["validation_semantics"] == {
        "unknown_fails_closed": True,
        "prohibition_precedes_all_other_assessment": True,
        "prohibition_is_non_overridable": True,
        "unsupported_is_not_authorization": True,
        "absence_of_catalog_entry_is_not_permission": True,
        "legal_or_regulatory_conclusion_is_not_automatic": True,
        "productive_activation_is_not_authorized": True,
    }


def test_each_security_floor_prohibition_is_deterministically_denied() -> None:
    prohibitions = _records(_contract()["immutable_prohibitions"])
    assert {record["id"] for record in prohibitions} == {
        "PF-01",
        "PF-02",
        "PF-03",
        "PF-04",
        "PF-05",
        "PF-06",
    }
    assert all(record["classification"] == "prohibited" for record in prohibitions)
    uses = {record["proposed_use"] for record in prohibitions}
    assert {
        "override_or_weaken_security_floor_with_policy_or_approval",
        "derive_or_expand_trusted_scope_or_authority_from_untrusted_content",
        "mutate_protected_state_outside_its_named_transition_gate",
        "cause_external_effect_without_all_action_gate_preconditions",
        "allow_productive_model_self_mutation_or_self_modification_of_controls",
        "claim_recognition_or_maturity_without_all_non_compensatory_evidence_gates",
    } == uses


def test_sensitive_or_unknown_uses_remain_unsupported_without_an_allow_path() -> None:
    contract = _contract()
    categories = _records(contract["unsupported_use_categories"])
    assert {record["id"] for record in categories} == {"UF-01", "UF-02", "UF-03", "UF-04"}
    assert all(record["classification"] == "unsupported" for record in categories)
    sensitive = next(record for record in categories if record["id"] == "UF-02")
    controls = _strings(sensitive["required_before_any_future_reassessment"])
    assert {
        "separately_accepted_risk_and_use_classification",
        "qualified_applicable_law_and_lawful_operation_evidence_where_required",
        "authenticated_authority",
        "scoped_controls",
        "complete_evidence_gates",
        "required_independent_human_approval",
    } <= controls
    boundary = contract["authority_boundary"]
    assert isinstance(boundary, dict)
    assert boundary["no_allow_outcome"] is True
    assert {
        "a legal determination",
        "a finding of lawfulness",
        "a deployment or release approval",
        "an authority grant",
        "a runtime capability enablement",
    } <= _strings(boundary["contract_is_not"])


def test_missing_stale_or_unaccepted_inputs_fail_closed() -> None:
    template = _contract()["classification_request_template"]
    assert isinstance(template, dict)
    assert {
        "proposed_use_identifier",
        "intended_purpose_contract_version",
        "scope_model",
        "data_classes",
        "risk_or_impact_classification",
        "evidence_references",
        "accountable_owner",
    } <= _strings(template["required_fields"])
    assert template["unknown_or_missing_required_field"] == "unsupported"
    assert template["stale_or_scope_mismatched_evidence"] == "unsupported"
    assert template["unaccepted_domain_specific_extension"] == "unsupported"
