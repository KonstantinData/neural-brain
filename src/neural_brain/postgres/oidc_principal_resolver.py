"""PostgreSQL adapter for resolving validated OIDC subjects to internal principals."""

from __future__ import annotations

import psycopg

from neural_brain.consumer.errors import OidcAuthenticationError
from neural_brain.postgres.tenant_pool import TenantPoolError, TenantPoolResolver


class PostgresOidcPrincipalResolver:
    """Resolve only an already-validated external subject through a protected function."""

    def __init__(self, connections: TenantPoolResolver) -> None:
        self._connections = connections

    def resolve_authenticated_subject(self, authenticated_subject: str, tenant_id: str) -> str:
        """Return the active principal bound to the authenticated OIDC identity."""
        try:
            with (
                self._connections.psycopg_connection(tenant_id) as connection,
                connection.transaction(),
                connection.cursor() as cursor,
            ):
                cursor.execute("SET LOCAL ROLE neural_brain_reader")
                cursor.execute(
                    "SELECT brain_security.resolve_authenticated_principal(%s)",
                    (authenticated_subject,),
                )
                row = cursor.fetchone()
        except (psycopg.Error, TenantPoolError) as error:
            raise OidcAuthenticationError("OIDC principal is unavailable") from error
        if row is None or not isinstance(row[0], str) or not row[0]:
            raise OidcAuthenticationError("OIDC principal resolution returned no principal")
        return row[0]
