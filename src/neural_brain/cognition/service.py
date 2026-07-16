"""Safe serial NB-1 cognitive-cycle application service."""

from typing import Literal

from neural_brain.cognition.adapters import model_manifest_digest
from neural_brain.cognition.errors import (
    CognitiveScopeError,
    StaleCognitiveCheckpointError,
    UnknownNeuralModelError,
)
from neural_brain.cognition.models import (
    ActiveCognitiveModelEvidence,
    CognitiveAuditEvidence,
    CognitiveCheckpoint,
    CognitiveCycleRequest,
    CognitiveCycleResult,
    CognitiveTransitionEnvelope,
    InternalGoalProposal,
    InternalPlanProposal,
    MetacognitiveAssessment,
)
from neural_brain.cognition.ports import ActiveNeuralWorkspaceProvider, CognitiveMemoryGate
from neural_brain.memory.models import MemoryScope, RuntimeContext
from neural_brain.memory.ports import RuntimeContextProvider


class CognitiveCycleService:
    """Run one authenticated, effect-free, fixed-model cognitive transition."""

    def __init__(
        self,
        *,
        context_provider: RuntimeContextProvider,
        memory_gate: CognitiveMemoryGate,
        workspace_provider: ActiveNeuralWorkspaceProvider,
    ) -> None:
        self._context_provider = context_provider
        self._memory_gate = memory_gate
        self._workspace_provider = workspace_provider

    def run_cycle(self, request: CognitiveCycleRequest) -> CognitiveCycleResult:
        """Commit one serial internal cycle or fail without an effect surface."""
        context = self._context_provider.current_context()
        scope = self._scope(context)
        active_model = self._workspace_provider.active_model(context=context)
        workspace = active_model.workspace
        manifest = active_model.manifest
        model_version = workspace.parameters.model_version
        current = None
        if request.previous_checkpoint_id is not None:
            current = self._memory_gate.load_checkpoint(
                context=context, checkpoint_id=request.previous_checkpoint_id
            )
        actual_version = 0 if current is None else current.version
        if actual_version != request.expected_checkpoint_version:
            raise StaleCognitiveCheckpointError("stale cognitive checkpoint version")
        if current is not None:
            if current.scope != scope:
                raise CognitiveScopeError("loaded checkpoint crossed authenticated scope")
            if current.model_version != model_version:
                raise UnknownNeuralModelError("checkpoint model version cannot change in place")

        previous_hidden = 0.0 if current is None else current.hidden_state[0]
        attention, hidden = workspace.step(
            observation=request.observation,
            previous_hidden=previous_hidden,
        )
        confidence = min(abs(hidden), 1.0)
        activation_ambiguity = 1.0 - confidence
        goal_ref = f"internal-goal:{scope.session_id}"
        objective: Literal["maintain_positive_context", "stabilize_negative_context"] = (
            "maintain_positive_context" if hidden >= 0.0 else "stabilize_negative_context"
        )
        if activation_ambiguity > 0.6:
            plan_steps: tuple[
                Literal["maintain_focus", "observe_more", "request_clarification"], ...
            ] = ("request_clarification",)
            metacognitive = MetacognitiveAssessment(
                decision="ask",
                activation_ambiguity=activation_ambiguity,
                reason="insufficient_context",
            )
        else:
            plan_steps = ("maintain_focus", "observe_more")
            metacognitive = MetacognitiveAssessment(
                decision="continue",
                activation_ambiguity=activation_ambiguity,
                reason="sufficient_context",
            )

        goal_proposal = InternalGoalProposal(
            goal_ref=goal_ref,
            objective=objective,
            confidence=confidence,
        )
        plan_proposal = InternalPlanProposal(
            plan_ref=f"internal-plan:{request.cycle_id}",
            steps=plan_steps,
        )
        active_model_evidence = ActiveCognitiveModelEvidence(
            manifest_digest=model_manifest_digest(manifest),
            parameter_digest=manifest.parameter_digest,
            training_artifact_digest=manifest.training_artifact_digest,
            code_digest=manifest.code_digest,
            contract_digest=manifest.contract_digest,
            evaluation_spec_digest=manifest.evaluation_spec_digest,
        )
        transition = CognitiveTransitionEnvelope(
            cycle_id=request.cycle_id,
            observation_id=request.observation.observation_id,
            previous_checkpoint_version=actual_version,
            next_checkpoint_version=actual_version + 1,
            model_version=model_version,
            hidden_state=(hidden,),
            attention=attention,
            goal_proposal=goal_proposal,
            plan_proposal=plan_proposal,
            metacognition=metacognitive,
            active_model=active_model_evidence,
        )
        committed = self._memory_gate.commit_checkpoint(
            context=context,
            cycle_id=request.cycle_id,
            expected_version=request.expected_checkpoint_version,
            transition=transition,
            observation=request.observation,
        )
        if committed.checkpoint.scope != scope:
            raise CognitiveScopeError("committed checkpoint crossed authenticated scope")
        checkpoint = CognitiveCheckpoint(
            checkpoint_id=committed.checkpoint.checkpoint_id,
            version=committed.checkpoint.working_memory_version,
            model_version=model_version,
            hidden_state=(hidden,),
            latest_observation_id=committed.observation.observation_id,
            scope=committed.checkpoint.scope,
        )
        result = CognitiveCycleResult(
            attention=attention,
            checkpoint=checkpoint,
            goal_proposal=goal_proposal,
            plan_proposal=plan_proposal,
            metacognition=metacognitive,
            evidence=CognitiveAuditEvidence(
                cycle_id=request.cycle_id,
                model_version=model_version,
                training_provenance_ref=workspace.parameters.training_provenance_ref,
                observation_id=request.observation.observation_id,
                previous_checkpoint_version=actual_version,
                committed_checkpoint_version=committed.checkpoint.working_memory_version,
                active_model=active_model_evidence,
                audit_committed=committed.audit_committed,
            ),
        )
        return result

    @staticmethod
    def _scope(context: RuntimeContext) -> MemoryScope:
        if context.project_id is None or context.session_id is None:
            raise CognitiveScopeError("NB-1 cognition requires project and session scope")
        return MemoryScope(
            tenant_id=context.tenant_id,
            area_id=context.area_id,
            project_id=context.project_id,
            session_id=context.session_id,
        )
