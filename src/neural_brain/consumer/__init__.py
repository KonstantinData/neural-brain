"""Authenticated, scope-safe consumer entrypoints for the Memory Core."""

from neural_brain.consumer.errors import OidcAuthenticationError
from neural_brain.consumer.oidc import (
    OidcJwtAuthenticator,
    OidcJwtConfiguration,
    canonical_authenticated_subject,
    load_jwks_file,
)
from neural_brain.consumer.service import OidcMemoryCoreConsumer

__all__ = [
    "OidcAuthenticationError",
    "OidcJwtAuthenticator",
    "OidcJwtConfiguration",
    "OidcMemoryCoreConsumer",
    "canonical_authenticated_subject",
    "load_jwks_file",
]
