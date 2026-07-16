import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
PATH = ROOT / "docs" / "architecture" / "contracts" / "memory-lifecycle.json"


def _map(value: object) -> dict[str, object]:
    assert isinstance(value, dict)
    return value


def _contract() -> dict[str, object]:
    return _map(json.loads(PATH.read_text(encoding="utf-8")))


def test_memory_operations_have_declared_stage_result_and_requirements() -> None:
    operations = _contract()["operations"]
    assert isinstance(operations, list)
    indexed = {str(item["id"]): item for item in operations if isinstance(item, dict)}
    assert set(indexed) == {
        "memory.observe",
        "memory.checkpoint",
        "memory.propose_candidate",
        "memory.dreaming_dry_run",
        "memory.persist_episode_or_claim",
        "memory.retrieve",
        "memory.promote_candidate",
        "memory.activate_dreaming_successor",
        "memory.quarantine_or_rollback",
        "memory.delete_or_anonymize",
    }
    assert indexed["memory.observe"]["minimum_memory_stage"] == "ms_1"
    assert indexed["memory.retrieve"]["minimum_memory_stage"] == "ms_2"
    assert indexed["memory.delete_or_anonymize"]["minimum_memory_stage"] == "ms_2"
    assert indexed["memory.promote_candidate"]["minimum_memory_stage"] == "ms_3"
    for operation in indexed.values():
        assert operation["result"]
        assert operation["requires"]


def test_memory_lifecycle_is_gate_owned_and_fail_closed() -> None:
    rules = _contract()["transition_rules"]
    assert isinstance(rules, list)
    text = " ".join(str(rule) for rule in rules)
    assert "Only the Memory Transition Gate" in text
    assert "denied and audited" in text
    assert "model output cannot directly" in text.lower()


def test_candidate_promotion_preserves_independence_and_provenance() -> None:
    rules = _contract()["transition_rules"]
    assert isinstance(rules, list)
    text = " ".join(str(rule) for rule in rules)
    assert "excluded from normal retrieval" in text
    assert "new immutable memory version" in text
    assert "cannot be approved solely by its producer" in text


def test_cross_area_memory_is_denied_by_default() -> None:
    cross_area = _map(_contract()["cross_area"])
    assert cross_area["minimum_memory_stage"] == "ms_4"
    assert cross_area["raw_memory_access"] == "denied"
    assert cross_area["automatic_copy"] == "denied"
    assert cross_area["generalization"] == (
        "candidate_only_until_separately_authorized_and_promoted"
    )


def test_reconciliation_blocks_readiness_and_blind_retry() -> None:
    reconciliation = _map(_contract()["reconciliation"])
    assert reconciliation["ready_default"] is False
    assert "before ready=true" in str(reconciliation["startup_or_restore"])
    assert "Do not retry" in str(reconciliation["unknown_commit_outcome"])
