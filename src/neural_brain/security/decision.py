"""Immutable, non-authorizing bindings for bounded policy decisions."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from neural_brain.security.memory_risk import MemoryRiskOutcome


class _StrictDecisionModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class PolicyDecisionBinding(_StrictDecisionModel):
    """Every fact whose change invalidates a previously evaluated decision."""

    actor_id: str = Field(min_length=1, max_length=128)
    tenant_id: str = Field(min_length=1, max_length=128)
    area_id: str = Field(min_length=1, max_length=128)
    project_id: str = Field(min_length=1, max_length=128)
    session_id: str = Field(min_length=1, max_length=128)
    authority_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    parameter_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    checkpoint_id: str = Field(min_length=1, max_length=128)
    policy_digest: str = Field(pattern=r"^[0-9a-f]{64}$")


class PolicyDecisionRecord(_StrictDecisionModel):
    """A decision record that cannot create authority or activate policy."""

    schema_version: Literal["policy-v1"] = "policy-v1"
    decision_id: str = Field(min_length=1, max_length=128)
    binding: PolicyDecisionBinding
    outcome: MemoryRiskOutcome
    reason_codes: tuple[str, ...] = Field(min_length=1)
    obligations: tuple[str, ...] = ()
    required_approver_roles: tuple[str, ...] = ()
    valid_until: datetime

    @field_validator("valid_until")
    @classmethod
    def validity_is_timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("decision validity must include a timezone offset")
        return value.astimezone(UTC)

    def is_valid_for(self, binding: PolicyDecisionBinding, *, now: datetime) -> bool:
        """Return false for expiry or any substituted protected decision input."""

        if now.tzinfo is None or now.utcoffset() is None:
            return False
        return self.binding == binding and now.astimezone(UTC) < self.valid_until
