import copy
import importlib
import json
from collections.abc import Iterator
from pathlib import Path
from typing import Protocol

import pytest

REPOSITORY_ROOT = Path(__file__).parents[2]
ENVELOPE_SCHEMA_PATH = REPOSITORY_ROOT / "docs" / "architecture" / "contracts" / "envelopes.json"

_jsonschema = importlib.import_module("jsonschema")
_draft_validator = _jsonschema.Draft202012Validator
_format_checker = _jsonschema.FormatChecker
_validation_error = importlib.import_module("jsonschema.exceptions").ValidationError
assert isinstance(_validation_error, type) and issubclass(_validation_error, Exception)
VALIDATION_ERROR: type[Exception] = _validation_error


class _SupportsValidation(Protocol):
    def validate(self, instance: object) -> None: ...


class EnvelopeValidator:
    """Typed boundary around jsonschema, whose distribution has external stubs."""

    def __init__(self, schema: dict[str, object]) -> None:
        self._validator: _SupportsValidation = _draft_validator(
            schema,
            format_checker=_format_checker(),
        )

    def validate(self, instance: dict[str, object]) -> None:
        self._validator.validate(instance)


def _check_schema(schema: dict[str, object]) -> None:
    _draft_validator.check_schema(schema)


@pytest.fixture(scope="module")
def envelope_schema() -> dict[str, object]:
    loaded: object
    with ENVELOPE_SCHEMA_PATH.open(encoding="utf-8") as schema_file:
        loaded = json.load(schema_file)
    assert isinstance(loaded, dict)
    return loaded


@pytest.fixture(scope="module")
def envelope_validator(
    envelope_schema: dict[str, object],
) -> EnvelopeValidator:
    _check_schema(envelope_schema)
    return EnvelopeValidator(envelope_schema)


def _header(scope: dict[str, object], *, kind: str) -> dict[str, object]:
    return {
        "contract_version": "1.0.0",
        "schema_id": f"schema.{kind}.v1",
        "envelope_id": f"envelope-{kind}-001",
        "envelope_kind": kind,
        "scope": scope,
        "actor": {
            "principal_id": "principal-001",
            "principal_kind": "service",
            "runtime_component_id": "component-001",
        },
        "trace": {"correlation_id": "correlation-001", "causation_id": None},
        "governance": {
            "classification_id": "classification.internal",
            "purpose_id": "purpose.verification",
            "retention_policy_id": "retention.default",
            "deletion_responsibility_id": "deletion.owner",
        },
        "provenance": {
            "provenance_kind_id": "provenance.direct-observation",
            "source_refs": [],
        },
        "recorded_at": "2026-07-15T10:00:00Z",
    }


def _digest() -> dict[str, object]:
    return {"algorithm_id": "digest.test-only", "value": "opaque-digest-value"}


def _artifact_envelope(scope: dict[str, object]) -> dict[str, object]:
    return {
        **_header(scope, kind="artifact"),
        "artifact_id": "artifact-001",
        "artifact_type_id": "artifact.contract-test",
        "media_type_id": "media.application-json",
        "structured_schema_id": "schema.payload.v1",
        "content_digest": _digest(),
        "byte_length": 42,
        "storage_handle": "opaque-storage-handle",
        "captured_at": "2026-07-15T09:59:59Z",
        "supersedes_artifact_id": None,
    }


def _evidence_envelope(scope: dict[str, object]) -> dict[str, object]:
    return {
        **_header(scope, kind="evidence"),
        "evidence_id": "evidence-001",
        "evidence_type_id": "evidence.contract-test",
        "subject_ref": {"object_kind_id": "goal", "object_id": "goal-001"},
        "criterion_ids": ["criterion-001"],
        "artifact_refs": [{"artifact_id": "artifact-001", "content_digest": _digest()}],
        "captured_at": "2026-07-15T09:59:59Z",
        "supersedes_evidence_id": None,
    }


@pytest.fixture(
    params=[
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
        {
            "scope_level": "goal",
            "tenant_id": "tenant-001",
            "area_id": "area-001",
            "project_id": "project-001",
            "session_id": "session-001",
            "goal_id": "goal-001",
        },
    ],
    ids=["area", "project", "session", "goal"],
)
def valid_scope(request: pytest.FixtureRequest) -> dict[str, object]:
    value = request.param
    assert isinstance(value, dict)
    return value


def test_envelope_contract_is_valid_draft_2020_12_schema(
    envelope_schema: dict[str, object],
) -> None:
    assert envelope_schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    _check_schema(envelope_schema)


def test_artifact_and_evidence_accept_every_valid_scope_level(
    envelope_validator: EnvelopeValidator,
    valid_scope: dict[str, object],
) -> None:
    envelope_validator.validate(_artifact_envelope(valid_scope))
    envelope_validator.validate(_evidence_envelope(valid_scope))


def _invalid_scope_cases() -> Iterator[tuple[str, dict[str, object]]]:
    yield "missing_tenant", {"scope_level": "area", "area_id": "area-001"}
    yield "missing_area", {"scope_level": "area", "tenant_id": "tenant-001"}
    yield (
        "project_without_project",
        {
            "scope_level": "project",
            "tenant_id": "tenant-001",
            "area_id": "area-001",
        },
    )
    yield (
        "session_without_project",
        {
            "scope_level": "session",
            "tenant_id": "tenant-001",
            "area_id": "area-001",
            "session_id": "session-001",
        },
    )
    yield (
        "goal_without_session",
        {
            "scope_level": "goal",
            "tenant_id": "tenant-001",
            "area_id": "area-001",
            "project_id": "project-001",
            "goal_id": "goal-001",
        },
    )
    yield (
        "area_with_project",
        {
            "scope_level": "area",
            "tenant_id": "tenant-001",
            "area_id": "area-001",
            "project_id": "project-001",
        },
    )
    yield (
        "unknown_scope_level",
        {
            "scope_level": "brain",
            "tenant_id": "tenant-001",
            "area_id": "area-001",
        },
    )


@pytest.mark.parametrize(("case_name", "scope"), list(_invalid_scope_cases()))
def test_invalid_scope_ancestry_is_rejected(
    envelope_validator: EnvelopeValidator,
    case_name: str,
    scope: dict[str, object],
) -> None:
    del case_name
    with pytest.raises(VALIDATION_ERROR):
        envelope_validator.validate(_artifact_envelope(scope))


@pytest.mark.parametrize(
    ("mutation_path", "value"),
    [
        (("unexpected_control_field",), "forbidden"),
        (("actor", "roles"), ["administrator"]),
        (("scope", "principal_id"), "forged-principal"),
        (("trace", "tenant_id"), "forged-tenant"),
    ],
)
def test_unknown_or_forged_control_fields_are_rejected(
    envelope_validator: EnvelopeValidator,
    mutation_path: tuple[str, ...],
    value: object,
) -> None:
    instance = _artifact_envelope(
        {
            "scope_level": "goal",
            "tenant_id": "tenant-001",
            "area_id": "area-001",
            "project_id": "project-001",
            "session_id": "session-001",
            "goal_id": "goal-001",
        }
    )
    target = instance
    for segment in mutation_path[:-1]:
        nested = target[segment]
        assert isinstance(nested, dict)
        target = nested
    target[mutation_path[-1]] = value

    with pytest.raises(VALIDATION_ERROR):
        envelope_validator.validate(instance)


def test_timestamp_format_is_enforced(
    envelope_validator: EnvelopeValidator,
) -> None:
    instance = _artifact_envelope(
        {"scope_level": "area", "tenant_id": "tenant-001", "area_id": "area-001"}
    )
    invalid = copy.deepcopy(instance)
    invalid["recorded_at"] = "2026-07-15 10:00:00"

    with pytest.raises(VALIDATION_ERROR):
        envelope_validator.validate(invalid)
