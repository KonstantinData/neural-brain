"""Live PostgreSQL proof for the Memory Core tenant-isolation boundary."""

# ruff: noqa: SIM117

from __future__ import annotations

from typing import Final, Literal, Protocol

import psycopg
import pytest
from psycopg import sql
from psycopg.types.json import Jsonb

type AuthorityState = Literal["missing", "expired", "disabled"]
type Context = dict[str, str]

DATABASE_ROLES: Final[tuple[str, ...]] = ("neural_brain_gate", "neural_brain_reader")
TABLE_PRIVILEGES: Final[tuple[str, ...]] = (
    "SELECT",
    "INSERT",
    "UPDATE",
    "DELETE",
    "TRUNCATE",
    "REFERENCES",
    "TRIGGER",
    "MAINTAIN",
)


class RuntimeDatabaseAccess(Protocol):
    """Structural fixture contract without importing pytest's conftest module."""

    @property
    def dsn(self) -> str:
        """Return the redacted least-privilege connection string."""
        ...


TENANT_A: Final[Context] = {
    "principal_id": "principal-a",
    "tenant_id": "tenant-a",
    "area_id": "area-a",
    "project_id": "project-a",
    "session_id": "session-a",
}
TENANT_B: Final[Context] = {
    "principal_id": "principal-c",
    "tenant_id": "tenant-b",
    "area_id": "area-a",
    "project_id": "project-a",
    "session_id": "session-a",
}
TENANT_B_WITH_TENANT_A_PRINCIPAL: Final[Context] = {
    **TENANT_B,
    "principal_id": "principal-a",
}
AREA_B: Final[Context] = {
    "principal_id": "principal-b",
    "tenant_id": "tenant-a",
    "area_id": "area-b",
    "project_id": "project-b",
    "session_id": "session-b",
}
AREA_B_WITH_AREA_A_PRINCIPAL: Final[Context] = {
    **AREA_B,
    "principal_id": "principal-a",
}


def _set_context(cursor: psycopg.Cursor[tuple[object, ...]], context: Context) -> None:
    for name, value in context.items():
        cursor.execute(
            "SELECT pg_catalog.set_config(%s, %s, true)",
            (f"neural_brain.{name}", value),
        )


def _seed_observation(
    database_dsn: str,
    *,
    context: Context,
    observation_id: str,
    content: str,
) -> None:
    with psycopg.connect(database_dsn, autocommit=True) as connection:
        with connection.transaction(), connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO memory_core.observations ("
                "tenant_id, area_id, project_id, observation_id, session_id, source_kind, "
                "classification, purpose, payload, occurred_at"
                ") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, statement_timestamp())",
                (
                    context["tenant_id"],
                    context["area_id"],
                    context["project_id"],
                    observation_id,
                    context["session_id"],
                    "consumer_event",
                    "internal",
                    "isolation_proof",
                    Jsonb(
                        {
                            "source_ref": f"{observation_id}-source",
                            "content": content,
                        }
                    ),
                ),
            )


def _read_observation(
    runtime_database_access: RuntimeDatabaseAccess,
    context: Context,
    observation_id: str,
) -> dict[str, object]:
    with (
        psycopg.connect(runtime_database_access.dsn, autocommit=True) as connection,
        connection.transaction(),
        connection.cursor() as cursor,
    ):
        cursor.execute("SET LOCAL ROLE neural_brain_reader")
        _set_context(cursor, context)
        cursor.execute(
            "SELECT memory_gate.read_observation(%s)",
            (observation_id,),
        )
        row = cursor.fetchone()
    assert row is not None
    document = row[0]
    assert isinstance(document, dict)
    return document


def _protected_relations(database_dsn: str) -> list[tuple[str, str, str]]:
    with psycopg.connect(database_dsn, autocommit=True) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT DISTINCT ON (namespace.nspname, relation.relname) "
                "namespace.nspname, relation.relname, attribute.attname "
                "FROM pg_catalog.pg_class AS relation "
                "JOIN pg_catalog.pg_namespace AS namespace "
                "ON namespace.oid = relation.relnamespace "
                "JOIN pg_catalog.pg_attribute AS attribute "
                "ON attribute.attrelid = relation.oid "
                "AND attribute.attnum > 0 AND NOT attribute.attisdropped "
                "WHERE namespace.nspname IN ('memory_core', 'memory_audit') "
                "AND relation.relkind IN ('r', 'p') "
                "ORDER BY namespace.nspname, relation.relname, attribute.attnum"
            )
            return [(str(row[0]), str(row[1]), str(row[2])) for row in cursor.fetchall()]


def test_every_memory_table_enables_and_forces_row_level_security(database_dsn: str) -> None:
    """A future unprotected Memory Core or audit table must fail this CI guard."""

    with psycopg.connect(database_dsn, autocommit=True) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT namespace.nspname, relation.relname, relation.relrowsecurity, "
                "relation.relforcerowsecurity "
                "FROM pg_catalog.pg_class AS relation "
                "JOIN pg_catalog.pg_namespace AS namespace "
                "ON namespace.oid = relation.relnamespace "
                "WHERE namespace.nspname IN ('memory_core', 'memory_audit') "
                "AND relation.relkind IN ('r', 'p') "
                "ORDER BY namespace.nspname, relation.relname"
            )
            relations = cursor.fetchall()

    assert relations
    assert all(row[2] is True and row[3] is True for row in relations), relations


def test_real_runtime_login_has_no_table_privileges_through_any_effective_role(
    database_dsn: str, runtime_database_access: RuntimeDatabaseAccess
) -> None:
    """Every effective runtime role lacks every direct protected-table privilege."""

    relations = _protected_relations(database_dsn)
    assert relations
    with psycopg.connect(runtime_database_access.dsn, autocommit=True) as connection:
        for role in DATABASE_ROLES:
            with connection.transaction(), connection.cursor() as cursor:
                cursor.execute(sql.SQL("SET LOCAL ROLE {}").format(sql.Identifier(role)))
                for schema_name, relation_name, _ in relations:
                    qualified_name = f"{schema_name}.{relation_name}"
                    for privilege in TABLE_PRIVILEGES:
                        cursor.execute(
                            "SELECT pg_catalog.has_table_privilege(current_user, %s, %s)",
                            (qualified_name, privilege),
                        )
                        assert cursor.fetchone() == (False,), (
                            role,
                            qualified_name,
                            privilege,
                        )


def test_real_runtime_login_cannot_access_any_protected_table_directly(
    database_dsn: str, runtime_database_access: RuntimeDatabaseAccess
) -> None:
    """Both effective roles are denied real reads and writes on every protected table."""

    relations = _protected_relations(database_dsn)
    assert relations
    with psycopg.connect(runtime_database_access.dsn, autocommit=True) as connection:
        for role in DATABASE_ROLES:
            for schema_name, relation_name, first_column in relations:
                relation = sql.SQL("{}.{}").format(
                    sql.Identifier(schema_name), sql.Identifier(relation_name)
                )
                statements = (
                    sql.SQL("SELECT * FROM {} LIMIT 0").format(relation),
                    sql.SQL("INSERT INTO {} DEFAULT VALUES").format(relation),
                    sql.SQL("UPDATE {} SET {} = {}").format(
                        relation,
                        sql.Identifier(first_column),
                        sql.Identifier(first_column),
                    ),
                    sql.SQL("DELETE FROM {}").format(relation),
                    sql.SQL("TRUNCATE TABLE {}").format(relation),
                )
                for statement in statements:
                    with (
                        pytest.raises(psycopg.errors.InsufficientPrivilege),
                        connection.transaction(),
                        connection.cursor() as cursor,
                    ):
                        cursor.execute(sql.SQL("SET LOCAL ROLE {}").format(sql.Identifier(role)))
                        cursor.execute(statement)


def test_read_gate_denies_cross_tenant_record_and_forged_tenant_claim(
    database_dsn: str, runtime_database_access: RuntimeDatabaseAccess
) -> None:
    """The gate hides foreign rows and rejects a principal without Tenant B authority."""

    _seed_observation(
        database_dsn,
        context=TENANT_B,
        observation_id="observation-tenant-b",
        content="tenant-b-content",
    )

    with pytest.raises(psycopg.errors.NoData):
        _read_observation(runtime_database_access, TENANT_A, "observation-tenant-b")
    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        _read_observation(
            runtime_database_access,
            TENANT_B_WITH_TENANT_A_PRINCIPAL,
            "observation-tenant-b",
        )

    document = _read_observation(runtime_database_access, TENANT_B, "observation-tenant-b")
    assert document["content"] == "tenant-b-content"


def test_read_gate_denies_cross_area_record_and_forged_area_claim(
    database_dsn: str, runtime_database_access: RuntimeDatabaseAccess
) -> None:
    """The gate hides foreign Areas and rejects a Principal without Area B authority."""

    _seed_observation(
        database_dsn,
        context=AREA_B,
        observation_id="observation-area-b",
        content="area-b-content",
    )

    with pytest.raises(psycopg.errors.NoData):
        _read_observation(runtime_database_access, TENANT_A, "observation-area-b")
    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        _read_observation(
            runtime_database_access,
            AREA_B_WITH_AREA_A_PRINCIPAL,
            "observation-area-b",
        )

    document = _read_observation(runtime_database_access, AREA_B, "observation-area-b")
    assert document["content"] == "area-b-content"


@pytest.mark.parametrize("authority_state", ("missing", "expired", "disabled"))
def test_read_gate_denies_invalid_authority_state(
    database_dsn: str,
    runtime_database_access: RuntimeDatabaseAccess,
    authority_state: AuthorityState,
) -> None:
    """Missing, expired, and disabled authority all fail closed at the database gate."""

    _seed_observation(
        database_dsn,
        context=TENANT_B,
        observation_id="observation-tenant-b",
        content="tenant-b-content",
    )
    with psycopg.connect(database_dsn, autocommit=True) as connection:
        with connection.transaction(), connection.cursor() as cursor:
            if authority_state == "missing":
                cursor.execute(
                    "DELETE FROM brain_security.principal_scope_bindings "
                    "WHERE principal_id = 'principal-c' AND tenant_id = 'tenant-b' "
                    "AND area_id = 'area-a'"
                )
            elif authority_state == "expired":
                cursor.execute(
                    "UPDATE brain_security.principal_scope_bindings "
                    "SET valid_until = statement_timestamp() - interval '1 second' "
                    "WHERE principal_id = 'principal-c' AND tenant_id = 'tenant-b' "
                    "AND area_id = 'area-a'"
                )
            else:
                cursor.execute(
                    "UPDATE brain_security.principals SET status = 'disabled' "
                    "WHERE principal_id = 'principal-c'"
                )

    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        _read_observation(runtime_database_access, TENANT_B, "observation-tenant-b")
