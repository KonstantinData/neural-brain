"""Tests for typed untrusted-payload envelope boundaries."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from neural_brain.security.envelopes import TrustSurface, UntrustedPayloadEnvelope


@pytest.mark.parametrize("surface", tuple(TrustSurface))
def test_each_untrusted_surface_accepts_only_opaque_payload_fields(surface: TrustSurface) -> None:
    envelope = UntrustedPayloadEnvelope(
        surface=surface, payload_schema_id="schema.v1", payload={"content": "untrusted"}
    )

    assert envelope.surface is surface


@pytest.mark.parametrize(
    "field",
    ("actor_id", "tenant_id", "authority", "policy", "classification", "legal_hold", "promotion"),
)
def test_untrusted_payload_cannot_supply_trusted_control(field: str) -> None:
    with pytest.raises(ValidationError, match="trusted control"):
        UntrustedPayloadEnvelope(
            surface=TrustSurface.INGESTION, payload_schema_id="schema.v1", payload={field: "forged"}
        )


def test_unknown_envelope_fields_are_rejected() -> None:
    with pytest.raises(ValidationError, match="Extra inputs"):
        UntrustedPayloadEnvelope.model_validate(
            {
                "surface": "ingestion",
                "payload_schema_id": "schema.v1",
                "payload": {},
                "tenant_id": "forged",
            }
        )
