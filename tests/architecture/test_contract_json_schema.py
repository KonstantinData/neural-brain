import copy
import importlib
import json
from pathlib import Path
from typing import Protocol

import pytest

ROOT = Path(__file__).parents[2]
PATH = ROOT / "docs" / "architecture" / "contracts" / "envelopes.json"

_jsonschema = importlib.import_module("jsonschema")
_validator_class = _jsonschema.Draft202012Validator
_format_checker = _jsonschema.FormatChecker
_validation_error = importlib.import_module("jsonschema.exceptions").ValidationError
assert isinstance(_validation_error, type) and issubclass(_validation_error, Exception)
VALIDATION_ERROR: type[Exception] = _validation_error


class _Validator(Protocol):
    def validate(self, instance: object) -> None: ...


def _schema() -> dict[str, object]:
    loaded: object = json.loads(PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _validator() -> _Validator:
    schema = _schema()
    _validator_class.check_schema(schema)
    validator: _Validator = _validator_class(schema, format_checker=_format_checker())
    return validator


def _request(*, scope: dict[str, object] | None = None) -> dict[str, object]:
    return {
        "contract_version": "1.0.0",
        "envelope_id": "envelope-001",
        "envelope_kind": "memory_request",
        "scope": scope or {"scope_level": "area", "tenant_id": "tenant-001", "area_id": "area-001"},
        "actor": {
            "principal_id": "principal-001",
            "principal_kind": "service",
            "runtime_component_id": "component-001",
        },
        "trace": {"correlation_id": "correlation-001", "causation_id": None},
        "governance": {
            "classification_id": "classification.internal",
            "purpose_id": "purpose.memory",
            "retention_policy_id": "retention.default",
            "deletion_responsibility_id": "deletion.owner",
        },
        "provenance": {
            "provenance_kind_id": "direct-observation",
            "source_refs": ["source-001"],
            "captured_at": "2026-07-15T10:00:00Z",
        },
        "recorded_at": "2026-07-15T10:00:01Z",
        "operation_id": "memory.observe",
        "payload_schema_id": "schema.observation.v1",
        "payload_digest": "opaque-digest",
    }


def test_envelope_schema_is_valid_draft_2020_12() -> None:
    schema = _schema()
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    _validator_class.check_schema(schema)


@pytest.mark.parametrize(
    "scope",
    [
        {"scope_level": "area", "tenant_id": "tenant-001", "area_id": "area-001"},
        {
            "scope_level": "project",
            "tenant_id": "tenant-001",
            "area_id": "area-001",
            "project_id": "project-001",
        },
        {
            "scope_level": "session",
            "tenant_id": "tenant-001",
            "area_id": "area-001",
            "project_id": "project-001",
            "session_id": "session-001",
        },
    ],
)
def test_memory_request_accepts_supported_scope(scope: dict[str, object]) -> None:
    _validator().validate(_request(scope=scope))


@pytest.mark.parametrize(
    "scope",
    [
        {"scope_level": "area", "tenant_id": "tenant-001"},
        {"scope_level": "project", "tenant_id": "tenant-001", "area_id": "area-001"},
        {
            "scope_level": "goal",
            "tenant_id": "tenant-001",
            "area_id": "area-001",
            "goal_id": "goal-001",
        },
    ],
)
def test_incomplete_or_goal_scope_is_rejected(scope: dict[str, object]) -> None:
    with pytest.raises(VALIDATION_ERROR):
        _validator().validate(_request(scope=scope))


def test_consumer_correlations_are_optional_opaque_metadata() -> None:
    request = _request()
    request["consumer_correlation"] = {
        "consumer_session_ref": "consumer-session-001",
        "consumer_goal_ref": "consumer-goal-001",
        "consumer_task_ref": "consumer-task-001",
    }
    _validator().validate(request)


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("scope", "goal_id"), "forged-goal"),
        (("scope", "principal_id"), "forged-principal"),
        (("actor", "roles"), ["administrator"]),
        (("consumer_correlation", "tenant_id"), "forged-tenant"),
    ],
)
def test_untrusted_control_or_unknown_fields_are_rejected(
    path: tuple[str, str], value: object
) -> None:
    request = _request()
    if path[0] == "consumer_correlation":
        request[path[0]] = {"consumer_task_ref": "task-001"}
    nested = request[path[0]]
    assert isinstance(nested, dict)
    nested[path[1]] = value
    with pytest.raises(VALIDATION_ERROR):
        _validator().validate(request)


def test_invalid_timestamp_is_rejected() -> None:
    invalid = copy.deepcopy(_request())
    provenance = invalid["provenance"]
    assert isinstance(provenance, dict)
    provenance["captured_at"] = "not-a-timestamp"
    with pytest.raises(VALIDATION_ERROR):
        _validator().validate(invalid)
