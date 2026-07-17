"""Label-free candidate boundary for externally owned hidden evaluation."""

import hashlib
import json
import math
from datetime import UTC, datetime
from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from neural_brain.cognition.adapters import (
    ActiveCognitiveModel,
    model_manifest_digest,
    workspace_parameter_digest,
)
from neural_brain.cognition.models import (
    ActiveCognitiveModelManifest,
    FeaturePair,
    NeuralWorkspaceParameters,
    RecordedObservation,
    Sha256Digest,
)
from neural_brain.memory.models import OpaqueId, StrictModel

type ContextLabel = Literal["positive", "negative"]

_EVALUATION_TIME = datetime(2000, 1, 1, tzinfo=UTC)
_EVALUATION_PROVENANCE = "external-hidden-evaluator-unlabeled-input"


def _canonical_digest(value: object) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return hashlib.sha256(payload).hexdigest()


class CandidateEvaluationBundle(StrictModel):
    """Self-verifying immutable candidate supplied before hidden-data attachment."""

    artifact_digest: Sha256Digest
    format_version: Literal[1] = 1
    source_commit: Annotated[str, Field(pattern=r"^[0-9a-f]{40}$")]
    source_tree_digest: Sha256Digest
    training_code_digest: Sha256Digest
    candidate_code_digest: Sha256Digest
    evaluation_contract_digest: Sha256Digest
    dependency_lock_digest: Sha256Digest
    fixed_train_majority_label: ContextLabel
    frozen_at: datetime
    model_manifest: ActiveCognitiveModelManifest
    model_manifest_digest: Sha256Digest
    parameters: NeuralWorkspaceParameters

    @model_validator(mode="after")
    def validate_bundle(self) -> Self:
        """Bind the manifest, learned parameters, training provenance, and bundle."""
        if self.model_manifest_digest != model_manifest_digest(self.model_manifest):
            raise ValueError("candidate model manifest digest does not match its content")
        if self.frozen_at.tzinfo is None or self.frozen_at.utcoffset() is None:
            raise ValueError("candidate frozen_at must include a timezone offset")
        if self.model_manifest.code_digest != self.training_code_digest:
            raise ValueError("training code digest does not match the model manifest")
        if self.model_manifest.model_version != self.parameters.model_version:
            raise ValueError("candidate model version does not match its parameters")
        if self.model_manifest.parameter_digest != workspace_parameter_digest_from_parameters(
            self.parameters
        ):
            raise ValueError("candidate parameter digest does not match its parameters")
        if self.model_manifest.training_artifact_digest != self.parameters.training_provenance_ref:
            raise ValueError("candidate parameters do not reference the manifest training artifact")
        if self.artifact_digest != candidate_evaluation_bundle_digest(
            model_manifest=self.model_manifest,
            model_manifest_digest_value=self.model_manifest_digest,
            parameters=self.parameters,
            source_commit=self.source_commit,
            source_tree_digest=self.source_tree_digest,
            training_code_digest=self.training_code_digest,
            candidate_code_digest=self.candidate_code_digest,
            evaluation_contract_digest=self.evaluation_contract_digest,
            dependency_lock_digest=self.dependency_lock_digest,
            fixed_train_majority_label=self.fixed_train_majority_label,
            frozen_at=self.frozen_at,
        ):
            raise ValueError("candidate bundle digest does not match its immutable content")
        return self


class UnlabeledEvaluationObservation(StrictModel):
    """One bounded observation without a label or hidden-artifact metadata."""

    observation_id: OpaqueId
    features: FeaturePair

    @model_validator(mode="after")
    def features_are_finite(self) -> Self:
        """Reject non-portable NaN or infinite candidate inputs."""
        if not all(math.isfinite(value) for value in self.features):
            raise ValueError("evaluation observation features must be finite")
        return self


class UnlabeledEvaluationSequence(StrictModel):
    """One ordered hidden input sequence without its expected outcome."""

    sequence_id: OpaqueId
    observations: Annotated[
        tuple[UnlabeledEvaluationObservation, ...], Field(min_length=2, max_length=8)
    ]

    @model_validator(mode="after")
    def observation_ids_are_unique(self) -> Self:
        """Reject ambiguous ordering caused by repeated observation identities."""
        observation_ids = tuple(observation.observation_id for observation in self.observations)
        if len(observation_ids) != len(set(observation_ids)):
            raise ValueError("evaluation observation IDs must be unique")
        return self


class UnlabeledEvaluationBatch(StrictModel):
    """Digest-bound ordered input whose schema cannot carry labels or hidden metadata."""

    artifact_digest: Sha256Digest
    run_id: OpaqueId
    sequences: Annotated[
        tuple[UnlabeledEvaluationSequence, ...], Field(min_length=1, max_length=4096)
    ]

    @model_validator(mode="after")
    def validate_batch(self) -> Self:
        """Require unique opaque identities and an exact canonical content digest."""
        sequence_ids = tuple(sequence.sequence_id for sequence in self.sequences)
        if len(sequence_ids) != len(set(sequence_ids)):
            raise ValueError("evaluation sequence IDs must be unique")
        observation_ids = tuple(
            observation.observation_id
            for sequence in self.sequences
            for observation in sequence.observations
        )
        if len(observation_ids) != len(set(observation_ids)):
            raise ValueError("evaluation observation IDs must be globally unique")
        if self.artifact_digest != unlabeled_evaluation_batch_digest(
            run_id=self.run_id, sequences=self.sequences
        ):
            raise ValueError("unlabeled evaluation batch digest does not match its content")
        return self


class PredictionRecord(StrictModel):
    """One ordered candidate prediction without correctness or reference-label data."""

    sequence_id: OpaqueId
    predicted_label: ContextLabel


class PredictionBatch(StrictModel):
    """Digest-bound, effect-free full-mechanism predictions for one candidate input."""

    artifact_digest: Sha256Digest
    run_id: OpaqueId
    candidate_digest: Sha256Digest
    input_digest: Sha256Digest
    predictions: Annotated[tuple[PredictionRecord, ...], Field(min_length=1, max_length=4096)]
    network_calls: Literal[0] = 0
    external_effects: Literal[0] = 0
    active_model_mutated: Literal[False] = False

    @model_validator(mode="after")
    def validate_predictions(self) -> Self:
        """Reject duplicate identities and any output-content digest mismatch."""
        sequence_ids = tuple(prediction.sequence_id for prediction in self.predictions)
        if len(sequence_ids) != len(set(sequence_ids)):
            raise ValueError("prediction sequence IDs must be unique")
        if self.artifact_digest != prediction_batch_digest(
            candidate_digest=self.candidate_digest,
            input_digest=self.input_digest,
            run_id=self.run_id,
            predictions=self.predictions,
        ):
            raise ValueError("prediction batch digest does not match its immutable content")
        return self


def workspace_parameter_digest_from_parameters(parameters: NeuralWorkspaceParameters) -> str:
    """Hash parameters through the same trusted workspace representation as runtime."""
    from neural_brain.cognition.workspace import NeuralWorkspace

    return workspace_parameter_digest(NeuralWorkspace(parameters))


def candidate_evaluation_bundle_digest(
    *,
    model_manifest: ActiveCognitiveModelManifest,
    model_manifest_digest_value: Sha256Digest,
    parameters: NeuralWorkspaceParameters,
    source_commit: str,
    source_tree_digest: Sha256Digest,
    training_code_digest: Sha256Digest,
    candidate_code_digest: Sha256Digest,
    evaluation_contract_digest: Sha256Digest,
    dependency_lock_digest: Sha256Digest,
    fixed_train_majority_label: ContextLabel,
    frozen_at: datetime,
) -> str:
    """Hash every non-self-referential candidate bundle field canonically."""
    return _canonical_digest(
        {
            "format_version": 1,
            "source_commit": source_commit,
            "source_tree_digest": source_tree_digest,
            "training_code_digest": training_code_digest,
            "candidate_code_digest": candidate_code_digest,
            "evaluation_contract_digest": evaluation_contract_digest,
            "dependency_lock_digest": dependency_lock_digest,
            "fixed_train_majority_label": fixed_train_majority_label,
            "frozen_at": frozen_at.isoformat(),
            "model_manifest": model_manifest.model_dump(mode="json"),
            "model_manifest_digest": model_manifest_digest_value,
            "parameters": parameters.model_dump(mode="json"),
        }
    )


def unlabeled_evaluation_batch_digest(
    *, run_id: OpaqueId, sequences: tuple[UnlabeledEvaluationSequence, ...]
) -> str:
    """Hash the exact sequence and observation order without hidden labels."""
    return _canonical_digest(
        {
            "run_id": run_id,
            "sequences": [sequence.model_dump(mode="json") for sequence in sequences],
        }
    )


def prediction_batch_digest(
    *,
    candidate_digest: Sha256Digest,
    input_digest: Sha256Digest,
    run_id: OpaqueId,
    predictions: tuple[PredictionRecord, ...],
) -> str:
    """Hash every non-self-referential prediction-batch field canonically."""
    return _canonical_digest(
        {
            "candidate_digest": candidate_digest,
            "input_digest": input_digest,
            "run_id": run_id,
            "predictions": [prediction.model_dump(mode="json") for prediction in predictions],
            "network_calls": 0,
            "external_effects": 0,
            "active_model_mutated": False,
        }
    )


def predict_full_mechanism(
    *,
    active_model: ActiveCognitiveModel,
    candidate: CandidateEvaluationBundle,
    batch: UnlabeledEvaluationBatch,
) -> PredictionBatch:
    """Run only the frozen full neural mechanism over ordered label-free input."""
    if type(active_model) is not ActiveCognitiveModel:
        raise TypeError("hidden prediction requires an ActiveCognitiveModel")
    if model_manifest_digest(active_model.manifest) != candidate.model_manifest_digest:
        raise ValueError("active model manifest does not match the frozen candidate")
    if active_model.manifest != candidate.model_manifest:
        raise ValueError("active model manifest content does not match the frozen candidate")
    if active_model.workspace.parameters != candidate.parameters:
        raise ValueError("active model parameters do not match the frozen candidate")
    if active_model.workspace._attention_mode != "learned":
        raise ValueError("hidden prediction requires the learned full-mechanism attention")
    if not active_model.workspace._recurrence_enabled:
        raise ValueError("hidden prediction requires the recurrent full mechanism")

    manifest_before = model_manifest_digest(active_model.manifest)
    parameters_before = active_model.workspace.parameters.model_dump_json()
    predictions: list[PredictionRecord] = []
    for sequence in batch.sequences:
        hidden = 0.0
        for observation in sequence.observations:
            _, hidden = active_model.workspace.step(
                observation=RecordedObservation(
                    observation_id=observation.observation_id,
                    source_kind="synthetic",
                    provenance_ref=_EVALUATION_PROVENANCE,
                    features=observation.features,
                    occurred_at=_EVALUATION_TIME,
                ),
                previous_hidden=hidden,
            )
        predictions.append(
            PredictionRecord(
                sequence_id=sequence.sequence_id,
                predicted_label="positive" if hidden >= 0.0 else "negative",
            )
        )

    if model_manifest_digest(active_model.manifest) != manifest_before:
        raise RuntimeError("active model manifest mutated during hidden prediction")
    if active_model.workspace.parameters.model_dump_json() != parameters_before:
        raise RuntimeError("active model parameters mutated during hidden prediction")
    immutable_predictions = tuple(predictions)
    artifact_digest = prediction_batch_digest(
        candidate_digest=candidate.artifact_digest,
        input_digest=batch.artifact_digest,
        run_id=batch.run_id,
        predictions=immutable_predictions,
    )
    return PredictionBatch(
        artifact_digest=artifact_digest,
        run_id=batch.run_id,
        candidate_digest=candidate.artifact_digest,
        input_digest=batch.artifact_digest,
        predictions=immutable_predictions,
    )
