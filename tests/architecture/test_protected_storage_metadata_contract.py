"""Strict metadata-only contract evidence for the future S1-11.2 storage boundary."""

from __future__ import annotations

import copy
import importlib
import json
from pathlib import Path
from typing import Protocol

import pytest

ROOT = Path(__file__).parents[2]
PATH = ROOT / "docs" / "architecture" / "contracts" / "protected-storage-metadata-v1.schema.json"
DIGEST = "b" * 64

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


def _versioned(reference_id: str) -> dict[str, object]:
    return {"reference_id": reference_id, "reference_version": 1}


def _digested(reference_id: str) -> dict[str, object]:
    return {**_versioned(reference_id), "reference_digest": DIGEST}


def _metadata() -> dict[str, object]:
    return {
        "contract_version": "protected-storage-metadata-v1",
        "governance_binding_id": "binding-1",
        "scope": {
            "tenant_id": "tenant-1",
            "area_id": "area-1",
            "project_id": "project-1",
            "session_id": "session-1",
        },
        "protected_record": {
            "record_kind": "observation",
            "record_id": "observation-1",
            "record_version": 1,
            "record_digest": DIGEST,
        },
        "data_object_type": _versioned("data-object.observation"),
        "security_classification": "restricted",
        "protected_data_classification": _digested("class.special.health"),
        "purpose": _versioned("purpose-1"),
        "processing_activity": _versioned("activity-1"),
        "data_subject_binding": {
            "binding_mode": "individual_reference",
            "subject_reference_id": "subject-ref-1",
            "subject_reference_digest": DIGEST,
        },
        "source_evidence_refs": [
            {
                "record_contract": "privacy-evidence-record-v1",
                "evidence_id": "source-1",
                "evidence_version": 1,
                "evidence_digest": DIGEST,
            }
        ],
        "retention_policy": _digested("retention-1"),
        "retention_state": {
            "evaluation_id": "retention-evaluation-1",
            "starts_at": "2026-07-28T12:00:00Z",
            "expires_at": "2026-08-28T12:00:00Z",
            "legal_hold": False,
            "deletion_owner_id": "deletion-owner-1",
            "evaluated_at": "2026-07-28T12:00:00Z",
        },
        "protection_profile": _digested("protection-1"),
        "processing_policy": _digested("policy-1"),
        "decision": {"decision_id": "decision-1", "decision_digest": DIGEST, "outcome": "ALLOW"},
        "approval_set_digest": DIGEST,
        "evidence_set_digest": DIGEST,
        "recorded_at": "2026-07-28T12:00:00Z",
    }


def _property_names(value: object) -> set[str]:
    names: set[str] = set()
    if isinstance(value, dict):
        properties = value.get("properties")
        if isinstance(properties, dict):
            names.update(str(key) for key in properties)
        for child in value.values():
            names.update(_property_names(child))
    elif isinstance(value, list):
        for child in value:
            names.update(_property_names(child))
    return names


def test_metadata_schema_is_strict_and_contains_no_protected_value_field() -> None:
    schema = _schema()
    boundary = schema["x-neural-brain-preparation-boundary"]
    assert isinstance(boundary, dict)
    assert boundary["runtime_enabled"] is False
    assert boundary["allow_authorized"] is False
    assert boundary["composition_required"] is True
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["additionalProperties"] is False
    _validator_class.check_schema(schema)
    assert _property_names(schema).isdisjoint(
        {
            "payload",
            "content",
            "raw_value",
            "personal_data",
            "special_category_value",
            "consent_text",
        }
    )


def test_complete_metadata_binding_is_machine_valid() -> None:
    _validator().validate(_metadata())


@pytest.mark.parametrize("outcome", ["DENY", "UNKNOWN", "EXPIRED", "REVOKED", "CONFLICT"])
def test_non_allow_decision_cannot_bind_protected_storage(outcome: str) -> None:
    document = _metadata()
    decision = document["decision"]
    assert isinstance(decision, dict)
    decision["outcome"] = outcome
    with pytest.raises(VALIDATION_ERROR):
        _validator().validate(document)


def test_unknown_fields_and_embedded_values_are_rejected() -> None:
    document = _metadata()
    document["payload"] = {"unexpected": "value"}
    with pytest.raises(VALIDATION_ERROR):
        _validator().validate(document)

    nested = _metadata()
    record = nested["protected_record"]
    assert isinstance(record, dict)
    record["content"] = "not permitted"
    with pytest.raises(VALIDATION_ERROR):
        _validator().validate(nested)


def test_data_subject_reference_branch_is_exact_and_digest_bound() -> None:
    validator = _validator()
    non_personal = _metadata()
    non_personal["data_subject_binding"] = {"binding_mode": "not_applicable"}
    validator.validate(non_personal)

    incomplete = copy.deepcopy(_metadata())
    incomplete["data_subject_binding"] = {
        "binding_mode": "individual_reference",
        "subject_reference_id": "subject-ref-1",
    }
    with pytest.raises(VALIDATION_ERROR):
        validator.validate(incomplete)


def test_scope_and_every_governance_reference_are_required() -> None:
    validator = _validator()
    for missing in (
        "scope",
        "protected_data_classification",
        "purpose",
        "processing_activity",
        "retention_policy",
        "retention_state",
        "protection_profile",
        "processing_policy",
        "decision",
        "approval_set_digest",
        "evidence_set_digest",
    ):
        document = _metadata()
        del document[missing]
        with pytest.raises(VALIDATION_ERROR):
            validator.validate(document)


def test_retention_state_requires_expiry_legal_hold_and_deletion_owner() -> None:
    validator = _validator()
    for missing in ("expires_at", "legal_hold", "deletion_owner_id"):
        document = _metadata()
        retention_state = document["retention_state"]
        assert isinstance(retention_state, dict)
        del retention_state[missing]
        with pytest.raises(VALIDATION_ERROR):
            validator.validate(document)
