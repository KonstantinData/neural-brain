import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
CONTRACTS = ROOT / "docs" / "architecture" / "contracts"


def _load(name: str) -> dict[str, object]:
    loaded: object = json.loads((CONTRACTS / name).read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _maps(value: object) -> list[dict[str, object]]:
    assert isinstance(value, list)
    assert all(isinstance(item, dict) for item in value)
    return [item for item in value if isinstance(item, dict)]


def test_contract_inventory_is_memory_only() -> None:
    assert {path.name for path in CONTRACTS.glob("*.json")} == {
        "envelopes.json",
        "dreaming.json",
        "inference-provider.json",
        "ledger-invariants.json",
        "memory-lifecycle.json",
        "release-stops.json",
        "stage-capabilities.json",
        "system-boundary.json",
        "scope-catalog.json",
    }


def test_system_boundary_excludes_agent_runtime_capabilities() -> None:
    contract = _load("system-boundary.json")
    assert contract["system_kind"] == "memory_system"
    excluded = set(
        contract["non_capabilities"] if isinstance(contract["non_capabilities"], list) else []
    )
    assert {
        "goal ownership or goal lifecycle management",
        "planning",
        "tool or adapter execution",
        "external side-effect execution",
        "action-intent lifecycle management",
        "autonomous task orchestration",
    } <= excluded
    assert contract["protected_state"] == {
        "sole_writer": "Memory Transition Gate",
        "direct_table_mutation": "forbidden",
        "model_or_consumer_write": "forbidden",
        "atomicity": (
            "A protected memory transition and its audit record commit in one PostgreSQL "
            "transaction or both roll back."
        ),
    }


def test_consumer_correlations_are_non_authoritative() -> None:
    contract = _load("system-boundary.json")
    consumer = contract["consumer_boundary"]
    assert isinstance(consumer, dict)
    correlations = consumer["consumer_correlations"]
    assert isinstance(correlations, dict)
    assert correlations["trust"] == "untrusted_metadata"
    assert correlations["authority"] == "none"


def test_tenant_root_conflict_is_resolved_by_typed_catalog_contract() -> None:
    boundary = _load("system-boundary.json")["tenant_root_boundary"]
    assert isinstance(boundary, dict)
    assert boundary["status"] == "resolved_by_ADR_016"
    assert "persisted singleton" in str(boundary["rule"])
    assert "sentinel Area" in boundary["prohibitions"]


def test_stage_capabilities_are_cumulative_memory_capabilities() -> None:
    contract = _load("stage-capabilities.json")
    semantics = contract["semantics"]
    assert isinstance(semantics, dict)
    stages = semantics["stage_order"]
    assert stages == ["stage_1", "stage_2", "stage_3", "stage_4"]
    assert semantics["domain"] == "memory_only"
    assert isinstance(stages, list)
    for capability in _maps(contract["capabilities"]):
        minimum = capability["minimum_stage"]
        assert isinstance(minimum, str)
        availability = capability["availability"]
        assert isinstance(availability, dict)
        minimum_index = stages.index(minimum)
        assert all(availability[stage] == "denied" for stage in stages[:minimum_index])
        assert all(availability[stage] == "allowed" for stage in stages[minimum_index:])


def test_later_stage_operations_are_denied_before_memory_processing() -> None:
    contract = _load("stage-capabilities.json")
    enforcement = contract["request_enforcement"]
    assert isinstance(enforcement, dict)
    known = enforcement["known_operation"]
    assert isinstance(known, dict)
    assert set(known["deny_before"] if isinstance(known["deny_before"], list) else []) >= {
        "content_processing",
        "inference_invocation",
        "Memory Transition Gate execution",
        "protected memory mutation",
        "retrieval result emission",
    }
    unknown = enforcement["unknown_operation"]
    assert isinstance(unknown, dict)
    assert unknown["result"] == "denied"
