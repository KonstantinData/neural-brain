"""PostgreSQL adapter for resolving validated OIDC subjects to internal principals."""

from __future__ import annotations

import psycopg

from neural_brain.consumer.errors import OidcAuthenticationError


class PostgresOidcPrincipalResolver:
    """Resolve only an already-validated external subject through a protected function."""

    def __init__(self, conninfo: str) -> None:
        self._conninfo = conninfo

    def resolve_authenticated_subject(self, authenticated_subject: str) -> str:
        """Return the active principal bound to the authenticated OIDC identity."""
        try:
            with (
                psycopg.connect(self._conninfo, autocommit=True) as connection,
                connection.transaction(),
                connection.cursor() as cursor,
            ):
                cursor.execute("SET LOCAL ROLE neural_brain_reader")
                cursor.execute(
                    "SELECT brain_security.resolve_authenticated_principal(%s)",
                    (authenticated_subject,),
                )
                row = cursor.fetchone()
        except psycopg.Error as error:
            raise OidcAuthenticationError("OIDC principal is unavailable") from error
        if row is None or not isinstance(row[0], str) or not row[0]:
            raise OidcAuthenticationError("OIDC principal resolution returned no principal")
        return row[0]
