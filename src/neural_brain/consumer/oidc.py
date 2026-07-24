"""Narrow RS256 OIDC/JWT validation for authenticated Memory Core consumers."""

from __future__ import annotations

import base64
import binascii
import json
import re
from collections.abc import Callable, Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol
from urllib.parse import urlsplit

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from pydantic import Field, field_validator

from neural_brain.consumer.errors import OidcAuthenticationError
from neural_brain.memory.models import RuntimeContext, StrictModel

_BASE64URL = re.compile(r"^[A-Za-z0-9_-]+$")
_MAX_TOKEN_LENGTH = 16_384
_MAX_IDENTIFIER_LENGTH = 200


class AuthenticatedPrincipalResolver(Protocol):
    """Resolve a validated external subject to one active internal principal."""

    def resolve_authenticated_subject(self, authenticated_subject: str) -> str:
        """Return the internal principal identifier or fail closed."""
        ...


class OidcJwtConfiguration(StrictModel):
    """Trusted OIDC configuration supplied by the deployment, never by a request."""

    issuer: str = Field(min_length=1, max_length=_MAX_IDENTIFIER_LENGTH)
    audience: str = Field(min_length=1, max_length=_MAX_IDENTIFIER_LENGTH)
    clock_skew_seconds: int = Field(default=60, ge=0, le=300)

    @field_validator("issuer")
    @classmethod
    def issuer_is_https_origin_without_fragment(cls, issuer: str) -> str:
        """Require a canonical HTTPS issuer to prevent ambiguous principal mapping."""
        parts = urlsplit(issuer)
        if (
            parts.scheme != "https"
            or not parts.netloc
            or parts.query
            or parts.fragment
            or issuer.endswith("/")
        ):
            raise ValueError(
                "issuer must be an HTTPS URL without query, fragment, or trailing slash"
            )
        return issuer


class _JwtParts(StrictModel):
    """Decoded JWT parts after strict compact-serialization parsing."""

    header: dict[str, object]
    claims: dict[str, object]
    signing_input: bytes
    signature: bytes


def canonical_authenticated_subject(issuer: str, subject: str) -> str:
    """Return the stable database identity key for an OIDC issuer-subject pair."""
    if not isinstance(issuer, str) or not isinstance(subject, str):
        raise OidcAuthenticationError("OIDC issuer and subject must be strings")
    if not issuer or not subject or len(subject) > _MAX_IDENTIFIER_LENGTH:
        raise OidcAuthenticationError("OIDC issuer or subject is invalid")
    result = json.dumps([issuer, subject], ensure_ascii=True, separators=(",", ":"))
    if len(result) > 512:
        raise OidcAuthenticationError("canonical authenticated subject is too long")
    return result


def load_jwks_file(path: Path) -> dict[str, object]:
    """Load an operator-provisioned, read-only public JWK set without network access."""
    try:
        document = _json_object(path.read_bytes(), "JWKS file")
    except OSError as error:
        raise OidcAuthenticationError("OIDC JWKS file is unavailable") from error
    keys = document.get("keys")
    if not isinstance(keys, list) or not keys:
        raise OidcAuthenticationError("OIDC JWKS file has no keys")
    return document


class OidcJwtAuthenticator:
    """Validate a bounded RS256 JWT and derive only signed runtime context."""

    def __init__(
        self,
        *,
        configuration: OidcJwtConfiguration,
        jwks: Mapping[str, object],
        principal_resolver: AuthenticatedPrincipalResolver,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self._configuration = configuration
        self._keys = _validated_keys(jwks)
        self._principal_resolver = principal_resolver
        self._now = now or (lambda: datetime.now(UTC))

    def authenticate(self, bearer_token: str) -> RuntimeContext:
        """Verify a bearer token and return immutable context derived from signed claims."""
        parts = _decode_compact_jwt(bearer_token)
        key_id = _required_string(parts.header, "kid")
        if parts.header.get("alg") != "RS256":
            raise OidcAuthenticationError("OIDC JWT algorithm is not allowed")
        public_key = self._keys.get(key_id)
        if public_key is None:
            raise OidcAuthenticationError("OIDC JWT signing key is unavailable")
        try:
            public_key.verify(
                parts.signature, parts.signing_input, padding.PKCS1v15(), hashes.SHA256()
            )
        except InvalidSignature as error:
            raise OidcAuthenticationError("OIDC JWT signature is invalid") from error

        claims = parts.claims
        self._validate_standard_claims(claims)
        subject = _required_string(claims, "sub")
        scope = _required_object(claims, "neural_brain_scope")
        authenticated_subject = canonical_authenticated_subject(self._configuration.issuer, subject)
        actor_id = self._principal_resolver.resolve_authenticated_subject(authenticated_subject)
        try:
            return RuntimeContext(
                actor_id=actor_id,
                tenant_id=_required_string(scope, "tenant_id"),
                area_id=_required_string(scope, "area_id"),
                project_id=_required_string(scope, "project_id"),
                session_id=_required_string(scope, "session_id"),
            )
        except ValueError as error:
            raise OidcAuthenticationError("OIDC JWT scope claim is invalid") from error

    def _validate_standard_claims(self, claims: Mapping[str, object]) -> None:
        if _required_string(claims, "iss") != self._configuration.issuer:
            raise OidcAuthenticationError("OIDC JWT issuer is invalid")
        audience = claims.get("aud")
        audiences = (audience,) if isinstance(audience, str) else audience
        if (
            not isinstance(audiences, list | tuple)
            or not all(isinstance(value, str) and value for value in audiences)
            or self._configuration.audience not in audiences
        ):
            raise OidcAuthenticationError("OIDC JWT audience is invalid")
        current_time = self._now()
        if current_time.tzinfo is None or current_time.utcoffset() is None:
            raise OidcAuthenticationError("OIDC clock must be timezone-aware")
        now = current_time.astimezone(UTC).timestamp()
        skew = self._configuration.clock_skew_seconds
        expiration = _numeric_claim(claims, "exp")
        if expiration <= now - skew:
            raise OidcAuthenticationError("OIDC JWT has expired")
        not_before = claims.get("nbf")
        if not_before is not None and _numeric_value(not_before, "nbf") > now + skew:
            raise OidcAuthenticationError("OIDC JWT is not active")


def _decode_compact_jwt(token: str) -> _JwtParts:
    if not isinstance(token, str) or not token or len(token) > _MAX_TOKEN_LENGTH:
        raise OidcAuthenticationError("OIDC bearer token is invalid")
    segments = token.split(".")
    if len(segments) != 3 or any(not segment for segment in segments):
        raise OidcAuthenticationError("OIDC bearer token is not compact JWT serialization")
    header = _json_object(_base64url_decode(segments[0], "JWT header"), "JWT header")
    claims = _json_object(_base64url_decode(segments[1], "JWT claims"), "JWT claims")
    return _JwtParts(
        header=header,
        claims=claims,
        signing_input=f"{segments[0]}.{segments[1]}".encode("ascii"),
        signature=_base64url_decode(segments[2], "JWT signature"),
    )


def _validated_keys(jwks: Mapping[str, object]) -> dict[str, rsa.RSAPublicKey]:
    raw_keys = jwks.get("keys")
    if not isinstance(raw_keys, list) or not raw_keys:
        raise OidcAuthenticationError("OIDC JWKS has no keys")
    keys: dict[str, rsa.RSAPublicKey] = {}
    for raw_key in raw_keys:
        if not isinstance(raw_key, Mapping):
            raise OidcAuthenticationError("OIDC JWKS key is invalid")
        key_id = _required_string(raw_key, "kid")
        if key_id in keys or raw_key.get("kty") != "RSA" or raw_key.get("alg") != "RS256":
            raise OidcAuthenticationError("OIDC JWKS key is not an unambiguous RS256 key")
        if raw_key.get("use") not in (None, "sig"):
            raise OidcAuthenticationError("OIDC JWKS key use is not signature verification")
        try:
            modulus = int.from_bytes(
                _base64url_decode(_required_jwk_string(raw_key, "n"), "JWK n"), "big"
            )
            exponent = int.from_bytes(
                _base64url_decode(_required_jwk_string(raw_key, "e"), "JWK e"), "big"
            )
            if modulus.bit_length() < 2048:
                raise ValueError("RSA modulus is too short")
            keys[key_id] = rsa.RSAPublicNumbers(exponent, modulus).public_key()
        except ValueError as error:
            raise OidcAuthenticationError("OIDC JWKS RSA key is invalid") from error
    return keys


def _base64url_decode(value: str, label: str) -> bytes:
    if not isinstance(value, str) or not value or not _BASE64URL.fullmatch(value):
        raise OidcAuthenticationError(f"{label} is not unpadded base64url")
    try:
        return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
    except (binascii.Error, ValueError) as error:
        raise OidcAuthenticationError(f"{label} cannot be decoded") from error


def _json_object(value: bytes, label: str) -> dict[str, object]:
    def reject_duplicates(items: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, item in items:
            if key in result:
                raise OidcAuthenticationError(f"{label} contains duplicate key")
            result[key] = item
        return result

    try:
        document = json.loads(value.decode("utf-8"), object_pairs_hook=reject_duplicates)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise OidcAuthenticationError(f"{label} is not valid JSON") from error
    if not isinstance(document, dict):
        raise OidcAuthenticationError(f"{label} is not a JSON object")
    return document


def _required_string(document: Mapping[str, object], key: str) -> str:
    value = document.get(key)
    if not isinstance(value, str) or not value or len(value) > _MAX_IDENTIFIER_LENGTH:
        raise OidcAuthenticationError(f"OIDC claim {key} is invalid")
    return value


def _required_jwk_string(document: Mapping[str, object], key: str) -> str:
    value = document.get(key)
    if not isinstance(value, str) or not value or len(value) > 1024:
        raise OidcAuthenticationError(f"OIDC JWK member {key} is invalid")
    return value


def _required_object(document: Mapping[str, object], key: str) -> dict[str, object]:
    value = document.get(key)
    if not isinstance(value, Mapping):
        raise OidcAuthenticationError(f"OIDC claim {key} is invalid")
    return {
        str(item_key): item_value
        for item_key, item_value in value.items()
        if isinstance(item_key, str)
    }


def _numeric_claim(document: Mapping[str, object], key: str) -> float:
    if key not in document:
        raise OidcAuthenticationError(f"OIDC claim {key} is missing")
    return _numeric_value(document[key], key)


def _numeric_value(value: object, key: str) -> float:
    if not isinstance(value, int | float) or isinstance(value, bool):
        raise OidcAuthenticationError(f"OIDC claim {key} is invalid")
    return float(value)
