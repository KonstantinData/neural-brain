"""Adapters from effect-free cognition to trusted model and Memory Core gates."""

import hashlib
import json
from dataclasses import dataclass

from neural_brain.cognition.errors import (
    CognitiveCheckpointUnavailableError,
    CognitiveRuntimeError,
    CognitiveScopeError,
    StaleCognitiveCheckpointError,
)
from neural_brain.cognition.models import (
    ActiveCognitiveModelManifest,
    CognitiveCheckpoint,
    RecordedObservation,
)
from neural_brain.cognition.workspace import NeuralWorkspace
from neural_brain.memory.errors import (
    CheckpointUnavailableError,
    ScopeIsolationError,
    StaleWorkingMemoryVersionError,
)
from neural_brain.memory.models import (
    CheckpointRequest,
    MemoryCycleResult,
    ObservationRequest,
    OpaqueId,
    RuntimeContext,
    WorkingMemoryEntryRequest,
    WorkingMemoryRequest,
)
from neural_brain.memory.service import MemoryService


def workspace_parameter_digest(workspace: NeuralWorkspace) -> str:
    """Hash canonical immutable parameters for manifest verification."""
    payload = workspace.parameters.model_dump_json().encode()
    return hashlib.sha256(payload).hexdigest()


def model_manifest_digest(manifest: ActiveCognitiveModelManifest) -> str:
    """Hash the canonical trusted model manifest."""
    return hashlib.sha256(manifest.model_dump_json().encode()).hexdigest()


@dataclass(frozen=True)
class ActiveCognitiveModel:
    """Trusted runtime composition of executable mechanism and manifest."""

    workspace: NeuralWorkspace
    manifest: ActiveCognitiveModelManifest


class FixedWorkspaceProvider:
    """Expose one immutable active model selected outside untrusted requests."""

    def __init__(self, workspace: NeuralWorkspace, manifest: ActiveCognitiveModelManifest) -> None:
        if manifest.model_version != workspace.parameters.model_version:
            raise CognitiveRuntimeError("active model manifest version mismatch")
        if manifest.parameter_digest != workspace_parameter_digest(workspace):
            raise CognitiveRuntimeError("active model parameter digest mismatch")
        self._active_model = ActiveCognitiveModel(workspace=workspace, manifest=manifest)

    def active_model(self, *, context: RuntimeContext) -> ActiveCognitiveModel:
        """Return the configured active model for authenticated runtime context."""
        del context
        return self._active_model


class MemoryServiceCognitiveGate:
    """Encode cognition state into the existing protected Memory Transition Gate."""

    _ENTRY_ID = "nb1-cognitive-workspace-state"

    def __init__(self, memory_service: MemoryService) -> None:
        self._memory_service = memory_service

    def load_checkpoint(
        self, *, context: RuntimeContext, checkpoint_id: OpaqueId
    ) -> CognitiveCheckpoint:
        """Read and validate one cognition checkpoint through Memory Core."""
        del context
        try:
            record = self._memory_service.read_checkpoint(
                CheckpointRequest(checkpoint_id=checkpoint_id)
            )
        except CheckpointUnavailableError as error:
            raise CognitiveCheckpointUnavailableError("cognitive checkpoint unavailable") from error
        except ScopeIsolationError as error:
            raise CognitiveScopeError("cognitive checkpoint crossed trusted scope") from error
        entries = tuple(entry for entry in record.entries if entry.entry_id == self._ENTRY_ID)
        if len(entries) != 1:
            raise CognitiveRuntimeError("cognitive checkpoint has no unique workspace state")
        try:
            payload = json.loads(entries[0].content)
            model_version = payload["model_version"]
            hidden_state = payload["hidden_state"]
            observation_id = payload["observation_id"]
        except (KeyError, TypeError, json.JSONDecodeError) as error:
            raise CognitiveRuntimeError("cognitive checkpoint state is invalid") from error
        if not isinstance(model_version, str) or not isinstance(observation_id, str):
            raise CognitiveRuntimeError("cognitive checkpoint identifiers are invalid")
        if not isinstance(hidden_state, (int, float)) or isinstance(hidden_state, bool):
            raise CognitiveRuntimeError("cognitive checkpoint hidden state is invalid")
        return CognitiveCheckpoint(
            checkpoint_id=record.checkpoint_id,
            version=record.working_memory_version,
            model_version=model_version,
            hidden_state=(float(hidden_state),),
            latest_observation_id=observation_id,
            scope=record.scope,
        )

    def commit_checkpoint(
        self,
        *,
        context: RuntimeContext,
        cycle_id: OpaqueId,
        expected_version: int,
        model_version: OpaqueId,
        hidden_state: float,
        observation: RecordedObservation,
    ) -> MemoryCycleResult:
        """Commit state and real audit evidence atomically through Memory Core."""
        if context.session_id is None:
            raise CognitiveRuntimeError("cognition checkpoint requires session scope")
        content = json.dumps(
            {
                "hidden_state": hidden_state,
                "model_version": model_version,
                "observation_id": observation.observation_id,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        try:
            return self._memory_service.record_observation_and_checkpoint(
                transition_request_id=cycle_id,
                observation=ObservationRequest(
                    observation_id=observation.observation_id,
                    source_kind=observation.source_kind,
                    source_ref=observation.provenance_ref,
                    classification="internal",
                    purpose="NB-1 effect-free cognitive workspace transition",
                    content=json.dumps(
                        {"features": observation.features},
                        separators=(",", ":"),
                    ),
                    occurred_at=observation.occurred_at,
                ),
                working_memory=WorkingMemoryRequest(
                    working_memory_id=f"nb1-cognition:{context.session_id}",
                    expected_version=expected_version,
                    entries=(
                        WorkingMemoryEntryRequest(
                            entry_id=self._ENTRY_ID,
                            source_observation_id=observation.observation_id,
                            content=content,
                        ),
                    ),
                ),
                checkpoint=CheckpointRequest(checkpoint_id=f"nb1:{cycle_id}"),
            )
        except StaleWorkingMemoryVersionError as error:
            raise StaleCognitiveCheckpointError("stale cognitive checkpoint version") from error
        except ScopeIsolationError as error:
            raise CognitiveScopeError("cognitive checkpoint crossed trusted scope") from error
