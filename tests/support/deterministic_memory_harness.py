"""Deterministic, effect-free test fixtures for protected Memory Core boundaries.

This module is test infrastructure.  It is deliberately not exported from the
runtime package and cannot open a connection, invoke a tool, or mutate an
active model.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from hashlib import sha256

from neural_brain.memory import (
    AtomicPersistenceError,
    CheckpointRecord,
    CheckpointRequest,
    CheckpointUnavailableError,
    DreamingRequest,
    DreamingResult,
    MemoryCycleResult,
    MemoryScope,
    ObservationRecord,
    ObservationRequest,
    OpaqueId,
    RuntimeContext,
    StaleWorkingMemoryVersionError,
    WorkingMemoryEntryRequest,
    WorkingMemoryRecord,
    WorkingMemoryRequest,
)

type ScopeKey = tuple[str, str, str | None, str | None]


@dataclass(slots=True)
class FrozenClock:
    """A test clock whose time changes only through an explicit advance."""

    current: datetime = datetime(2026, 7, 26, 12, 0, tzinfo=UTC)

    def now(self) -> datetime:
        """Return the current fixed instant."""
        return self.current

    def advance(self, duration: timedelta) -> datetime:
        """Advance deterministically and return the new instant."""
        if duration < timedelta():
            raise ValueError("deterministic clocks cannot move backwards")
        self.current += duration
        return self.current


@dataclass(slots=True)
class DeterministicIds:
    """Generate stable opaque IDs without UUIDs, system time, or random state."""

    seed: str = "memory-harness"
    _counters: dict[str, int] = field(default_factory=dict)

    def next(self, namespace: str) -> str:
        """Return the next stable identifier in one declared namespace."""
        counter = self._counters.get(namespace, 0) + 1
        self._counters[namespace] = counter
        digest = sha256(f"{self.seed}:{namespace}".encode()).hexdigest()[:12]
        return f"{namespace}-{digest}-{counter:04d}"


def reproduce_seed(seed: str, *, namespace: str = "memory") -> str:
    """Return a stable scenario token without exposing external randomness."""
    if not seed or not namespace:
        raise ValueError("seed and namespace are required")
    return sha256(f"{namespace}:{seed}".encode()).hexdigest()


class MemoryFailpoint(StrEnum):
    """Crash boundary supported by the deterministic persistent-memory fake."""

    BEFORE_COMMIT = "before_commit"


@dataclass(frozen=True, slots=True)
class MemoryCycleInputs:
    """One reproducible, scope-free request set for a protected memory cycle."""

    transition_request_id: OpaqueId
    observation: ObservationRequest
    working_memory: WorkingMemoryRequest
    checkpoint: CheckpointRequest


@dataclass(slots=True)
class MemoryCycleFactory:
    """Create deterministic cycle requests; trusted scope remains caller-owned."""

    clock: FrozenClock
    ids: DeterministicIds

    def build(self, *, expected_version: int = 0) -> MemoryCycleInputs:
        """Build a valid request set with a single observation-derived entry."""
        observation_id = self.ids.next("observation")
        return MemoryCycleInputs(
            transition_request_id=self.ids.next("transition"),
            observation=ObservationRequest(
                observation_id=observation_id,
                source_kind="deterministic_fixture",
                source_ref=reproduce_seed(self.ids.seed, namespace="source"),
                classification="internal",
                purpose="deterministic_memory_boundary_test",
                content=reproduce_seed(self.ids.seed, namespace="content"),
                occurred_at=self.clock.now(),
            ),
            working_memory=WorkingMemoryRequest(
                working_memory_id="working-memory-fixture",
                expected_version=expected_version,
                entries=(
                    WorkingMemoryEntryRequest(
                        entry_id=self.ids.next("entry"),
                        source_observation_id=observation_id,
                        content=reproduce_seed(self.ids.seed, namespace="entry"),
                    ),
                ),
            ),
            checkpoint=CheckpointRequest(checkpoint_id=self.ids.next("checkpoint")),
        )


class DeterministicMemoryRepository:
    """Atomic, scoped persistent-boundary fake with explicit crash injection."""

    def __init__(self) -> None:
        self.observations: dict[tuple[ScopeKey, str], ObservationRecord] = {}
        self.working_memories: dict[tuple[ScopeKey, str], WorkingMemoryRecord] = {}
        self.checkpoints: dict[tuple[ScopeKey, str], CheckpointRecord] = {}
        self.audit_ids: list[str] = []
        self._receipts: dict[tuple[ScopeKey, str], tuple[str, MemoryCycleResult]] = {}
        self._failpoint: MemoryFailpoint | None = None

    def inject(self, failpoint: MemoryFailpoint) -> None:
        """Arm exactly one explicit crash boundary for the next commit."""
        self._failpoint = failpoint

    def commit_memory_cycle(
        self,
        *,
        context: RuntimeContext,
        transition_request_id: OpaqueId,
        observation: ObservationRequest,
        working_memory: WorkingMemoryRequest,
        checkpoint: CheckpointRequest,
    ) -> MemoryCycleResult:
        """Stage all records and publish them only after the simulated commit."""
        scope_key = self._scope_key(context)
        receipt_key = (scope_key, transition_request_id)
        signature = "|".join(
            (
                observation.model_dump_json(),
                working_memory.model_dump_json(),
                checkpoint.model_dump_json(),
            )
        )
        prior = self._receipts.get(receipt_key)
        if prior is not None:
            if prior[0] != signature:
                raise AtomicPersistenceError("idempotency key reused with another payload")
            return prior[1]

        working_key = (scope_key, working_memory.working_memory_id)
        current = self.working_memories.get(working_key)
        version = 0 if current is None else current.version
        if version != working_memory.expected_version:
            raise StaleWorkingMemoryVersionError("stale working-memory version")

        scope = self._scope(context)
        result = MemoryCycleResult(
            observation=ObservationRecord(**observation.model_dump(), scope=scope),
            working_memory=WorkingMemoryRecord(
                working_memory_id=working_memory.working_memory_id,
                version=version + 1,
                entries=working_memory.entries,
                scope=scope,
            ),
            checkpoint=CheckpointRecord(
                checkpoint_id=checkpoint.checkpoint_id,
                working_memory_id=working_memory.working_memory_id,
                working_memory_version=version + 1,
                entries=working_memory.entries,
                scope=scope,
            ),
            audit_committed=True,
        )
        if self._failpoint is MemoryFailpoint.BEFORE_COMMIT:
            self._failpoint = None
            raise AtomicPersistenceError("injected failure before atomic commit")

        self.observations[(scope_key, observation.observation_id)] = result.observation
        self.working_memories[working_key] = result.working_memory
        self.checkpoints[(scope_key, checkpoint.checkpoint_id)] = result.checkpoint
        self._receipts[receipt_key] = (signature, result)
        self.audit_ids.append(transition_request_id)
        return result

    def read_checkpoint(
        self, *, context: RuntimeContext, checkpoint_id: OpaqueId
    ) -> CheckpointRecord:
        """Return a checkpoint only from the authenticated scope."""
        return self._read(self.checkpoints, context=context, record_id=checkpoint_id)

    def read_observation(
        self, *, context: RuntimeContext, observation_id: OpaqueId
    ) -> ObservationRecord:
        """Return an observation only from the authenticated scope."""
        return self._read(self.observations, context=context, record_id=observation_id)

    def read_working_memory(
        self, *, context: RuntimeContext, working_memory_id: OpaqueId
    ) -> WorkingMemoryRecord:
        """Return working memory only from the authenticated scope."""
        return self._read(self.working_memories, context=context, record_id=working_memory_id)

    def execute_dreaming_dry_run(
        self, *, context: RuntimeContext, request: DreamingRequest
    ) -> DreamingResult:
        """Keep unavailable Dreaming outside the test fake's capability surface."""
        del context, request
        raise AssertionError("Dreaming is not part of the deterministic Memory Core fixture")

    @staticmethod
    def _scope(context: RuntimeContext) -> MemoryScope:
        return MemoryScope(
            tenant_id=context.tenant_id,
            area_id=context.area_id,
            project_id=context.project_id,
            session_id=context.session_id,
        )

    @classmethod
    def _scope_key(cls, context: RuntimeContext) -> ScopeKey:
        scope = cls._scope(context)
        return (scope.tenant_id, scope.area_id, scope.project_id, scope.session_id)

    @classmethod
    def _read[T](
        cls,
        records: dict[tuple[ScopeKey, str], T],
        *,
        context: RuntimeContext,
        record_id: OpaqueId,
    ) -> T:
        try:
            return records[(cls._scope_key(context), record_id)]
        except KeyError as error:
            raise CheckpointUnavailableError("record unavailable") from error


class ScriptedMemoryRepository:
    """Script untrusted adapter outcomes without an external dependency."""

    def __init__(self, outcomes: tuple[MemoryCycleResult | Exception, ...]) -> None:
        self._outcomes: deque[MemoryCycleResult | Exception] = deque(outcomes)
        self.calls: list[str] = []

    def commit_memory_cycle(
        self,
        *,
        context: RuntimeContext,
        transition_request_id: OpaqueId,
        observation: ObservationRequest,
        working_memory: WorkingMemoryRequest,
        checkpoint: CheckpointRequest,
    ) -> MemoryCycleResult:
        """Return one declared adapter result and retain only a method call receipt."""
        del context, transition_request_id, observation, working_memory, checkpoint
        self.calls.append("commit_memory_cycle")
        if not self._outcomes:
            raise AssertionError("no scripted adapter outcome remains")
        outcome = self._outcomes.popleft()
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    def read_checkpoint(
        self, *, context: RuntimeContext, checkpoint_id: OpaqueId
    ) -> CheckpointRecord:
        del context, checkpoint_id
        raise AssertionError("checkpoint reads require an explicit scripted adapter")

    def read_observation(
        self, *, context: RuntimeContext, observation_id: OpaqueId
    ) -> ObservationRecord:
        del context, observation_id
        raise AssertionError("observation reads require an explicit scripted adapter")

    def read_working_memory(
        self, *, context: RuntimeContext, working_memory_id: OpaqueId
    ) -> WorkingMemoryRecord:
        del context, working_memory_id
        raise AssertionError("working-memory reads require an explicit scripted adapter")

    def execute_dreaming_dry_run(
        self, *, context: RuntimeContext, request: DreamingRequest
    ) -> DreamingResult:
        del context, request
        raise AssertionError("Dreaming is not scriptable by this Memory Core fixture")
