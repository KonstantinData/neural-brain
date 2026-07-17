"""Unit evidence for the label-free NB-1 hidden-evaluation candidate boundary."""

from datetime import UTC, datetime
from typing import Any

import pytest
from pydantic import ValidationError

from neural_brain.cognition.adapters import (
    ActiveCognitiveModel,
    model_manifest_digest,
    workspace_parameter_digest,
)
from neural_brain.cognition.hidden_contract import (
    CandidateEvaluationBundle,
    PredictionBatch,
    PredictionRecord,
    UnlabeledEvaluationBatch,
    UnlabeledEvaluationObservation,
    UnlabeledEvaluationSequence,
    candidate_evaluation_bundle_digest,
    predict_full_mechanism,
    prediction_batch_digest,
    unlabeled_evaluation_batch_digest,
)
from neural_brain.cognition.models import ActiveCognitiveModelManifest, NeuralWorkspaceParameters
from neural_brain.cognition.workspace import NeuralWorkspace


def _active_model() -> ActiveCognitiveModel:
    parameters = NeuralWorkspaceParameters(
        model_version="hidden-contract-model-v1",
        training_provenance_ref="a" * 64,
        attention_logits=(4.0, -4.0),
        input_weights=(1.0, 1.0),
        recurrent_weight=1.5,
    )
    workspace = NeuralWorkspace(parameters)
    manifest = ActiveCognitiveModelManifest(
        model_version=parameters.model_version,
        parameter_digest=workspace_parameter_digest(workspace),
        training_artifact_digest=parameters.training_provenance_ref,
        code_digest="b" * 64,
        contract_digest="c" * 64,
        evaluation_spec_digest="d" * 64,
    )
    return ActiveCognitiveModel(workspace=workspace, manifest=manifest)


def _candidate(active_model: ActiveCognitiveModel) -> CandidateEvaluationBundle:
    manifest_digest = model_manifest_digest(active_model.manifest)
    frozen_at = datetime(2026, 7, 17, 9, 0, tzinfo=UTC)
    digest = candidate_evaluation_bundle_digest(
        model_manifest=active_model.manifest,
        model_manifest_digest_value=manifest_digest,
        parameters=active_model.workspace.parameters,
        source_commit="1" * 40,
        source_tree_digest="2" * 64,
        training_code_digest=active_model.manifest.code_digest,
        candidate_code_digest="5" * 64,
        evaluation_contract_digest="3" * 64,
        dependency_lock_digest="4" * 64,
        fixed_train_majority_label="positive",
        frozen_at=frozen_at,
    )
    return CandidateEvaluationBundle(
        artifact_digest=digest,
        model_manifest=active_model.manifest,
        model_manifest_digest=manifest_digest,
        parameters=active_model.workspace.parameters,
        source_commit="1" * 40,
        source_tree_digest="2" * 64,
        training_code_digest=active_model.manifest.code_digest,
        candidate_code_digest="5" * 64,
        evaluation_contract_digest="3" * 64,
        dependency_lock_digest="4" * 64,
        fixed_train_majority_label="positive",
        frozen_at=frozen_at,
    )


def _sequences() -> tuple[UnlabeledEvaluationSequence, ...]:
    return (
        UnlabeledEvaluationSequence(
            sequence_id="opaque-sequence-2",
            observations=(
                UnlabeledEvaluationObservation(
                    observation_id="opaque-observation-2-a", features=(1.0, -2.0)
                ),
                UnlabeledEvaluationObservation(
                    observation_id="opaque-observation-2-b", features=(-0.5, 0.2)
                ),
            ),
        ),
        UnlabeledEvaluationSequence(
            sequence_id="opaque-sequence-1",
            observations=(
                UnlabeledEvaluationObservation(
                    observation_id="opaque-observation-1-a", features=(-1.0, 2.0)
                ),
                UnlabeledEvaluationObservation(
                    observation_id="opaque-observation-1-b", features=(0.5, -0.2)
                ),
            ),
        ),
    )


def _batch() -> UnlabeledEvaluationBatch:
    sequences = _sequences()
    return UnlabeledEvaluationBatch(
        artifact_digest=unlabeled_evaluation_batch_digest(
            run_id="opaque-run-1", sequences=sequences
        ),
        run_id="opaque-run-1",
        sequences=sequences,
    )


@pytest.mark.parametrize("forbidden", ["expected_label", "seed", "provider", "role"])
def test_unlabeled_boundary_rejects_hidden_metadata(forbidden: str) -> None:
    payload: dict[str, Any] = {
        "observation_id": "observation-1",
        "features": (1.0, 0.0),
        forbidden: "must-not-cross",
    }
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        UnlabeledEvaluationObservation.model_validate(payload)


def test_full_mechanism_prediction_preserves_exact_input_order_without_correctness() -> None:
    active_model = _active_model()
    candidate = _candidate(active_model)
    batch = _batch()

    result = predict_full_mechanism(
        active_model=active_model,
        candidate=candidate,
        batch=batch,
    )

    assert tuple(prediction.sequence_id for prediction in result.predictions) == (
        "opaque-sequence-2",
        "opaque-sequence-1",
    )
    assert result.candidate_digest == candidate.artifact_digest
    assert result.input_digest == batch.artifact_digest
    assert result.run_id == batch.run_id
    assert result.network_calls == 0
    assert result.external_effects == 0
    assert result.active_model_mutated is False
    assert "correct" not in result.model_dump(mode="json")
    assert "expected_label" not in result.model_dump_json()


def test_batch_rejects_digest_tamper_duplicate_ids_and_extra_fields() -> None:
    sequences = _sequences()
    with pytest.raises(ValidationError, match="batch digest"):
        UnlabeledEvaluationBatch(
            artifact_digest="0" * 64, run_id="opaque-run-1", sequences=sequences
        )
    with pytest.raises(ValidationError, match="sequence IDs must be unique"):
        UnlabeledEvaluationBatch(
            artifact_digest=unlabeled_evaluation_batch_digest(
                run_id="opaque-run-1", sequences=(sequences[0], sequences[0])
            ),
            run_id="opaque-run-1",
            sequences=(sequences[0], sequences[0]),
        )
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        UnlabeledEvaluationBatch.model_validate(
            {
                "artifact_digest": unlabeled_evaluation_batch_digest(
                    run_id="opaque-run-1", sequences=sequences
                ),
                "run_id": "opaque-run-1",
                "sequences": sequences,
                "expected_label": "positive",
            }
        )


def test_observation_ids_must_be_unique_within_and_across_sequences() -> None:
    duplicate_within = UnlabeledEvaluationObservation(
        observation_id="duplicate", features=(1.0, 0.0)
    )
    with pytest.raises(ValidationError, match="observation IDs must be unique"):
        UnlabeledEvaluationSequence(
            sequence_id="sequence",
            observations=(duplicate_within, duplicate_within),
        )

    sequences = _sequences()
    reused = UnlabeledEvaluationSequence(
        sequence_id="third-sequence",
        observations=(
            sequences[0].observations[0],
            UnlabeledEvaluationObservation(observation_id="new-observation", features=(0.0, 0.0)),
        ),
    )
    combined = (*sequences, reused)
    with pytest.raises(ValidationError, match="globally unique"):
        UnlabeledEvaluationBatch(
            artifact_digest=unlabeled_evaluation_batch_digest(
                run_id="opaque-run-1", sequences=combined
            ),
            run_id="opaque-run-1",
            sequences=combined,
        )


def test_prediction_batch_rejects_tamper_reordering_and_extra_fields() -> None:
    predictions = (
        PredictionRecord(sequence_id="first", predicted_label="positive"),
        PredictionRecord(sequence_id="second", predicted_label="negative"),
    )
    digest = prediction_batch_digest(
        candidate_digest="a" * 64,
        input_digest="b" * 64,
        run_id="opaque-run-1",
        predictions=predictions,
    )
    PredictionBatch(
        artifact_digest=digest,
        run_id="opaque-run-1",
        candidate_digest="a" * 64,
        input_digest="b" * 64,
        predictions=predictions,
    )
    with pytest.raises(ValidationError, match="prediction batch digest"):
        PredictionBatch(
            artifact_digest=digest,
            run_id="opaque-run-1",
            candidate_digest="a" * 64,
            input_digest="b" * 64,
            predictions=tuple(reversed(predictions)),
        )
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        PredictionRecord.model_validate(
            {"sequence_id": "first", "predicted_label": "positive", "correct": True}
        )


def test_candidate_tamper_or_active_model_mismatch_fails_closed() -> None:
    active_model = _active_model()
    candidate = _candidate(active_model)
    tampered = candidate.model_dump(mode="python")
    tampered["artifact_digest"] = "f" * 64
    with pytest.raises(ValidationError, match="candidate bundle digest"):
        CandidateEvaluationBundle.model_validate(tampered)

    other_model = _active_model()
    other_model.workspace._recurrence_enabled = False
    with pytest.raises(ValueError, match="recurrent full mechanism"):
        predict_full_mechanism(
            active_model=other_model,
            candidate=candidate,
            batch=_batch(),
        )


@pytest.mark.parametrize(
    ("field", "replacement", "message"),
    [
        ("source_commit", "not-a-commit", "string_pattern_mismatch"),
        ("source_tree_digest", "5" * 64, "candidate bundle digest"),
        ("dependency_lock_digest", "6" * 64, "candidate bundle digest"),
        ("evaluation_contract_digest", "7" * 64, "candidate bundle digest"),
        ("fixed_train_majority_label", "negative", "candidate bundle digest"),
        ("frozen_at", datetime(2026, 7, 17, 9, 0), "timezone offset"),
    ],
)
def test_candidate_freeze_receipt_rejects_tampered_fields(
    field: str, replacement: object, message: str
) -> None:
    payload = _candidate(_active_model()).model_dump(mode="python")
    payload[field] = replacement
    with pytest.raises(ValidationError, match=message):
        CandidateEvaluationBundle.model_validate(payload)


def test_run_id_is_bound_across_input_and_prediction() -> None:
    input_payload = _batch().model_dump(mode="python")
    input_payload["run_id"] = "different-run"
    with pytest.raises(ValidationError, match="batch digest"):
        UnlabeledEvaluationBatch.model_validate(input_payload)

    result = predict_full_mechanism(
        active_model=_active_model(),
        candidate=_candidate(_active_model()),
        batch=_batch(),
    )
    output_payload = result.model_dump(mode="python")
    output_payload["run_id"] = "different-run"
    with pytest.raises(ValidationError, match="prediction batch digest"):
        PredictionBatch.model_validate(output_payload)
