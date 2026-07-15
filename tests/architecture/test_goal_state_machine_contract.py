import itertools
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[2]
PATH = ROOT / "docs" / "architecture" / "contracts" / "goal-state-machine.json"
STATES = [
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
TERMINAL = {"achieved", "failed", "discarded"}
PURPOSES = {"execution", "verification", "cancellation", "reconciliation", "compensation"}
TRANSITION_FIELDS = {
    "transition_id",
    "source",
    "target",
    "permitted_request_actors",
    "related_intent_purposes",
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


def _allows(
    contract: dict[str, object], source: str, target: str, actor: str, purpose: str | None
) -> bool:
    for transition in _transitions(contract):
        purposes = _strings(transition["related_intent_purposes"])
        if (
            transition["source"] == source
            and transition["target"] == target
            and actor in _strings(transition["permitted_request_actors"])
            and ((purpose in purposes) if purposes else purpose is None)
        ):
            return True
    return False


def test_goal_enums_and_graph_are_exact(contract: dict[str, object]) -> None:
    assert _strings(contract["states"]) == STATES
    assert contract["initial_state"] == "proposed"
    assert set(_strings(contract["terminal_states"])) == TERMINAL
    successors = _map(contract["successors_by_state"])
    assert set(successors) == set(STATES)
    edges = {(str(item["source"]), str(item["target"])) for item in _transitions(contract)}
    assert edges == {
        (source, target) for source, targets in successors.items() for target in _strings(targets)
    }


def test_each_goal_transition_has_typed_complete_contract(contract: dict[str, object]) -> None:
    actors = set(_strings(contract["actors"]))
    transition_ids: set[str] = set()
    rule_ids: set[str] = set()
    operation_ids: set[str] = set()
    successors = _map(contract["successors_by_state"])
    for transition in _transitions(contract):
        assert set(transition) >= TRANSITION_FIELDS
        transition_id = str(transition["transition_id"])
        assert transition_id not in transition_ids
        transition_ids.add(transition_id)
        assert transition["source"] in STATES and transition["target"] in STATES
        assert set(_strings(transition["permitted_request_actors"])) <= actors
        assert _strings(transition["permitted_request_actors"])
        assert set(_strings(transition["related_intent_purposes"])) <= PURPOSES
        assert _strings(transition["authority"])
        assert _strings(transition["policy"])
        assert _strings(transition["evidence"])
        assert set(_strings(transition["allowed_successors"])) <= set(
            _strings(successors[str(transition["target"])])
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
            assert isinstance(rule["rule_id"], str) and str(rule["rule_id"]).startswith(
                f"{transition_id}."
            )
            assert rule["rule_id"] not in rule_ids
            rule_ids.add(str(rule["rule_id"]))
            if field == "quiescence":
                assert isinstance(rule["required"], bool)
                assert rule["predicate_ref"] is None or isinstance(rule["predicate_ref"], str)
            else:
                assert isinstance(rule["operator"], str) and rule["operator"]
            assert str(rule["unknown"]).startswith(("deny", "false"))
        crash = _map(transition["crash_recovery"])
        assert crash["before_commit"] == "rollback"
        assert crash["after_commit"] == "recover_from_durable_state_and_audit"
        guards = _map(transition["guards"])
        assert guards["operator"] == "all_true"
        assert guards["unknown_rule"] == "deny_and_audit"
        for guard in [_map(item) for item in _list(guards["rules"])]:
            assert guard["unknown"] == "false"
            assert guard["rule_id"] not in rule_ids
            rule_ids.add(str(guard["rule_id"]))
        effects = _map(transition["atomic_side_effects"])
        assert effects["operator"] == "all_or_none"
        assert effects["audit_atomic"] is True
        for operation in [_map(item) for item in _list(effects["operations"])]:
            assert operation["transaction"] == "same_as_state_and_audit"
            assert operation["operation_id"] not in operation_ids
            operation_ids.add(str(operation["operation_id"]))
        assert isinstance(transition["audit_event"], str) and transition["audit_event"]


def test_declared_goal_edges_are_allowed_and_all_undeclared_edges_denied(
    contract: dict[str, object],
) -> None:
    declared = {(str(item["source"]), str(item["target"])) for item in _transitions(contract)}
    for transition in _transitions(contract):
        purposes = _strings(transition["related_intent_purposes"])
        assert _allows(
            contract,
            str(transition["source"]),
            str(transition["target"]),
            _strings(transition["permitted_request_actors"])[0],
            purposes[0] if purposes else None,
        )
    for source, target in itertools.product(STATES, repeat=2):
        if (source, target) not in declared:
            assert not _allows(contract, source, target, _strings(contract["actors"])[0], None)


def test_unknown_goal_state_actor_and_purpose_fail_closed(contract: dict[str, object]) -> None:
    deny = _map(contract["default_deny"])
    assert deny["unknown_state"] == "deny_and_audit"
    assert deny["unknown_actor"] == "deny_and_audit"
    assert deny["unknown_purpose"] == "deny_and_audit"
    assert deny["undeclared_transition"] == "deny_and_audit"
    assert not _allows(contract, "unknown", "active", "goal_requester", None)
    assert not _allows(contract, "proposed", "active", "unknown", None)
    assert not _allows(contract, "active", "blocked", "guardian", "unknown")


def test_terminal_goal_states_have_no_outgoing_transition(contract: dict[str, object]) -> None:
    assert not any(item["source"] in TERMINAL for item in _transitions(contract))


def test_achieved_requires_independent_evidence_and_quiescence(
    contract: dict[str, object],
) -> None:
    achieved = next(
        item for item in _transitions(contract) if item["transition_id"] == "goal.achieve"
    )
    assert achieved["source"] == "verifying" and achieved["target"] == "achieved"
    assert _strings(achieved["permitted_request_actors"]) == ["independent_verifier"]
    assert _strings(achieved["related_intent_purposes"]) == ["verification"]
    assert {"goal.verify_completion", "evidence.verify"} <= set(_strings(achieved["authority"]))
    assert {
        "independent_verification_decision_achieved",
        "criterion_results",
        "complete_evidence_package",
        "quiescence_evidence",
    } <= set(_strings(achieved["evidence"]))
    quiescence = _map(achieved["quiescence"])
    assert quiescence["required"] is True
    assert quiescence["predicate_ref"] == "neural-brain.quiescence#goal_is_quiescent"
    assert quiescence["unknown"] == "false"


def test_blocked_from_state_and_termination_disposition_are_closed(
    contract: dict[str, object],
) -> None:
    data = _map(contract["state_data"])
    blocked = _map(data["blocked_from_state"])
    assert _strings(blocked["allowed_values"]) == ["proposed", "active", "verifying", "terminating"]
    assert "resuming to the same recorded state" in str(blocked["rule"])
    disposition = _map(data["termination_disposition"])
    assert _strings(disposition["allowed_values"]) == ["failed", "discarded"]
    assert "immutable thereafter" in str(disposition["rule"])
    assert "terminal target must equal the disposition" in str(disposition["rule"])
    for transition in _transitions(contract):
        descriptions = " ".join(
            str(_map(item)["description"])
            for item in _list(_map(transition["atomic_side_effects"])["operations"])
        )
        if transition["target"] == "blocked":
            assert "blocked_from_state" in descriptions
        if transition["source"] == "blocked" and str(transition["transition_id"]).startswith(
            "goal.unblock"
        ):
            assert "clear blocked_from_state" in descriptions
    for transition_id, expected in (("goal.fail", "failed"), ("goal.discard", "discarded")):
        transition = next(
            item for item in _transitions(contract) if item["transition_id"] == transition_id
        )
        guards = " ".join(
            str(_map(item)["description"]) for item in _list(_map(transition["guards"])["rules"])
        )
        assert f"termination_disposition equals {expected}" in guards
