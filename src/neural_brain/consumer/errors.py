"""Fail-closed errors for the OIDC/JWT consumer boundary."""


class OidcAuthenticationError(RuntimeError):
    """Raised when a bearer token cannot establish trusted runtime context."""
