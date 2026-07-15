import json
from pathlib import Path

from hypothesis import given
from hypothesis import strategies as st

ROOT = Path(__file__).parents[2]
CONTRACT_DIR = ROOT / "docs" / "architecture" / "contracts"


def _load(name: str) -> dict[str, object]:
    with (CONTRACT_DIR / name).open(encoding="utf-8") as source:
        value: object = json.load(source)
    assert isinstance(value, dict)
    return value


def _list(value: object) -> list[object]:
    assert isinstance(value, list)
    return value


def _strings(value: object) -> list[str]:
    values = _list(value)
    assert all(isinstance(item, str) for item in values)
    return [item for item in values if isinstance(item, str)]


GOAL = _load("goal-state-machine.json")
ACTION = _load("action-intent-state-machine.json")
GOAL_STATES = tuple(_strings(GOAL["states"]))
ACTION_STATES = tuple(_strings(ACTION["states"]))
PURPOSES = tuple(_strings(ACTION["purposes"]))
GOAL_EDGES = {
    (str(item["source"]), str(item["target"]))
    for raw in _list(GOAL["transitions"])
    for item in [raw if isinstance(raw, dict) else {}]
}
ACTION_EDGES = {
    (str(item["source"]), str(item["target"]))
    for raw in _list(ACTION["transitions"])
    for item in [raw if isinstance(raw, dict) else {}]
}


@given(st.sampled_from(GOAL_STATES), st.sampled_from(GOAL_STATES))
def test_goal_contract_interpreter_matches_declared_graph(source: str, target: str) -> None:
    successors = GOAL["successors_by_state"]
    assert isinstance(successors, dict)
    assert ((source, target) in GOAL_EDGES) is (target in _strings(successors[source]))


@given(st.sampled_from(ACTION_STATES), st.sampled_from(ACTION_STATES))
def test_action_contract_interpreter_matches_declared_graph(source: str, target: str) -> None:
    successors = ACTION["successors_by_state"]
    assert isinstance(successors, dict)
    assert ((source, target) in ACTION_EDGES) is (target in _strings(successors[source]))


@given(
    st.text(min_size=1).filter(lambda value: value not in GOAL_STATES),
    st.sampled_from(GOAL_STATES),
)
def test_unknown_goal_state_never_forms_declared_edge(unknown: str, known: str) -> None:
    assert (unknown, known) not in GOAL_EDGES
    assert (known, unknown) not in GOAL_EDGES


@given(
    st.text(min_size=1).filter(lambda value: value not in ACTION_STATES),
    st.sampled_from(ACTION_STATES),
)
def test_unknown_action_state_never_forms_declared_edge(unknown: str, known: str) -> None:
    assert (unknown, known) not in ACTION_EDGES
    assert (known, unknown) not in ACTION_EDGES


@given(
    st.sampled_from(PURPOSES),
    st.sampled_from(("effect_confirmed", "no_effect_confirmed", "effect_compensated")),
)
def test_indeterminate_resolution_preserves_subject_purpose(
    subject_purpose: str, outcome: str
) -> None:
    resolution = ACTION["indeterminate_resolution"]
    assert isinstance(resolution, dict)
    assert resolution["subject_purpose_immutable"] is True
    assert subject_purpose in _strings(resolution["subject_purposes"])
    outcomes = resolution["allowed_outcomes"]
    assert isinstance(outcomes, dict)
    assert outcome in outcomes
    assert resolution["resolution_request_purpose"] == "reconciliation"
