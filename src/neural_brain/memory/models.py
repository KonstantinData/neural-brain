"""Strict request and immutable result models for the MS-1 Memory Core kernel."""

from datetime import datetime
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

type OpaqueId = Annotated[str, Field(strict=True, min_length=1, max_length=128)]
type StrictContent = Annotated[str, Field(strict=True, min_length=1, max_length=65_536)]
type DataClassification = Literal["public", "internal", "confidential", "restricted"]


class StrictModel(BaseModel):
    """Reject coercion, mutation, and undeclared fields at every schema boundary."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class RuntimeContext(StrictModel):
    """Trusted identity and immutable scope resolved by the runtime."""

    actor_id: OpaqueId
    tenant_id: OpaqueId
    area_id: OpaqueId
    project_id: OpaqueId | None = None
    session_id: OpaqueId | None = None

    @model_validator(mode="after")
    def session_requires_project(self) -> Self:
        """Ensure session-bound scope carries every required ancestor."""
        if self.session_id is not None and self.project_id is None:
            raise ValueError("session_id requires project_id")
        return self


class ObservationRequest(StrictModel):
    """Untrusted observation content; scope and actor fields are intentionally absent."""

    observation_id: OpaqueId
    source_kind: OpaqueId
    source_ref: OpaqueId
    classification: DataClassification
    purpose: Annotated[str, Field(strict=True, min_length=1, max_length=256)]
    content: StrictContent
    occurred_at: datetime

    @model_validator(mode="after")
    def occurred_at_is_timezone_aware(self) -> Self:
        """Reject timestamps whose meaning changes with process-local timezone settings."""
        if self.occurred_at.tzinfo is None or self.occurred_at.utcoffset() is None:
            raise ValueError("occurred_at must include a timezone offset")
        return self


class WorkingMemoryEntryRequest(StrictModel):
    """One bounded working-memory entry derived from an observation."""

    entry_id: OpaqueId
    source_observation_id: OpaqueId
    content: StrictContent


class WorkingMemoryRequest(StrictModel):
    """Untrusted compare-and-set update for bounded working memory."""

    working_memory_id: OpaqueId
    expected_version: Annotated[int, Field(strict=True, ge=0)]
    entries: Annotated[tuple[WorkingMemoryEntryRequest, ...], Field(max_length=256)]

    @model_validator(mode="after")
    def entry_ids_are_unique(self) -> Self:
        """Reject ambiguous snapshots containing duplicate entry identifiers."""
        entry_ids = tuple(entry.entry_id for entry in self.entries)
        if len(entry_ids) != len(set(entry_ids)):
            raise ValueError("working-memory entry_id values must be unique")
        return self


class CheckpointRequest(StrictModel):
    """Untrusted checkpoint identifier; authenticated scope is attached later."""

    checkpoint_id: OpaqueId


class DreamingRequest(StrictModel):
    """Trusted trigger data without scope, candidate, promotion, or pointer controls."""

    dreaming_run_id: OpaqueId
    requested_reason: Annotated[str, Field(strict=True, min_length=1, max_length=256)]


class MemoryScope(StrictModel):
    """Authenticated operational-memory scope attached by the kernel."""

    tenant_id: OpaqueId
    area_id: OpaqueId
    project_id: OpaqueId | None = None
    session_id: OpaqueId | None = None

    @model_validator(mode="after")
    def session_requires_project(self) -> Self:
        """Ensure a session-bound memory scope contains its project ancestor."""
        if self.session_id is not None and self.project_id is None:
            raise ValueError("session_id requires project_id")
        return self


class ObservationRecord(StrictModel):
    """Persisted observation with immutable authenticated scope."""

    observation_id: OpaqueId
    source_kind: OpaqueId
    source_ref: OpaqueId
    classification: DataClassification
    purpose: Annotated[str, Field(strict=True, min_length=1, max_length=256)]
    content: StrictContent
    occurred_at: datetime
    scope: MemoryScope


class WorkingMemoryRecord(StrictModel):
    """Versioned working-memory state committed by one atomic cycle."""

    working_memory_id: OpaqueId
    version: Annotated[int, Field(strict=True, ge=1)]
    entries: tuple[WorkingMemoryEntryRequest, ...]
    scope: MemoryScope


class CheckpointRecord(StrictModel):
    """Deterministic immutable snapshot of a working-memory version."""

    checkpoint_id: OpaqueId
    working_memory_id: OpaqueId
    working_memory_version: Annotated[int, Field(strict=True, ge=1)]
    entries: tuple[WorkingMemoryEntryRequest, ...]
    scope: MemoryScope


class MemoryCycleResult(StrictModel):
    """Atomic observation, working-memory, checkpoint, and audit commit result."""

    observation: ObservationRecord
    working_memory: WorkingMemoryRecord
    checkpoint: CheckpointRecord
    audit_committed: Literal[True]

    @model_validator(mode="after")
    def committed_records_form_one_cycle(self) -> Self:
        """Reject internally inconsistent repository results."""
        scope = self.observation.scope
        if self.working_memory.scope != scope or self.checkpoint.scope != scope:
            raise ValueError("memory-cycle records must share one scope")
        if self.checkpoint.working_memory_id != self.working_memory.working_memory_id:
            raise ValueError("checkpoint must reference the committed working memory")
        if self.checkpoint.working_memory_version != self.working_memory.version:
            raise ValueError("checkpoint must reference the committed memory version")
        if self.checkpoint.entries != self.working_memory.entries:
            raise ValueError("checkpoint must contain the committed memory entries")
        return self


class InactiveMemoryCandidate(StrictModel):
    """Non-retrievable MS-1 Dreaming output."""

    candidate_id: OpaqueId
    source_observation_id: OpaqueId
    candidate_kind: OpaqueId
    scope: MemoryScope
    state: Literal["inactive"] = "inactive"
    retrievable: Literal[False] = False


class DreamingReport(StrictModel):
    """Terminal MS-1 dry-run report."""

    dreaming_run_id: OpaqueId
    scope: MemoryScope
    status: Literal["skipped", "completed"]
    skip_reason: StrictContent | None = None
    candidate_count: Annotated[int, Field(strict=True, ge=0)]
    validation_result: Literal["passed", "not_run"]
    active_pointer_updated: Literal[False]
    audit_committed: Literal[True]

    @model_validator(mode="after")
    def skip_reason_matches_status(self) -> Self:
        """Require an explanation for skips and prohibit one on completion."""
        if self.status == "skipped" and self.skip_reason is None:
            raise ValueError("skipped Dreaming reports require skip_reason")
        if self.status == "completed" and self.skip_reason is not None:
            raise ValueError("completed Dreaming reports cannot have skip_reason")
        if self.status == "skipped" and self.validation_result != "not_run":
            raise ValueError("skipped Dreaming reports cannot claim validation")
        if self.status == "completed" and self.validation_result != "passed":
            raise ValueError("completed Dreaming reports require passed validation")
        return self


class DreamingResult(StrictModel):
    """MS-1 Dreaming output with no activation or pointer surface."""

    report: DreamingReport
    candidates: tuple[InactiveMemoryCandidate, ...]

    @model_validator(mode="after")
    def skipped_runs_have_no_candidates(self) -> Self:
        """A protected skip cannot produce analysis-derived candidates."""
        if self.report.status == "skipped" and self.candidates:
            raise ValueError("skipped Dreaming runs cannot produce candidates")
        if any(candidate.scope != self.report.scope for candidate in self.candidates):
            raise ValueError("Dreaming report and candidates must share one scope")
        if self.report.candidate_count != len(self.candidates):
            raise ValueError("Dreaming candidate count must match persisted candidate output")
        return self
