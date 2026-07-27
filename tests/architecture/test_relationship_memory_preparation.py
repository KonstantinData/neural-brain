"""Deterministic evidence for the preparation-only Relationship Memory boundary."""

import importlib
import json
from pathlib import Path
from typing import Protocol

import pytest

ROOT = Path(__file__).parents[2]
PROPOSAL = ROOT / "docs/architecture/relationship-memory-adr-018-revalidation-proposal-v1.md"
CONTRACT = ROOT / "docs/architecture/contracts/relationship-memory-signal-contract-v1.json"

_jsonschema = importlib.import_module("jsonschema")
_validation_error = importlib.import_module("jsonschema.exceptions").ValidationError
assert isinstance(_validation_error, type) and issubclass(_validation_error, Exception)
VALIDATION_ERROR: type[Exception] = _validation_error


class _Validator(Protocol):
    def validate(self, instance: object) -> None: ...


def _text(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def test_positions_remain_preparation_only_and_non_authorizing() -> None:
    text = _text(PROPOSAL)
    for term in (
        "never a Goal, Authority, Gate",
        "cannot authorize a transition",
        "no customer self-service",
        "service-managed intake and response path",
        "separately authorizable future technical enforcement package",
        "runtime-disabled",
    ):
        assert term in text
    for exclusion in (
        "migration",
        "runtime component",
        "retrieval endpoint",
        "Dreaming execution",
        "Planner integration",
        "deployment",
        "release",
    ):
        assert exclusion in text


def test_signal_contract_is_fail_closed_and_non_runtime() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    _jsonschema.Draft202012Validator.check_schema(contract)
    assert contract["runtime_enabled"] is False
    assert contract["migrations_authorized"] is False
    validator: _Validator = _jsonschema.Draft202012Validator(contract)
    with pytest.raises(VALIDATION_ERROR):
        validator.validate(None)


def test_position_three_and_runtime_boundaries_are_explicit() -> None:
    threat_plan = _text(
        ROOT / "docs/architecture/relationship-memory-threat-model-and-test-plan-v1.md"
    )
    runbook = _text(ROOT / "docs/runbooks/relationship-memory-governance-preparation.md")
    planner = _text(
        ROOT / "docs/architecture/nb1-planner-verification-adr-018-revalidation-proposal-v1.md"
    )
    for term in (
        "schema",
        "Memory Gate",
        "deletion propagation",
        "negative Scope/Purpose tests",
        "independent verification",
    ):
        assert term in threat_plan
    assert "deny_and_do_not_use" in runbook
    assert (
        "approved, minimized, provenance-bound Relationship Memory signals as untrusted context"
        in planner
    )
