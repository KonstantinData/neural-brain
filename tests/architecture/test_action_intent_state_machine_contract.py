import itertools
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[2]
PATH = ROOT / "docs" / "architecture" / "contracts" / "action-intent-state-machine.json"
STATES = [
    "proposed",
    "preparing",
    "prepared",
    "committed",
    "executing",
    "cancel_requested",
    "settling",
    "indeterminate",
    "completed",
    "aborted",
]
PURPOSES = ["execution", "verification", "cancellation", "reconciliation", "compensation"]
TERMINAL = {"completed", "aborted"}
COMMON_FIELDS = {
    "transition_id",
    "contract_version",
    "source",
    "target",
    "permitted_request_actors",
    "authority",
    "policy",
    "approval",
    "guards",
    "quiescence",
    "evidence",
    "atomic_side_effects",
    "audit_event",
    "deadline",
    "timeout",
    "cancellation",
    "crash_recovery",
    "reconciliation",
    "allowed_successors",
}


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


def _transitions(contract: dict[str, object]) -> list[dict[str, object]]:
    return [_map(item) for item in _list(contract["transitions"])]


def _subject_purposes(transition: dict[str, object]) -> list[str]:
    key = (
        "subject_intent_purposes" if "subject_intent_purposes" in transition else "intent_purposes"
    )
    return _strings(transition[key])


def _allows(
    contract: dict[str, object], source: str, target: str, actor: str, purpose: str
) -> bool:
    return any(
        item["source"] == source
        and item["target"] == target
        and actor in _strings(item["permitted_request_actors"])
        and purpose in _subject_purposes(item)
        for item in _transitions(contract)
    )


def test_action_enums_and_graph_are_exact(contract: dict[str, object]) -> None:
    assert _strings(contract["states"]) == STATES
    assert _strings(contract["purposes"]) == PURPOSES
    assert contract["initial_state"] == "proposed"
    assert set(_strings(contract["terminal_states"])) == TERMINAL
    successors = _map(contract["successors_by_state"])
    edges = {(str(item["source"]), str(item["target"])) for item in _transitions(contract)}
    assert edges == {
        (source, target) for source, targets in successors.items() for target in _strings(targets)
    }


def test_each_action_transition_has_typed_complete_contract(contract: dict[str, object]) -> None:
    actors = set(_strings(contract["actors"]))
    successors = _map(contract["successors_by_state"])
    transition_ids: set[str] = set()
    rule_ids: set[str] = set()
    operation_ids: set[str] = set()
    for transition in _transitions(contract):
        assert set(transition) >= COMMON_FIELDS
        assert ("intent_purposes" in transition) != ("subject_intent_purposes" in transition)
        transition_id = str(transition["transition_id"])
        assert transition_id not in transition_ids
        transition_ids.add(transition_id)
        assert transition["contract_version"] == "1.0.0"
        assert transition["source"] in STATES and transition["target"] in STATES
        assert _subject_purposes(transition) == PURPOSES
        assert set(_strings(transition["permitted_request_actors"])) <= actors
        assert _strings(transition["authority"]) and _strings(transition["policy"])
        assert _strings(transition["evidence"])
        assert _strings(transition["allowed_successors"]) == _strings(
            successors[str(transition["target"])]
        )
        for field in (
            "approval",
            "quiescence",
            "deadline",
            "timeout",
            "cancellation",
            "crash_recovery",
            "reconciliation",
        ):
            rule = _map(transition[field])
            assert str(rule["rule_id"]).startswith(f"{transition_id}.")
            assert rule["rule_id"] not in rule_ids
            rule_ids.add(str(rule["rule_id"]))
            if field == "quiescence":
                assert isinstance(rule["required"], bool)
                assert rule["predicate_ref"] is None or isinstance(rule["predicate_ref"], str)
            else:
                assert isinstance(rule["operator"], str) and rule["operator"]
        crash = _map(transition["crash_recovery"])
        assert crash["before_commit"] == "rollback"
        assert crash["after_commit"] == "recover_from_durable_state_and_audit"
        guards = _map(transition["guards"])
        assert guards["operator"] == "all_true" and guards["unknown_rule"] == "deny_and_audit"
        assert all(_map(item)["unknown"] == "false" for item in _list(guards["rules"]))
        effects = _map(transition["atomic_side_effects"])
        assert effects["operator"] == "all_or_none"
        for category in ("protected_state", "claims", "audit"):
            for operation in [_map(item) for item in _list(effects[category])]:
                assert operation["transaction"] == "same_as_state_and_audit"
                assert operation["operation_id"] not in operation_ids
                operation_ids.add(str(operation["operation_id"]))
        assert _list(effects["protected_state"]) and _list(effects["audit"])


def test_declared_action_edges_are_allowed_and_undeclared_edges_denied(
    contract: dict[str, object],
) -> None:
    declared = {(str(item["source"]), str(item["target"])) for item in _transitions(contract)}
    for transition in _transitions(contract):
        assert _allows(
            contract,
            str(transition["source"]),
            str(transition["target"]),
            _strings(transition["permitted_request_actors"])[0],
            _subject_purposes(transition)[0],
        )
    for source, target in itertools.product(STATES, repeat=2):
        if (source, target) not in declared:
            assert not _allows(
                contract, source, target, _strings(contract["actors"])[0], PURPOSES[0]
            )


def test_unknown_action_state_actor_and_purpose_fail_closed(contract: dict[str, object]) -> None:
    deny = _map(contract["default_deny"])
    assert deny["unknown_state"] == "deny_and_audit"
    assert deny["unknown_actor"] == "deny_and_audit"
    assert deny["unknown_purpose"] == "deny_and_audit"
    assert deny["undeclared_transition"] == "deny_and_audit"
    assert not _allows(contract, "unknown", "preparing", "planner", "execution")
    assert not _allows(contract, "proposed", "preparing", "unknown", "execution")
    assert not _allows(contract, "proposed", "preparing", "planner", "unknown")


def test_terminal_actions_have_no_outgoing_transition(contract: dict[str, object]) -> None:
    assert not any(item["source"] in TERMINAL for item in _transitions(contract))


def test_creation_requires_complete_scope_and_immutable_purpose(
    contract: dict[str, object],
) -> None:
    creation = _map(contract["creation"])
    assert {"tenant_id", "area_id", "project_id", "session_id", "goal_id", "purpose"} <= set(
        _strings(creation["required_fields"])
    )
    assert creation["writer_component"] == "action_transition_gate"
    assert (
        contract["purpose_rule"] == "purpose is immutable from proposal through the terminal state"
    )


def test_all_subject_purposes_resolve_all_indeterminate_outcomes_without_mutation(
    contract: dict[str, object],
) -> None:
    resolution = _map(contract["indeterminate_resolution"])
    assert resolution["subject_purpose_immutable"] is True
    assert _strings(resolution["subject_purposes"]) == PURPOSES
    assert resolution["resolution_request_purpose"] == "reconciliation"
    outcomes = _map(resolution["allowed_outcomes"])
    assert outcomes == {
        "effect_confirmed": "settling",
        "no_effect_confirmed": "aborted",
        "effect_compensated": "aborted",
    }
    by_id = {str(item["transition_id"]): item for item in _transitions(contract)}
    for purpose, outcome in itertools.product(PURPOSES, outcomes):
        transition = by_id[f"action.resolve_{outcome}"]
        assert purpose in _strings(transition["subject_intent_purposes"])
        assert _strings(transition["resolution_request_purposes"]) == ["reconciliation"]
        assert transition["source"] == "indeterminate"
        assert transition["target"] == outcomes[outcome]
    assert {"automatic retry", "claim release before resolution", "purpose mutation"} <= set(
        _strings(resolution["forbidden"])
    )


def test_effect_compensation_requires_a_separate_compensation_intent(
    contract: dict[str, object],
) -> None:
    transition = next(
        item
        for item in _transitions(contract)
        if item["transition_id"] == "action.resolve_effect_compensated"
    )
    assert transition["required_related_intent_purpose"] == "compensation"
    assert _strings(transition["permitted_request_actors"]) == ["human_incident_resolver"]
    assert "compensation_intent" in _strings(transition["evidence"])
    guards = " ".join(
        str(_map(item)["description"]) for item in _list(_map(transition["guards"])["rules"])
    )
    assert "separate purpose=compensation intent" in guards
    assert "no adapter is called by this transition" in guards
