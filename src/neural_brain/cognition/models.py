"""Strict immutable models for the first effect-free NB-1 cognition slice."""

import math
from datetime import datetime
from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from neural_brain.memory.models import MemoryScope, OpaqueId, StrictModel

type FeaturePair = Annotated[tuple[float, float], Field(min_length=2, max_length=2)]
type WorkspaceUnit = Annotated[tuple[float], Field(min_length=1, max_length=1)]
type MetacognitiveDecision = Literal["continue", "ask", "defer", "stop"]
type InternalPlanStep = Literal["maintain_focus", "observe_more", "request_clarification"]
type Sha256Digest = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]


class RecordedObservation(StrictModel):
    """Untrusted recorded or synthetic observation without actor or scope fields."""

    observation_id: OpaqueId
    source_kind: Literal["recorded", "synthetic"]
    provenance_ref: OpaqueId
    features: FeaturePair
    occurred_at: datetime

    @model_validator(mode="after")
    def validate_observation(self) -> Self:
        """Require finite features and an unambiguous timestamp."""
        if self.occurred_at.tzinfo is None or self.occurred_at.utcoffset() is None:
            raise ValueError("occurred_at must include a timezone offset")
        if not all(math.isfinite(value) for value in self.features):
            raise ValueError("observation features must be finite")
        return self


class CognitiveCycleRequest(StrictModel):
    """One untrusted request for a serial internal cognitive transition."""

    cycle_id: OpaqueId
    expected_checkpoint_version: Annotated[int, Field(strict=True, ge=0)]
    previous_checkpoint_id: OpaqueId | None = None
    observation: RecordedObservation

    @model_validator(mode="after")
    def checkpoint_reference_matches_version(self) -> Self:
        """Require an explicit immutable predecessor for every continued cycle."""
        if self.expected_checkpoint_version == 0 and self.previous_checkpoint_id is not None:
            raise ValueError("an initial cycle cannot name a previous checkpoint")
        if self.expected_checkpoint_version > 0 and self.previous_checkpoint_id is None:
            raise ValueError("a continued cycle requires its previous checkpoint")
        return self


class NeuralWorkspaceParameters(StrictModel):
    """Fixed-version trainable parameters loaded outside the request boundary."""

    model_version: OpaqueId
    training_provenance_ref: OpaqueId
    attention_logits: FeaturePair
    input_weights: FeaturePair
    recurrent_weight: Annotated[float, Field(strict=True, ge=-4.0, le=4.0)]
    bias: Annotated[float, Field(strict=True, ge=-4.0, le=4.0)] = 0.0

    @model_validator(mode="after")
    def values_are_finite(self) -> Self:
        """Reject unusable or platform-dependent parameter values."""
        values = (*self.attention_logits, *self.input_weights, self.recurrent_weight, self.bias)
        if not all(math.isfinite(value) for value in values):
            raise ValueError("neural workspace parameters must be finite")
        return self


class ActiveCognitiveModelManifest(StrictModel):
    """Trusted immutable identity and provenance for the active runtime model."""

    model_version: OpaqueId
    parameter_digest: Sha256Digest
    training_artifact_digest: Sha256Digest
    code_digest: Sha256Digest
    contract_digest: Sha256Digest
    evaluation_spec_digest: Sha256Digest


class ActiveCognitiveModelEvidence(StrictModel):
    """Manifest identity copied into committed cycle evidence."""

    manifest_digest: Sha256Digest
    parameter_digest: Sha256Digest
    training_artifact_digest: Sha256Digest
    code_digest: Sha256Digest
    contract_digest: Sha256Digest
    evaluation_spec_digest: Sha256Digest


class AttentionDecision(StrictModel):
    """Bounded learned allocation over exactly two input channels."""

    distribution: FeaturePair
    selected_feature_index: Literal[0, 1]

    @model_validator(mode="after")
    def distribution_is_normalized(self) -> Self:
        """Require a proper deterministic attention distribution."""
        if any(value < 0.0 or value > 1.0 for value in self.distribution):
            raise ValueError("attention weights must be probabilities")
        if not math.isclose(sum(self.distribution), 1.0, abs_tol=1e-12):
            raise ValueError("attention distribution must sum to one")
        return self


class CognitiveCheckpoint(StrictModel):
    """Authenticated session-bound recurrent state committed by compare-and-set."""

    checkpoint_id: OpaqueId
    version: Annotated[int, Field(strict=True, ge=1)]
    model_version: OpaqueId
    hidden_state: WorkspaceUnit
    latest_observation_id: OpaqueId
    scope: MemoryScope


class InternalGoalProposal(StrictModel):
    """Internal goal proposal with no authority or protected-state write surface."""

    goal_ref: OpaqueId
    objective: Literal["maintain_positive_context", "stabilize_negative_context"]
    confidence: Annotated[float, Field(strict=True, ge=0.0, le=1.0)]


class InternalPlanProposal(StrictModel):
    """Bounded internal plan whose steps cannot represent an external effect."""

    plan_ref: OpaqueId
    steps: Annotated[tuple[InternalPlanStep, ...], Field(min_length=1, max_length=2)]


class MetacognitiveAssessment(StrictModel):
    """Activation-ambiguity heuristic; not a calibrated uncertainty estimate."""

    decision: MetacognitiveDecision
    activation_ambiguity: Annotated[float, Field(strict=True, ge=0.0, le=1.0)]
    reason: Literal["sufficient_context", "insufficient_context"]


class CognitiveAuditEvidence(StrictModel):
    """Deterministic evidence attached to the committed internal cycle."""

    cycle_id: OpaqueId
    model_version: OpaqueId
    training_provenance_ref: OpaqueId
    observation_id: OpaqueId
    previous_checkpoint_version: Annotated[int, Field(strict=True, ge=0)]
    committed_checkpoint_version: Annotated[int, Field(strict=True, ge=1)]
    active_model: ActiveCognitiveModelEvidence
    external_effects_occurred: Literal[False] = False
    active_model_mutated: Literal[False] = False
    audit_committed: Literal[True]


class CognitiveCycleResult(StrictModel):
    """Committed NB-1 internal cycle result."""

    attention: AttentionDecision
    checkpoint: CognitiveCheckpoint
    goal_proposal: InternalGoalProposal
    plan_proposal: InternalPlanProposal
    metacognition: MetacognitiveAssessment
    evidence: CognitiveAuditEvidence

    @model_validator(mode="after")
    def evidence_matches_checkpoint(self) -> Self:
        """Reject internally inconsistent runtime results."""
        if self.evidence.model_version != self.checkpoint.model_version:
            raise ValueError("evidence and checkpoint model versions must match")
        if self.evidence.committed_checkpoint_version != self.checkpoint.version:
            raise ValueError("evidence must reference the committed checkpoint")
        if self.evidence.observation_id != self.checkpoint.latest_observation_id:
            raise ValueError("evidence must reference the checkpoint observation")
        return self
