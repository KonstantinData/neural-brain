"""Validate ordered PostgreSQL migrations in disposable PostgreSQL 18 databases."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import secrets
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Final

import psycopg
from psycopg import sql
from psycopg.conninfo import make_conninfo

ROOT: Final = Path(__file__).resolve().parents[1]
MIGRATION_NAME: Final = re.compile(r"^(?P<sequence>[0-9]{4})_[a-z0-9]+(?:_[a-z0-9]+)*\.sql$")
TRANSACTION_CONTROL: Final = re.compile(
    r"(?im)^\s*(?:BEGIN|START\s+TRANSACTION|COMMIT|ROLLBACK|SAVEPOINT|RELEASE\s+SAVEPOINT)\b"
)
DOLLAR_QUOTED_BODY: Final = re.compile(
    r"\$(?P<tag>[A-Za-z_][A-Za-z0-9_]*|)\$.*?\$(?P=tag)\$", re.DOTALL
)
DATABASE_PREFIX: Final = "neural_brain_migration_validation_"


@dataclass(frozen=True, slots=True)
class Migration:
    """One validated migration file."""

    sequence: int
    name: str
    path: Path
    sql: str
    content_sha256: str


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """Digest evidence produced by a complete migration validation run."""

    migration_count: int
    plan_sha256: str
    fresh_schema_sha256: str
    upgraded_schema_sha256: str


SCHEMA_QUERIES: Final[tuple[tuple[str, str], ...]] = (
    (
        "schema",
        """
        SELECT n.nspname, COALESCE(n.nspacl::text, ''), COALESCE(obj_description(n.oid, 'pg_namespace'), '')
        FROM pg_catalog.pg_namespace AS n
        WHERE n.nspname NOT LIKE 'pg_%' AND n.nspname <> 'information_schema'
        ORDER BY n.nspname
        """,
    ),
    (
        "relation",
        """
        SELECT n.nspname, c.relname, c.relkind, c.relpersistence, c.relrowsecurity,
               c.relforcerowsecurity, COALESCE(c.relacl::text, '')
        FROM pg_catalog.pg_class AS c
        JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace
        WHERE n.nspname NOT LIKE 'pg_%' AND n.nspname <> 'information_schema'
          AND c.relkind IN ('r', 'p', 'v', 'm', 'S', 'f')
        ORDER BY n.nspname, c.relname, c.relkind
        """,
    ),
    (
        "column",
        """
        SELECT n.nspname, c.relname, a.attnum, a.attname,
               pg_catalog.format_type(a.atttypid, a.atttypmod), a.attnotnull,
               a.attidentity, a.attgenerated,
               COALESCE(pg_catalog.pg_get_expr(d.adbin, d.adrelid), ''),
               COALESCE(coll.collname, '')
        FROM pg_catalog.pg_attribute AS a
        JOIN pg_catalog.pg_class AS c ON c.oid = a.attrelid
        JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace
        LEFT JOIN pg_catalog.pg_attrdef AS d ON d.adrelid = a.attrelid AND d.adnum = a.attnum
        LEFT JOIN pg_catalog.pg_collation AS coll ON coll.oid = a.attcollation
        WHERE n.nspname NOT LIKE 'pg_%' AND n.nspname <> 'information_schema'
          AND a.attnum > 0 AND NOT a.attisdropped
          AND c.relkind IN ('r', 'p', 'v', 'm', 'f')
        ORDER BY n.nspname, c.relname, a.attnum
        """,
    ),
    (
        "sequence",
        """
        SELECT schemaname, sequencename, data_type, start_value, min_value, max_value,
               increment_by, cycle, cache_size
        FROM pg_catalog.pg_sequences
        WHERE schemaname NOT LIKE 'pg_%' AND schemaname <> 'information_schema'
        ORDER BY schemaname, sequencename
        """,
    ),
    (
        "constraint",
        """
        SELECT n.nspname, c.relname, con.conname, con.contype,
               pg_catalog.pg_get_constraintdef(con.oid, true)
        FROM pg_catalog.pg_constraint AS con
        JOIN pg_catalog.pg_class AS c ON c.oid = con.conrelid
        JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace
        WHERE n.nspname NOT LIKE 'pg_%' AND n.nspname <> 'information_schema'
        ORDER BY n.nspname, c.relname, con.conname
        """,
    ),
    (
        "index",
        """
        SELECT n.nspname, c.relname, i.relname, pg_catalog.pg_get_indexdef(i.oid)
        FROM pg_catalog.pg_index AS x
        JOIN pg_catalog.pg_class AS c ON c.oid = x.indrelid
        JOIN pg_catalog.pg_class AS i ON i.oid = x.indexrelid
        JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace
        WHERE n.nspname NOT LIKE 'pg_%' AND n.nspname <> 'information_schema'
        ORDER BY n.nspname, c.relname, i.relname
        """,
    ),
    (
        "view",
        """
        SELECT n.nspname, c.relname, pg_catalog.pg_get_viewdef(c.oid, true)
        FROM pg_catalog.pg_class AS c
        JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace
        WHERE n.nspname NOT LIKE 'pg_%' AND n.nspname <> 'information_schema'
          AND c.relkind IN ('v', 'm')
        ORDER BY n.nspname, c.relname
        """,
    ),
    (
        "routine",
        """
        SELECT n.nspname, p.proname, p.prokind,
               pg_catalog.pg_get_function_identity_arguments(p.oid),
               pg_catalog.pg_get_function_result(p.oid),
               pg_catalog.pg_get_functiondef(p.oid)
        FROM pg_catalog.pg_proc AS p
        JOIN pg_catalog.pg_namespace AS n ON n.oid = p.pronamespace
        WHERE n.nspname NOT LIKE 'pg_%' AND n.nspname <> 'information_schema'
        ORDER BY n.nspname, p.proname, pg_catalog.pg_get_function_identity_arguments(p.oid)
        """,
    ),
    (
        "trigger",
        """
        SELECT n.nspname, c.relname, t.tgname, pg_catalog.pg_get_triggerdef(t.oid, true)
        FROM pg_catalog.pg_trigger AS t
        JOIN pg_catalog.pg_class AS c ON c.oid = t.tgrelid
        JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace
        WHERE n.nspname NOT LIKE 'pg_%' AND n.nspname <> 'information_schema'
          AND NOT t.tgisinternal
        ORDER BY n.nspname, c.relname, t.tgname
        """,
    ),
    (
        "policy",
        """
        SELECT schemaname, tablename, policyname, permissive, roles::text,
               cmd, COALESCE(qual, ''), COALESCE(with_check, '')
        FROM pg_catalog.pg_policies
        WHERE schemaname NOT LIKE 'pg_%' AND schemaname <> 'information_schema'
        ORDER BY schemaname, tablename, policyname
        """,
    ),
    (
        "enum",
        """
        SELECT n.nspname, t.typname, e.enumsortorder, e.enumlabel
        FROM pg_catalog.pg_enum AS e
        JOIN pg_catalog.pg_type AS t ON t.oid = e.enumtypid
        JOIN pg_catalog.pg_namespace AS n ON n.oid = t.typnamespace
        WHERE n.nspname NOT LIKE 'pg_%' AND n.nspname <> 'information_schema'
        ORDER BY n.nspname, t.typname, e.enumsortorder
        """,
    ),
    (
        "extension",
        """
        SELECT e.extname, e.extversion, n.nspname
        FROM pg_catalog.pg_extension AS e
        JOIN pg_catalog.pg_namespace AS n ON n.oid = e.extnamespace
        WHERE e.extname <> 'plpgsql'
        ORDER BY e.extname
        """,
    ),
)


def _normalized_sql(path: Path) -> str:
    try:
        raw = path.read_bytes()
        text = raw.decode("utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise ValueError(f"Cannot read migration as UTF-8: {path.name}") from error
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    if not normalized.strip():
        raise ValueError(f"Migration is empty: {path.name}")
    top_level_sql = DOLLAR_QUOTED_BODY.sub("$body$", normalized)
    if TRANSACTION_CONTROL.search(top_level_sql):
        raise ValueError(f"Migration contains transaction control: {path.name}")
    return normalized


def discover_migrations(directory: Path, *, allow_empty: bool = False) -> tuple[Migration, ...]:
    """Return a validated contiguous migration plan."""

    if not directory.is_dir():
        raise ValueError(f"Migration directory does not exist: {directory}")
    paths = sorted(directory.glob("*.sql"))
    if not paths and not allow_empty:
        raise ValueError(
            "No migration files found; use --allow-empty only before the first schema slice"
        )

    migrations: list[Migration] = []
    for expected_sequence, path in enumerate(paths, start=1):
        match = MIGRATION_NAME.fullmatch(path.name)
        if match is None:
            raise ValueError(f"Invalid migration filename: {path.name}")
        sequence = int(match.group("sequence"))
        if sequence != expected_sequence:
            raise ValueError(
                f"Migration sequence must be contiguous from 0001: expected {expected_sequence:04d}, "
                f"found {sequence:04d}"
            )
        migration_sql = _normalized_sql(path)
        migrations.append(
            Migration(
                sequence=sequence,
                name=path.name,
                path=path,
                sql=migration_sql,
                content_sha256=hashlib.sha256(migration_sql.encode("utf-8")).hexdigest(),
            )
        )
    return tuple(migrations)


def migration_plan_digest(migrations: tuple[Migration, ...]) -> str:
    """Return a stable digest of names, order, and normalized content."""

    payload = [
        {"sequence": item.sequence, "name": item.name, "sha256": item.content_sha256}
        for item in migrations
    ]
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _database_name() -> str:
    return f"{DATABASE_PREFIX}{secrets.token_hex(8)}"


def validate_disposable_database_name(name: str) -> None:
    """Reject every database name outside the generated validation namespace."""

    suffix = name.removeprefix(DATABASE_PREFIX)
    if not name.startswith(DATABASE_PREFIX) or re.fullmatch(r"[0-9a-f]{16}", suffix) is None:
        raise ValueError("Refusing database cleanup outside the migration-validation namespace")


def _database_dsn(admin_dsn: str, database_name: str) -> str:
    return make_conninfo(admin_dsn, dbname=database_name)


def _verify_postgresql_18(connection: psycopg.Connection[tuple[object, ...]]) -> None:
    if connection.info.server_version // 10000 != 18:
        raise RuntimeError(
            f"Migration validation requires PostgreSQL 18, found server version "
            f"{connection.info.server_version}"
        )


def _create_database(admin_dsn: str, database_name: str) -> None:
    validate_disposable_database_name(database_name)
    with psycopg.connect(admin_dsn, autocommit=True) as connection:
        _verify_postgresql_18(connection)
        with connection.cursor() as cursor:
            cursor.execute(
                sql.SQL("CREATE DATABASE {} WITH TEMPLATE template0 ENCODING 'UTF8'").format(
                    sql.Identifier(database_name)
                )
            )


def _drop_database(admin_dsn: str, database_name: str) -> None:
    validate_disposable_database_name(database_name)
    with psycopg.connect(admin_dsn, autocommit=True) as connection:
        _verify_postgresql_18(connection)
        with connection.cursor() as cursor:
            cursor.execute(
                sql.SQL("DROP DATABASE {} WITH (FORCE)").format(sql.Identifier(database_name))
            )


def _apply_migrations(database_dsn: str, migrations: tuple[Migration, ...]) -> None:
    with psycopg.connect(database_dsn, autocommit=True) as connection:
        _verify_postgresql_18(connection)
        for migration in migrations:
            with connection.transaction(), connection.cursor() as cursor:
                cursor.execute(migration.sql, prepare=False)


def _stable_cell(value: object) -> str:
    if value is None:
        return "<NULL>"
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def schema_digest(database_dsn: str) -> str:
    """Return a deterministic digest of security- and behavior-relevant schema metadata."""

    records: list[list[str]] = []
    with psycopg.connect(database_dsn, autocommit=True) as connection:
        _verify_postgresql_18(connection)
        with connection.cursor() as cursor:
            for section, query in SCHEMA_QUERIES:
                cursor.execute(query)
                records.extend(
                    [section, *(_stable_cell(value) for value in row)] for row in cursor.fetchall()
                )
    encoded = json.dumps(records, ensure_ascii=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate_migrations(admin_dsn: str, migrations: tuple[Migration, ...]) -> ValidationResult:
    """Validate fresh and previous-schema upgrade paths in isolated databases."""

    fresh_database = _database_name()
    upgrade_database = _database_name()
    created: list[str] = []
    primary_error: BaseException | None = None
    try:
        for database_name in (fresh_database, upgrade_database):
            _create_database(admin_dsn, database_name)
            created.append(database_name)

        fresh_dsn = _database_dsn(admin_dsn, fresh_database)
        upgrade_dsn = _database_dsn(admin_dsn, upgrade_database)
        _apply_migrations(fresh_dsn, migrations)
        fresh_digest = schema_digest(fresh_dsn)

        previous = migrations[:-1] if migrations else ()
        latest = migrations[-1:] if migrations else ()
        _apply_migrations(upgrade_dsn, previous)
        _apply_migrations(upgrade_dsn, latest)
        upgrade_digest = schema_digest(upgrade_dsn)
        if fresh_digest != upgrade_digest:
            raise RuntimeError(
                "Fresh and previous-schema upgrade paths produced different schema digests"
            )
        return ValidationResult(
            migration_count=len(migrations),
            plan_sha256=migration_plan_digest(migrations),
            fresh_schema_sha256=fresh_digest,
            upgraded_schema_sha256=upgrade_digest,
        )
    except BaseException as error:
        primary_error = error
        raise
    finally:
        cleanup_errors: list[str] = []
        for database_name in reversed(created):
            try:
                _drop_database(admin_dsn, database_name)
            except Exception as error:
                cleanup_errors.append(f"{database_name}: {error}")
        if cleanup_errors and primary_error is None:
            raise RuntimeError("Migration validation cleanup failed: " + "; ".join(cleanup_errors))
        if cleanup_errors and primary_error is not None:
            primary_error.add_note(
                "Migration validation cleanup also failed: " + "; ".join(cleanup_errors)
            )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--admin-dsn", required=True, help="PostgreSQL 18 administrative DSN")
    parser.add_argument(
        "--migrations-dir",
        type=Path,
        default=ROOT / "migrations",
        help="Directory containing ordered migration SQL files",
    )
    parser.add_argument(
        "--allow-empty",
        action="store_true",
        help="Explicitly permit an empty plan before the first product schema migration",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run migration validation without printing credentials or SQL payloads."""

    arguments = _parser().parse_args(argv)
    try:
        migrations = discover_migrations(
            arguments.migrations_dir, allow_empty=arguments.allow_empty
        )
        result = validate_migrations(arguments.admin_dsn, migrations)
    except (OSError, ValueError, RuntimeError, psycopg.Error) as error:
        print(f"migration validation failed: {error}", file=sys.stderr)
        return 1
    print(f"migrations: {result.migration_count}")
    print(f"plan-sha256: {result.plan_sha256}")
    print(f"fresh-schema-sha256: {result.fresh_schema_sha256}")
    print(f"upgraded-schema-sha256: {result.upgraded_schema_sha256}")
    print("migration validation: passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
