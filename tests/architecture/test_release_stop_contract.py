import json
from pathlib import Path
from typing import Any

REPOSITORY_ROOT = Path(__file__).parents[2]
CONTRACT_PATH = REPOSITORY_ROOT / "docs" / "architecture" / "contracts" / "release-stops.json"
DIRECTIVE_PATH = REPOSITORY_ROOT / "docs" / "architecture" / "architecture-directive-v1.1.md"


def _load_contract() -> dict[str, Any]:
    loaded: object = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def test_release_stop_contract_contains_exact_continuous_set() -> None:
    contract = _load_contract()
    criteria = contract["criteria"]
    assert [criterion["id"] for criterion in criteria] == [
        f"RS-{number:02d}" for number in range(1, 16)
    ]
    assert len({criterion["condition"] for criterion in criteria}) == 15
    assert contract["default_behavior"] == "stop_implementation_and_release"
    assert contract["waiver"] == "prohibited"


def test_release_stop_contract_matches_directive() -> None:
    directive = " ".join(DIRECTIVE_PATH.read_text(encoding="utf-8").split())
    for criterion in _load_contract()["criteria"]:
        condition = criterion["condition"]
        if condition == "Achieved is reachable without independent evidence.":
            condition = "`Achieved` is reachable without independent evidence."
        if condition == "Startup or restore can report ready=true before reconciliation.":
            condition = "Startup or restore can report `ready=true` before reconciliation."
        assert condition in directive


def test_unknown_release_stop_evaluation_fails_closed() -> None:
    rules = _load_contract()["rules"]
    assert "Unknown evaluation state is treated as a triggered release stop." in rules
