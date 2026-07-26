"""Shared fail-closed risk vocabulary for Memory Core lifecycle decisions."""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict

MEMORY_RISK_CONTRACT_VERSION = "memory-risk-outcomes-v1"
type DataClassification = Literal["public", "internal", "confidential", "restricted"]


class MemoryLifecycleOperation(StrEnum):
    """Lifecycle operations that must share one security outcome vocabulary."""

    INTAKE = "intake"
    RETRIEVAL = "retrieval"
    DISCLOSURE = "disclosure"
    PROMOTION = "promotion"
    CORRECTION = "correction"
    RETENTION = "retention"
    DELETION = "deletion"


class MemoryRiskClass(StrEnum):
    """Ordered handling risk, independent from configurable policy."""

    LOW = "low"
    ELEVATED = "elevated"
    HIGH = "high"
    CRITICAL = "critical"


class MemoryRiskOutcome(StrEnum):
    """Terminal decision outcomes; only ``ALLOW`` can admit an operation."""

    ALLOW = "allow"
    DENY = "deny"
    DEFER = "defer"


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class MemoryRiskRequest(_StrictModel):
    """Typed lifecycle facts required before a risk outcome is decided."""

    operation: MemoryLifecycleOperation
    classification: DataClassification
    has_authenticated_scope: bool
    has_provenance: bool
    has_purpose: bool
    has_lifecycle_gate: bool


class MemoryRiskDecision(_StrictModel):
    """Deterministic, non-authorizing risk result for a lifecycle request."""

    contract_version: str = MEMORY_RISK_CONTRACT_VERSION
    operation: MemoryLifecycleOperation
    risk_class: MemoryRiskClass
    outcome: MemoryRiskOutcome
    reason_code: str


def decide_memory_risk(request: MemoryRiskRequest) -> MemoryRiskDecision:
    """Return the fixed v1 outcome without accepting policy or override input.

    Missing trusted context, provenance, purpose, or a required lifecycle gate is
    denied. The early Memory Core admits only gated intake. All retrieval,
    disclosure, promotion, correction, retention, and deletion work remains
    denied until its dedicated stage and gate are implemented.
    """

    risk_class = _risk_class(request.operation, request.classification)
    if not request.has_authenticated_scope:
        return _decision(request, risk_class, MemoryRiskOutcome.DENY, "missing_authenticated_scope")
    if not request.has_provenance:
        return _decision(request, risk_class, MemoryRiskOutcome.DENY, "missing_provenance")
    if not request.has_purpose:
        return _decision(request, risk_class, MemoryRiskOutcome.DENY, "missing_purpose")
    if not request.has_lifecycle_gate:
        return _decision(request, risk_class, MemoryRiskOutcome.DENY, "missing_lifecycle_gate")
    if request.operation is MemoryLifecycleOperation.INTAKE:
        return _decision(request, risk_class, MemoryRiskOutcome.ALLOW, "gated_intake_admitted")
    return _decision(request, risk_class, MemoryRiskOutcome.DENY, "operation_not_released")


def _risk_class(
    operation: MemoryLifecycleOperation, classification: DataClassification
) -> MemoryRiskClass:
    if operation in {
        MemoryLifecycleOperation.PROMOTION,
        MemoryLifecycleOperation.DELETION,
        MemoryLifecycleOperation.DISCLOSURE,
    }:
        return MemoryRiskClass.CRITICAL
    if classification == "restricted":
        return MemoryRiskClass.CRITICAL
    if classification == "confidential":
        return MemoryRiskClass.HIGH
    if classification == "internal":
        return MemoryRiskClass.ELEVATED
    return MemoryRiskClass.LOW


def _decision(
    request: MemoryRiskRequest,
    risk_class: MemoryRiskClass,
    outcome: MemoryRiskOutcome,
    reason_code: str,
) -> MemoryRiskDecision:
    return MemoryRiskDecision(
        operation=request.operation,
        risk_class=risk_class,
        outcome=outcome,
        reason_code=reason_code,
    )
