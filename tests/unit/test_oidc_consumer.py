"""Unit evidence for the fail-closed OIDC/JWT consumer authentication boundary."""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass, field
from datetime import UTC, datetime

import pytest
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from neural_brain.consumer import (
    OidcAuthenticationError,
    OidcJwtAuthenticator,
    OidcJwtConfiguration,
    OidcMemoryCoreConsumer,
    canonical_authenticated_subject,
)
from neural_brain.memory import (
    CheckpointRecord,
    CheckpointRequest,
    DreamingRequest,
    DreamingResult,
    MemoryCycleResult,
    MemoryScope,
    ObservationRecord,
    ObservationRequest,
    OpaqueId,
    RuntimeContext,
    WorkingMemoryRecord,
    WorkingMemoryRequest,
)

_NOW = datetime(2026, 7, 24, 14, 0, tzinfo=UTC)
_ISSUER = "https://issuer.example.test"
_AUDIENCE = "neural-brain-memory-core"


def _encode(value: object) -> str:
    return (
        base64.urlsafe_b64encode(
            json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
        )
        .rstrip(b"=")
        .decode("ascii")
    )


def _jwk(private_key: rsa.RSAPrivateKey) -> dict[str, object]:
    numbers = private_key.public_key().public_numbers()
    return {
        "kid": "key-1",
        "kty": "RSA",
        "alg": "RS256",
        "use": "sig",
        "n": base64.urlsafe_b64encode(numbers.n.to_bytes(256, "big")).rstrip(b"=").decode("ascii"),
        "e": base64.urlsafe_b64encode(numbers.e.to_bytes(3, "big")).rstrip(b"=").decode("ascii"),
    }


def _token(private_key: rsa.RSAPrivateKey, claims: dict[str, object]) -> str:
    header = _encode({"alg": "RS256", "kid": "key-1", "typ": "JWT"})
    payload = _encode(claims)
    signing_input = f"{header}.{payload}".encode("ascii")
    signature = private_key.sign(signing_input, padding.PKCS1v15(), hashes.SHA256())
    encoded_signature = base64.urlsafe_b64encode(signature).rstrip(b"=").decode("ascii")
    return f"{header}.{payload}.{encoded_signature}"


def _claims() -> dict[str, object]:
    return {
        "iss": _ISSUER,
        "aud": [_AUDIENCE],
        "sub": "operator-123",
        "exp": _NOW.timestamp() + 120,
        "nbf": _NOW.timestamp() - 10,
        "neural_brain_scope": {
            "tenant_id": "tenant-a",
            "area_id": "area-a",
            "project_id": "project-a",
            "session_id": "session-a",
        },
    }


@dataclass
class _Resolver:
    principal_id: str = "principal-a"
    subjects: list[str] = field(default_factory=list)

    def resolve_authenticated_subject(self, authenticated_subject: str) -> str:
        self.subjects.append(authenticated_subject)
        return self.principal_id


@dataclass
class _CheckpointRepository:
    contexts: list[RuntimeContext] = field(default_factory=list)

    def read_checkpoint(
        self, *, context: RuntimeContext, checkpoint_id: OpaqueId
    ) -> CheckpointRecord:
        self.contexts.append(context)
        return CheckpointRecord(
            checkpoint_id=checkpoint_id,
            working_memory_id="primary",
            working_memory_version=1,
            entries=(),
            scope=MemoryScope(
                tenant_id=context.tenant_id,
                area_id=context.area_id,
                project_id=context.project_id,
                session_id=context.session_id,
            ),
        )

    def commit_memory_cycle(
        self,
        *,
        context: RuntimeContext,
        transition_request_id: OpaqueId,
        observation: ObservationRequest,
        working_memory: WorkingMemoryRequest,
        checkpoint: CheckpointRequest,
    ) -> MemoryCycleResult:
        del context, transition_request_id, observation, working_memory, checkpoint
        raise AssertionError("not exercised by the checkpoint consumer test")

    def read_observation(
        self, *, context: RuntimeContext, observation_id: OpaqueId
    ) -> ObservationRecord:
        del context, observation_id
        raise AssertionError("not exercised by the checkpoint consumer test")

    def read_working_memory(
        self, *, context: RuntimeContext, working_memory_id: OpaqueId
    ) -> WorkingMemoryRecord:
        del context, working_memory_id
        raise AssertionError("not exercised by the checkpoint consumer test")

    def execute_dreaming_dry_run(
        self, *, context: RuntimeContext, request: DreamingRequest
    ) -> DreamingResult:
        del context, request
        raise AssertionError("not exercised by the checkpoint consumer test")


@pytest.fixture
def private_key() -> rsa.RSAPrivateKey:
    """Create an ephemeral test-only signing key; no credential is stored."""
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


def _authenticator(private_key: rsa.RSAPrivateKey, resolver: _Resolver) -> OidcJwtAuthenticator:
    return OidcJwtAuthenticator(
        configuration=OidcJwtConfiguration(issuer=_ISSUER, audience=_AUDIENCE),
        jwks={"keys": [_jwk(private_key)]},
        principal_resolver=resolver,
        now=lambda: _NOW,
    )


def test_valid_rs256_token_derives_context_only_from_signed_claims(
    private_key: rsa.RSAPrivateKey,
) -> None:
    resolver = _Resolver()
    context = _authenticator(private_key, resolver).authenticate(_token(private_key, _claims()))

    assert context == RuntimeContext(
        actor_id="principal-a",
        tenant_id="tenant-a",
        area_id="area-a",
        project_id="project-a",
        session_id="session-a",
    )
    assert resolver.subjects == [canonical_authenticated_subject(_ISSUER, "operator-123")]


@pytest.mark.parametrize(
    ("claim", "value"),
    [
        ("iss", "https://other.example.test"),
        ("aud", ["other-audience"]),
        ("exp", _NOW.timestamp() - 61),
        ("nbf", _NOW.timestamp() + 61),
        ("neural_brain_scope", {"tenant_id": "tenant-a"}),
    ],
)
def test_invalid_or_incomplete_signed_claims_fail_closed(
    private_key: rsa.RSAPrivateKey, claim: str, value: object
) -> None:
    claims = _claims()
    claims[claim] = value

    with pytest.raises(OidcAuthenticationError):
        _authenticator(private_key, _Resolver()).authenticate(_token(private_key, claims))


def test_tampered_signature_and_disallowed_algorithm_fail_before_subject_resolution(
    private_key: rsa.RSAPrivateKey,
) -> None:
    resolver = _Resolver()
    token = _token(private_key, _claims())
    header, payload, signature = token.split(".")
    tampered_signature = ("A" if signature[0] != "A" else "B") + signature[1:]
    tampered = f"{header}.{payload}.{tampered_signature}"

    with pytest.raises(OidcAuthenticationError):
        _authenticator(private_key, resolver).authenticate(tampered)
    assert resolver.subjects == []

    none_header = _encode({"alg": "none", "kid": "key-1"})
    with pytest.raises(OidcAuthenticationError):
        _authenticator(private_key, resolver).authenticate(f"{none_header}.{payload}.{signature}")
    assert resolver.subjects == []


def test_consumer_binds_verified_context_to_the_existing_read_gate(
    private_key: rsa.RSAPrivateKey,
) -> None:
    repository = _CheckpointRepository()
    consumer = OidcMemoryCoreConsumer(
        authenticator=_authenticator(private_key, _Resolver()),
        repository=repository,
    )

    checkpoint = consumer.read_checkpoint(
        bearer_token=_token(private_key, _claims()), checkpoint_id="checkpoint-a"
    )

    assert checkpoint.checkpoint_id == "checkpoint-a"
    assert repository.contexts == [
        RuntimeContext(
            actor_id="principal-a",
            tenant_id="tenant-a",
            area_id="area-a",
            project_id="project-a",
            session_id="session-a",
        )
    ]


def test_issuer_configuration_rejects_non_https_and_ambiguous_values() -> None:
    with pytest.raises(ValueError):
        OidcJwtConfiguration(issuer="http://issuer.example.test", audience=_AUDIENCE)
    with pytest.raises(ValueError):
        OidcJwtConfiguration(issuer=f"{_ISSUER}/", audience=_AUDIENCE)


def test_oidc_authentication_failure_exposes_a_stable_operator_code() -> None:
    """Token diagnostics remain typed without exposing a raw bearer token."""
    assert OidcAuthenticationError.code == "NB-MC-AUTHENTICATION-FAILED"
