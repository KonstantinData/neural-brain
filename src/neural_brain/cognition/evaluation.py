"""Independent-dataset evaluation harness for the first NB-1 mechanism slice."""

import hashlib
import json
import math
import random
from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from neural_brain.cognition.adapters import ActiveCognitiveModel, model_manifest_digest
from neural_brain.cognition.models import RecordedObservation
from neural_brain.cognition.workspace import NeuralWorkspace
from neural_brain.memory.models import StrictModel

type ContextLabel = Literal["positive", "negative"]
type DatasetRole = Literal["development", "hidden_test"]
type EvaluationMode = Literal[
    "full",
    "majority_class",
    "seeded_random",
    "stateless_last_observation",
    "uniform_pooling",
    "non_neural_finite_state",
    "parameter_matched_stateless",
    "uniform_feature_gate",
    "zero_recurrent_weight",
    "reset_workspace_state_each_step",
]


class EvaluationSequence(StrictModel):
    """One externally supplied labeled sequence."""

    sequence_id: str
    observations: Annotated[tuple[RecordedObservation, ...], Field(min_length=2, max_length=8)]
    expected_label: ContextLabel


class EvaluationDataset(StrictModel):
    """Immutable development or independently held hidden-test artifact."""

    role: DatasetRole
    artifact_digest: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    sequences: Annotated[tuple[EvaluationSequence, ...], Field(min_length=1, max_length=4096)]

    @model_validator(mode="after")
    def digest_matches_content(self) -> Self:
        """Reject mislabeled or mutated evaluation artifacts."""
        if self.artifact_digest != evaluation_sequence_digest(self.sequences):
            raise ValueError("evaluation dataset digest does not match its sequences")
        return self


class ConfidenceInterval(StrictModel):
    """Closed metric interval at the declared confidence level."""

    lower: Annotated[float, Field(strict=True, ge=-1.0, le=1.0)]
    upper: Annotated[float, Field(strict=True, ge=-1.0, le=1.0)]
    confidence_level: Annotated[float, Field(strict=True, ge=0.95, le=0.95)] = 0.95


class ModeResult(StrictModel):
    """Measured outcome for one full, baseline, or ablation mode."""

    mode: EvaluationMode
    correct: Annotated[int, Field(strict=True, ge=0)]
    total: Annotated[int, Field(strict=True, ge=1)]
    accuracy: Annotated[float, Field(strict=True, ge=0.0, le=1.0)]
    accuracy_interval: ConfidenceInterval
    per_sequence_correct: tuple[bool, ...]


class PairedLift(StrictModel):
    """Full-mechanism accuracy lift over one measured comparator."""

    comparator: EvaluationMode
    absolute_lift: Annotated[float, Field(strict=True, ge=-1.0, le=1.0)]
    bootstrap_interval: ConfidenceInterval
    replicates: Literal[10000] = 10000


class Nb1EvaluationReport(StrictModel):
    """Behavioral report that cannot itself claim a maturity-gate pass."""

    spec_id: Literal["EVAL-01.NB-1.safe-serial-cognition.v2"]
    spec_digest: Literal["0dd87fb28a17534ea08c4f681e8c8fc19d559faf171a23b7c14f396ad05c26d9"]
    dataset_role: DatasetRole
    dataset_digest: str
    independent_evaluator_id: str
    model_manifest_digest: str
    mode_results: tuple[ModeResult, ...]
    paired_lifts: tuple[PairedLift, ...]
    evaluation_gates_passed: tuple[()] = ()
    recognition_gates_passed: tuple[()] = ()
    claim_status: Literal[
        "development_only_hidden_test_required", "independent_hidden_result_requires_gate_review"
    ]


def evaluation_sequence_digest(sequences: tuple[EvaluationSequence, ...]) -> str:
    """Hash canonical sequence content independently of dataset role."""
    payload = json.dumps(
        [sequence.model_dump(mode="json") for sequence in sequences],
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return hashlib.sha256(payload).hexdigest()


def evaluate_dataset(
    *,
    active_model: ActiveCognitiveModel,
    dataset: EvaluationDataset,
    independent_evaluator_id: str,
    majority_label: ContextLabel,
) -> Nb1EvaluationReport:
    """Measure all preregistered modes on one immutable external artifact."""
    if dataset.role == "hidden_test" and not independent_evaluator_id.startswith("independent:"):
        raise ValueError("hidden evaluation requires an independent evaluator identity")
    modes: tuple[EvaluationMode, ...] = (
        "full",
        "majority_class",
        "seeded_random",
        "stateless_last_observation",
        "uniform_pooling",
        "non_neural_finite_state",
        "parameter_matched_stateless",
        "uniform_feature_gate",
        "zero_recurrent_weight",
        "reset_workspace_state_each_step",
    )
    results = tuple(
        _evaluate_mode(
            mode=mode,
            active_model=active_model,
            sequences=dataset.sequences,
            majority_label=majority_label,
            dataset_digest=dataset.artifact_digest,
        )
        for mode in modes
    )
    full = results[0]
    lifts = tuple(
        _paired_lift(full, comparator, dataset.artifact_digest) for comparator in results[1:]
    )
    status: Literal[
        "development_only_hidden_test_required", "independent_hidden_result_requires_gate_review"
    ] = (
        "development_only_hidden_test_required"
        if dataset.role == "development"
        else "independent_hidden_result_requires_gate_review"
    )
    return Nb1EvaluationReport(
        spec_id="EVAL-01.NB-1.safe-serial-cognition.v2",
        spec_digest="0dd87fb28a17534ea08c4f681e8c8fc19d559faf171a23b7c14f396ad05c26d9",
        dataset_role=dataset.role,
        dataset_digest=dataset.artifact_digest,
        independent_evaluator_id=independent_evaluator_id,
        model_manifest_digest=model_manifest_digest(active_model.manifest),
        mode_results=results,
        paired_lifts=lifts,
        claim_status=status,
    )


def _evaluate_mode(
    *,
    mode: EvaluationMode,
    active_model: ActiveCognitiveModel,
    sequences: tuple[EvaluationSequence, ...],
    majority_label: ContextLabel,
    dataset_digest: str,
) -> ModeResult:
    outcomes = tuple(
        _predict(mode, active_model.workspace, sequence, majority_label, dataset_digest)
        == sequence.expected_label
        for sequence in sequences
    )
    correct = sum(outcomes)
    total = len(outcomes)
    accuracy = correct / total
    lower, upper = _wilson_interval(correct, total)
    return ModeResult(
        mode=mode,
        correct=correct,
        total=total,
        accuracy=accuracy,
        accuracy_interval=ConfidenceInterval(lower=lower, upper=upper),
        per_sequence_correct=outcomes,
    )


def _predict(
    mode: EvaluationMode,
    workspace: NeuralWorkspace,
    sequence: EvaluationSequence,
    majority_label: ContextLabel,
    dataset_digest: str,
) -> ContextLabel:
    if mode == "majority_class":
        return majority_label
    if mode == "seeded_random":
        digest = hashlib.sha256(f"{dataset_digest}:{sequence.sequence_id}".encode()).digest()
        return "positive" if digest[0] % 2 == 0 else "negative"
    if mode == "stateless_last_observation":
        return _label(sequence.observations[-1].features[0])
    if mode == "uniform_pooling":
        score = sum(sum(observation.features) for observation in sequence.observations)
        return _label(score)
    if mode == "non_neural_finite_state":
        state = 0.0
        for observation in sequence.observations:
            state = 0.5 * state + (1.0 if observation.features[0] >= 0.0 else -1.0)
        return _label(state)

    attention_mode: Literal["learned", "uniform"] = (
        "uniform" if mode == "uniform_feature_gate" else "learned"
    )
    recurrence_enabled = mode not in {"parameter_matched_stateless", "zero_recurrent_weight"}
    mechanism = NeuralWorkspace(
        workspace.parameters,
        attention_mode=attention_mode,
        recurrence_enabled=recurrence_enabled,
    )
    hidden = 0.0
    for observation in sequence.observations:
        previous = 0.0 if mode == "reset_workspace_state_each_step" else hidden
        _, hidden = mechanism.step(observation=observation, previous_hidden=previous)
    return _label(hidden)


def _label(score: float) -> ContextLabel:
    return "positive" if score >= 0.0 else "negative"


def _wilson_interval(correct: int, total: int) -> tuple[float, float]:
    z = 1.959963984540054
    proportion = correct / total
    denominator = 1.0 + z * z / total
    center = (proportion + z * z / (2.0 * total)) / denominator
    margin = (
        z
        * math.sqrt(proportion * (1.0 - proportion) / total + z * z / (4.0 * total * total))
        / denominator
    )
    return (max(0.0, center - margin), min(1.0, center + margin))


def _paired_lift(full: ModeResult, comparator: ModeResult, seed_material: str) -> PairedLift:
    differences = tuple(
        int(full_value) - int(comparator_value)
        for full_value, comparator_value in zip(
            full.per_sequence_correct, comparator.per_sequence_correct, strict=True
        )
    )
    lift = sum(differences) / len(differences)
    randomizer = random.Random(f"{seed_material}:{comparator.mode}")
    samples = sorted(
        sum(randomizer.choice(differences) for _ in differences) / len(differences)
        for _ in range(10000)
    )
    return PairedLift(
        comparator=comparator.mode,
        absolute_lift=lift,
        bootstrap_interval=ConfidenceInterval(
            lower=samples[249],
            upper=samples[9749],
        ),
    )
