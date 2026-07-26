"""Versioned, canonical, expiry-bound policy documents for the Security Floor."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from neural_brain.security.memory_risk import DataClassification, MemoryLifecycleOperation

POLICY_SCHEMA_VERSION = "policy-v1"


class PolicyCompilationError(ValueError):
    """Raised when a policy document cannot safely enter the runtime contract."""


class _StrictPolicyModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class PolicyDocument(_StrictPolicyModel):
    """Bounded declarative policy input; never an override of the Security Floor."""

    schema_version: Literal["policy-v1"]
    policy_id: str = Field(min_length=1, max_length=128, pattern=r"^[a-z0-9][a-z0-9._-]*$")
    expires_at: datetime
    allowed_operations: tuple[MemoryLifecycleOperation, ...] = Field(min_length=1)
    allowed_classifications: tuple[DataClassification, ...] = Field(min_length=1)

    @field_validator("expires_at")
    @classmethod
    def expiry_is_timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("policy expiry must include a timezone offset")
        return value.astimezone(UTC)

    @field_validator("allowed_operations", "allowed_classifications")
    @classmethod
    def values_are_unique(cls, value: tuple[object, ...]) -> tuple[object, ...]:
        if len(value) != len(set(value)):
            raise ValueError("policy allow-list values must be unique")
        return value


class CompiledPolicy(_StrictPolicyModel):
    """Immutable compiler output bound to canonical document bytes and expiry."""

    schema_version: Literal["policy-v1"]
    policy_id: str
    policy_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    expires_at: datetime
    allowed_operations: tuple[MemoryLifecycleOperation, ...]
    allowed_classifications: tuple[DataClassification, ...]


def canonical_policy_json(policy: PolicyDocument) -> bytes:
    """Return the exact sorted-key compact JSON representation used for its digest."""

    document = policy.model_dump(mode="json")
    return json.dumps(document, sort_keys=True, separators=(",", ":")).encode("utf-8")


def compile_policy(policy: PolicyDocument, *, now: datetime) -> CompiledPolicy:
    """Validate expiry and reject any document that would widen current capability."""

    if now.tzinfo is None or now.utcoffset() is None:
        raise PolicyCompilationError("policy compiler clock must be timezone-aware")
    if policy.expires_at <= now.astimezone(UTC):
        raise PolicyCompilationError("policy is expired")
    if policy.allowed_operations != (MemoryLifecycleOperation.INTAKE,):
        raise PolicyCompilationError("policy cannot widen the current Security Floor")
    digest = hashlib.sha256(canonical_policy_json(policy)).hexdigest()
    return CompiledPolicy(
        schema_version=policy.schema_version,
        policy_id=policy.policy_id,
        policy_digest=digest,
        expires_at=policy.expires_at,
        allowed_operations=policy.allowed_operations,
        allowed_classifications=policy.allowed_classifications,
    )
