"""Disposable PostgreSQL 18 fixture for live MS-1 database evidence."""

# ruff: noqa: SIM117

from __future__ import annotations

import os
import re
import secrets
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import override

import psycopg
import pytest
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict, make_conninfo

from neural_brain.postgres.tenant_pool import TenantDatabaseEndpoint, TenantPoolResolver
from tools.bootstrap_database_roles import bootstrap_roles
from tools.validate_migrations import discover_migrations

DATABASE_PREFIX = "neural_brain_database_test_"
ROOT = Path(__file__).parents[2]


class RedactedDsn(str):
    """Keep pytest failure reports from rendering database credentials."""

    @override
    def __repr__(self) -> str:
        return "<redacted database dsn>"


@dataclass(frozen=True, slots=True)
class RuntimeDatabaseAccess:
    """A disposable, least-privilege PostgreSQL login for live boundary tests."""

    dsn: RedactedDsn
    role_name: str
    tenant_id: str


class _TestSecretProvider:
    def __init__(self, accesses: dict[str, RuntimeDatabaseAccess]) -> None:
        self._accesses = accesses

    def get_database_endpoint(self, tenant_id: str) -> TenantDatabaseEndpoint:
        access = self._accesses[tenant_id]
        return TenantDatabaseEndpoint(
            tenant_id=tenant_id,
            endpoint_id="disposable-postgresql-18",
            credential_revision="1",
            conninfo=access.dsn,
        )


def _database_name() -> str:
    return f"{DATABASE_PREFIX}{secrets.token_hex(8)}"


def _assert_disposable(name: str) -> None:
    suffix = name.removeprefix(DATABASE_PREFIX)
    if not name.startswith(DATABASE_PREFIX) or re.fullmatch(r"[0-9a-f]{16}", suffix) is None:
        raise RuntimeError("Refusing database cleanup outside the integration-test namespace")


@pytest.fixture
def database_dsn() -> Iterator[str]:
    """Create, migrate, seed, and destroy one isolated integration database."""

    admin_dsn = os.getenv("MIGRATION_ADMIN_DSN")
    if not admin_dsn:
        pytest.skip("MIGRATION_ADMIN_DSN is required for live PostgreSQL tests")

    bootstrap_roles(admin_dsn)
    database_name = _database_name()
    _assert_disposable(database_name)
    with psycopg.connect(admin_dsn, autocommit=True) as connection, connection.cursor() as cursor:
        if connection.info.server_version // 10000 != 18:
            pytest.fail("live database tests require PostgreSQL 18")
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database_name)))

    database_dsn = make_conninfo(admin_dsn, dbname=database_name)
    try:
        migrations = discover_migrations(ROOT / "migrations")
        with psycopg.connect(database_dsn, autocommit=True) as connection:
            for migration in migrations:
                with connection.transaction(), connection.cursor() as cursor:
                    cursor.execute(migration.sql, prepare=False)
        _seed(database_dsn)
        yield RedactedDsn(database_dsn)
    finally:
        _assert_disposable(database_name)
        with (
            psycopg.connect(admin_dsn, autocommit=True) as connection,
            connection.cursor() as cursor,
        ):
            cursor.execute(
                sql.SQL("DROP DATABASE {} WITH (FORCE)").format(sql.Identifier(database_name))
            )


@pytest.fixture
def runtime_database_accesses(
    database_dsn: str,
) -> Iterator[dict[str, RuntimeDatabaseAccess]]:
    """Create one distinct, mapped NOINHERIT runtime login for each test Tenant."""

    database_name = conninfo_to_dict(database_dsn).get("dbname")
    if not isinstance(database_name, str):
        raise RuntimeError("Disposable database DSN has no database name")
    credentials = {
        tenant_id: (
            f"neural_brain_database_test_{tenant_id.replace('-', '_')}_{secrets.token_hex(6)}",
            secrets.token_urlsafe(32),
        )
        for tenant_id in ("tenant-a", "tenant-b")
    }
    with psycopg.connect(database_dsn, autocommit=True) as connection:
        with connection.transaction(), connection.cursor() as cursor:
            for tenant_id, (role_name, password) in credentials.items():
                cursor.execute(
                    sql.SQL(
                        "CREATE ROLE {} LOGIN PASSWORD {} NOSUPERUSER NOCREATEDB "
                        "NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS"
                    ).format(sql.Identifier(role_name), sql.Literal(password))
                )
                cursor.execute(
                    sql.SQL(
                        "GRANT neural_brain_gate, neural_brain_reader TO {} "
                        "WITH ADMIN FALSE, INHERIT FALSE, SET TRUE"
                    ).format(sql.Identifier(role_name))
                )
                cursor.execute(
                    sql.SQL("GRANT CONNECT ON DATABASE {} TO {}").format(
                        sql.Identifier(database_name), sql.Identifier(role_name)
                    )
                )
                cursor.execute(
                    sql.SQL("GRANT USAGE ON SCHEMA brain_security TO {}").format(
                        sql.Identifier(role_name)
                    )
                )
                cursor.execute(
                    "INSERT INTO brain_security.tenant_runtime_identities "
                    "(database_role, tenant_id) VALUES (%s, %s)",
                    (role_name, tenant_id),
                )
    accesses = {
        tenant_id: RuntimeDatabaseAccess(
            dsn=RedactedDsn(make_conninfo(database_dsn, user=role_name, password=password)),
            role_name=role_name,
            tenant_id=tenant_id,
        )
        for tenant_id, (role_name, password) in credentials.items()
    }
    try:
        yield accesses
    finally:
        with psycopg.connect(database_dsn, autocommit=True) as connection:
            with connection.transaction(), connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM brain_security.tenant_runtime_identities "
                    "WHERE tenant_id = ANY(%s)",
                    (list(credentials),),
                )
                for role_name, _ in credentials.values():
                    cursor.execute(
                        sql.SQL("REVOKE CONNECT ON DATABASE {} FROM {}").format(
                            sql.Identifier(database_name), sql.Identifier(role_name)
                        )
                    )
                    cursor.execute(
                        sql.SQL("REVOKE USAGE ON SCHEMA brain_security FROM {}").format(
                            sql.Identifier(role_name)
                        )
                    )
                    cursor.execute(
                        sql.SQL("REVOKE neural_brain_gate, neural_brain_reader FROM {}").format(
                            sql.Identifier(role_name)
                        )
                    )
                    cursor.execute(sql.SQL("DROP ROLE {}").format(sql.Identifier(role_name)))


@pytest.fixture
def runtime_database_access(
    runtime_database_accesses: dict[str, RuntimeDatabaseAccess],
) -> RuntimeDatabaseAccess:
    """Compatibility alias for tests that require only the Tenant A login."""

    return runtime_database_accesses["tenant-a"]


@pytest.fixture
def tenant_pool_resolver(
    runtime_database_accesses: dict[str, RuntimeDatabaseAccess],
) -> Iterator[TenantPoolResolver]:
    """Return a bounded resolver backed by two real tenant-specific pools."""

    resolver = TenantPoolResolver(
        secret_provider=_TestSecretProvider(runtime_database_accesses),
        max_cached_pools=2,
        pool_max_size=2,
    )
    try:
        yield resolver
    finally:
        resolver.close()


def _seed(database_dsn: str) -> None:
    """Provision neutral catalog and principal fixtures through the administrative path."""

    with psycopg.connect(database_dsn, autocommit=True) as connection, connection.transaction():
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO brain_catalog.brains (brain_id, display_name) VALUES (%s, %s)",
                ("brain-neural", "Neural Brain"),
            )
            cursor.executemany(
                "INSERT INTO brain_catalog.tenants (tenant_id, brain_id, display_name) "
                "VALUES (%s, %s, %s)",
                (
                    ("tenant-a", "brain-neural", "Tenant A"),
                    ("tenant-b", "brain-neural", "Tenant B"),
                ),
            )
            cursor.executemany(
                "INSERT INTO brain_catalog.areas (tenant_id, area_id, display_name) "
                "VALUES (%s, %s, %s)",
                (
                    ("tenant-a", "area-a", "Area A"),
                    ("tenant-a", "area-b", "Area B"),
                    ("tenant-b", "area-a", "Other Tenant Area"),
                ),
            )
            cursor.executemany(
                "INSERT INTO brain_catalog.projects "
                "(tenant_id, area_id, project_id, display_name) VALUES (%s, %s, %s, %s)",
                (
                    ("tenant-a", "area-a", "project-a", "Project A"),
                    ("tenant-a", "area-b", "project-b", "Project B"),
                    ("tenant-b", "area-a", "project-a", "Other Project"),
                ),
            )
            cursor.executemany(
                "INSERT INTO brain_catalog.sessions "
                "(tenant_id, area_id, project_id, session_id, activity_state, activity_expires_at) "
                "VALUES (%s, %s, %s, %s, 'active', statement_timestamp() + interval '1 hour')",
                (
                    ("tenant-a", "area-a", "project-a", "session-a"),
                    ("tenant-a", "area-b", "project-b", "session-b"),
                    ("tenant-b", "area-a", "project-a", "session-a"),
                ),
            )
            cursor.executemany(
                "INSERT INTO brain_security.principals "
                "(principal_id, authenticated_subject) VALUES (%s, %s)",
                (
                    ("principal-a", "test://principal-a"),
                    ("principal-b", "test://principal-b"),
                    ("principal-c", "test://principal-c"),
                ),
            )
            cursor.executemany(
                "INSERT INTO brain_security.principal_scope_bindings "
                "(principal_id, tenant_id, area_id, can_ingest, can_read, can_dream) "
                "VALUES (%s, %s, %s, true, true, true)",
                (
                    ("principal-a", "tenant-a", "area-a"),
                    ("principal-b", "tenant-a", "area-b"),
                ),
            )
            cursor.execute(
                "INSERT INTO brain_security.principal_scope_bindings "
                "(principal_id, tenant_id, area_id, can_read) VALUES (%s, %s, %s, true)",
                ("principal-c", "tenant-b", "area-a"),
            )
