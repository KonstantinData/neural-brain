"""Live PostgreSQL evidence for the clean local Memory Core operator path."""

from __future__ import annotations

import os
import re
import secrets
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

import psycopg
import pytest
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict, make_conninfo

from tools.bootstrap_database_roles import bootstrap_roles
from tools.install_memory_core import (
    INSTALL_SCHEMA,
    OWNER_ROLE,
    apply_migrations,
    grant_runtime_roles,
    harden_local_database_ownership,
    install_local_memory_core,
    verify_product_acl_contract,
)
from tools.memory_demo import ROOT, run_memory_demo

DATABASE_PREFIX = "neural_brain_memory_demo_test_"
ROLE_PREFIX = "neural_brain_memory_demo_test_"


@dataclass(frozen=True, slots=True)
class DemoDatabase:
    """Disposable administrative and runtime connection details."""

    admin_dsn: str
    runtime_dsn: str
    runtime_role: str


def _generated_name(prefix: str) -> str:
    return f"{prefix}{secrets.token_hex(8)}"


def _assert_disposable(name: str, prefix: str) -> None:
    suffix = name.removeprefix(prefix)
    if not name.startswith(prefix) or re.fullmatch(r"[0-9a-f]{16}", suffix) is None:
        raise RuntimeError("Refusing cleanup outside the Memory Core demo test namespace")


@pytest.fixture
def demo_database() -> Iterator[DemoDatabase]:
    """Create an empty PostgreSQL 18 database with a separate restricted login."""

    cluster_admin_dsn = os.getenv("MIGRATION_ADMIN_DSN")
    if not cluster_admin_dsn:
        pytest.skip("MIGRATION_ADMIN_DSN is required for live PostgreSQL tests")
    database_name = _generated_name(DATABASE_PREFIX)
    runtime_role = _generated_name(ROLE_PREFIX)
    runtime_password = secrets.token_urlsafe(32)
    _assert_disposable(database_name, DATABASE_PREFIX)
    _assert_disposable(runtime_role, ROLE_PREFIX)
    role_created = False
    database_created = False
    primary_error: BaseException | None = None
    try:
        bootstrap_roles(cluster_admin_dsn)
        with (
            psycopg.connect(cluster_admin_dsn, autocommit=True) as connection,
            connection.cursor() as cursor,
        ):
            if connection.info.server_version // 10000 != 18:
                pytest.fail("live Memory Core demo tests require PostgreSQL 18")
            cursor.execute(
                sql.SQL(
                    "CREATE ROLE {} LOGIN PASSWORD {} NOSUPERUSER NOCREATEDB NOCREATEROLE "
                    "NOINHERIT NOREPLICATION NOBYPASSRLS"
                ).format(sql.Identifier(runtime_role), sql.Literal(runtime_password))
            )
            role_created = True
            cursor.execute(
                sql.SQL("CREATE DATABASE {} OWNER {}").format(
                    sql.Identifier(database_name), sql.Identifier(OWNER_ROLE)
                )
            )
            database_created = True

        admin_dsn = make_conninfo(cluster_admin_dsn, dbname=database_name)
        runtime_dsn = make_conninfo(
            cluster_admin_dsn,
            dbname=database_name,
            user=runtime_role,
            password=runtime_password,
        )
        yield DemoDatabase(
            admin_dsn=admin_dsn,
            runtime_dsn=runtime_dsn,
            runtime_role=runtime_role,
        )
    except BaseException as error:
        primary_error = error
        raise
    finally:
        cleanup_errors: list[str] = []
        if database_created:
            try:
                with (
                    psycopg.connect(cluster_admin_dsn, autocommit=True) as connection,
                    connection.cursor() as cursor,
                ):
                    cursor.execute(
                        sql.SQL("DROP DATABASE {} WITH (FORCE)").format(
                            sql.Identifier(database_name)
                        )
                    )
            except Exception as error:
                cleanup_errors.append(f"database cleanup: {type(error).__name__}")
        if role_created:
            try:
                with (
                    psycopg.connect(cluster_admin_dsn, autocommit=True) as connection,
                    connection.cursor() as cursor,
                ):
                    cursor.execute(sql.SQL("DROP ROLE {}").format(sql.Identifier(runtime_role)))
            except Exception as error:
                cleanup_errors.append(f"role cleanup: {type(error).__name__}")
        if cleanup_errors and primary_error is None:
            raise RuntimeError("; ".join(cleanup_errors))
        if cleanup_errors and primary_error is not None:
            primary_error.add_note("Cleanup also failed: " + "; ".join(cleanup_errors))


def test_clean_concurrent_install_round_trip_and_fail_closed_guards(
    demo_database: DemoDatabase,
) -> None:
    """The documented core installs concurrently, audits honestly, and denies unsafe state."""

    def execute_demo(_: int) -> dict[str, object]:
        return run_memory_demo(
            demo_database.admin_dsn,
            demo_database.runtime_dsn,
            demo_database.runtime_role,
        )

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = tuple(executor.map(execute_demo, range(2)))
    assert all(result["status"] == "passed" for result in results)
    assert all(result["audit_committed"] is True for result in results)
    assert all(result["checkpoint_readback"] is True for result in results)
    assert results[0]["checkpoint_id"] != results[1]["checkpoint_id"]

    with (
        psycopg.connect(demo_database.admin_dsn, autocommit=True) as connection,
        connection.cursor() as cursor,
    ):
        cursor.execute(
            sql.SQL("SELECT count(*) FROM {}.schema_migrations").format(
                sql.Identifier(INSTALL_SCHEMA)
            )
        )
        assert cursor.fetchone() == (6,)
        cursor.execute(
            "SELECT pg_catalog.pg_get_userbyid(datdba) FROM pg_catalog.pg_database "
            "WHERE datname = current_database()"
        )
        assert cursor.fetchone() == (OWNER_ROLE,)
        cursor.execute(
            "SELECT COALESCE(grantee.rolname, 'PUBLIC'), acl.privilege_type, "
            "acl.is_grantable "
            "FROM pg_catalog.pg_database AS database_record "
            "CROSS JOIN LATERAL pg_catalog.aclexplode(COALESCE(database_record.datacl, "
            "pg_catalog.acldefault('d', database_record.datdba))) AS acl "
            "LEFT JOIN pg_catalog.pg_roles AS grantee ON grantee.oid = acl.grantee "
            "WHERE database_record.datname = current_database() "
            "AND acl.grantee <> database_record.datdba ORDER BY 1, 2"
        )
        assert cursor.fetchall() == [(demo_database.runtime_role, "CONNECT", False)]
        cursor.execute(
            "SELECT count(*) FROM pg_catalog.pg_namespace AS namespace "
            "CROSS JOIN LATERAL pg_catalog.aclexplode(COALESCE(namespace.nspacl, "
            "pg_catalog.acldefault('n', namespace.nspowner))) AS acl "
            "WHERE namespace.nspname = 'public' AND acl.grantee <> namespace.nspowner"
        )
        assert cursor.fetchone() == (0,)
        cursor.execute(
            "SELECT event_type, count(*) FROM memory_audit.events "
            "GROUP BY event_type ORDER BY event_type"
        )
        assert cursor.fetchall() == [
            ("local_demo_scope_provisioned", 2),
            ("local_oidc_demo_principal_provisioned", 2),
            ("memory_cycle_committed", 2),
        ]
        cursor.execute(
            "SELECT principal_id, subject_kind, subject_id FROM memory_audit.events "
            "WHERE event_type = 'local_demo_scope_provisioned' LIMIT 1"
        )
        audit_actor, subject_kind, subject_id = cursor.fetchone() or (None, None, None)
        assert audit_actor == connection.info.user
        assert subject_kind == "principal_scope_binding"
        assert subject_id == "principal-local-demo"
        cursor.execute("SELECT count(*) FROM memory_core.transition_receipts")
        assert cursor.fetchone() == (2,)
        cursor.execute(
            "SELECT granted.rolname, membership.admin_option, membership.inherit_option, "
            "membership.set_option FROM pg_catalog.pg_auth_members AS membership "
            "JOIN pg_catalog.pg_roles AS granted ON granted.oid = membership.roleid "
            "JOIN pg_catalog.pg_roles AS member ON member.oid = membership.member "
            "WHERE member.rolname = %s ORDER BY granted.rolname",
            (demo_database.runtime_role,),
        )
        assert cursor.fetchall() == [
            ("neural_brain_gate", False, False, True),
            ("neural_brain_reader", False, False, True),
        ]

    with (
        psycopg.connect(demo_database.runtime_dsn, autocommit=True) as connection,
        connection.cursor() as cursor,
        pytest.raises(psycopg.errors.InsufficientPrivilege),
    ):
        cursor.execute("CREATE SCHEMA denied_runtime_ddl")

    with (
        psycopg.connect(demo_database.runtime_dsn, autocommit=True) as connection,
        connection.cursor() as cursor,
        pytest.raises(psycopg.errors.InsufficientPrivilege),
    ):
        cursor.execute("SELECT brain_security.provision_local_demo_scope('runtime-denied')")

    with psycopg.connect(demo_database.admin_dsn, autocommit=True) as connection:
        with connection.transaction(), connection.cursor() as cursor:
            cursor.execute(
                sql.SQL("REVOKE neural_brain_gate, neural_brain_reader FROM {}").format(
                    sql.Identifier(demo_database.runtime_role)
                )
            )
            cursor.execute(
                sql.SQL("GRANT {} TO {} WITH ADMIN FALSE, INHERIT FALSE, SET TRUE").format(
                    sql.Identifier(OWNER_ROLE), sql.Identifier(demo_database.runtime_role)
                )
            )
        with pytest.raises(RuntimeError, match="fixed role memberships"):
            grant_runtime_roles(demo_database.admin_dsn, demo_database.runtime_role)
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT granted.rolname FROM pg_catalog.pg_auth_members AS membership "
                "JOIN pg_catalog.pg_roles AS granted ON granted.oid = membership.roleid "
                "JOIN pg_catalog.pg_roles AS member ON member.oid = membership.member "
                "WHERE member.rolname = %s ORDER BY granted.rolname",
                (demo_database.runtime_role,),
            )
            assert cursor.fetchall() == [(OWNER_ROLE,)]
        with connection.transaction(), connection.cursor() as cursor:
            cursor.execute(
                sql.SQL("REVOKE {} FROM {}").format(
                    sql.Identifier(OWNER_ROLE), sql.Identifier(demo_database.runtime_role)
                )
            )
        grant_runtime_roles(demo_database.admin_dsn, demo_database.runtime_role)

    database_name = conninfo_to_dict(demo_database.admin_dsn).get("dbname")
    assert isinstance(database_name, str)
    acl_attacks = (
        (
            sql.SQL("GRANT CONNECT ON DATABASE {} TO neural_brain_dreamer").format(
                sql.Identifier(database_name)
            ),
            sql.SQL("REVOKE CONNECT ON DATABASE {} FROM neural_brain_dreamer").format(
                sql.Identifier(database_name)
            ),
            "database",
        ),
        (
            sql.SQL("GRANT CREATE ON SCHEMA brain_catalog TO {}").format(
                sql.Identifier(demo_database.runtime_role)
            ),
            sql.SQL("REVOKE CREATE ON SCHEMA brain_catalog FROM {}").format(
                sql.Identifier(demo_database.runtime_role)
            ),
            "product schema",
        ),
        (
            sql.SQL("GRANT UPDATE ON brain_catalog.tenants TO {}").format(
                sql.Identifier(demo_database.runtime_role)
            ),
            sql.SQL("REVOKE UPDATE ON brain_catalog.tenants FROM {}").format(
                sql.Identifier(demo_database.runtime_role)
            ),
            "relation",
        ),
        (
            sql.SQL(
                "GRANT EXECUTE ON FUNCTION brain_security.provision_local_demo_scope(text) TO {}"
            ).format(sql.Identifier(demo_database.runtime_role)),
            sql.SQL(
                "REVOKE EXECUTE ON FUNCTION brain_security.provision_local_demo_scope(text) FROM {}"
            ).format(sql.Identifier(demo_database.runtime_role)),
            "function",
        ),
        (
            sql.SQL("GRANT USAGE ON SCHEMA memory_core TO PUBLIC"),
            sql.SQL("REVOKE USAGE ON SCHEMA memory_core FROM PUBLIC"),
            "product schema",
        ),
        (
            sql.SQL("GRANT SELECT ON brain_catalog.tenants TO PUBLIC"),
            sql.SQL("REVOKE SELECT ON brain_catalog.tenants FROM PUBLIC"),
            "relation",
        ),
        (
            sql.SQL(
                "GRANT EXECUTE ON FUNCTION brain_security.provision_local_demo_scope(text) "
                "TO PUBLIC"
            ),
            sql.SQL(
                "REVOKE EXECUTE ON FUNCTION brain_security.provision_local_demo_scope(text) "
                "FROM PUBLIC"
            ),
            "function",
        ),
        (
            sql.SQL("GRANT USAGE ON SCHEMA brain_catalog TO neural_brain_gate WITH GRANT OPTION"),
            sql.SQL("REVOKE GRANT OPTION FOR USAGE ON SCHEMA brain_catalog FROM neural_brain_gate"),
            "product schema",
        ),
    )
    with psycopg.connect(demo_database.admin_dsn, autocommit=True) as connection:
        for grant_statement, revoke_statement, error_fragment in acl_attacks:
            with connection.transaction(), connection.cursor() as cursor:
                cursor.execute(grant_statement)
            with pytest.raises(RuntimeError, match=error_fragment):
                verify_product_acl_contract(demo_database.admin_dsn, demo_database.runtime_role)
            with connection.transaction(), connection.cursor() as cursor:
                cursor.execute(revoke_statement)
    verify_product_acl_contract(demo_database.admin_dsn, demo_database.runtime_role)

    with psycopg.connect(demo_database.admin_dsn, autocommit=True) as connection:
        with connection.transaction(), connection.cursor() as cursor:
            cursor.execute(
                sql.SQL("GRANT CREATE ON SCHEMA {} TO {}").format(
                    sql.Identifier(INSTALL_SCHEMA), sql.Identifier(demo_database.runtime_role)
                )
            )
        with pytest.raises(RuntimeError, match="untrusted ACL"):
            apply_migrations(demo_database.admin_dsn, ROOT / "migrations")
        with connection.transaction(), connection.cursor() as cursor:
            cursor.execute(
                sql.SQL("REVOKE ALL ON SCHEMA {} FROM {}").format(
                    sql.Identifier(INSTALL_SCHEMA), sql.Identifier(demo_database.runtime_role)
                )
            )
            cursor.execute(
                sql.SQL("GRANT UPDATE (content_sha256) ON {}.schema_migrations TO {}").format(
                    sql.Identifier(INSTALL_SCHEMA), sql.Identifier(demo_database.runtime_role)
                )
            )
        with pytest.raises(RuntimeError, match="untrusted column ACL"):
            apply_migrations(demo_database.admin_dsn, ROOT / "migrations")
        with connection.transaction(), connection.cursor() as cursor:
            cursor.execute(
                sql.SQL("REVOKE UPDATE (content_sha256) ON {}.schema_migrations FROM {}").format(
                    sql.Identifier(INSTALL_SCHEMA), sql.Identifier(demo_database.runtime_role)
                )
            )
        with connection.transaction(), connection.cursor() as cursor:
            cursor.execute(
                "UPDATE brain_catalog.areas SET status = 'retired' "
                "WHERE tenant_id = 'tenant-local-demo' AND area_id = 'area-local-demo'"
            )
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT count(*) FROM memory_audit.events "
                "WHERE event_type = 'local_demo_scope_provisioned'"
            )
            audit_count = cursor.fetchone()
        with (
            connection.transaction(),
            connection.cursor() as cursor,
            pytest.raises(psycopg.errors.ObjectNotInPrerequisiteState),
        ):
            cursor.execute(
                "SELECT brain_security.provision_local_demo_scope('conflicting-hierarchy')"
            )
        with connection.transaction(), connection.cursor() as cursor:
            cursor.execute(
                "UPDATE brain_catalog.areas SET status = 'active' "
                "WHERE tenant_id = 'tenant-local-demo' AND area_id = 'area-local-demo'"
            )
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT count(*) FROM memory_audit.events "
                "WHERE event_type = 'local_demo_scope_provisioned'"
            )
            assert cursor.fetchone() == audit_count

    with psycopg.connect(demo_database.admin_dsn, autocommit=True) as connection:
        with connection.transaction(), connection.cursor() as cursor:
            cursor.execute(
                sql.SQL("ALTER SCHEMA {} OWNER TO {}").format(
                    sql.Identifier(INSTALL_SCHEMA), sql.Identifier(demo_database.runtime_role)
                )
            )
        with pytest.raises(RuntimeError, match="untrusted owner"):
            apply_migrations(demo_database.admin_dsn, ROOT / "migrations")
        with connection.transaction(), connection.cursor() as cursor:
            cursor.execute(
                sql.SQL("ALTER SCHEMA {} OWNER TO {}").format(
                    sql.Identifier(INSTALL_SCHEMA), sql.Identifier(OWNER_ROLE)
                )
            )
            cursor.execute(
                sql.SQL(
                    "UPDATE {}.schema_migrations SET content_sha256 = %s WHERE sequence = 1"
                ).format(sql.Identifier(INSTALL_SCHEMA)),
                ("0" * 64,),
            )
    with pytest.raises(RuntimeError, match="checksum drift"):
        apply_migrations(demo_database.admin_dsn, ROOT / "migrations")


def test_compromised_owner_membership_is_rejected_before_schema_mutation(
    demo_database: DemoDatabase,
) -> None:
    """A rogue fixed-role edge must stop the first install before migrations."""

    with psycopg.connect(demo_database.admin_dsn, autocommit=True) as connection:
        with connection.transaction(), connection.cursor() as cursor:
            cursor.execute(
                sql.SQL("GRANT {} TO {} WITH ADMIN FALSE, INHERIT FALSE, SET TRUE").format(
                    sql.Identifier(OWNER_ROLE), sql.Identifier(demo_database.runtime_role)
                )
            )
        with pytest.raises(RuntimeError, match="fixed role memberships"):
            install_local_memory_core(
                demo_database.admin_dsn,
                demo_database.runtime_role,
                ROOT / "migrations",
            )
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT pg_catalog.to_regnamespace(%s), pg_catalog.to_regnamespace('memory_core')",
                (INSTALL_SCHEMA,),
            )
            assert cursor.fetchone() == (None, None)
        with connection.transaction(), connection.cursor() as cursor:
            cursor.execute(
                sql.SQL("REVOKE {} FROM {}").format(
                    sql.Identifier(OWNER_ROLE), sql.Identifier(demo_database.runtime_role)
                )
            )
        harden_local_database_ownership(demo_database.admin_dsn, demo_database.runtime_role)
        apply_migrations(demo_database.admin_dsn, ROOT / "migrations")
        with connection.transaction(), connection.cursor() as cursor:
            cursor.execute("GRANT SELECT ON brain_catalog.tenants TO PUBLIC")
        with pytest.raises(RuntimeError, match="relation"):
            install_local_memory_core(
                demo_database.admin_dsn,
                demo_database.runtime_role,
                ROOT / "migrations",
            )
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT count(*) FROM pg_catalog.pg_auth_members AS membership "
                "JOIN pg_catalog.pg_roles AS member ON member.oid = membership.member "
                "WHERE member.rolname = %s",
                (demo_database.runtime_role,),
            )
            assert cursor.fetchone() == (0,)
