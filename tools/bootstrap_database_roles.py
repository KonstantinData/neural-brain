"""Create the fixed NOLOGIN PostgreSQL roles required by Neural Brain migrations."""

from __future__ import annotations

import argparse
import sys
from typing import Final

import psycopg
from psycopg import sql
from psycopg.conninfo import make_conninfo

ROLE_NAMES: Final[tuple[str, ...]] = (
    "neural_brain_owner",
    "neural_brain_gate",
    "neural_brain_reader",
    "neural_brain_dreamer",
)
PROVISIONER_ROLE: Final = "neural_brain_provisioner"
ROLE_BOOTSTRAP_LOCK_ID: Final = 5_825_982_108_055_326_093
ROLE_BOOTSTRAP_DATABASE: Final = "postgres"


def coordination_dsn(admin_dsn: str) -> str:
    """Pin cluster-global role coordination to one database-scoped lock domain."""

    return make_conninfo(admin_dsn, dbname=ROLE_BOOTSTRAP_DATABASE)


def bootstrap_roles(admin_dsn: str) -> None:
    """Create or harden cluster-global roles without exposing connection secrets."""

    with psycopg.connect(coordination_dsn(admin_dsn), autocommit=True) as connection:
        if connection.info.server_version // 10000 != 18:
            raise RuntimeError("Database role bootstrap requires PostgreSQL 18")
        with connection.cursor() as cursor:
            cursor.execute("SET lock_timeout = '5s'")
            try:
                cursor.execute("SELECT pg_catalog.pg_advisory_lock(%s)", (ROLE_BOOTSTRAP_LOCK_ID,))
            except psycopg.errors.LockNotAvailable as error:
                raise RuntimeError(
                    "Timed out waiting for the database role bootstrap lock"
                ) from error
            try:
                for role_name in ROLE_NAMES:
                    cursor.execute(
                        "SELECT 1 FROM pg_catalog.pg_roles WHERE rolname = %s", (role_name,)
                    )
                    if cursor.fetchone() is None:
                        cursor.execute(
                            sql.SQL(
                                "CREATE ROLE {} NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE "
                                "NOINHERIT NOREPLICATION NOBYPASSRLS"
                            ).format(sql.Identifier(role_name))
                        )
                    else:
                        cursor.execute(
                            sql.SQL(
                                "ALTER ROLE {} NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE "
                                "NOINHERIT NOREPLICATION NOBYPASSRLS"
                            ).format(sql.Identifier(role_name))
                        )
                cursor.execute(
                    "SELECT 1 FROM pg_catalog.pg_roles WHERE rolname = %s",
                    (PROVISIONER_ROLE,),
                )
                provisioner_statement = "ALTER ROLE" if cursor.fetchone() else "CREATE ROLE"
                cursor.execute(
                    sql.SQL(
                        provisioner_statement + " {} NOLOGIN NOSUPERUSER NOCREATEDB CREATEROLE "
                        "INHERIT NOREPLICATION NOBYPASSRLS"
                    ).format(sql.Identifier(PROVISIONER_ROLE))
                )
                for runtime_role in ("neural_brain_gate", "neural_brain_reader"):
                    cursor.execute(
                        sql.SQL("GRANT {} TO {} WITH ADMIN TRUE, INHERIT FALSE, SET FALSE").format(
                            sql.Identifier(runtime_role),
                            sql.Identifier(PROVISIONER_ROLE),
                        )
                    )
                cursor.execute(
                    sql.SQL(
                        "GRANT pg_signal_backend TO {} WITH ADMIN FALSE, INHERIT TRUE, SET FALSE"
                    ).format(sql.Identifier(PROVISIONER_ROLE))
                )
                cursor.execute(
                    "SELECT member.rolname, granted.rolname "
                    "FROM pg_catalog.pg_auth_members AS membership "
                    "JOIN pg_catalog.pg_roles AS member ON member.oid = membership.member "
                    "JOIN pg_catalog.pg_roles AS granted ON granted.oid = membership.roleid "
                    "WHERE member.rolname = ANY(%s) ORDER BY member.rolname, granted.rolname",
                    (list(ROLE_NAMES),),
                )
                if cursor.fetchall():
                    raise RuntimeError(
                        "Fixed Neural Brain roles must not inherit or SET any other role"
                    )
            finally:
                cursor.execute(
                    "SELECT pg_catalog.pg_advisory_unlock(%s)", (ROLE_BOOTSTRAP_LOCK_ID,)
                )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--admin-dsn", required=True, help="PostgreSQL 18 administrative DSN")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the fail-closed role bootstrap."""

    arguments = _parser().parse_args(argv)
    try:
        bootstrap_roles(arguments.admin_dsn)
    except (RuntimeError, psycopg.Error) as error:
        print(f"database role bootstrap failed: {error}", file=sys.stderr)
        return 1
    print(f"database role bootstrap: passed ({len(ROLE_NAMES) + 1} roles)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
