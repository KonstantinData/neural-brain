"""Install and provision the local Memory Core without weakening database gates."""

from __future__ import annotations

import time
import uuid
from collections.abc import Mapping
from pathlib import Path
from typing import Final

import psycopg
from psycopg import sql

from tools.bootstrap_database_roles import ROLE_NAMES, bootstrap_roles
from tools.validate_migrations import Migration, discover_migrations

INSTALL_LOCK_ID: Final = 6_826_005_939_411_273_457
PROVISIONING_LOCK_ID: Final = 8_002_627_327_335_360_689
INSTALL_LOCK_TIMEOUT_SECONDS: Final = 10.0
INSTALL_SCHEMA: Final = "neural_brain_install"
OWNER_ROLE: Final = "neural_brain_owner"
PRODUCT_SCHEMAS: Final[tuple[str, ...]] = (
    "brain_catalog",
    "brain_security",
    "memory_core",
    "memory_audit",
    "memory_gate",
)
RUNTIME_ROLES: Final[tuple[str, ...]] = ("neural_brain_gate", "neural_brain_reader")

DEMO_TENANT_ID: Final = "tenant-local-demo"
DEMO_AREA_ID: Final = "area-local-demo"
DEMO_PROJECT_ID: Final = "project-local-demo"
DEMO_SESSION_ID: Final = "session-local-demo"
DEMO_PRINCIPAL_ID: Final = "principal-local-demo"


def _verify_postgresql_18(connection: psycopg.Connection[tuple[object, ...]]) -> None:
    if connection.info.server_version // 10000 != 18:
        raise RuntimeError("Memory Core installation requires PostgreSQL 18")


def _acquire_install_lock(cursor: psycopg.Cursor[tuple[object, ...]]) -> None:
    deadline = time.monotonic() + INSTALL_LOCK_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        cursor.execute("SELECT pg_catalog.pg_try_advisory_lock(%s)", (INSTALL_LOCK_ID,))
        if cursor.fetchone() == (True,):
            return
        time.sleep(0.1)
    raise RuntimeError("Timed out waiting for the Memory Core installation lock")


def _acquire_provisioning_lock(cursor: psycopg.Cursor[tuple[object, ...]]) -> None:
    deadline = time.monotonic() + INSTALL_LOCK_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        cursor.execute("SELECT pg_catalog.pg_try_advisory_lock(%s)", (PROVISIONING_LOCK_ID,))
        if cursor.fetchone() == (True,):
            return
        time.sleep(0.1)
    raise RuntimeError("Timed out waiting for the Memory Core provisioning lock")


def _product_schema_exists(cursor: psycopg.Cursor[tuple[object, ...]]) -> bool:
    cursor.execute(
        "SELECT EXISTS (SELECT 1 FROM pg_catalog.pg_namespace WHERE nspname = ANY(%s))",
        (list(PRODUCT_SCHEMAS),),
    )
    row = cursor.fetchone()
    if row is None or not isinstance(row[0], bool):
        raise RuntimeError("Cannot determine the installed Memory Core schema state")
    return row[0]


def _schema_owner(cursor: psycopg.Cursor[tuple[object, ...]]) -> str | None:
    cursor.execute(
        "SELECT pg_catalog.pg_get_userbyid(nspowner) FROM pg_catalog.pg_namespace "
        "WHERE nspname = %s",
        (INSTALL_SCHEMA,),
    )
    row = cursor.fetchone()
    if row is None:
        return None
    if not isinstance(row[0], str):
        raise RuntimeError("The Memory Core install schema owner is malformed")
    return row[0]


def _verify_install_ledger_contract(cursor: psycopg.Cursor[tuple[object, ...]]) -> None:
    if _schema_owner(cursor) != OWNER_ROLE:
        raise RuntimeError("The Memory Core install schema has an untrusted owner")
    cursor.execute(
        "SELECT relation.relkind, relation.relpersistence, relation.relrowsecurity, "
        "relation.relforcerowsecurity, pg_catalog.pg_get_userbyid(relation.relowner) "
        "FROM pg_catalog.pg_class AS relation "
        "JOIN pg_catalog.pg_namespace AS namespace ON namespace.oid = relation.relnamespace "
        "WHERE namespace.nspname = %s AND relation.relname = 'schema_migrations'",
        (INSTALL_SCHEMA,),
    )
    if cursor.fetchone() != ("r", "p", False, False, OWNER_ROLE):
        raise RuntimeError("The Memory Core migration ledger relation is untrusted")
    cursor.execute(
        "SELECT count(*) FROM pg_catalog.pg_namespace AS namespace "
        "CROSS JOIN LATERAL pg_catalog.aclexplode(COALESCE(namespace.nspacl, "
        "pg_catalog.acldefault('n', namespace.nspowner))) AS acl "
        "WHERE namespace.nspname = %s AND acl.grantee <> namespace.nspowner",
        (INSTALL_SCHEMA,),
    )
    if cursor.fetchone() != (0,):
        raise RuntimeError("The Memory Core install schema has an untrusted ACL")
    cursor.execute(
        "SELECT count(*) FROM pg_catalog.pg_class AS relation "
        "JOIN pg_catalog.pg_namespace AS namespace ON namespace.oid = relation.relnamespace "
        "CROSS JOIN LATERAL pg_catalog.aclexplode(COALESCE(relation.relacl, "
        "pg_catalog.acldefault('r', relation.relowner))) AS acl "
        "WHERE namespace.nspname = %s AND relation.relname = 'schema_migrations' "
        "AND acl.grantee <> relation.relowner",
        (INSTALL_SCHEMA,),
    )
    if cursor.fetchone() != (0,):
        raise RuntimeError("The Memory Core migration ledger has an untrusted ACL")
    cursor.execute(
        "SELECT count(*) FROM pg_catalog.pg_attribute AS attribute "
        "JOIN pg_catalog.pg_class AS relation ON relation.oid = attribute.attrelid "
        "JOIN pg_catalog.pg_namespace AS namespace ON namespace.oid = relation.relnamespace "
        "WHERE namespace.nspname = %s AND relation.relname = 'schema_migrations' "
        "AND attribute.attnum > 0 AND NOT attribute.attisdropped "
        "AND attribute.attacl IS NOT NULL",
        (INSTALL_SCHEMA,),
    )
    if cursor.fetchone() != (0,):
        raise RuntimeError("The Memory Core migration ledger has an untrusted column ACL")
    cursor.execute(
        "SELECT attribute.attname, pg_catalog.format_type(attribute.atttypid, attribute.atttypmod), "
        "attribute.attnotnull, COALESCE(pg_catalog.pg_get_expr(default_value.adbin, "
        "default_value.adrelid), '') "
        "FROM pg_catalog.pg_attribute AS attribute "
        "JOIN pg_catalog.pg_class AS relation ON relation.oid = attribute.attrelid "
        "JOIN pg_catalog.pg_namespace AS namespace ON namespace.oid = relation.relnamespace "
        "LEFT JOIN pg_catalog.pg_attrdef AS default_value "
        "ON default_value.adrelid = relation.oid AND default_value.adnum = attribute.attnum "
        "WHERE namespace.nspname = %s AND relation.relname = 'schema_migrations' "
        "AND attribute.attnum > 0 AND NOT attribute.attisdropped ORDER BY attribute.attnum",
        (INSTALL_SCHEMA,),
    )
    if cursor.fetchall() != [
        ("sequence", "integer", True, ""),
        ("name", "text", True, ""),
        ("content_sha256", "text", True, ""),
        ("applied_at", "timestamp with time zone", True, "transaction_timestamp()"),
    ]:
        raise RuntimeError("The Memory Core migration ledger columns are untrusted")
    cursor.execute(
        "SELECT constraint_record.contype, pg_catalog.pg_get_constraintdef(constraint_record.oid) "
        "FROM pg_catalog.pg_constraint AS constraint_record "
        "JOIN pg_catalog.pg_class AS relation ON relation.oid = constraint_record.conrelid "
        "JOIN pg_catalog.pg_namespace AS namespace ON namespace.oid = relation.relnamespace "
        "WHERE namespace.nspname = %s AND relation.relname = 'schema_migrations' "
        "ORDER BY constraint_record.contype, pg_catalog.pg_get_constraintdef(constraint_record.oid)",
        (INSTALL_SCHEMA,),
    )
    constraints = {(str(row[0]), str(row[1])) for row in cursor.fetchall()}
    expected_constraints = {
        ("c", "CHECK ((sequence > 0))"),
        ("c", "CHECK ((content_sha256 ~ '^[0-9a-f]{64}$'::text))"),
        ("n", "NOT NULL applied_at"),
        ("n", "NOT NULL content_sha256"),
        ("n", "NOT NULL name"),
        ("n", "NOT NULL sequence"),
        ("p", "PRIMARY KEY (sequence)"),
        ("u", "UNIQUE (name)"),
    }
    if constraints != expected_constraints:
        raise RuntimeError("The Memory Core migration ledger constraints are untrusted")
    cursor.execute(
        "SELECT relation.relname, relation.relkind FROM pg_catalog.pg_class AS relation "
        "JOIN pg_catalog.pg_namespace AS namespace ON namespace.oid = relation.relnamespace "
        "WHERE namespace.nspname = %s AND relation.relkind NOT IN ('i', 'I') "
        "ORDER BY relation.relname",
        (INSTALL_SCHEMA,),
    )
    if cursor.fetchall() != [("schema_migrations", "r")]:
        raise RuntimeError("The Memory Core install schema contains unexpected relations")
    cursor.execute(
        "SELECT count(*) FROM pg_catalog.pg_proc AS routine "
        "JOIN pg_catalog.pg_namespace AS namespace ON namespace.oid = routine.pronamespace "
        "WHERE namespace.nspname = %s",
        (INSTALL_SCHEMA,),
    )
    if cursor.fetchone() != (0,):
        raise RuntimeError("The Memory Core install schema contains unexpected routines")
    cursor.execute(
        "SELECT count(*) FROM pg_catalog.pg_trigger AS trigger_record "
        "JOIN pg_catalog.pg_class AS relation ON relation.oid = trigger_record.tgrelid "
        "JOIN pg_catalog.pg_namespace AS namespace ON namespace.oid = relation.relnamespace "
        "WHERE namespace.nspname = %s AND NOT trigger_record.tgisinternal",
        (INSTALL_SCHEMA,),
    )
    if cursor.fetchone() != (0,):
        raise RuntimeError("The Memory Core migration ledger contains unexpected triggers")


def _ensure_install_ledger(connection: psycopg.Connection[tuple[object, ...]]) -> None:
    with connection.transaction(), connection.cursor() as cursor:
        owner = _schema_owner(cursor)
        if owner is None:
            cursor.execute(
                sql.SQL("CREATE SCHEMA {} AUTHORIZATION {}").format(
                    sql.Identifier(INSTALL_SCHEMA), sql.Identifier(OWNER_ROLE)
                )
            )
        elif owner != OWNER_ROLE:
            raise RuntimeError("The Memory Core install schema has an untrusted owner")
        cursor.execute(
            "SELECT pg_catalog.to_regclass(%s)", (f"{INSTALL_SCHEMA}.schema_migrations",)
        )
        ledger_exists = cursor.fetchone() != (None,)
        if not ledger_exists:
            cursor.execute(
                sql.SQL(
                    "CREATE TABLE {}.schema_migrations ("
                    "sequence integer PRIMARY KEY CHECK (sequence > 0), "
                    "name text NOT NULL UNIQUE, "
                    "content_sha256 text NOT NULL CHECK (content_sha256 ~ '^[0-9a-f]{{64}}$'), "
                    "applied_at timestamptz NOT NULL DEFAULT transaction_timestamp())"
                ).format(sql.Identifier(INSTALL_SCHEMA))
            )
            cursor.execute(
                sql.SQL("ALTER TABLE {}.schema_migrations OWNER TO {}").format(
                    sql.Identifier(INSTALL_SCHEMA), sql.Identifier(OWNER_ROLE)
                )
            )
        cursor.execute(
            sql.SQL("REVOKE ALL ON SCHEMA {} FROM PUBLIC").format(sql.Identifier(INSTALL_SCHEMA))
        )
        cursor.execute(
            sql.SQL("REVOKE ALL ON TABLE {}.schema_migrations FROM PUBLIC").format(
                sql.Identifier(INSTALL_SCHEMA)
            )
        )
        _verify_install_ledger_contract(cursor)


def _read_applied_migrations(
    cursor: psycopg.Cursor[tuple[object, ...]],
) -> tuple[tuple[int, str, str], ...]:
    cursor.execute(
        sql.SQL(
            "SELECT sequence, name, content_sha256 FROM {}.schema_migrations ORDER BY sequence"
        ).format(sql.Identifier(INSTALL_SCHEMA))
    )
    applied: list[tuple[int, str, str]] = []
    for sequence, name, content_sha256 in cursor.fetchall():
        if (
            not isinstance(sequence, int)
            or not isinstance(name, str)
            or not isinstance(content_sha256, str)
        ):
            raise RuntimeError("The Memory Core migration ledger is malformed")
        applied.append((sequence, name, content_sha256))
    return tuple(applied)


def _verify_applied_prefix(
    applied: tuple[tuple[int, str, str], ...], migrations: tuple[Migration, ...]
) -> None:
    if len(applied) > len(migrations):
        raise RuntimeError("The database contains migrations absent from this checkout")
    for expected_sequence, (sequence, name, content_sha256) in enumerate(applied, start=1):
        migration = migrations[expected_sequence - 1]
        if sequence != expected_sequence:
            raise RuntimeError("The Memory Core migration ledger is not contiguous")
        if name != migration.name or content_sha256 != migration.content_sha256:
            raise RuntimeError(f"Migration checksum drift detected at sequence {sequence:04d}")


def apply_migrations(admin_dsn: str, migrations_dir: Path) -> int:
    """Apply each pending migration atomically under a bounded advisory lock."""

    migrations = discover_migrations(migrations_dir)
    with psycopg.connect(admin_dsn, autocommit=True) as connection:
        _verify_postgresql_18(connection)
        with connection.cursor() as cursor:
            _acquire_install_lock(cursor)
        try:
            _ensure_install_ledger(connection)
            with connection.cursor() as cursor:
                applied = _read_applied_migrations(cursor)
                if not applied and _product_schema_exists(cursor):
                    raise RuntimeError(
                        "Existing product schemas have no trusted migration ledger; refusing adoption"
                    )
            _verify_applied_prefix(applied, migrations)
            for migration in migrations[len(applied) :]:
                with connection.transaction(), connection.cursor() as cursor:
                    cursor.execute(migration.sql, prepare=False)
                    cursor.execute(
                        sql.SQL(
                            "INSERT INTO {}.schema_migrations "
                            "(sequence, name, content_sha256) VALUES (%s, %s, %s)"
                        ).format(sql.Identifier(INSTALL_SCHEMA)),
                        (migration.sequence, migration.name, migration.content_sha256),
                    )
        finally:
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_catalog.pg_advisory_unlock(%s)", (INSTALL_LOCK_ID,))
    return len(migrations)


def harden_local_database_ownership(admin_dsn: str, runtime_role: str) -> None:
    """Move database ownership to the fixed NOLOGIN owner and restrict the runtime login."""

    with psycopg.connect(admin_dsn, autocommit=True) as connection, connection.cursor() as cursor:
        _verify_postgresql_18(connection)
        cursor.execute(
            "SELECT current_database(), pg_catalog.pg_get_userbyid(datdba) "
            "FROM pg_catalog.pg_database WHERE datname = current_database()"
        )
        row = cursor.fetchone()
        if row is None or not isinstance(row[0], str) or not isinstance(row[1], str):
            raise RuntimeError("Cannot determine the local Memory Core database owner")
        database_name, owner = row
        if owner == runtime_role:
            cursor.execute(
                sql.SQL("ALTER DATABASE {} OWNER TO {}").format(
                    sql.Identifier(database_name), sql.Identifier(OWNER_ROLE)
                )
            )
        elif owner != OWNER_ROLE:
            raise RuntimeError("The local Memory Core database has an untrusted owner")
        cursor.execute(
            sql.SQL("REVOKE ALL ON DATABASE {} FROM {}").format(
                sql.Identifier(database_name), sql.Identifier(runtime_role)
            )
        )
        cursor.execute(
            sql.SQL("REVOKE ALL ON DATABASE {} FROM PUBLIC").format(sql.Identifier(database_name))
        )
        cursor.execute(
            sql.SQL("GRANT CONNECT ON DATABASE {} TO {}").format(
                sql.Identifier(database_name), sql.Identifier(runtime_role)
            )
        )
        cursor.execute("REVOKE ALL ON SCHEMA public FROM PUBLIC")
        cursor.execute(
            sql.SQL("REVOKE ALL ON SCHEMA public FROM {}").format(sql.Identifier(runtime_role))
        )
        cursor.execute(
            "SELECT EXISTS ("
            "SELECT 1 FROM pg_catalog.pg_namespace WHERE nspname NOT LIKE 'pg_temp_%%' "
            "AND pg_catalog.pg_get_userbyid(nspowner) = %s UNION ALL "
            "SELECT 1 FROM pg_catalog.pg_class AS relation "
            "JOIN pg_catalog.pg_namespace AS namespace ON namespace.oid = relation.relnamespace "
            "WHERE namespace.nspname NOT LIKE 'pg_temp_%%' "
            "AND pg_catalog.pg_get_userbyid(relation.relowner) = %s)",
            (runtime_role, runtime_role),
        )
        if cursor.fetchone() != (False,):
            raise RuntimeError("The runtime role owns protected database objects")


def _expected_fixed_role_memberships(runtime_role: str) -> list[tuple[str, str, bool, bool, bool]]:
    return [
        ("neural_brain_gate", runtime_role, False, False, True),
        ("neural_brain_reader", runtime_role, False, False, True),
    ]


def _read_fixed_role_memberships(
    cursor: psycopg.Cursor[tuple[object, ...]], runtime_role: str
) -> list[tuple[object, ...]]:
    cursor.execute(
        "SELECT granted.rolname, member.rolname, membership.admin_option, "
        "membership.inherit_option, membership.set_option "
        "FROM pg_catalog.pg_auth_members AS membership "
        "JOIN pg_catalog.pg_roles AS granted ON granted.oid = membership.roleid "
        "JOIN pg_catalog.pg_roles AS member ON member.oid = membership.member "
        "WHERE granted.rolname = ANY(%s) OR member.rolname = ANY(%s) "
        "OR member.rolname = %s ORDER BY granted.rolname, member.rolname",
        (list(ROLE_NAMES), list(ROLE_NAMES), runtime_role),
    )
    return cursor.fetchall()


def _verify_runtime_role(cursor: psycopg.Cursor[tuple[object, ...]], runtime_role: str) -> None:
    cursor.execute(
        "SELECT rolcanlogin, rolsuper, rolcreaterole, rolcreatedb, rolreplication, "
        "rolinherit, rolbypassrls FROM pg_catalog.pg_roles WHERE rolname = %s",
        (runtime_role,),
    )
    if cursor.fetchone() != (True, False, False, False, False, False, False):
        raise RuntimeError(
            "The runtime role must be a NOINHERIT login without administrative attributes"
        )


def validate_fixed_role_graph(admin_dsn: str, runtime_role: str) -> None:
    """Reject compromised fixed roles before assigning protected ownership."""

    with psycopg.connect(admin_dsn, autocommit=True) as connection, connection.cursor() as cursor:
        _verify_postgresql_18(connection)
        _verify_runtime_role(cursor, runtime_role)
        expected = set(_expected_fixed_role_memberships(runtime_role))
        if not set(_read_fixed_role_memberships(cursor, runtime_role)).issubset(expected):
            raise RuntimeError("The fixed role memberships are not least-privilege")


def grant_runtime_roles(admin_dsn: str, runtime_role: str) -> None:
    """Grant exactly the ingest and read gate roles to one restricted login."""

    with (
        psycopg.connect(admin_dsn, autocommit=True) as connection,
        connection.transaction(),
        connection.cursor() as cursor,
    ):
        _verify_postgresql_18(connection)
        _verify_runtime_role(cursor, runtime_role)
        expected = _expected_fixed_role_memberships(runtime_role)
        if not set(_read_fixed_role_memberships(cursor, runtime_role)).issubset(set(expected)):
            raise RuntimeError("The fixed role memberships are not least-privilege")
        for role_name in RUNTIME_ROLES:
            cursor.execute(
                sql.SQL("GRANT {} TO {} WITH ADMIN FALSE, INHERIT FALSE, SET TRUE").format(
                    sql.Identifier(role_name), sql.Identifier(runtime_role)
                )
            )
        if _read_fixed_role_memberships(cursor, runtime_role) != expected:
            raise RuntimeError("The fixed role memberships are not least-privilege")


def verify_product_acl_contract(admin_dsn: str, runtime_role: str) -> None:
    """Reject direct access that could bypass protected database gates."""

    with psycopg.connect(admin_dsn, autocommit=True) as connection, connection.cursor() as cursor:
        _verify_postgresql_18(connection)
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
        if cursor.fetchall() != [(runtime_role, "CONNECT", False)]:
            raise RuntimeError("The Memory Core database has an untrusted ACL")
        cursor.execute(
            "SELECT count(*) FROM pg_catalog.pg_namespace AS namespace "
            "CROSS JOIN LATERAL pg_catalog.aclexplode(COALESCE(namespace.nspacl, "
            "pg_catalog.acldefault('n', namespace.nspowner))) AS acl "
            "WHERE namespace.nspname = 'public' AND acl.grantee <> namespace.nspowner"
        )
        if cursor.fetchone() != (0,):
            raise RuntimeError("The public schema has an untrusted ACL")
        cursor.execute(
            "SELECT namespace.nspname, COALESCE(grantee.rolname, 'PUBLIC'), "
            "acl.privilege_type, acl.is_grantable "
            "FROM pg_catalog.pg_namespace AS namespace "
            "CROSS JOIN LATERAL pg_catalog.aclexplode(COALESCE(namespace.nspacl, "
            "pg_catalog.acldefault('n', namespace.nspowner))) AS acl "
            "LEFT JOIN pg_catalog.pg_roles AS grantee ON grantee.oid = acl.grantee "
            "WHERE namespace.nspname = ANY(%s) AND acl.grantee <> namespace.nspowner "
            "ORDER BY 1, 2, 3",
            (list(PRODUCT_SCHEMAS),),
        )
        expected_schema_acls = sorted(
            (schema_name, role_name, "USAGE", False)
            for schema_name in PRODUCT_SCHEMAS
            for role_name in ROLE_NAMES[1:]
        )
        if cursor.fetchall() != expected_schema_acls:
            raise RuntimeError("A Memory Core product schema has an untrusted ACL")
        cursor.execute(
            "SELECT namespace.nspname, relation.relname, "
            "COALESCE(grantee.rolname, 'PUBLIC'), acl.privilege_type, acl.is_grantable "
            "FROM pg_catalog.pg_class AS relation "
            "JOIN pg_catalog.pg_namespace AS namespace ON namespace.oid = relation.relnamespace "
            "CROSS JOIN LATERAL pg_catalog.aclexplode(COALESCE(relation.relacl, "
            "pg_catalog.acldefault(CASE WHEN relation.relkind = 'S' THEN 'S'::\"char\" "
            "ELSE 'r'::\"char\" END, relation.relowner))) AS acl "
            "LEFT JOIN pg_catalog.pg_roles AS grantee ON grantee.oid = acl.grantee "
            "WHERE namespace.nspname = ANY(%s) AND acl.grantee <> relation.relowner "
            "ORDER BY 1, 2, 3, 4",
            (list(PRODUCT_SCHEMAS),),
        )
        readable_catalog_relations = ("areas", "projects", "sessions", "tenants")
        expected_relation_acls = sorted(
            ("brain_catalog", relation_name, role_name, "SELECT", False)
            for relation_name in readable_catalog_relations
            for role_name in ROLE_NAMES[1:]
        )
        if cursor.fetchall() != expected_relation_acls:
            raise RuntimeError("A Memory Core relation has an untrusted ACL")
        cursor.execute(
            "SELECT namespace.nspname, routine.proname, "
            "COALESCE(grantee.rolname, 'PUBLIC'), acl.privilege_type, acl.is_grantable "
            "FROM pg_catalog.pg_proc AS routine "
            "JOIN pg_catalog.pg_namespace AS namespace ON namespace.oid = routine.pronamespace "
            "CROSS JOIN LATERAL pg_catalog.aclexplode(COALESCE(routine.proacl, "
            "pg_catalog.acldefault('f', routine.proowner))) AS acl "
            "LEFT JOIN pg_catalog.pg_roles AS grantee ON grantee.oid = acl.grantee "
            "WHERE namespace.nspname = ANY(%s) AND acl.grantee <> routine.proowner "
            "ORDER BY 1, 2, 3, 4",
            (list(PRODUCT_SCHEMAS),),
        )
        expected_function_acls = sorted(
            [
                (
                    "brain_security",
                    "assert_scope_authority",
                    role_name,
                    "EXECUTE",
                    False,
                )
                for role_name in ROLE_NAMES[1:]
            ]
            + [("memory_gate", "commit_memory_cycle", "neural_brain_gate", "EXECUTE", False)]
            + [
                ("memory_gate", "read_checkpoint", role_name, "EXECUTE", False)
                for role_name in RUNTIME_ROLES
            ]
            + [
                (
                    "memory_gate",
                    "commit_cognitive_cycle",
                    "neural_brain_gate",
                    "EXECUTE",
                    False,
                )
            ]
            + [
                ("memory_gate", "read_cognitive_checkpoint", role_name, "EXECUTE", False)
                for role_name in RUNTIME_ROLES
            ]
        )
        if cursor.fetchall() != expected_function_acls:
            raise RuntimeError("A Memory Core function has an untrusted ACL")
        cursor.execute(
            "SELECT count(*) FROM pg_catalog.pg_attribute AS attribute "
            "JOIN pg_catalog.pg_class AS relation ON relation.oid = attribute.attrelid "
            "JOIN pg_catalog.pg_namespace AS namespace ON namespace.oid = relation.relnamespace "
            "WHERE namespace.nspname = ANY(%s) AND attribute.attnum > 0 "
            "AND NOT attribute.attisdropped AND attribute.attacl IS NOT NULL",
            (list(PRODUCT_SCHEMAS),),
        )
        if cursor.fetchone() != (0,):
            raise RuntimeError("A Memory Core relation has an untrusted column ACL")
        cursor.execute(
            "SELECT count(*) FROM pg_catalog.pg_namespace AS namespace "
            "WHERE namespace.nspname = ANY(%s) "
            "AND pg_catalog.pg_get_userbyid(namespace.nspowner) <> %s",
            (list(PRODUCT_SCHEMAS), OWNER_ROLE),
        )
        if cursor.fetchone() != (0,):
            raise RuntimeError("A Memory Core product schema has an untrusted owner")
        cursor.execute(
            "SELECT count(*) FROM pg_catalog.pg_class AS relation "
            "JOIN pg_catalog.pg_namespace AS namespace ON namespace.oid = relation.relnamespace "
            "WHERE namespace.nspname = ANY(%s) "
            "AND pg_catalog.pg_get_userbyid(relation.relowner) <> %s",
            (list(PRODUCT_SCHEMAS), OWNER_ROLE),
        )
        if cursor.fetchone() != (0,):
            raise RuntimeError("A Memory Core relation has an untrusted owner")
        cursor.execute(
            "SELECT count(*) FROM pg_catalog.pg_proc AS routine "
            "JOIN pg_catalog.pg_namespace AS namespace ON namespace.oid = routine.pronamespace "
            "WHERE namespace.nspname = ANY(%s) "
            "AND pg_catalog.pg_get_userbyid(routine.proowner) <> %s",
            (list(PRODUCT_SCHEMAS), OWNER_ROLE),
        )
        if cursor.fetchone() != (0,):
            raise RuntimeError("A Memory Core function has an untrusted owner")


def provision_local_demo_scope(admin_dsn: str) -> str:
    """Invoke the fixed authenticated administrative provisioning gate."""

    transition_request_id = f"local-demo-provision-{uuid.uuid4().hex}"
    with (
        psycopg.connect(admin_dsn, autocommit=True) as connection,
        connection.transaction(),
        connection.cursor() as cursor,
    ):
        _verify_postgresql_18(connection)
        cursor.execute(
            "SELECT brain_security.provision_local_demo_scope(%s)",
            (transition_request_id,),
        )
        row = cursor.fetchone()
        if row is None or not isinstance(row[0], Mapping):
            raise RuntimeError("The local demo provisioning gate returned malformed evidence")
        expected = {
            "principal_id": DEMO_PRINCIPAL_ID,
            "tenant_id": DEMO_TENANT_ID,
            "area_id": DEMO_AREA_ID,
            "project_id": DEMO_PROJECT_ID,
            "session_id": DEMO_SESSION_ID,
        }
        if any(row[0].get(key) != value for key, value in expected.items()):
            raise RuntimeError("The local demo provisioning gate returned conflicting scope")
        if not isinstance(row[0].get("authenticated_admin"), str):
            raise RuntimeError("The local demo provisioning gate omitted its authenticated actor")
    return transition_request_id


def install_local_memory_core(admin_dsn: str, runtime_role: str, migrations_dir: Path) -> int:
    """Install migrations, least-privilege runtime grants, and the fixed local demo scope."""

    with psycopg.connect(admin_dsn, autocommit=True) as connection, connection.cursor() as cursor:
        _verify_postgresql_18(connection)
        _acquire_provisioning_lock(cursor)
        try:
            bootstrap_roles(admin_dsn)
            validate_fixed_role_graph(admin_dsn, runtime_role)
            harden_local_database_ownership(admin_dsn, runtime_role)
            migration_count = apply_migrations(admin_dsn, migrations_dir)
            verify_product_acl_contract(admin_dsn, runtime_role)
            grant_runtime_roles(admin_dsn, runtime_role)
            verify_product_acl_contract(admin_dsn, runtime_role)
            provision_local_demo_scope(admin_dsn)
            return migration_count
        finally:
            cursor.execute("SELECT pg_catalog.pg_advisory_unlock(%s)", (PROVISIONING_LOCK_ID,))
