import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
PATH = ROOT / "docs" / "architecture" / "contracts" / "release-stops.json"


def _contract() -> dict[str, object]:
    loaded: object = json.loads(PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def test_memory_release_stops_are_closed_and_non_waivable() -> None:
    contract = _contract()
    criteria = contract["criteria"]
    assert isinstance(criteria, list)
    assert [item["id"] for item in criteria if isinstance(item, dict)] == [
        f"MRS-{number:02d}" for number in range(1, 19)
    ]
    assert contract["default_behavior"] == "stop_implementation_and_release"
    assert contract["waiver"] == "prohibited"


def test_release_stops_cover_memory_safety_boundaries() -> None:
    criteria = _contract()["criteria"]
    assert isinstance(criteria, list)
    text = " ".join(str(item["condition"]) for item in criteria if isinstance(item, dict)).lower()
    for expected in (
        "goals, plans, tools",
        "memory transition gate",
        "cross-tenant or cross-area",
        "provenance",
        "freshness",
        "candidate promotion",
        "deletion or anonymization",
        "ready=true",
        "unknown commit outcome",
        "tenant scope",
        "backup or restore",
        "delivery-stage gate",
    ):
        assert expected in text


def test_unknown_release_stop_evaluation_fails_closed() -> None:
    rules = _contract()["rules"]
    assert isinstance(rules, list)
    assert "Unknown evaluation state is treated as a triggered release stop." in rules
