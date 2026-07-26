import ast
import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
CATALOG_PATH = ROOT / "docs" / "traceability" / "requirement-to-test-catalog-v1.json"
CONTRACTS = ROOT / "docs" / "architecture" / "contracts"

REQUIRED_MAPPING_FIELDS = {
    "mapping_id",
    "source",
    "requirement_ids",
    "requirement",
    "test_ids",
    "expected_state",
    "ledger_effect",
    "audit_event",
    "failure_code",
    "evidence_state",
}


def _load_catalog() -> dict[str, object]:
    loaded: object = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _ids(contract_name: str, key: str) -> set[str]:
    contract: object = json.loads((CONTRACTS / contract_name).read_text(encoding="utf-8"))
    assert isinstance(contract, dict)
    values = contract[key]
    assert isinstance(values, list)
    return {str(item["id"]) for item in values if isinstance(item, dict)}


def _test_exists(test_id: str) -> bool:
    path_text, separator, function_name = test_id.partition("::")
    if not separator or not function_name:
        return False
    path = ROOT / path_text
    if not path.is_file():
        return False
    module = ast.parse(path.read_text(encoding="utf-8"))
    return any(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name
        for node in module.body
    )


def test_requirement_catalog_is_bounded_versioned_and_fail_closed() -> None:
    catalog = _load_catalog()
    assert catalog["document_type"] == "neural_brain_requirement_to_test_catalog"
    assert catalog["catalog_version"] == "1.0.0"
    assert catalog["status"] == "bounded_current_contract_traceability"
    assert catalog["authority"] == ["ADR-018", "ADR-019", "architecture-directive-v4.0"]

    scope = catalog["scope"]
    assert isinstance(scope, dict)
    excluded = scope["excluded"]
    assert isinstance(excluded, list)
    assert any("historical" in item for item in excluded if isinstance(item, str))
    assert scope["current_maturity"] == "memory_core_foundation"


def test_requirement_catalog_has_complete_scoped_release_stop_and_transition_coverage() -> None:
    catalog = _load_catalog()
    mappings = catalog["mappings"]
    assert isinstance(mappings, list)
    assert all(isinstance(item, dict) for item in mappings)
    typed_mappings = [item for item in mappings if isinstance(item, dict)]

    by_mapping_id = {str(item["mapping_id"]): item for item in typed_mappings}
    assert set(by_mapping_id) == {
        "SYS-CP-001",
        "NBRS",
        "MRS",
        "MLI",
        "MLT",
        "ADR019-IDENTITY",
        "TARGET-NB1-CYCLE",
        "TARGET-GOAL-GATE-PREREQUISITE",
        "TARGET-EVALUATION",
        "TARGET-RECOGNITION",
    }
    assert set(by_mapping_id["NBRS"]["requirement_ids"]) == _ids("release-stops.json", "criteria")
    assert set(by_mapping_id["MRS"]["requirement_ids"]) == _ids(
        "memory-release-stops.json", "criteria"
    )
    assert set(by_mapping_id["MLI"]["requirement_ids"]) == _ids(
        "ledger-invariants.json", "invariants"
    )
    assert by_mapping_id["MLT"]["requirement_ids"] == [
        f"MLT-{number:03d}" for number in range(1, 11)
    ]
    assert len(by_mapping_id["MLT"]["requirement_ids"]) == len(
        json.loads((CONTRACTS / "memory-lifecycle.json").read_text(encoding="utf-8"))[
            "transition_rules"
        ]
    )


def test_requirement_catalog_has_evidence_fields_and_real_test_ids() -> None:
    catalog = _load_catalog()
    mappings = catalog["mappings"]
    assert isinstance(mappings, list)
    sources: list[str] = []
    has_explicit_target_na = False
    for mapping in mappings:
        assert isinstance(mapping, dict)
        assert set(mapping) >= REQUIRED_MAPPING_FIELDS
        assert mapping["requirement_ids"]
        assert mapping["test_ids"]
        assert all(_test_exists(test_id) for test_id in mapping["test_ids"])
        assert all(
            isinstance(mapping[field], str) and mapping[field]
            for field in REQUIRED_MAPPING_FIELDS
            - {"mapping_id", "source", "requirement_ids", "test_ids"}
        )
        source = mapping["source"]
        assert isinstance(source, str)
        sources.append(source)
        if mapping["evidence_state"] == "N/A_target_not_implemented":
            assert mapping["expected_state"].startswith("N/A")
            assert mapping["ledger_effect"].startswith("N/A")
            assert mapping["audit_event"].startswith("N/A")
            has_explicit_target_na = True

    assert has_explicit_target_na
    assert not any(
        "architecture-directive-v1" in source
        or "architecture-directive-v2" in source
        or "architecture-directive-v3" in source
        for source in sources
    )
