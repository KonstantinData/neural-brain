"""Development-only mechanism evidence for EVAL-01 v2."""

from datetime import UTC, datetime
from typing import Literal

import pytest
from pydantic import ValidationError

from neural_brain.cognition import (
    ActiveCognitiveModel,
    ActiveCognitiveModelManifest,
    EvaluationDataset,
    EvaluationSequence,
    NeuralWorkspace,
    NeuralWorkspaceParameters,
    RecordedObservation,
    evaluate_dataset,
    evaluation_sequence_digest,
    workspace_parameter_digest,
)


def active_model() -> ActiveCognitiveModel:
    workspace = NeuralWorkspace(
        NeuralWorkspaceParameters(
            model_version="nb1-development-model-v2",
            training_provenance_ref="offline-development-fit-v2",
            attention_logits=(4.0, -4.0),
            input_weights=(1.0, 1.0),
            recurrent_weight=1.5,
            bias=0.0,
        )
    )
    digest = "b" * 64
    return ActiveCognitiveModel(
        workspace=workspace,
        manifest=ActiveCognitiveModelManifest(
            model_version=workspace.parameters.model_version,
            parameter_digest=workspace_parameter_digest(workspace),
            training_artifact_digest=digest,
            code_digest=digest,
            contract_digest=digest,
            evaluation_spec_digest=(
                "3ac6d895d3f33b5d63c462471ca335d6d538cc379ae8eb3ad0611c81271b3fc8"
            ),
        ),
    )


def development_sequences(size: int = 64) -> tuple[EvaluationSequence, ...]:
    timestamp = datetime(2026, 7, 16, 20, 0, tzinfo=UTC)
    sequences: list[EvaluationSequence] = []
    for sequence_index in range(size):
        positive = sequence_index % 2 == 0
        sign = 1.0 if positive else -1.0
        features = (
            (sign, -2.0 * sign),
            (sign, -2.0 * sign),
            (sign, -2.0 * sign),
            (-0.5 * sign, 0.2 * sign),
        )
        sequence_id = f"development-{sequence_index:04d}"
        observations = tuple(
            RecordedObservation(
                observation_id=f"{sequence_id}:{position}",
                source_kind="synthetic",
                provenance_ref="development-generator-v2",
                features=feature_pair,
                occurred_at=timestamp,
            )
            for position, feature_pair in enumerate(features)
        )
        sequences.append(
            EvaluationSequence(
                sequence_id=sequence_id,
                observations=observations,
                expected_label="positive" if positive else "negative",
            )
        )
    return tuple(sequences)


def dataset(
    role: Literal["development", "hidden_test"] = "development",
) -> EvaluationDataset:
    sequences = development_sequences()
    return EvaluationDataset(
        role=role,
        artifact_digest=evaluation_sequence_digest(sequences),
        sequences=sequences,
    )


def test_development_run_measures_baselines_ablations_and_confidence() -> None:
    report = evaluate_dataset(
        active_model=active_model(),
        dataset=dataset(),
        independent_evaluator_id="implementer:development-only",
        majority_label="positive",
    )
    by_mode = {result.mode: result for result in report.mode_results}
    lifts = {lift.comparator: lift for lift in report.paired_lifts}

    assert by_mode["full"].accuracy == 1.0
    assert by_mode["parameter_matched_stateless"].accuracy == 0.0
    assert by_mode["uniform_feature_gate"].accuracy == 0.0
    assert by_mode["zero_recurrent_weight"].accuracy == 0.0
    assert by_mode["reset_workspace_state_each_step"].accuracy == 0.0
    assert lifts["non_neural_finite_state"].bootstrap_interval.lower > 0.05
    assert report.claim_status == "development_only_hidden_test_required"
    assert report.evaluation_gates_passed == ()
    assert report.recognition_gates_passed == ()


def test_dataset_digest_is_verified_and_hidden_run_requires_independence() -> None:
    payload = dataset().model_dump(mode="json")
    payload["artifact_digest"] = "0" * 64
    with pytest.raises(ValidationError):
        EvaluationDataset.model_validate(payload)

    hidden = dataset("hidden_test")
    with pytest.raises(ValueError, match="independent evaluator"):
        evaluate_dataset(
            active_model=active_model(),
            dataset=hidden,
            independent_evaluator_id="implementer:not-independent",
            majority_label="positive",
        )


def test_development_evaluation_is_deterministic() -> None:
    model = active_model()
    development = dataset()
    first = evaluate_dataset(
        active_model=model,
        dataset=development,
        independent_evaluator_id="implementer:development-only",
        majority_label="positive",
    )
    second = evaluate_dataset(
        active_model=model,
        dataset=development,
        independent_evaluator_id="implementer:development-only",
        majority_label="positive",
    )
    assert first == second
