"""Safety and behavior tests for the first effect-free NB-1 runtime slice."""

import json
from datetime import UTC, datetime
from threading import Lock

import pytest
from pydantic import ValidationError

from neural_brain.cognition import (
    ActiveCognitiveModelManifest,
    CognitiveCheckpointUnavailableError,
    CognitiveCycleRequest,
    CognitiveCycleService,
    CognitiveRuntimeError,
    CognitiveScopeError,
    FixedWorkspaceProvider,
    MemoryServiceCognitiveGate,
    NeuralWorkspace,
    NeuralWorkspaceParameters,
    RecordedObservation,
    StaleCognitiveCheckpointError,
    UnknownNeuralModelError,
    workspace_parameter_digest,
)
from neural_brain.memory.errors import (
    AtomicPersistenceError,
    CheckpointUnavailableError,
    ScopeIsolationError,
    StaleWorkingMemoryVersionError,
)
from neural_brain.memory.models import (
    CheckpointRecord,
    CheckpointRequest,
    DreamingRequest,
    DreamingResult,
    MemoryCycleResult,
    MemoryScope,
    ObservationRecord,
    ObservationRequest,
    OpaqueId,
    RuntimeContext,
    WorkingMemoryRecord,
    WorkingMemoryRequest,
)
from neural_brain.memory.service import MemoryService

type ScopeKey = tuple[str, str, str, str]


class ContextProvider:
    """Mutable trusted-context test provider."""

    def __init__(self, context: RuntimeContext) -> None:
        self.context = context

    def current_context(self) -> RuntimeContext:
        return self.context


class AtomicMemoryRepository:
    """MS-1 test double with CAS, idempotency, scope, checkpoint, and audit semantics."""

    def __init__(self) -> None:
        self.observations: dict[tuple[ScopeKey, str], ObservationRecord] = {}
        self.working: dict[tuple[ScopeKey, str], WorkingMemoryRecord] = {}
        self.checkpoints: dict[tuple[ScopeKey, str], CheckpointRecord] = {}
        self.receipts: dict[tuple[ScopeKey, str], tuple[str, MemoryCycleResult]] = {}
        self.audit_ids: list[str] = []
        self.fail_before_commit = False
        self._lock = Lock()

    def commit_memory_cycle(
        self,
        *,
        context: RuntimeContext,
        transition_request_id: OpaqueId,
        observation: ObservationRequest,
        working_memory: WorkingMemoryRequest,
        checkpoint: CheckpointRequest,
    ) -> MemoryCycleResult:
        scope = self._scope(context)
        key = self._key(context)
        signature = "|".join(
            (
                observation.model_dump_json(),
                working_memory.model_dump_json(),
                checkpoint.model_dump_json(),
            )
        )
        receipt_key = (key, transition_request_id)
        with self._lock:
            prior = self.receipts.get(receipt_key)
            if prior is not None:
                if prior[0] != signature:
                    raise AtomicPersistenceError("idempotency key reused with another payload")
                return prior[1]
            working_key = (key, working_memory.working_memory_id)
            current = self.working.get(working_key)
            actual = 0 if current is None else current.version
            if actual != working_memory.expected_version:
                raise StaleWorkingMemoryVersionError("stale working-memory version")
            if self.fail_before_commit:
                raise AtomicPersistenceError("injected atomic commit failure")
            version = actual + 1
            observation_record = ObservationRecord(**observation.model_dump(), scope=scope)
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
            result = MemoryCycleResult(
                observation=observation_record,
                working_memory=working_record,
                checkpoint=checkpoint_record,
                audit_committed=True,
            )
            self.working[working_key] = working_record
            self.observations[(key, observation.observation_id)] = observation_record
            self.checkpoints[(key, checkpoint.checkpoint_id)] = checkpoint_record
            self.receipts[receipt_key] = (signature, result)
            self.audit_ids.append(transition_request_id)
            return result

    def read_checkpoint(
        self, *, context: RuntimeContext, checkpoint_id: OpaqueId
    ) -> CheckpointRecord:
        record = self.checkpoints.get((self._key(context), checkpoint_id))
        if record is None:
            raise CheckpointUnavailableError("checkpoint unavailable")
        return record

    def read_observation(
        self, *, context: RuntimeContext, observation_id: OpaqueId
    ) -> ObservationRecord:
        record = self.observations.get((self._key(context), observation_id))
        if record is None:
            raise CheckpointUnavailableError("observation unavailable")
        return record

    def read_working_memory(
        self, *, context: RuntimeContext, working_memory_id: OpaqueId
    ) -> WorkingMemoryRecord:
        record = self.working.get((self._key(context), working_memory_id))
        if record is None:
            raise CheckpointUnavailableError("working memory unavailable")
        return record

    def execute_dreaming_dry_run(
        self, *, context: RuntimeContext, request: DreamingRequest
    ) -> DreamingResult:
        del context, request
        raise NotImplementedError

    @staticmethod
    def _scope(context: RuntimeContext) -> MemoryScope:
        if context.project_id is None or context.session_id is None:
            raise ScopeIsolationError("session scope required")
        return MemoryScope(
            tenant_id=context.tenant_id,
            area_id=context.area_id,
            project_id=context.project_id,
            session_id=context.session_id,
        )

    @classmethod
    def _key(cls, context: RuntimeContext) -> ScopeKey:
        scope = cls._scope(context)
        assert scope.project_id is not None
        assert scope.session_id is not None
        return (scope.tenant_id, scope.area_id, scope.project_id, scope.session_id)


def context(session_id: str = "session-a") -> RuntimeContext:
    return RuntimeContext(
        actor_id="actor-a",
        tenant_id="tenant-a",
        area_id="area-a",
        project_id="project-a",
        session_id=session_id,
    )


def parameters(model_version: str = "nb1-model-v1") -> NeuralWorkspaceParameters:
    return NeuralWorkspaceParameters(
        model_version=model_version,
        training_provenance_ref="offline-training-artifact-sha256",
        attention_logits=(2.0, -2.0),
        input_weights=(1.0, 1.0),
        recurrent_weight=1.0,
        bias=0.0,
    )


def observation(observation_id: str, features: tuple[float, float]) -> RecordedObservation:
    return RecordedObservation(
        observation_id=observation_id,
        source_kind="synthetic",
        provenance_ref="fixture-sha256",
        features=features,
        occurred_at=datetime(2026, 7, 16, 20, 0, tzinfo=UTC),
    )


def build_service(
    *,
    provider: ContextProvider | None = None,
    repository: AtomicMemoryRepository | None = None,
    model_version: str = "nb1-model-v1",
) -> tuple[CognitiveCycleService, ContextProvider, AtomicMemoryRepository]:
    context_provider = provider or ContextProvider(context())
    memory_repository = repository or AtomicMemoryRepository()
    memory_service = MemoryService(context_provider=context_provider, repository=memory_repository)
    workspace = NeuralWorkspace(parameters(model_version))
    digest = "a" * 64
    service = CognitiveCycleService(
        context_provider=context_provider,
        memory_gate=MemoryServiceCognitiveGate(memory_service, context_provider),
        workspace_provider=FixedWorkspaceProvider(
            workspace,
            ActiveCognitiveModelManifest(
                model_version=model_version,
                parameter_digest=workspace_parameter_digest(workspace),
                training_artifact_digest=digest,
                code_digest=digest,
                contract_digest=digest,
                evaluation_spec_digest=digest,
            ),
        ),
    )
    return service, context_provider, memory_repository


def request(
    cycle_id: str,
    observation_id: str,
    features: tuple[float, float],
    *,
    expected_version: int = 0,
    previous_checkpoint_id: str | None = None,
) -> CognitiveCycleRequest:
    return CognitiveCycleRequest(
        cycle_id=cycle_id,
        expected_checkpoint_version=expected_version,
        previous_checkpoint_id=previous_checkpoint_id,
        observation=observation(observation_id, features),
    )


def test_cycle_commits_serial_state_and_real_memory_audit() -> None:
    service, _, repository = build_service()

    first = service.run_cycle(request("cycle-1", "obs-1", (1.0, -1.0)))
    second = service.run_cycle(
        request(
            "cycle-2",
            "obs-2",
            (-0.2, 1.0),
            expected_version=1,
            previous_checkpoint_id=first.checkpoint.checkpoint_id,
        )
    )

    assert first.checkpoint.version == 1
    assert second.checkpoint.version == 2
    assert second.evidence.audit_committed is True
    assert repository.audit_ids == ["cycle-1", "cycle-2"]
    assert second.checkpoint.hidden_state != first.checkpoint.hidden_state
    assert second.goal_proposal.goal_ref == "internal-goal:session-a"
    working_key = (repository._key(context()), "nb1-cognition:session-a")
    persisted = json.loads(repository.working[working_key].entries[0].content)
    assert persisted["attention"] == second.attention.model_dump(mode="json")
    assert persisted["goal_proposal"] == second.goal_proposal.model_dump(mode="json")
    assert persisted["plan_proposal"] == second.plan_proposal.model_dump(mode="json")
    assert persisted["metacognition"] == second.metacognition.model_dump(mode="json")
    assert persisted["active_model"] == second.evidence.active_model.model_dump(mode="json")
    assert persisted["next_checkpoint_version"] == second.checkpoint.version


def test_exact_replay_is_idempotent_but_changed_payload_is_denied() -> None:
    service, _, repository = build_service()
    original = request("cycle-1", "obs-1", (1.0, -1.0))

    first = service.run_cycle(original)
    replay = service.run_cycle(original)

    assert replay == first
    assert repository.audit_ids == ["cycle-1"]
    with pytest.raises(AtomicPersistenceError):
        service.run_cycle(request("cycle-1", "obs-1", (-1.0, 1.0)))


def test_stale_competing_transition_is_denied_without_partial_commit() -> None:
    service, _, repository = build_service()
    first = service.run_cycle(request("cycle-1", "obs-1", (1.0, -1.0)))
    stale = request(
        "cycle-stale",
        "obs-stale",
        (1.0, -1.0),
        expected_version=1,
        previous_checkpoint_id=first.checkpoint.checkpoint_id,
    )
    service.run_cycle(
        request(
            "cycle-2",
            "obs-2",
            (1.0, -1.0),
            expected_version=1,
            previous_checkpoint_id=first.checkpoint.checkpoint_id,
        )
    )

    with pytest.raises(StaleCognitiveCheckpointError):
        service.run_cycle(stale)
    assert "cycle-stale" not in repository.audit_ids


def test_atomic_failure_exposes_no_checkpoint_or_audit() -> None:
    service, _, repository = build_service()
    repository.fail_before_commit = True

    with pytest.raises(AtomicPersistenceError):
        service.run_cycle(request("cycle-fail", "obs-fail", (1.0, -1.0)))

    assert repository.checkpoints == {}
    assert repository.audit_ids == []


def test_cross_scope_checkpoint_and_incomplete_scope_fail_closed() -> None:
    service, provider, repository = build_service()
    first = service.run_cycle(request("cycle-1", "obs-1", (1.0, -1.0)))
    provider.context = context("session-b")

    with pytest.raises(CognitiveCheckpointUnavailableError):
        service.run_cycle(
            request(
                "cycle-2",
                "obs-2",
                (1.0, -1.0),
                expected_version=1,
                previous_checkpoint_id=first.checkpoint.checkpoint_id,
            )
        )

    provider.context = RuntimeContext(actor_id="actor-a", tenant_id="tenant-a", area_id="area-a")
    with pytest.raises(CognitiveScopeError):
        service.run_cycle(request("cycle-3", "obs-3", (1.0, -1.0)))
    assert repository.audit_ids == ["cycle-1"]


def test_divergent_cognitive_and_memory_context_providers_fail_before_commit() -> None:
    cognitive_context = ContextProvider(context("session-a"))
    memory_context = ContextProvider(context("session-b"))
    repository = AtomicMemoryRepository()
    memory_service = MemoryService(
        context_provider=memory_context,
        repository=repository,
    )
    workspace = NeuralWorkspace(parameters())
    digest = "c" * 64
    service = CognitiveCycleService(
        context_provider=cognitive_context,
        memory_gate=MemoryServiceCognitiveGate(memory_service, memory_context),
        workspace_provider=FixedWorkspaceProvider(
            workspace,
            ActiveCognitiveModelManifest(
                model_version=workspace.parameters.model_version,
                parameter_digest=workspace_parameter_digest(workspace),
                training_artifact_digest=digest,
                code_digest=digest,
                contract_digest=digest,
                evaluation_spec_digest=digest,
            ),
        ),
    )

    with pytest.raises(CognitiveScopeError, match="context providers diverged"):
        service.run_cycle(request("cycle-divergent", "obs-divergent", (1.0, -1.0)))
    assert repository.checkpoints == {}
    assert repository.audit_ids == []


def test_trusted_provider_prevents_request_model_selection_and_model_switch() -> None:
    service, provider, repository = build_service()
    with pytest.raises(ValidationError):
        CognitiveCycleRequest.model_validate(
            {
                **request("cycle-x", "obs-x", (1.0, -1.0)).model_dump(),
                "model_version": "attacker-selected",
            }
        )
    first = service.run_cycle(request("cycle-1", "obs-1", (1.0, -1.0)))
    changed_service, _, _ = build_service(
        provider=provider, repository=repository, model_version="nb1-model-v2"
    )
    with pytest.raises(UnknownNeuralModelError):
        changed_service.run_cycle(
            request(
                "cycle-2",
                "obs-2",
                (1.0, -1.0),
                expected_version=1,
                previous_checkpoint_id=first.checkpoint.checkpoint_id,
            )
        )


@pytest.mark.parametrize(
    "invalid",
    [
        {"tenant_id": "attacker"},
        {"actor_id": "attacker"},
        {"authority": "admin"},
        {"features": (float("nan"), 1.0)},
        {"features": (float("inf"), 1.0)},
        {"features": (1.0,)},
        {"occurred_at": datetime(2026, 7, 16, 20, 0)},
    ],
)
def test_observation_boundary_rejects_scope_authority_and_invalid_signal(
    invalid: dict[str, object],
) -> None:
    payload: dict[str, object] = observation("obs", (1.0, -1.0)).model_dump()
    payload.update(invalid)
    with pytest.raises(ValidationError):
        RecordedObservation.model_validate(payload)


def test_parameters_are_immutable_and_no_effect_surface_is_exposed() -> None:
    workspace = NeuralWorkspace(parameters())
    with pytest.raises(ValidationError):
        workspace.parameters.model_version = "mutated"
    public_names = set(dir(CognitiveCycleService)) | set(dir(MemoryServiceCognitiveGate))
    assert not public_names & {
        "act",
        "dispatch",
        "execute",
        "tool_call",
        "write_action_intent",
    }


def test_corrupt_checkpoint_is_rejected() -> None:
    service, _, repository = build_service()
    first = service.run_cycle(request("cycle-1", "obs-1", (1.0, -1.0)))
    key = next(key for key in repository.checkpoints if key[1] == first.checkpoint.checkpoint_id)
    record = repository.checkpoints[key]
    repository.checkpoints[key] = record.model_copy(update={"entries": ()})

    with pytest.raises(CognitiveRuntimeError):
        service.run_cycle(
            request(
                "cycle-2",
                "obs-2",
                (1.0, -1.0),
                expected_version=1,
                previous_checkpoint_id=first.checkpoint.checkpoint_id,
            )
        )
