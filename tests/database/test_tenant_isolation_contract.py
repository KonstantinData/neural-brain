"""Live PostgreSQL proof for the Memory Core tenant-isolation boundary."""

# ruff: noqa: SIM117

from __future__ import annotations

from datetime import UTC, datetime
from typing import Final, Literal, Protocol

import psycopg
import pytest
from psycopg import sql
from psycopg.types.json import Jsonb

import neural_brain.postgres.tenant_pool as tenant_pool_module
from neural_brain.postgres.tenant_pool import TenantDatabaseEndpoint, TenantPoolResolver

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

    @property
    def role_name(self) -> str:
        """Return the disposable login role name."""
        ...


class _SingleTenantSecretProvider:
    def __init__(self, access: RuntimeDatabaseAccess) -> None:
        self._access = access

    def get_database_endpoint(self, tenant_id: str) -> TenantDatabaseEndpoint:
        assert tenant_id == "tenant-a"
        return TenantDatabaseEndpoint(
            tenant_id=tenant_id,
            endpoint_id="reset-discard-proof",
            credential_revision="1",
            conninfo=self._access.dsn,
        )


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


def test_every_operational_domain_table_has_authenticated_scope_columns(database_dsn: str) -> None:
    """Future operational tables cannot silently omit Tenant or Area scope."""

    with psycopg.connect(database_dsn, autocommit=True) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT namespace.nspname, relation.relname, "
                "array_agg(attribute.attname ORDER BY attribute.attname) "
                "FROM pg_catalog.pg_class AS relation "
                "JOIN pg_catalog.pg_namespace AS namespace "
                "ON namespace.oid = relation.relnamespace "
                "JOIN pg_catalog.pg_attribute AS attribute "
                "ON attribute.attrelid = relation.oid "
                "AND attribute.attnum > 0 AND NOT attribute.attisdropped "
                "WHERE namespace.nspname IN ('memory_core', 'memory_audit', 'memory_gate') "
                "AND relation.relkind IN ('r', 'p') "
                "GROUP BY namespace.nspname, relation.relname "
                "ORDER BY namespace.nspname, relation.relname"
            )
            relations = cursor.fetchall()

    assert relations
    missing_scope = [
        (str(schema), str(relation), columns)
        for schema, relation, columns in relations
        if not {"tenant_id", "area_id"}.issubset(set(columns))
    ]
    assert not missing_scope


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
    database_dsn: str,
    runtime_database_accesses: dict[str, RuntimeDatabaseAccess],
) -> None:
    """A Tenant A login cannot use even a legitimately authorized Tenant B principal."""

    _seed_observation(
        database_dsn,
        context=TENANT_B,
        observation_id="observation-tenant-b",
        content="tenant-b-content",
    )

    with pytest.raises(psycopg.errors.NoData):
        _read_observation(runtime_database_accesses["tenant-a"], TENANT_A, "observation-tenant-b")
    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        _read_observation(
            runtime_database_accesses["tenant-a"],
            TENANT_B,
            "observation-tenant-b",
        )

    document = _read_observation(
        runtime_database_accesses["tenant-b"], TENANT_B, "observation-tenant-b"
    )
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
    runtime_database_accesses: dict[str, RuntimeDatabaseAccess],
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
        _read_observation(runtime_database_accesses["tenant-b"], TENANT_B, "observation-tenant-b")


def test_database_login_binding_cannot_be_overridden_by_tenant_context(
    runtime_database_accesses: dict[str, RuntimeDatabaseAccess],
) -> None:
    """session_user remains the immutable Tenant anchor across SET ROLE and forged GUCs."""

    access = runtime_database_accesses["tenant-a"]
    with psycopg.connect(access.dsn, autocommit=True) as connection:
        with connection.transaction(), connection.cursor() as cursor:
            cursor.execute("SET LOCAL ROLE neural_brain_reader")
            _set_context(cursor, TENANT_B)
            cursor.execute("SELECT brain_security.bound_tenant_id()")
            assert cursor.fetchone() == ("tenant-a",)
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                cursor.execute("SELECT brain_security.assert_tenant_context()")


def test_tenant_login_cannot_assume_another_tenant_login(
    runtime_database_accesses: dict[str, RuntimeDatabaseAccess],
) -> None:
    """Tenant logins have no membership or SET path to another Tenant identity."""

    tenant_a = runtime_database_accesses["tenant-a"]
    tenant_b = runtime_database_accesses["tenant-b"]
    with psycopg.connect(tenant_a.dsn, autocommit=True) as connection:
        with (
            pytest.raises(psycopg.errors.InsufficientPrivilege),
            connection.transaction(),
            connection.cursor() as cursor,
        ):
            cursor.execute(sql.SQL("SET LOCAL ROLE {}").format(sql.Identifier(tenant_b.role_name)))


def test_cross_tenant_direct_writes_are_denied_for_real_login(
    runtime_database_accesses: dict[str, RuntimeDatabaseAccess],
) -> None:
    """A forged Tenant B context cannot create, update, or delete protected rows."""

    access = runtime_database_accesses["tenant-a"]
    statements = (
        "INSERT INTO memory_core.observations DEFAULT VALUES",
        "UPDATE memory_core.observations SET tenant_id = 'tenant-b'",
        "DELETE FROM memory_core.observations WHERE tenant_id = 'tenant-b'",
    )
    with psycopg.connect(access.dsn, autocommit=True) as connection:
        for statement in statements:
            with (
                pytest.raises(psycopg.errors.InsufficientPrivilege),
                connection.transaction(),
                connection.cursor() as cursor,
            ):
                cursor.execute("SET LOCAL ROLE neural_brain_gate")
                _set_context(cursor, TENANT_B)
                cursor.execute(statement)


def test_cross_tenant_commit_gate_is_denied_for_real_login(
    runtime_database_accesses: dict[str, RuntimeDatabaseAccess],
) -> None:
    """A Tenant A login cannot commit through the gate using valid Tenant B authority."""

    access = runtime_database_accesses["tenant-a"]
    arguments = (
        "cross-tenant-request",
        "cross-tenant-observation",
        "consumer_event",
        "internal",
        "isolation_proof",
        Jsonb({"source_ref": "cross-tenant-source", "content": "denied"}),
        datetime(2026, 7, 26, 12, 0, tzinfo=UTC),
        "cross-tenant-working-memory",
        Jsonb({"entries": []}),
        0,
        "cross-tenant-checkpoint",
    )
    with psycopg.connect(access.dsn, autocommit=True) as connection:
        with (
            pytest.raises(psycopg.errors.InsufficientPrivilege),
            connection.transaction(),
            connection.cursor() as cursor,
        ):
            cursor.execute("SET LOCAL ROLE neural_brain_gate")
            _set_context(cursor, TENANT_B)
            cursor.execute(
                "SELECT memory_gate.commit_memory_cycle("
                "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                arguments,
            )


def test_policy_and_security_definer_guards_bind_every_memory_table_to_login_tenant(
    database_dsn: str,
) -> None:
    """Future policies and privileged functions must preserve the immutable login anchor."""

    with psycopg.connect(database_dsn, autocommit=True) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT namespace.nspname, relation.relname, policy.polname, "
                "pg_catalog.pg_get_expr(policy.polqual, policy.polrelid), "
                "pg_catalog.pg_get_expr(policy.polwithcheck, policy.polrelid) "
                "FROM pg_catalog.pg_class AS relation "
                "JOIN pg_catalog.pg_namespace AS namespace ON namespace.oid = relation.relnamespace "
                "LEFT JOIN pg_catalog.pg_policy AS policy ON policy.polrelid = relation.oid "
                "WHERE namespace.nspname IN ('memory_core', 'memory_audit') "
                "AND relation.relkind IN ('r', 'p') ORDER BY 1, 2, 3"
            )
            policies = cursor.fetchall()
            assert policies
            assert all(row[2] is not None for row in policies), policies
            assert all("bound_tenant_id" in str(row[3]) for row in policies), policies
            assert all("bound_tenant_id" in str(row[4]) for row in policies), policies

            cursor.execute(
                "SELECT namespace.nspname, routine.proname, routine.prosecdef, "
                "routine.proconfig FROM pg_catalog.pg_proc AS routine "
                "JOIN pg_catalog.pg_namespace AS namespace ON namespace.oid = routine.pronamespace "
                "WHERE namespace.nspname IN ('brain_security', 'memory_gate') "
                "AND routine.prosecdef ORDER BY 1, 2"
            )
            functions = cursor.fetchall()
            assert functions
            assert all(row[3] == ["search_path=pg_catalog"] for row in functions), functions


def test_tenant_runtime_role_catalog_invariants(
    database_dsn: str,
    runtime_database_accesses: dict[str, RuntimeDatabaseAccess],
) -> None:
    """Every Tenant login is least privilege, owns nothing, and maps to exactly one Tenant."""

    role_names = [access.role_name for access in runtime_database_accesses.values()]
    with psycopg.connect(database_dsn, autocommit=True) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT rolname, rolcanlogin, rolsuper, rolcreatedb, rolcreaterole, "
                "rolinherit, rolreplication, rolbypassrls FROM pg_catalog.pg_roles "
                "WHERE rolname = ANY(%s) ORDER BY rolname",
                (role_names,),
            )
            roles = cursor.fetchall()
            assert len(roles) == 2
            assert all(row[1:] == (True, False, False, False, False, False, False) for row in roles)
            cursor.execute(
                "SELECT database_role::text, tenant_id, status "
                "FROM brain_security.tenant_runtime_identities "
                "WHERE database_role = ANY(%s) ORDER BY tenant_id",
                (role_names,),
            )
            assert cursor.fetchall() == [
                (runtime_database_accesses["tenant-a"].role_name, "tenant-a", "active"),
                (runtime_database_accesses["tenant-b"].role_name, "tenant-b", "active"),
            ]
            cursor.execute(
                "SELECT count(*) FROM pg_catalog.pg_class WHERE relowner = ANY("
                "SELECT oid FROM pg_catalog.pg_roles WHERE rolname = ANY(%s))",
                (role_names,),
            )
            assert cursor.fetchone() == (0,)
            cursor.execute(
                "SELECT count(*) FROM pg_catalog.pg_auth_members AS membership "
                "JOIN pg_catalog.pg_roles AS member ON member.oid = membership.member "
                "WHERE member.rolname = ANY(%s)",
                (
                    [
                        "neural_brain_owner",
                        "neural_brain_gate",
                        "neural_brain_reader",
                        "neural_brain_dreamer",
                    ],
                ),
            )
            assert cursor.fetchone() == (0,)
            for role_name in role_names:
                for schema_name in (
                    "brain_catalog",
                    "brain_security",
                    "memory_core",
                    "memory_audit",
                ):
                    cursor.execute(
                        "SELECT pg_catalog.has_schema_privilege(%s, %s, 'CREATE')",
                        (role_name, schema_name),
                    )
                    assert cursor.fetchone() == (False,)


def test_real_pool_discards_physical_connection_when_reset_hook_fails(
    runtime_database_accesses: dict[str, RuntimeDatabaseAccess],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """psycopg_pool never leases a physical connection whose trusted reset failed."""

    def fail_reset(connection: object) -> None:
        del connection
        raise RuntimeError("injected trusted reset failure")

    monkeypatch.setattr(tenant_pool_module, "_discard_session_state", fail_reset)
    resolver = TenantPoolResolver(
        secret_provider=_SingleTenantSecretProvider(runtime_database_accesses["tenant-a"]),
        max_cached_pools=1,
        pool_max_size=1,
    )
    try:
        with resolver.psycopg_connection("tenant-a") as first_connection:
            first_row = first_connection.execute("SELECT pg_catalog.pg_backend_pid()").fetchone()
        assert first_row is not None
        with resolver.psycopg_connection("tenant-a") as second_connection:
            second_row = second_connection.execute("SELECT pg_catalog.pg_backend_pid()").fetchone()
        assert second_row is not None
        assert second_row[0] != first_row[0]
    finally:
        resolver.close()
