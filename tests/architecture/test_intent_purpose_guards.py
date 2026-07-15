import itertools
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[2]
PATH = ROOT / "docs" / "architecture" / "contracts" / "intent-purpose-guards.json"
PURPOSES = ["execution", "verification", "cancellation", "reconciliation", "compensation"]
GOAL_STATES = [
    "proposed",
    "active",
    "suspended",
    "blocked",
    "verifying",
    "terminating",
    "achieved",
    "failed",
    "discarded",
]


def _map(value: object) -> dict[str, object]:
    assert isinstance(value, dict)
    return value


def _list(value: object) -> list[object]:
    assert isinstance(value, list)
    return value


def _strings(value: object) -> list[str]:
    values = _list(value)
    assert all(isinstance(item, str) for item in values)
    return [item for item in values if isinstance(item, str)]


@pytest.fixture(scope="module")
def contract() -> dict[str, object]:
    with PATH.open(encoding="utf-8") as source:
        return _map(json.load(source))


def _purpose_allowed(matrix: dict[str, object], state: str, purpose: str) -> bool:
    return state in matrix and purpose in _strings(matrix[state])


def test_purpose_profiles_and_goal_matrix_are_exact(contract: dict[str, object]) -> None:
    assert _strings(contract["canonical_purposes"]) == PURPOSES
    profiles = _map(contract["purpose_profiles"])
    assert list(profiles) == PURPOSES
    for purpose in PURPOSES:
        profile = _map(profiles[purpose])
        assert {
            "permitted_request_actors",
            "proposal_authority",
            "commit_authority_snapshot",
            "required_policy",
            "approval",
            "evidence",
            "external_effect",
        } <= set(profile)
        assert _strings(profile["permitted_request_actors"])
        assert _strings(profile["proposal_authority"])
        assert _strings(profile["commit_authority_snapshot"])
        assert _strings(profile["required_policy"])
        assert _strings(profile["evidence"])
    matrix = _map(contract["goal_state_matrix"])
    assert list(matrix) == GOAL_STATES
    assert {state: _strings(values) for state, values in matrix.items()} == {
        "proposed": [],
        "active": ["execution"],
        "suspended": [],
        "blocked": ["cancellation", "reconciliation", "compensation"],
        "verifying": ["verification"],
        "terminating": ["cancellation", "reconciliation", "compensation"],
        "achieved": [],
        "failed": [],
        "discarded": [],
    }


def test_goal_state_purpose_matrix_is_total_cartesian_decision(
    contract: dict[str, object],
) -> None:
    matrix = _map(contract["goal_state_matrix"])
    decisions = {
        (state, purpose): _purpose_allowed(matrix, state, purpose)
        for state, purpose in itertools.product(GOAL_STATES, PURPOSES)
    }
    assert len(decisions) == len(GOAL_STATES) * len(PURPOSES)
    assert sum(decisions.values()) == 8
    assert not _purpose_allowed(matrix, "unknown", "execution")
    assert not _purpose_allowed(matrix, "active", "unknown")


def test_scope_guard_contains_complete_session_bound_hierarchy(contract: dict[str, object]) -> None:
    registry = _map(contract["rule_registry"])
    scope = _map(registry["PG-SCOPE-MATCH"])
    assert scope["operator"] == "all_equal"
    assert scope["left"] == "intent.scope" and scope["right"] == "goal.scope"
    assert _strings(scope["fields"]) == [
        "tenant_id",
        "area_id",
        "project_id",
        "session_id",
        "goal_id",
    ]


def test_unknown_state_actor_purpose_and_scope_mismatch_are_default_deny(
    contract: dict[str, object],
) -> None:
    deny = _map(contract["default_deny"])
    assert deny["unknown_goal_state"] == "deny"
    assert deny["unknown_action_state"] == "deny"
    assert deny["unknown_actor"] == "deny_and_audit"
    assert deny["unknown_purpose"] == "deny_and_audit"
    assert deny["unknown_transition"] == "deny_and_audit"
    assert deny["scope_mismatch"] == "deny_and_audit"


def test_compensation_is_distinct_and_indeterminate_paths_are_closed(
    contract: dict[str, object],
) -> None:
    registry = _map(contract["rule_registry"])
    compensation = _map(registry["PG-COMPENSATION-SEPARATE-INTENT"])
    assert compensation["operator"] == "requires_distinct_intent"
    assert compensation["purpose"] == "compensation"
    assert {"purpose_mutation", "reuse_original_execution_grant"} == set(
        _strings(compensation["forbids"])
    )
    restriction = _map(registry["PG-INDETERMINATE-RESTRICT"])
    assert _strings(restriction["transition_ids"]) == [
        "action.resolve_effect_confirmed",
        "action.resolve_no_effect_confirmed",
        "action.resolve_effect_compensated",
    ]
    assert _map(restriction["when"])["action_state"] == "indeterminate"


def test_approval_never_supplies_authority_and_elevated_risk_separates_actors(
    contract: dict[str, object],
) -> None:
    registry = _map(contract["rule_registry"])
    approval = _map(registry["PG-APPROVAL-NOT-AUTHORITY"])
    assert approval["operator"] == "must_not_satisfy"
    assert approval["requirement"] == "missing_authority_or_security_floor_denial"
    separation = _map(registry["PG-SOD-ELEVATED-RISK"])
    assert separation["operator"] == "not_equal"
    assert separation["left"] == "requester_principal_id"
    assert separation["right"] == "approver_principal_id"
