"""Live evidence for protected OIDC subject-to-principal resolution."""

import psycopg
import pytest

from neural_brain.consumer import OidcAuthenticationError, canonical_authenticated_subject
from neural_brain.postgres import PostgresOidcPrincipalResolver


def test_oidc_principal_resolver_uses_the_protected_active_principal_mapping(
    database_dsn: str,
) -> None:
    """A validated issuer/subject maps only through the least-privilege function."""
    authenticated_subject = canonical_authenticated_subject(
        "https://issuer.example.invalid", "operator-42"
    )
    with (
        psycopg.connect(database_dsn, autocommit=True) as connection,
        connection.cursor() as cursor,
    ):
        cursor.execute(
            "INSERT INTO brain_security.principals (principal_id, authenticated_subject) "
            "VALUES (%s, %s)",
            ("principal-oidc-42", authenticated_subject),
        )

    resolver = PostgresOidcPrincipalResolver(database_dsn)

    assert resolver.resolve_authenticated_subject(authenticated_subject) == "principal-oidc-42"


def test_oidc_principal_resolver_fails_closed_for_an_unmapped_subject(database_dsn: str) -> None:
    """A valid token identity without an active database principal is denied."""
    resolver = PostgresOidcPrincipalResolver(database_dsn)

    with pytest.raises(OidcAuthenticationError, match="principal is unavailable"):
        resolver.resolve_authenticated_subject(
            canonical_authenticated_subject("https://issuer.example.invalid", "unknown-operator")
        )
