import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
PATH = ROOT / "docs" / "architecture" / "contracts" / "release-stops.json"


def _contract() -> dict[str, object]:
    loaded: object = json.loads(PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _named_contract(name: str) -> dict[str, object]:
    loaded: object = json.loads((PATH.parent / name).read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def test_complete_system_release_stops_are_closed_and_non_waivable() -> None:
    contract = _contract()
    criteria = contract["criteria"]
    assert isinstance(criteria, list)
    assert [item["id"] for item in criteria if isinstance(item, dict)] == [
        f"NBRS-{number:02d}" for number in range(1, 17)
    ]
    assert contract["default_behavior"] == "stop_implementation_or_release_of_affected_capability"
    assert contract["waiver"] == "security_floor_prohibitions_are_non_waivable"


def test_release_stops_cover_cognition_learning_action_and_safety() -> None:
    criteria = _contract()["criteria"]
    assert isinstance(criteria, list)
    text = " ".join(str(item["condition"]) for item in criteria if isinstance(item, dict)).lower()
    for expected in (
        "goal, action, memory, or active-model state",
        "identity, scope, authority, policy, approval",
        "directly execute an external action",
        "committed intent",
        "indeterminate effect",
        "goal success",
        "modify its own productive model",
        "held-out retention and transfer evidence",
        "component ablation",
        "unknown recognition, evaluation, privacy, authority, or safety gate",
        "direct observation or current fact",
        "tenant or area boundary",
        "shutdown, credential revocation",
        "later-stage capability",
        "product claims exceed",
    ):
        assert expected in text


def test_unknown_or_failed_evaluation_fails_closed() -> None:
    rules = _contract()["rules"]
    assert isinstance(rules, list)
    assert "Unknown evaluation state triggers the release stop." in rules
    assert "Capability gain cannot compensate for a failed safety or control gate." in rules
    assert "Approval does not create missing authority." in rules


def test_memory_core_release_stops_remain_binding_under_adr_018() -> None:
    contract = _named_contract("memory-release-stops.json")
    assert contract["status"] == "normative_subsystem"
    assert contract["namespace"] == "Memory Core"
    assert contract["default_behavior"] == (
        "stop_implementation_or_release_of_affected_memory_capability"
    )
    criteria = contract["criteria"]
    assert isinstance(criteria, list)
    indexed = {item["id"]: item["condition"] for item in criteria if isinstance(item, dict)}
    assert set(indexed) == {f"MRS-{number:02d}" for number in range(1, 23)}
    required_terms = {
        "MRS-06": ("classification", "purpose", "retention", "provenance"),
        "MRS-08": ("freshness", "current fact"),
        "MRS-10": ("producer", "promotion"),
        "MRS-11": ("deletion", "derivations", "embeddings"),
        "MRS-12": ("restore", "reconciliation"),
        "MRS-15": ("secrets", "credentials"),
        "MRS-19": ("dreaming", "active session", "lease"),
        "MRS-20": ("snapshot", "cross-area"),
        "MRS-22": ("independent validation", "rollback target"),
    }
    for stop_id, terms in required_terms.items():
        condition = str(indexed[stop_id]).lower()
        assert all(term in condition for term in terms)

    rules = contract["rules"]
    assert isinstance(rules, list)
    assert "Unknown evaluation state triggers the release stop." in rules
    assert contract["waiver"] == "security_floor_prohibitions_are_non_waivable"
