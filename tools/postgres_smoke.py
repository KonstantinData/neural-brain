"""Verify both local PostgreSQL scopes through explicit autocommit connections."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

import psycopg
from psycopg.pq import TransactionStatus

ROOT = Path(__file__).resolve().parents[1]
ENVIRONMENT_FILE = ROOT / ".local" / "dev.env"


class _RollbackProbe(Exception):
    """Internal sentinel used to prove explicit transaction rollback."""


def _read_environment(path: Path) -> dict[str, str]:
    environment: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        name, separator, value = line.partition("=")
        if not separator or not name or not value:
            raise ValueError("The generated local environment is malformed.")
        environment[name] = value
    return environment


def _verify_application_role(cursor: psycopg.Cursor[tuple[object, ...]]) -> None:
    cursor.execute("SELECT rolsuper FROM pg_roles WHERE rolname = current_user")
    row = cursor.fetchone()
    if row is None:
        raise RuntimeError("Could not inspect the current PostgreSQL role.")
    if bool(row[0]):
        raise RuntimeError("Local scope role must not be a PostgreSQL superuser.")


def _verify_transaction_mutation(connection: psycopg.Connection[tuple[object, ...]]) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            "CREATE TEMPORARY TABLE neural_brain_smoke_probe "
            "(marker text PRIMARY KEY) ON COMMIT PRESERVE ROWS"
        )

    with connection.transaction(), connection.cursor() as cursor:
        cursor.execute("INSERT INTO neural_brain_smoke_probe (marker) VALUES ('commit')")
    if connection.info.transaction_status is not TransactionStatus.IDLE:
        raise RuntimeError("The explicit commit probe left an open transaction.")
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM neural_brain_smoke_probe WHERE marker = 'commit'")
        row = cursor.fetchone()
    if row != (1,):
        raise RuntimeError("The explicit commit probe did not persist its write.")

    try:
        with connection.transaction(), connection.cursor() as cursor:
            cursor.execute("INSERT INTO neural_brain_smoke_probe (marker) VALUES ('rollback')")
            raise _RollbackProbe
    except _RollbackProbe:
        pass
    if connection.info.transaction_status is not TransactionStatus.IDLE:
        raise RuntimeError("The explicit rollback probe left an open transaction.")
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM neural_brain_smoke_probe WHERE marker = 'rollback'")
        row = cursor.fetchone()
    if row != (0,):
        raise RuntimeError("The explicit rollback probe persisted a rolled-back write.")


def _verify_database(environment: dict[str, str], scope: str) -> str:
    prefix = f"NEURAL_BRAIN_{scope.upper()}_"
    with psycopg.connect(
        host="127.0.0.1",
        port=int(environment[f"{prefix}PORT"]),
        dbname=environment[f"{prefix}DB"],
        user=environment[f"{prefix}USER"],
        password=environment[f"{prefix}PASSWORD"],
        autocommit=True,
        connect_timeout=5,
        application_name="neural-brain-foundation-smoke",
    ) as connection:
        if not connection.autocommit:
            raise RuntimeError("ADR-013 requires autocommit connections.")
        with connection.cursor() as cursor:
            cursor.execute("SHOW server_version")
            row = cursor.fetchone()
        if row is None:
            raise RuntimeError("PostgreSQL did not return its server version.")
        version = str(row[0])
        if not version.startswith("18.4"):
            raise RuntimeError(f"Unexpected Foundation PostgreSQL version: {version}")
        with connection.cursor() as cursor:
            _verify_application_role(cursor)
        if connection.info.transaction_status is not TransactionStatus.IDLE:
            raise RuntimeError("The smoke query left an open database transaction.")

        _verify_transaction_mutation(connection)
        return version


def _parse_args(arguments: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--environment-file",
        type=Path,
        default=ENVIRONMENT_FILE,
        help="Path to the local environment file created by tools/dev.ps1.",
    )
    return parser.parse_args(arguments)


def main(arguments: Sequence[str] | None = None) -> int:
    """Verify development and test databases without exposing credentials."""

    args = _parse_args(arguments)
    environment = _read_environment(args.environment_file)
    for scope in ("dev", "test"):
        version = _verify_database(environment, scope)
        print(
            f"{scope}: PostgreSQL {version}; autocommit, explicit commit, "
            "and explicit rollback verified"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
