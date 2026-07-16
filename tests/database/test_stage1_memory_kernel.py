"""Live PostgreSQL evidence for scoped Stage 1 memory and Dreaming gates."""

# ruff: noqa: SIM117

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from typing import Any, Final

import psycopg
import pytest
from psycopg import sql
from psycopg.types.json import Jsonb

type Context = dict[str, str]

AREA_A: Final[Context] = {
    "principal_id": "principal-a",
    "tenant_id": "tenant-a",
    "area_id": "area-a",
    "project_id": "project-a",
    "session_id": "session-a",
}
AREA_B: Final[Context] = {
    "principal_id": "principal-b",
    "tenant_id": "tenant-a",
    "area_id": "area-b",
    "project_id": "project-b",
    "session_id": "session-b",
}


def test_catalog_enforces_singleton_brain_and_project_bound_session(database_dsn: str) -> None:
    """ADR-016 lineage is constrained in PostgreSQL, not only documented."""
    with (
        psycopg.connect(database_dsn, autocommit=True) as connection,
        connection.cursor() as cursor,
    ):
        with pytest.raises(psycopg.errors.UniqueViolation):
            cursor.execute(
                "INSERT INTO brain_catalog.brains (brain_id, display_name) VALUES (%s, %s)",
                ("brain-second", "Forbidden second Brain"),
            )
        cursor.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_schema = 'brain_catalog' AND table_name = 'tenants'"
        )
        assert "area_id" not in {row[0] for row in cursor.fetchall()}
        with pytest.raises(psycopg.errors.ForeignKeyViolation):
            cursor.execute(
                "INSERT INTO brain_catalog.sessions "
                "(tenant_id, area_id, project_id, session_id) VALUES (%s, %s, %s, %s)",
                ("tenant-a", "area-a", "missing-project", "invalid-session"),
            )


def _set_context(cursor: psycopg.Cursor[tuple[Any, ...]], context: Context) -> None:
    for key, value in context.items():
        cursor.execute("SELECT set_config(%s, %s, true)", (f"neural_brain.{key}", value))


def _cycle_arguments(
    *,
    request_id: str = "request-1",
    observation_id: str = "observation-1",
    checkpoint_id: str = "checkpoint-1",
    expected_version: int = 0,
) -> tuple[object, ...]:
    return (
        request_id,
        observation_id,
        "consumer_event",
        "internal",
        "working_context",
        Jsonb({"content": "evidence", "source_ref": "consumer-message-1"}),
        datetime(2026, 7, 15, 12, 0, tzinfo=UTC),
        "primary",
        Jsonb({"entries": [{"content": "evidence", "source_observation_id": observation_id}]}),
        expected_version,
        checkpoint_id,
    )


def _call_cycle(
    database_dsn: str, context: Context, arguments: tuple[object, ...]
) -> dict[str, object]:
    with psycopg.connect(database_dsn, autocommit=True) as connection, connection.transaction():
        with connection.cursor() as cursor:
            cursor.execute("SET LOCAL ROLE neural_brain_gate")
            _set_context(cursor, context)
            cursor.execute(
                "SELECT memory_gate.commit_memory_cycle("
                "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                arguments,
            )
            row = cursor.fetchone()
            assert row is not None
            result = row[0]
            assert isinstance(result, dict)
            return result


def _count(database_dsn: str, relation: str, condition: str = "true") -> int:
    with (
        psycopg.connect(database_dsn, autocommit=True) as connection,
        connection.cursor() as cursor,
    ):
        cursor.execute(
            sql.SQL("SELECT count(*) FROM {} WHERE " + condition).format(
                sql.SQL(".").join(sql.Identifier(part) for part in relation.split("."))
            )
        )
        row = cursor.fetchone()
        assert row is not None
        return int(row[0])


def test_catalog_hierarchy_has_no_tenant_area_and_requires_project_session(
    database_dsn: str,
) -> None:
    """The accepted catalog shape is enforced by columns and composite foreign keys."""

    with (
        psycopg.connect(database_dsn, autocommit=True) as connection,
        connection.cursor() as cursor,
    ):
        cursor.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_schema = 'brain_catalog' AND table_name = 'tenants'"
        )
        tenant_columns = {str(row[0]) for row in cursor.fetchall()}
        assert "brain_id" in tenant_columns
        assert "tenant_id" in tenant_columns
        assert "area_id" not in tenant_columns

        with pytest.raises(psycopg.errors.NotNullViolation):
            cursor.execute(
                "INSERT INTO brain_catalog.sessions "
                "(tenant_id, area_id, session_id, activity_state) "
                "VALUES ('tenant-a', 'area-a', 'missing-project', 'inactive')"
            )


def test_gate_commits_observation_working_context_checkpoint_and_audit_atomically(
    database_dsn: str,
) -> None:
    """One protected call commits the complete vertical slice and supports exact replay."""

    first = _call_cycle(database_dsn, AREA_A, _cycle_arguments())
    replay = _call_cycle(database_dsn, AREA_A, _cycle_arguments())

    assert first == replay
    assert first["working_version"] == 1
    checkpoint = first["checkpoint"]
    assert isinstance(checkpoint, dict)
    primary = checkpoint["primary"]
    assert isinstance(primary, dict)
    assert primary["version"] == 1
    assert _count(database_dsn, "memory_core.observations") == 1
    assert _count(database_dsn, "memory_core.checkpoints") == 1
    assert _count(database_dsn, "memory_audit.events") == 1


def test_checkpoint_readback_is_scope_and_session_checked(database_dsn: str) -> None:
    """Direct Stage-1 readback is deterministic and unavailable outside trusted scope."""

    _call_cycle(database_dsn, AREA_A, _cycle_arguments())

    with psycopg.connect(database_dsn, autocommit=True) as connection, connection.transaction():
        with connection.cursor() as cursor:
            cursor.execute("SET LOCAL ROLE neural_brain_reader")
            _set_context(cursor, AREA_A)
            cursor.execute("SELECT memory_gate.read_checkpoint(%s)", ("checkpoint-1",))
            first = cursor.fetchone()
            cursor.execute("SELECT memory_gate.read_checkpoint(%s)", ("checkpoint-1",))
            second = cursor.fetchone()
            assert first == second

    with psycopg.connect(database_dsn, autocommit=True) as connection, connection.transaction():
        with connection.cursor() as cursor:
            cursor.execute("SET LOCAL ROLE neural_brain_reader")
            _set_context(cursor, AREA_B)
            with pytest.raises(psycopg.errors.NoData):
                cursor.execute("SELECT memory_gate.read_checkpoint(%s)", ("checkpoint-1",))


def test_runtime_role_cannot_mutate_protected_tables_directly(database_dsn: str) -> None:
    """RLS is not the only barrier: the runtime role has no table DML grants."""

    with psycopg.connect(database_dsn, autocommit=True) as connection, connection.transaction():
        with connection.cursor() as cursor:
            cursor.execute("SET LOCAL ROLE neural_brain_gate")
            _set_context(cursor, AREA_A)
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                cursor.execute("DELETE FROM memory_core.observations")


def test_stale_version_and_changed_replay_fail_without_partial_state(database_dsn: str) -> None:
    """Stale compare-and-set and replay mismatch preserve the prior committed state."""

    _call_cycle(database_dsn, AREA_A, _cycle_arguments())

    with pytest.raises(psycopg.errors.SerializationFailure):
        _call_cycle(
            database_dsn,
            AREA_A,
            _cycle_arguments(
                request_id="request-stale",
                observation_id="observation-stale",
                checkpoint_id="checkpoint-stale",
                expected_version=0,
            ),
        )
    with pytest.raises(psycopg.errors.DataException):
        _call_cycle(
            database_dsn,
            AREA_A,
            _cycle_arguments(observation_id="observation-changed"),
        )

    assert _count(database_dsn, "memory_core.observations") == 1
    assert _count(database_dsn, "memory_audit.events") == 1


def test_audit_failure_rolls_back_the_complete_transition(database_dsn: str) -> None:
    """An injected audit failure leaves no observation, context version, or checkpoint."""

    with psycopg.connect(database_dsn, autocommit=True) as connection, connection.transaction():
        with connection.cursor() as cursor:
            cursor.execute(
                "CREATE FUNCTION memory_audit.fail_test_insert() RETURNS trigger "
                "LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'injected audit failure'; END; $$"
            )
            cursor.execute(
                "CREATE TRIGGER injected_audit_failure BEFORE INSERT ON memory_audit.events "
                "FOR EACH ROW EXECUTE FUNCTION memory_audit.fail_test_insert()"
            )
    try:
        with pytest.raises(psycopg.errors.RaiseException):
            _call_cycle(
                database_dsn,
                AREA_B,
                _cycle_arguments(
                    request_id="request-audit-fail",
                    observation_id="observation-audit-fail",
                    checkpoint_id="checkpoint-audit-fail",
                ),
            )
        assert (
            _count(
                database_dsn,
                "memory_core.observations",
                "observation_id = 'observation-audit-fail'",
            )
            == 0
        )
    finally:
        with psycopg.connect(database_dsn, autocommit=True) as connection, connection.transaction():
            with connection.cursor() as cursor:
                cursor.execute("DROP TRIGGER injected_audit_failure ON memory_audit.events")
                cursor.execute("DROP FUNCTION memory_audit.fail_test_insert()")


def test_concurrent_duplicate_request_cannot_double_commit(database_dsn: str) -> None:
    """A concurrent duplicate either replays or fails closed, but never commits twice."""

    arguments = _cycle_arguments(
        request_id="request-concurrent",
        observation_id="observation-concurrent",
        checkpoint_id="checkpoint-concurrent",
        expected_version=0,
    )

    def invoke() -> object:
        try:
            return _call_cycle(database_dsn, AREA_B, arguments)
        except psycopg.Error as error:
            return error

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(lambda _: invoke(), range(2)))

    assert any(isinstance(result, dict) for result in results)
    assert (
        _count(
            database_dsn,
            "memory_core.observations",
            "observation_id = 'observation-concurrent'",
        )
        == 1
    )


def _call_dreaming(database_dsn: str, context: Context, run_id: str) -> dict[str, object]:
    with psycopg.connect(database_dsn, autocommit=True) as connection, connection.transaction():
        with connection.cursor() as cursor:
            cursor.execute("SET LOCAL ROLE neural_brain_dreamer")
            _set_context(cursor, context)
            cursor.execute(
                "SELECT memory_gate.run_dreaming_dry_run(%s, %s)",
                (run_id, "stage1 verification"),
            )
            row = cursor.fetchone()
            assert row is not None and isinstance(row[0], dict)
            return row[0]


def test_dreaming_skips_active_work_then_creates_only_inactive_candidates(
    database_dsn: str,
) -> None:
    """Dreaming is Area-local, offline, non-activating, and audited."""

    _call_cycle(database_dsn, AREA_A, _cycle_arguments())

    skipped = _call_dreaming(database_dsn, AREA_A, "dream-active")
    assert skipped["status"] == "skipped"
    assert skipped["skip_reason"] == "active_work"
    assert skipped["active_pointer_updated"] is False

    with psycopg.connect(database_dsn, autocommit=True) as connection, connection.transaction():
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE brain_catalog.sessions SET activity_state = 'inactive', "
                "activity_expires_at = NULL WHERE tenant_id = 'tenant-a' AND area_id = 'area-a'"
            )

    completed = _call_dreaming(database_dsn, AREA_A, "dream-complete")
    assert completed["status"] == "completed"
    assert completed["validation_result"] == "passed"
    assert completed["active_pointer_updated"] is False
    candidate_count = completed["candidate_count"]
    assert isinstance(candidate_count, int)
    assert candidate_count >= 1

    with (
        psycopg.connect(database_dsn, autocommit=True) as connection,
        connection.cursor() as cursor,
    ):
        cursor.execute(
            "SELECT DISTINCT state FROM memory_core.memory_candidates "
            "WHERE tenant_id = 'tenant-a' AND area_id = 'area-a'"
        )
        assert cursor.fetchall() == [("inactive",)]
        with pytest.raises(psycopg.errors.CheckViolation):
            cursor.execute(
                "UPDATE memory_core.memory_candidates SET state = 'active' "
                "WHERE tenant_id = 'tenant-a' AND area_id = 'area-a'"
            )


def test_dreaming_denies_cross_area_principal(database_dsn: str) -> None:
    """Changing trusted scope without a matching principal binding fails closed."""

    forged = dict(AREA_B)
    forged["principal_id"] = "principal-a"
    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        _call_dreaming(database_dsn, forged, "dream-cross-area")
