"""Psycopg adapter for protected, effect-free NB-1 cognitive checkpoints."""

import json
from collections.abc import Mapping
from typing import Never

import psycopg
from psycopg import Cursor
from psycopg.types.json import Jsonb
from pydantic import ValidationError

from neural_brain.cognition.errors import (
    CognitiveCheckpointUnavailableError,
    CognitiveRuntimeError,
    CognitiveScopeError,
    StaleCognitiveCheckpointError,
)
from neural_brain.cognition.models import (
    CognitiveCheckpoint,
    CognitiveTransitionEnvelope,
    RecordedObservation,
)
from neural_brain.memory.models import (
    CheckpointRecord,
    MemoryCycleResult,
    MemoryScope,
    ObservationRecord,
    OpaqueId,
    RuntimeContext,
    WorkingMemoryEntryRequest,
    WorkingMemoryRecord,
)
from neural_brain.postgres.memory_repository import PostgresMemoryRepository


class PostgresCognitiveRepository:
    """Persist cognition only through dedicated Memory Transition Gate functions."""

    _ENTRY_ID = "nb1-cognitive-workspace-state"

    def __init__(
        self,
        conninfo: str,
        *,
        training_provenance_by_model: Mapping[str, OpaqueId],
    ) -> None:
        self._conninfo = conninfo
        self._training_provenance_by_model = dict(training_provenance_by_model)

    def load_checkpoint(
        self, *, context: RuntimeContext, checkpoint_id: OpaqueId
    ) -> CognitiveCheckpoint:
        """Load a cognition checkpoint from authenticated session scope."""
        scope = self._scope(context)
        try:
            with (
                psycopg.connect(self._conninfo, autocommit=True) as connection,
                connection.transaction(),
                connection.cursor() as cursor,
            ):
                PostgresMemoryRepository._set_context(cursor, context, "neural_brain_reader")
                cursor.execute(
                    "SELECT memory_gate.read_cognitive_checkpoint(%s)",
                    (checkpoint_id,),
                )
                document = self._single_json_result(cursor)
        except psycopg.Error as error:
            self._raise_domain_error(error)

        try:
            transition = CognitiveTransitionEnvelope.model_validate_json(
                json.dumps(
                    self._object(document, "transition_envelope"),
                    separators=(",", ":"),
                )
            )
        except ValidationError as error:
            raise CognitiveRuntimeError("cognitive checkpoint transition is invalid") from error
        version = self._integer(document, "checkpoint_version")
        returned_id = self._string(document, "checkpoint_id")
        if returned_id != checkpoint_id:
            raise CognitiveRuntimeError("database returned a different cognitive checkpoint")
        if transition.next_checkpoint_version != version:
            raise CognitiveRuntimeError("checkpoint version and transition evidence diverged")
        self._validate_audit(
            document,
            transition,
            version,
            self._trusted_training_provenance(transition.model_version),
        )
        return CognitiveCheckpoint(
            checkpoint_id=returned_id,
            version=version,
            model_version=transition.model_version,
            hidden_state=transition.hidden_state,
            latest_observation_id=transition.observation_id,
            scope=scope,
        )

    def commit_checkpoint(
        self,
        *,
        context: RuntimeContext,
        cycle_id: OpaqueId,
        expected_version: int,
        transition: CognitiveTransitionEnvelope,
        observation: RecordedObservation,
    ) -> MemoryCycleResult:
        """Atomically commit envelope, checkpoint, receipt, and audit evidence."""
        scope = self._scope(context)
        if transition.cycle_id != cycle_id:
            raise CognitiveRuntimeError("transition cycle identity mismatch")
        if transition.observation_id != observation.observation_id:
            raise CognitiveRuntimeError("transition observation identity mismatch")
        if transition.previous_checkpoint_version != expected_version:
            raise CognitiveRuntimeError("transition predecessor version mismatch")
        training_provenance_ref = self._trusted_training_provenance(transition.model_version)
        if training_provenance_ref != transition.active_model.training_artifact_digest:
            raise CognitiveRuntimeError(
                "trusted training provenance does not match active model evidence"
            )
        checkpoint_id = f"nb1:{cycle_id}"
        try:
            with (
                psycopg.connect(self._conninfo, autocommit=True) as connection,
                connection.transaction(),
                connection.cursor() as cursor,
            ):
                PostgresMemoryRepository._set_context(cursor, context, "neural_brain_gate")
                cursor.execute(
                    "SELECT memory_gate.commit_cognitive_cycle("
                    "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (
                        cycle_id,
                        observation.observation_id,
                        observation.source_kind,
                        observation.provenance_ref,
                        Jsonb(observation.features),
                        observation.occurred_at,
                        expected_version,
                        checkpoint_id,
                        Jsonb(transition.model_dump(mode="json")),
                        training_provenance_ref,
                    ),
                )
                document = self._single_json_result(cursor)
        except psycopg.Error as error:
            self._raise_domain_error(error)

        version = self._integer(document, "working_version")
        returned_checkpoint = self._string(document, "checkpoint_id")
        try:
            persisted_transition = CognitiveTransitionEnvelope.model_validate_json(
                json.dumps(
                    self._object(document, "transition_envelope"),
                    separators=(",", ":"),
                )
            )
        except ValidationError as error:
            raise CognitiveRuntimeError("committed cognitive transition is invalid") from error
        if persisted_transition != transition:
            raise CognitiveRuntimeError("committed cognitive transition differs from request")
        if returned_checkpoint != checkpoint_id or version != transition.next_checkpoint_version:
            raise CognitiveRuntimeError("committed checkpoint identity or version diverged")
        self._validate_audit(document, transition, version, training_provenance_ref)

        transition_content = transition.model_dump_json()
        observation_content = json.dumps(
            {"features": observation.features},
            separators=(",", ":"),
        )
        entry = WorkingMemoryEntryRequest(
            entry_id=self._ENTRY_ID,
            source_observation_id=observation.observation_id,
            content=transition_content,
        )
        observation_record = ObservationRecord(
            observation_id=observation.observation_id,
            source_kind=observation.source_kind,
            source_ref=observation.provenance_ref,
            classification="internal",
            purpose="NB-1 effect-free cognitive workspace transition",
            content=observation_content,
            occurred_at=observation.occurred_at,
            scope=scope,
        )
        working_memory_id = f"nb1-cognition:{scope.session_id}"
        working_record = WorkingMemoryRecord(
            working_memory_id=working_memory_id,
            version=version,
            entries=(entry,),
            scope=scope,
        )
        checkpoint_record = CheckpointRecord(
            checkpoint_id=checkpoint_id,
            working_memory_id=working_memory_id,
            working_memory_version=version,
            entries=(entry,),
            scope=scope,
        )
        return MemoryCycleResult(
            observation=observation_record,
            working_memory=working_record,
            checkpoint=checkpoint_record,
            audit_committed=True,
        )

    @staticmethod
    def _validate_audit(
        document: Mapping[str, object],
        transition: CognitiveTransitionEnvelope,
        version: int,
        training_provenance_ref: OpaqueId,
    ) -> None:
        audit = PostgresCognitiveRepository._object(document, "audit_evidence")
        expected: dict[str, object] = {
            "cycle_id": transition.cycle_id,
            "model_version": transition.model_version,
            "training_provenance_ref": training_provenance_ref,
            "observation_id": transition.observation_id,
            "previous_checkpoint_version": transition.previous_checkpoint_version,
            "committed_checkpoint_version": version,
            "active_model": transition.active_model.model_dump(mode="json"),
            "external_effects_occurred": False,
            "active_model_mutated": False,
            "audit_committed": True,
        }
        if audit != expected:
            raise CognitiveRuntimeError("committed cognitive audit evidence is incomplete")

    def _trusted_training_provenance(self, model_version: OpaqueId) -> OpaqueId:
        try:
            return self._training_provenance_by_model[model_version]
        except KeyError as error:
            raise CognitiveRuntimeError(
                "active model has no trusted training provenance"
            ) from error

    @staticmethod
    def _scope(context: RuntimeContext) -> MemoryScope:
        if context.project_id is None or context.session_id is None:
            raise CognitiveScopeError("cognitive repository requires project and session scope")
        return MemoryScope(
            tenant_id=context.tenant_id,
            area_id=context.area_id,
            project_id=context.project_id,
            session_id=context.session_id,
        )

    @staticmethod
    def _single_json_result(cursor: Cursor[tuple[object, ...]]) -> dict[str, object]:
        row = cursor.fetchone()
        if row is None:
            raise CognitiveRuntimeError("database gate returned no cognitive result")
        return PostgresCognitiveRepository._mapping(row[0], "database gate result")

    @staticmethod
    def _mapping(value: object, label: str) -> dict[str, object]:
        if not isinstance(value, Mapping):
            raise CognitiveRuntimeError(f"{label} is not a JSON object")
        result: dict[str, object] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise CognitiveRuntimeError(f"{label} contains a non-string key")
            result[key] = item
        return result

    @staticmethod
    def _object(document: Mapping[str, object], key: str) -> dict[str, object]:
        return PostgresCognitiveRepository._mapping(document.get(key), key)

    @staticmethod
    def _string(document: Mapping[str, object], key: str) -> str:
        value = document.get(key)
        if not isinstance(value, str):
            raise CognitiveRuntimeError(f"{key} is not a string")
        return value

    @staticmethod
    def _integer(document: Mapping[str, object], key: str) -> int:
        value = document.get(key)
        if not isinstance(value, int) or isinstance(value, bool):
            raise CognitiveRuntimeError(f"{key} is not an integer")
        return value

    @staticmethod
    def _raise_domain_error(error: psycopg.Error) -> Never:
        if error.sqlstate == "40001":
            raise StaleCognitiveCheckpointError("stale cognitive checkpoint version") from error
        if error.sqlstate == "02000":
            raise CognitiveCheckpointUnavailableError("cognitive checkpoint unavailable") from error
        if error.sqlstate in {"42501", "55000"}:
            raise CognitiveScopeError("database gate denied trusted scope or authority") from error
        raise CognitiveRuntimeError("protected PostgreSQL cognitive operation failed") from error
