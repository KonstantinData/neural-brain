"""Verify both local PostgreSQL scopes through explicit autocommit connections."""

from __future__ import annotations

from pathlib import Path

import psycopg
from psycopg.pq import TransactionStatus

ROOT = Path(__file__).resolve().parents[1]
ENVIRONMENT_FILE = ROOT / ".local" / "dev.env"


class _RollbackProbe(Exception):
    """Internal sentinel used to prove explicit transaction rollback."""


def _read_environment() -> dict[str, str]:
    environment: dict[str, str] = {}
    for line in ENVIRONMENT_FILE.read_text(encoding="utf-8").splitlines():
        name, separator, value = line.partition("=")
        if not separator or not name or not value:
            raise ValueError("The generated local environment is malformed.")
        environment[name] = value
    return environment


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
        if connection.info.transaction_status is not TransactionStatus.IDLE:
            raise RuntimeError("The smoke query left an open database transaction.")

        with connection.transaction(), connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        if connection.info.transaction_status is not TransactionStatus.IDLE:
            raise RuntimeError("The explicit commit probe left an open transaction.")

        try:
            with connection.transaction(), connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                raise _RollbackProbe
        except _RollbackProbe:
            pass
        if connection.info.transaction_status is not TransactionStatus.IDLE:
            raise RuntimeError("The explicit rollback probe left an open transaction.")
        return version


def main() -> int:
    """Verify development and test databases without exposing credentials."""

    environment = _read_environment()
    for scope in ("dev", "test"):
        version = _verify_database(environment, scope)
        print(
            f"{scope}: PostgreSQL {version}; autocommit, explicit commit, "
            "and explicit rollback verified"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
