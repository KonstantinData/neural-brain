"""Psycopg 3 adapter for the protected Stage 1 memory and Dreaming gates."""

from collections.abc import Mapping
from typing import Literal, Never

import psycopg
from psycopg import Cursor
from psycopg.types.json import Jsonb

from neural_brain.memory.errors import (
    AtomicPersistenceError,
    CheckpointUnavailableError,
    ScopeIsolationError,
    StaleWorkingMemoryVersionError,
)
from neural_brain.memory.models import (
    CheckpointRecord,
    CheckpointRequest,
    DreamingReport,
    DreamingRequest,
    DreamingResult,
    InactiveMemoryCandidate,
    MemoryCycleResult,
    MemoryScope,
    ObservationRecord,
    ObservationRequest,
    OpaqueId,
    RuntimeContext,
    WorkingMemoryEntryRequest,
    WorkingMemoryRecord,
    WorkingMemoryRequest,
)


class PostgresMemoryRepository:
    """Call only SECURITY DEFINER gates through explicit short transactions."""

    def __init__(self, conninfo: str) -> None:
        self._conninfo = conninfo

    def commit_memory_cycle(
        self,
        *,
        context: RuntimeContext,
        transition_request_id: OpaqueId,
        observation: ObservationRequest,
        working_memory: WorkingMemoryRequest,
        checkpoint: CheckpointRequest,
    ) -> MemoryCycleResult:
        """Commit observation, working context, checkpoint, receipt, and audit atomically."""
        if context.project_id is None or context.session_id is None:
            raise ScopeIsolationError("memory cycle requires project and session scope")
        working_value = {
            "entries": [entry.model_dump(mode="json") for entry in working_memory.entries]
        }
        observation_payload = {
            "source_ref": observation.source_ref,
            "content": observation.content,
        }
        try:
            with (
                psycopg.connect(self._conninfo, autocommit=True) as connection,
                connection.transaction(),
                connection.cursor() as cursor,
            ):
                self._set_context(cursor, context, "neural_brain_gate")
                cursor.execute(
                    "SELECT memory_gate.commit_memory_cycle("
                    "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (
                        transition_request_id,
                        observation.observation_id,
                        observation.source_kind,
                        observation.classification,
                        observation.purpose,
                        Jsonb(observation_payload),
                        observation.occurred_at,
                        working_memory.working_memory_id,
                        Jsonb(working_value),
                        working_memory.expected_version,
                        checkpoint.checkpoint_id,
                    ),
                )
                document = self._single_json_result(cursor)
        except psycopg.Error as error:
            self._raise_domain_error(error)

        version = self._integer(document, "working_version")
        scope = self._session_scope(context)
        observation_record = ObservationRecord(
            observation_id=observation.observation_id,
            source_kind=observation.source_kind,
            source_ref=observation.source_ref,
            classification=observation.classification,
            purpose=observation.purpose,
            content=observation.content,
            occurred_at=observation.occurred_at,
            scope=scope,
        )
        working_record = WorkingMemoryRecord(
            working_memory_id=working_memory.working_memory_id,
            version=version,
            entries=working_memory.entries,
            scope=scope,
        )
        checkpoint_record = CheckpointRecord(
            checkpoint_id=checkpoint.checkpoint_id,
            working_memory_id=working_memory.working_memory_id,
            working_memory_version=version,
            entries=working_memory.entries,
            scope=scope,
        )
        return MemoryCycleResult(
            observation=observation_record,
            working_memory=working_record,
            checkpoint=checkpoint_record,
            audit_committed=True,
        )

    def read_checkpoint(
        self, *, context: RuntimeContext, checkpoint_id: OpaqueId
    ) -> CheckpointRecord:
        """Read a checkpoint only through authenticated session scope."""
        if context.project_id is None or context.session_id is None:
            raise ScopeIsolationError("checkpoint read requires project and session scope")
        try:
            with (
                psycopg.connect(self._conninfo, autocommit=True) as connection,
                connection.transaction(),
                connection.cursor() as cursor,
            ):
                self._set_context(cursor, context, "neural_brain_reader")
                cursor.execute("SELECT memory_gate.read_checkpoint(%s)", (checkpoint_id,))
                document = self._single_json_result(cursor)
        except psycopg.Error as error:
            self._raise_domain_error(error)

        working_memory_id = self._string(document, "working_memory_id")
        snapshot = self._object(document, "snapshot")
        working_snapshot = self._mapping(snapshot.get(working_memory_id), "working snapshot")
        version = self._integer(working_snapshot, "version")
        value = self._object(working_snapshot, "value")
        raw_entries = value.get("entries")
        if not isinstance(raw_entries, list):
            raise AtomicPersistenceError("checkpoint entries are not a JSON array")
        entries = tuple(WorkingMemoryEntryRequest.model_validate(item) for item in raw_entries)
        return CheckpointRecord(
            checkpoint_id=checkpoint_id,
            working_memory_id=working_memory_id,
            working_memory_version=version,
            entries=entries,
            scope=self._session_scope(context),
        )

    def execute_dreaming_dry_run(
        self, *, context: RuntimeContext, request: DreamingRequest
    ) -> DreamingResult:
        """Run guarded Area-local Dreaming and expose only inactive candidates."""
        try:
            with (
                psycopg.connect(self._conninfo, autocommit=True) as connection,
                connection.transaction(),
                connection.cursor() as cursor,
            ):
                self._set_context(cursor, context, "neural_brain_dreamer")
                cursor.execute(
                    "SELECT memory_gate.run_dreaming_dry_run(%s, %s)",
                    (request.dreaming_run_id, request.requested_reason),
                )
                document = self._single_json_result(cursor)
        except psycopg.Error as error:
            self._raise_domain_error(error)

        scope = MemoryScope(tenant_id=context.tenant_id, area_id=context.area_id)
        raw_status = self._string(document, "status")
        if raw_status == "skipped":
            status: Literal["skipped", "completed"] = "skipped"
        elif raw_status == "completed":
            status = "completed"
        else:
            raise AtomicPersistenceError("Dreaming returned an unknown status")
        raw_validation = self._string(document, "validation_result")
        if raw_validation == "passed":
            validation: Literal["passed", "not_run"] = "passed"
        elif raw_validation == "not_run":
            validation = "not_run"
        else:
            raise AtomicPersistenceError("Dreaming returned an unknown validation result")
        raw_skip_reason = document.get("skip_reason")
        if raw_skip_reason is not None and not isinstance(raw_skip_reason, str):
            raise AtomicPersistenceError("Dreaming skip reason is not a string")
        raw_candidates = document.get("candidates")
        if not isinstance(raw_candidates, list):
            raise AtomicPersistenceError("Dreaming candidates are not a JSON array")
        candidates = tuple(
            InactiveMemoryCandidate(
                candidate_id=self._string(self._mapping(item, "candidate"), "candidate_id"),
                source_observation_id=self._string(
                    self._mapping(item, "candidate"), "source_observation_id"
                ),
                candidate_kind=self._string(self._mapping(item, "candidate"), "candidate_kind"),
                scope=scope,
            )
            for item in raw_candidates
        )
        report = DreamingReport(
            dreaming_run_id=request.dreaming_run_id,
            scope=scope,
            status=status,
            skip_reason=raw_skip_reason,
            candidate_count=self._integer(document, "candidate_count"),
            validation_result=validation,
            active_pointer_updated=self._false(document, "active_pointer_updated"),
            audit_committed=True,
        )
        return DreamingResult(report=report, candidates=candidates)

    @staticmethod
    def _set_context(
        cursor: Cursor[tuple[object, ...]], context: RuntimeContext, role: str
    ) -> None:
        roles = {
            "neural_brain_gate": "SET LOCAL ROLE neural_brain_gate",
            "neural_brain_reader": "SET LOCAL ROLE neural_brain_reader",
            "neural_brain_dreamer": "SET LOCAL ROLE neural_brain_dreamer",
        }
        try:
            role_statement = roles[role]
        except KeyError as error:
            raise AtomicPersistenceError("unknown database role") from error
        cursor.execute(role_statement)
        values = {
            "principal_id": context.actor_id,
            "tenant_id": context.tenant_id,
            "area_id": context.area_id,
            "project_id": context.project_id or "",
            "session_id": context.session_id or "",
        }
        for name, value in values.items():
            cursor.execute(
                "SELECT pg_catalog.set_config(%s, %s, true)",
                (f"neural_brain.{name}", value),
            )

    @staticmethod
    def _single_json_result(cursor: Cursor[tuple[object, ...]]) -> dict[str, object]:
        row = cursor.fetchone()
        if row is None:
            raise AtomicPersistenceError("database gate returned no result")
        return PostgresMemoryRepository._mapping(row[0], "database gate result")

    @staticmethod
    def _mapping(value: object, label: str) -> dict[str, object]:
        if not isinstance(value, Mapping):
            raise AtomicPersistenceError(f"{label} is not a JSON object")
        result: dict[str, object] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise AtomicPersistenceError(f"{label} contains a non-string key")
            result[key] = item
        return result

    @staticmethod
    def _object(document: Mapping[str, object], key: str) -> dict[str, object]:
        return PostgresMemoryRepository._mapping(document.get(key), key)

    @staticmethod
    def _string(document: Mapping[str, object], key: str) -> str:
        value = document.get(key)
        if not isinstance(value, str):
            raise AtomicPersistenceError(f"{key} is not a string")
        return value

    @staticmethod
    def _integer(document: Mapping[str, object], key: str) -> int:
        value = document.get(key)
        if not isinstance(value, int) or isinstance(value, bool):
            raise AtomicPersistenceError(f"{key} is not an integer")
        return value

    @staticmethod
    def _false(document: Mapping[str, object], key: str) -> Literal[False]:
        value = document.get(key)
        if value is not False:
            raise AtomicPersistenceError(f"{key} must remain false")
        return False

    @staticmethod
    def _session_scope(context: RuntimeContext) -> MemoryScope:
        if context.project_id is None or context.session_id is None:
            raise ScopeIsolationError("session scope is incomplete")
        return MemoryScope(
            tenant_id=context.tenant_id,
            area_id=context.area_id,
            project_id=context.project_id,
            session_id=context.session_id,
        )

    @staticmethod
    def _raise_domain_error(error: psycopg.Error) -> Never:
        if error.sqlstate == "40001":
            raise StaleWorkingMemoryVersionError("stale working-memory version") from error
        if error.sqlstate == "02000":
            raise CheckpointUnavailableError("checkpoint unavailable") from error
        if error.sqlstate in {"42501", "55000"}:
            raise ScopeIsolationError("database gate denied trusted scope or authority") from error
        raise AtomicPersistenceError("protected PostgreSQL operation failed") from error
