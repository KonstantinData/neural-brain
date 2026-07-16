"""Deterministic offline-only training evidence for EVAL-01 NB-1 v3."""

import hashlib
import json
import random
from datetime import UTC, datetime
from typing import Annotated, Final, Literal, Self

from pydantic import Field, model_validator

from neural_brain.cognition.adapters import (
    model_manifest_digest,
    workspace_parameter_digest,
)
from neural_brain.cognition.evaluation import EvaluationSequence
from neural_brain.cognition.models import (
    ActiveCognitiveModelManifest,
    NeuralWorkspaceParameters,
    RecordedObservation,
    Sha256Digest,
)
from neural_brain.cognition.workspace import NeuralWorkspace
from neural_brain.memory.models import StrictModel

SPEC_ID: Final[Literal["EVAL-01.NB-1.safe-serial-cognition.v3"]] = (
    "EVAL-01.NB-1.safe-serial-cognition.v3"
)
SPEC_DIGEST: Final[Literal["3ac6d895d3f33b5d63c462471ca335d6d538cc379ae8eb3ad0611c81271b3fc8"]] = (
    "3ac6d895d3f33b5d63c462471ca335d6d538cc379ae8eb3ad0611c81271b3fc8"
)
GENERATOR_CONTRACT: Final[Literal["nb1-serial-context-generator-v2"]] = (
    "nb1-serial-context-generator-v2"
)
TRAINING_SEED: Final[Literal[1931]] = 1931
TRAINING_SIZE: Final[Literal[512]] = 512


def _canonical_digest(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


class TrainingDataset(StrictModel):
    """Immutable train-only artifact; development and hidden roles cannot be fitted."""

    role: Literal["train"] = "train"
    generator_contract: Literal["nb1-serial-context-generator-v2"]
    seed: Literal[1931]
    artifact_digest: Sha256Digest
    sequences: Annotated[tuple[EvaluationSequence, ...], Field(min_length=512, max_length=512)]

    @model_validator(mode="after")
    def digest_matches_artifact(self) -> Self:
        """Reject metadata or sequence tampering before fitting."""
        if self.artifact_digest != training_dataset_digest(
            generator_contract=self.generator_contract,
            seed=self.seed,
            sequences=self.sequences,
        ):
            raise ValueError("training dataset digest does not match its immutable content")
        return self


class GridCandidate(StrictModel):
    """One bounded trainable parameter candidate."""

    attention_logits: tuple[float, float]
    input_weights: tuple[float, float]
    recurrent_weight: Annotated[float, Field(strict=True, ge=-4.0, le=4.0)]
    bias: Annotated[float, Field(strict=True, ge=-4.0, le=4.0)] = 0.0


class TrainingAttempt(StrictModel):
    """Complete disclosed score for one candidate on the training split."""

    candidate_index: Annotated[int, Field(strict=True, ge=0)]
    candidate: GridCandidate
    correct: Annotated[int, Field(strict=True, ge=0, le=512)]
    total: Literal[512] = 512
    accuracy: Annotated[float, Field(strict=True, ge=0.0, le=1.0)]


class TrainingProvenance(StrictModel):
    """Immutable evidence for one bounded train-only selection run."""

    artifact_digest: Sha256Digest
    spec_id: Literal["EVAL-01.NB-1.safe-serial-cognition.v3"]
    spec_digest: Literal["3ac6d895d3f33b5d63c462471ca335d6d538cc379ae8eb3ad0611c81271b3fc8"]
    recipe: Literal["offline_deterministic_bounded_grid_search"]
    dataset_role: Literal["train"]
    dataset_digest: Sha256Digest
    seed: Literal[1931]
    training_code_digest: Sha256Digest
    contract_digest: Sha256Digest
    environment_digest: Sha256Digest
    recipe_digest: Sha256Digest
    attempted_candidates: tuple[TrainingAttempt, ...]
    selected_candidate_index: Annotated[int, Field(strict=True, ge=0)]
    selection_rule: Literal["maximum_train_accuracy_then_lowest_candidate_index"]
    runtime_training_surface: Literal[False] = False
    external_effects: Literal[0] = 0
    evaluation_gates_passed: tuple[()] = ()
    recognition_gates_passed: tuple[()] = ()
    stage_release_authorized: Literal[False] = False
    claim_status: Literal["offline_development_candidate_only"]

    @model_validator(mode="after")
    def validate_provenance(self) -> Self:
        """Reject missing attempts, invalid selection, and digest tampering."""
        if not self.attempted_candidates:
            raise ValueError("training provenance requires every attempted candidate")
        if tuple(attempt.candidate_index for attempt in self.attempted_candidates) != tuple(
            range(len(self.attempted_candidates))
        ):
            raise ValueError("training attempt indexes must be complete and ordered")
        expected_selected = min(
            self.attempted_candidates,
            key=lambda attempt: (-attempt.accuracy, attempt.candidate_index),
        ).candidate_index
        if self.selected_candidate_index != expected_selected:
            raise ValueError("selected candidate violates the preregistered selection rule")
        if self.artifact_digest != training_provenance_digest(self):
            raise ValueError("training provenance digest does not match its immutable content")
        return self


class ParameterArtifact(StrictModel):
    """Immutable selected parameter artifact."""

    parameter_digest: Sha256Digest
    parameters: NeuralWorkspaceParameters

    @model_validator(mode="after")
    def digest_matches_parameters(self) -> Self:
        """Reject parameter or identity tampering."""
        if self.parameter_digest != workspace_parameter_digest(NeuralWorkspace(self.parameters)):
            raise ValueError("parameter artifact digest does not match its parameters")
        return self


class OfflineTrainingBundle(StrictModel):
    """Self-verifying non-promoted model and provenance bundle."""

    format_version: Literal[1] = 1
    parameter_artifact: ParameterArtifact
    training_provenance: TrainingProvenance
    model_manifest: ActiveCognitiveModelManifest
    model_manifest_digest: Sha256Digest
    evaluation_gates_passed: tuple[()] = ()
    recognition_gates_passed: tuple[()] = ()
    stage_release_authorized: Literal[False] = False
    active_model_promoted: Literal[False] = False

    @model_validator(mode="after")
    def bundle_is_consistent(self) -> Self:
        """Bind model, parameters, training, code, contract, and spec identities."""
        parameters = self.parameter_artifact.parameters
        provenance = self.training_provenance
        manifest = self.model_manifest
        if parameters.training_provenance_ref != provenance.artifact_digest:
            raise ValueError("parameters do not reference their training provenance")
        if manifest.model_version != parameters.model_version:
            raise ValueError("manifest model version does not match parameters")
        if manifest.parameter_digest != self.parameter_artifact.parameter_digest:
            raise ValueError("manifest parameter digest does not match parameter artifact")
        if manifest.training_artifact_digest != provenance.artifact_digest:
            raise ValueError("manifest training digest does not match provenance")
        if manifest.code_digest != provenance.training_code_digest:
            raise ValueError("manifest code digest does not match training provenance")
        if manifest.contract_digest != provenance.contract_digest:
            raise ValueError("manifest contract digest does not match training provenance")
        if manifest.evaluation_spec_digest != provenance.spec_digest:
            raise ValueError("manifest evaluation specification digest is invalid")
        if self.model_manifest_digest != model_manifest_digest(manifest):
            raise ValueError("model manifest digest does not match its immutable content")
        return self


def training_dataset_digest(
    *,
    generator_contract: str,
    seed: int,
    sequences: tuple[EvaluationSequence, ...],
) -> str:
    """Hash training role, public generator provenance, and canonical sequences."""
    return _canonical_digest(
        {
            "role": "train",
            "generator_contract": generator_contract,
            "seed": seed,
            "sequences": [sequence.model_dump(mode="json") for sequence in sequences],
        }
    )


def training_provenance_digest(provenance: TrainingProvenance) -> str:
    """Hash provenance without its self-referential digest field."""
    payload = provenance.model_dump(mode="json", exclude={"artifact_digest"})
    return _canonical_digest(payload)


def generate_training_dataset() -> TrainingDataset:
    """Generate only the public preregistered training split with its fixed seed."""
    randomizer = random.Random(TRAINING_SEED)
    occurred_at = datetime(2026, 7, 16, 19, 20, tzinfo=UTC)
    sequences: list[EvaluationSequence] = []
    for index in range(TRAINING_SIZE):
        positive = randomizer.randrange(2) == 0
        sign = 1.0 if positive else -1.0
        jitter = randomizer.choice((-0.1, 0.0, 0.1))
        feature_pairs = (
            (sign + jitter, -2.0 * sign),
            (sign, -2.0 * sign - jitter),
            (sign - jitter, -2.0 * sign),
            (-0.5 * sign, 0.2 * sign),
        )
        sequence_id = f"train-{index:04d}"
        observations = tuple(
            _training_observation(
                sequence_id=sequence_id,
                position=position,
                features=features,
                occurred_at=occurred_at,
            )
            for position, features in enumerate(feature_pairs)
        )
        sequences.append(
            EvaluationSequence(
                sequence_id=sequence_id,
                observations=observations,
                expected_label="positive" if positive else "negative",
            )
        )
    immutable_sequences = tuple(sequences)
    return TrainingDataset(
        generator_contract=GENERATOR_CONTRACT,
        seed=TRAINING_SEED,
        artifact_digest=training_dataset_digest(
            generator_contract=GENERATOR_CONTRACT,
            seed=TRAINING_SEED,
            sequences=immutable_sequences,
        ),
        sequences=immutable_sequences,
    )


def _training_observation(
    *, sequence_id: str, position: int, features: tuple[float, float], occurred_at: datetime
) -> RecordedObservation:
    return RecordedObservation(
        observation_id=f"{sequence_id}:{position}",
        source_kind="synthetic",
        provenance_ref=GENERATOR_CONTRACT,
        features=features,
        occurred_at=occurred_at,
    )


def bounded_grid() -> tuple[GridCandidate, ...]:
    """Return the complete, ordered and resource-bounded EVAL-01 training grid."""
    attention_options = ((4.0, -4.0), (2.0, -2.0), (0.0, 0.0))
    input_options = ((1.0, 1.0), (1.0, -1.0), (-1.0, 1.0))
    recurrence_options = (1.5, 0.5, 0.0)
    return tuple(
        GridCandidate(
            attention_logits=attention,
            input_weights=inputs,
            recurrent_weight=recurrence,
        )
        for attention in attention_options
        for inputs in input_options
        for recurrence in recurrence_options
    )


def recipe_digest() -> str:
    """Identify the exact ordered search space and selection rule."""
    return _canonical_digest(
        {
            "kind": "offline_deterministic_bounded_grid_search",
            "seed": TRAINING_SEED,
            "training_split_only": True,
            "candidates": [candidate.model_dump(mode="json") for candidate in bounded_grid()],
            "selection_rule": "maximum_train_accuracy_then_lowest_candidate_index",
        }
    )


def train_offline(
    *,
    dataset: TrainingDataset,
    training_code_digest: Sha256Digest,
    contract_digest: Sha256Digest,
    environment_digest: Sha256Digest,
) -> OfflineTrainingBundle:
    """Fit a non-promoted candidate using the immutable training split only."""
    attempts = tuple(
        _score_candidate(candidate_index=index, candidate=candidate, dataset=dataset)
        for index, candidate in enumerate(bounded_grid())
    )
    selected_index = min(
        attempts, key=lambda attempt: (-attempt.accuracy, attempt.candidate_index)
    ).candidate_index
    provenance_content = {
        "spec_id": SPEC_ID,
        "spec_digest": SPEC_DIGEST,
        "recipe": "offline_deterministic_bounded_grid_search",
        "dataset_role": "train",
        "dataset_digest": dataset.artifact_digest,
        "seed": TRAINING_SEED,
        "training_code_digest": training_code_digest,
        "contract_digest": contract_digest,
        "environment_digest": environment_digest,
        "recipe_digest": recipe_digest(),
        "attempted_candidates": [attempt.model_dump(mode="json") for attempt in attempts],
        "selected_candidate_index": selected_index,
        "selection_rule": "maximum_train_accuracy_then_lowest_candidate_index",
        "runtime_training_surface": False,
        "external_effects": 0,
        "evaluation_gates_passed": [],
        "recognition_gates_passed": [],
        "stage_release_authorized": False,
        "claim_status": "offline_development_candidate_only",
    }
    provenance = TrainingProvenance(
        artifact_digest=_canonical_digest(provenance_content),
        spec_id=SPEC_ID,
        spec_digest=SPEC_DIGEST,
        recipe="offline_deterministic_bounded_grid_search",
        dataset_role="train",
        dataset_digest=dataset.artifact_digest,
        seed=TRAINING_SEED,
        training_code_digest=training_code_digest,
        contract_digest=contract_digest,
        environment_digest=environment_digest,
        recipe_digest=recipe_digest(),
        attempted_candidates=attempts,
        selected_candidate_index=selected_index,
        selection_rule="maximum_train_accuracy_then_lowest_candidate_index",
        claim_status="offline_development_candidate_only",
    )
    selected = attempts[selected_index].candidate
    model_version = f"nb1-offline-grid-v1-{provenance.artifact_digest[:16]}"
    parameters = NeuralWorkspaceParameters(
        model_version=model_version,
        training_provenance_ref=provenance.artifact_digest,
        attention_logits=selected.attention_logits,
        input_weights=selected.input_weights,
        recurrent_weight=selected.recurrent_weight,
        bias=selected.bias,
    )
    parameter_artifact = ParameterArtifact(
        parameter_digest=workspace_parameter_digest(NeuralWorkspace(parameters)),
        parameters=parameters,
    )
    manifest = ActiveCognitiveModelManifest(
        model_version=model_version,
        parameter_digest=parameter_artifact.parameter_digest,
        training_artifact_digest=provenance.artifact_digest,
        code_digest=training_code_digest,
        contract_digest=contract_digest,
        evaluation_spec_digest=SPEC_DIGEST,
    )
    return OfflineTrainingBundle(
        parameter_artifact=parameter_artifact,
        training_provenance=provenance,
        model_manifest=manifest,
        model_manifest_digest=model_manifest_digest(manifest),
    )


def _score_candidate(
    *, candidate_index: int, candidate: GridCandidate, dataset: TrainingDataset
) -> TrainingAttempt:
    parameters = NeuralWorkspaceParameters(
        model_version="offline-grid-scoring-only",
        training_provenance_ref="uncommitted-training-provenance",
        attention_logits=candidate.attention_logits,
        input_weights=candidate.input_weights,
        recurrent_weight=candidate.recurrent_weight,
        bias=candidate.bias,
    )
    workspace = NeuralWorkspace(parameters)
    correct = 0
    for sequence in dataset.sequences:
        hidden = 0.0
        for observation in sequence.observations:
            _, hidden = workspace.step(observation=observation, previous_hidden=hidden)
        predicted = "positive" if hidden >= 0.0 else "negative"
        correct += int(predicted == sequence.expected_label)
    return TrainingAttempt(
        candidate_index=candidate_index,
        candidate=candidate,
        correct=correct,
        accuracy=correct / len(dataset.sequences),
    )
