"""Typed envelopes that keep untrusted payloads separate from trusted control."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TrustSurface(StrEnum):
    INGESTION = "ingestion"
    MODEL = "model"
    MEMORY = "memory"
    INTEGRATION = "integration"


class UntrustedPayloadEnvelope(BaseModel):
    """Opaque payload plus non-authoritative metadata from one untrusted surface."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    surface: TrustSurface
    payload_schema_id: str = Field(min_length=1, max_length=128)
    payload: dict[str, Any]

    @model_validator(mode="after")
    def has_no_trusted_control_fields(self) -> UntrustedPayloadEnvelope:
        forbidden = {
            "actor_id",
            "principal_id",
            "tenant_id",
            "area_id",
            "project_id",
            "session_id",
            "authority",
            "approval",
            "policy",
            "purpose",
            "classification",
            "retention",
            "legal_hold",
            "promotion",
            "lifecycle_state",
        }
        if forbidden.intersection(self.payload):
            raise ValueError("untrusted payload cannot contain trusted control fields")
        return self
