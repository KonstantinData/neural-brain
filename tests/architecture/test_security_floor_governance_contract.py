"""Evidence for S1-15.3 Security Floor governance traceability."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
CONTRACT_PATH = ROOT / "docs" / "architecture" / "contracts" / "security-floor-governance-v1.json"


def _contract() -> dict[str, object]:
    loaded: object = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _strings(value: object) -> set[str]:
    assert isinstance(value, list)
    assert all(isinstance(item, str) for item in value)
    return set(value)


def test_every_immutable_prohibition_has_non_overridable_security_floor_mapping() -> None:
    contract = _contract()
    assert contract["contract_id"] == "neural-brain.security-floor-governance"
    assert contract["contract_version"] == "1.0.0"
    assert contract["governing_decisions"] == ["ADR-005", "ADR-018"]
    rules = contract["non_overridable_security_floor_rules"]
    assert isinstance(rules, list)
    assert len(rules) == 6
    assert {rule["source_prohibition_id"] for rule in rules if isinstance(rule, dict)} == {
        "PF-01",
        "PF-02",
        "PF-03",
        "PF-04",
        "PF-05",
        "PF-06",
    }
    assert all(
        isinstance(rule, dict) and rule["violation_outcome"] == "prohibited_and_denied"
        for rule in rules
    )


def test_current_s1021_memory_core_enforcement_is_not_overclaimed_as_target_runtime() -> None:
    scope = _contract()["implementation_scope"]
    assert isinstance(scope, dict)
    assert scope["runtime_expansion"] is False
    assert "memory_ingest and memory_read" in str(scope["current_runtime_enforcement"])
    assert "do not assert" in str(scope["target_governance_mapping"])


def test_sensitive_or_high_risk_candidate_requires_human_review_but_never_authorizes() -> None:
    boundary = _contract()["sensitive_or_high_risk_candidate_review_boundary"]
    assert isinstance(boundary, dict)
    assert {
        "sensitive_high_impact_or_high_risk_use",
        "high_risk_candidate",
        "prohibited_candidate",
        "not_assessed",
        "unknown_missing_stale_scope_mismatched_or_contradictory_evidence",
    } <= _strings(boundary["applies_to"])
    assert "qualified_independent_human_review" in _strings(
        boundary[
            "required_before_any_separately_governed_future_reassessment_or_release_evaluation"
        ]
    )
    assert (
        boundary["fail_closed_outcome_when_absent"]
        == "unsupported_and_deployment_specific_release_blocked"
    )
    assert {
        "a legal or regulatory classification",
        "an authority grant or scope expansion",
        "a policy decision or Security Floor override",
        "a protected-state transition, gate decision, or runtime enablement",
        "a deployment, productive-use, or release approval",
    } <= _strings(boundary["human_review_is_not"])
    assert "may not convert prohibited or unsupported into allow" in str(
        boundary["non_override_rule"]
    )


def test_deterministic_order_denies_before_review_and_has_no_allow_outcome() -> None:
    order = _contract()["deterministic_governance_order"]
    assert isinstance(order, list)
    assert len(order) == 4
    assert "before considering review evidence" in str(order[0])
    assert "unknown, missing, stale, contradictory, scope-mismatched, or unaccepted" in str(
        order[1]
    )
    assert "no allow, authorization, activation, or release outcome" in str(order[3])
