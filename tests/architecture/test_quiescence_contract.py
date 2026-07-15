import itertools
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[2]
CONTRACT_DIR = ROOT / "docs" / "architecture" / "contracts"


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


def _load(name: str) -> dict[str, object]:
    with (CONTRACT_DIR / name).open(encoding="utf-8") as source:
        return _map(json.load(source))


@pytest.fixture(scope="module")
def quiescence() -> dict[str, object]:
    return _load("quiescence.json")


@pytest.fixture(scope="module")
def ledger() -> dict[str, object]:
    return _load("ledger-invariants.json")


def _clauses(contract: dict[str, object]) -> list[dict[str, object]]:
    return [_map(item) for item in _list(_map(contract["predicate"])["required_clauses"])]


def _candidate_blocks(status: str, persistence_status: str, transition_status: str) -> bool:
    return (status, persistence_status, transition_status) != ("inactive", "complete", "committed")


def test_predicate_scope_and_goal_targets_are_exact(quiescence: dict[str, object]) -> None:
    predicate = _map(quiescence["predicate"])
    assert predicate["id"] == "goal_is_quiescent"
    assert _strings(predicate["scope"]) == [
        "tenant_id",
        "area_id",
        "project_id",
        "session_id",
        "goal_id",
    ]
    assert _strings(quiescence["required_for_goal_targets"]) == [
        "suspended",
        "achieved",
        "failed",
        "discarded",
    ]
    assert [str(item["id"]) for item in _clauses(quiescence)] == [
        f"Q-{number:03d}" for number in range(1, 10)
    ]


def test_action_states_partition_terminal_and_open(quiescence: dict[str, object]) -> None:
    action = _clauses(quiescence)[0]
    terminal = set(_strings(action["terminal_states"]))
    open_states = set(_strings(action["open_states"]))
    assert terminal == {"completed", "aborted"}
    assert "indeterminate" in open_states
    assert terminal.isdisjoint(open_states)
    assert terminal | open_states == {
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
    }


def test_every_declared_quiescence_blocker_matches_ledger_registry(
    quiescence: dict[str, object], ledger: dict[str, object]
) -> None:
    registries = _map(ledger["status_registries"])
    for clause in _clauses(quiescence)[1:]:
        kind = str(clause["entity_kind"])
        assert kind in registries
        assert set(_strings(clause["blocking_statuses"])) == set(
            _strings(_map(registries[kind])["blocking"])
        )
        for status in _strings(clause["blocking_statuses"]):
            assert status in _strings(clause["blocking_statuses"])


def test_unknown_status_and_failures_make_quiescence_false(quiescence: dict[str, object]) -> None:
    evaluation = _map(quiescence["evaluation"])
    assert evaluation["unknown_or_unavailable_clause"] == "false"
    assert evaluation["scope_mismatch"] == "deny_and_audit"
    assert evaluation["audit_failure"] == "rollback_and_deny"
    assert evaluation["cache_use"] == "prohibited"
    assert evaluation["model_or_tool_inference"] == "prohibited"
    deny = _map(quiescence["default_deny"])
    assert deny == {
        "unknown_state": "deny",
        "unknown_claim_status": "treat_as_open",
        "unknown_effect_status": "treat_as_possible",
        "missing_evidence": "false",
        "read_or_audit_failure": "false",
    }


def test_inactive_candidate_is_nonblocking_only_for_exact_conditions(
    quiescence: dict[str, object],
) -> None:
    rule = _map(quiescence["inactive_memory_candidate_rule"])
    assert rule["operator"] == "does_not_block_when"
    assert rule["entity_kind"] == "memory_candidate"
    conditions = _map(rule["conditions"])
    assert conditions == {
        "status": "inactive",
        "persistence_status": "complete",
        "transition_status": "committed",
    }
    values = {
        "status": ["inactive", "active", "unknown"],
        "persistence": ["complete", "partial", "unknown"],
        "transition": ["committed", "prepared", "unknown"],
    }
    for status, persistence, transition in itertools.product(*values.values()):
        assert _candidate_blocks(status, persistence, transition) is (
            (status, persistence, transition) != ("inactive", "complete", "committed")
        )


def test_indeterminate_and_cancellation_remain_blocking(quiescence: dict[str, object]) -> None:
    assert "makes quiescence false" in str(quiescence["indeterminate_rule"])
    assert "keeps its associated budget and resource claims" in str(
        quiescence["indeterminate_rule"]
    )
    assert "does not establish quiescence" in str(quiescence["cancellation_rule"])
