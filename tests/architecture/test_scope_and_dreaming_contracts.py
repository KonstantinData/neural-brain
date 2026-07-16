"""Executable assertions for ADR-016 hierarchy scope and ADR-017 Dreaming."""

import importlib
import json
from pathlib import Path
from typing import Protocol

import pytest

ROOT = Path(__file__).parents[2]
CONTRACTS = ROOT / "docs" / "architecture" / "contracts"

_jsonschema = importlib.import_module("jsonschema")
_validation_error = importlib.import_module("jsonschema.exceptions").ValidationError
assert isinstance(_validation_error, type) and issubclass(_validation_error, Exception)
VALIDATION_ERROR: type[Exception] = _validation_error


class _Validator(Protocol):
    def validate(self, instance: object) -> None: ...


def _load(name: str) -> dict[str, object]:
    value: object = json.loads((CONTRACTS / name).read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _scope_validator() -> _Validator:
    schema = _load("scope-catalog.json")
    _jsonschema.Draft202012Validator.check_schema(schema)
    validator: _Validator = _jsonschema.Draft202012Validator(schema)
    return validator


@pytest.mark.parametrize(
    "entry",
    [
        {"catalog_kind": "brain", "brain_id": "brain-neural"},
        {"catalog_kind": "tenant", "brain_id": "brain-neural", "tenant_id": "tenant-a"},
        {"catalog_kind": "area", "tenant_id": "tenant-a", "area_id": "area-a"},
        {
            "catalog_kind": "project",
            "tenant_id": "tenant-a",
            "area_id": "area-a",
            "project_id": "project-a",
        },
        {
            "catalog_kind": "session",
            "tenant_id": "tenant-a",
            "area_id": "area-a",
            "project_id": "project-a",
            "session_id": "session-a",
        },
        {
            "catalog_kind": "goal",
            "tenant_id": "tenant-a",
            "area_id": "area-a",
            "project_id": "project-a",
            "session_id": "session-a",
            "goal_id": "goal-a",
        },
    ],
)
def test_typed_catalog_accepts_exact_parent_lineage(entry: dict[str, object]) -> None:
    _scope_validator().validate(entry)


@pytest.mark.parametrize(
    "invalid",
    [
        {
            "catalog_kind": "tenant",
            "brain_id": "brain-neural",
            "tenant_id": "tenant-a",
            "area_id": "sentinel",
        },
        {
            "catalog_kind": "session",
            "tenant_id": "tenant-a",
            "area_id": "area-a",
            "session_id": "session-a",
        },
        {
            "catalog_kind": "goal",
            "tenant_id": "tenant-a",
            "area_id": "area-a",
            "project_id": "project-a",
            "goal_id": "goal-a",
        },
        {"scope_kind": "operational_memory", "tenant_id": "tenant-a"},
    ],
)
def test_catalog_rejects_descendant_or_incomplete_scope(invalid: dict[str, object]) -> None:
    with pytest.raises(VALIDATION_ERROR):
        _scope_validator().validate(invalid)


def test_ms_1_dreaming_is_area_local_and_cannot_activate() -> None:
    contract = _load("dreaming.json")
    scope = contract["scope"]
    stage_behavior = contract["memory_stage_behavior"]
    protected_writes = contract["protected_writes"]
    assert isinstance(scope, dict)
    assert isinstance(stage_behavior, dict)
    assert isinstance(protected_writes, dict)
    ms_1 = stage_behavior["ms_1"]
    assert isinstance(ms_1, dict)
    assert scope["cardinality"] == "exactly_one_authenticated_tenant_and_area"
    assert "cross-area input or output" in ms_1["denied"]
    assert "candidate promotion" in ms_1["denied"]
    assert "active pointer change" in ms_1["denied"]
    assert protected_writes["worker_direct_write"] == "forbidden"
    assert protected_writes["model_direct_write"] == "forbidden"
