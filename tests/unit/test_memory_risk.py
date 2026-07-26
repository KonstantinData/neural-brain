"""Tests for the shared, fail-closed Memory Core risk outcome contract."""

from __future__ import annotations

import pytest

from neural_brain.security import (
    MEMORY_RISK_CONTRACT_VERSION,
    MemoryLifecycleOperation,
    MemoryRiskClass,
    MemoryRiskOutcome,
    MemoryRiskRequest,
    decide_memory_risk,
)
from neural_brain.security.memory_risk import DataClassification


def _request(
    *,
    operation: MemoryLifecycleOperation = MemoryLifecycleOperation.INTAKE,
    classification: DataClassification = "internal",
    has_authenticated_scope: bool = True,
    has_provenance: bool = True,
    has_purpose: bool = True,
    has_lifecycle_gate: bool = True,
) -> MemoryRiskRequest:
    return MemoryRiskRequest(
        operation=operation,
        classification=classification,
        has_authenticated_scope=has_authenticated_scope,
        has_provenance=has_provenance,
        has_purpose=has_purpose,
        has_lifecycle_gate=has_lifecycle_gate,
    )


def test_gated_intake_has_a_deterministic_allow_outcome() -> None:
    decision = decide_memory_risk(_request())

    assert decision.contract_version == MEMORY_RISK_CONTRACT_VERSION
    assert decision.risk_class is MemoryRiskClass.ELEVATED
    assert decision.outcome is MemoryRiskOutcome.ALLOW
    assert decision.reason_code == "gated_intake_admitted"


@pytest.mark.parametrize(
    ("field", "reason_code"),
    (
        ("has_authenticated_scope", "missing_authenticated_scope"),
        ("has_provenance", "missing_provenance"),
        ("has_purpose", "missing_purpose"),
        ("has_lifecycle_gate", "missing_lifecycle_gate"),
    ),
)
def test_missing_required_fact_fails_closed(field: str, reason_code: str) -> None:
    if field == "has_authenticated_scope":
        decision = decide_memory_risk(_request(has_authenticated_scope=False))
    elif field == "has_provenance":
        decision = decide_memory_risk(_request(has_provenance=False))
    elif field == "has_purpose":
        decision = decide_memory_risk(_request(has_purpose=False))
    else:
        decision = decide_memory_risk(_request(has_lifecycle_gate=False))

    assert decision.outcome is MemoryRiskOutcome.DENY
    assert decision.reason_code == reason_code


@pytest.mark.parametrize("operation", tuple(MemoryLifecycleOperation))
def test_unreleased_lifecycle_operations_are_denied_after_complete_prechecks(
    operation: MemoryLifecycleOperation,
) -> None:
    decision = decide_memory_risk(_request(operation=operation))

    expected = (
        MemoryRiskOutcome.ALLOW
        if operation is MemoryLifecycleOperation.INTAKE
        else MemoryRiskOutcome.DENY
    )
    assert decision.outcome is expected


@pytest.mark.parametrize(
    ("operation", "classification", "expected"),
    (
        (MemoryLifecycleOperation.INTAKE, "public", MemoryRiskClass.LOW),
        (MemoryLifecycleOperation.INTAKE, "confidential", MemoryRiskClass.HIGH),
        (MemoryLifecycleOperation.RETRIEVAL, "restricted", MemoryRiskClass.CRITICAL),
        (MemoryLifecycleOperation.DELETION, "public", MemoryRiskClass.CRITICAL),
    ),
)
def test_risk_classification_is_deterministic(
    operation: MemoryLifecycleOperation,
    classification: DataClassification,
    expected: MemoryRiskClass,
) -> None:
    assert (
        decide_memory_risk(_request(operation=operation, classification=classification)).risk_class
        is expected
    )
