"""Independent hidden-evaluator boundary tests without a repository hidden dataset."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from neural_brain.cognition import (
    ActiveCognitiveModel,
    ActiveCognitiveModelManifest,
    EvaluationDataset,
    EvaluationSequence,
    IndependentEvaluatorIdentity,
    NeuralWorkspace,
    NeuralWorkspaceParameters,
    RecordedObservation,
    evaluate_hidden_dataset,
    evaluation_sequence_digest,
    workspace_parameter_digest,
)


def _model() -> ActiveCognitiveModel:
    workspace = NeuralWorkspace(
        NeuralWorkspaceParameters(
            model_version="interface-test-only",
            training_provenance_ref="interface-test-provenance",
            attention_logits=(4.0, -4.0),
            input_weights=(1.0, 1.0),
            recurrent_weight=1.5,
        )
    )
    digest = "a" * 64
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


def _external_contract_fixture() -> EvaluationDataset:
    """Build interface-only data that is never stored or represented as hidden evidence."""
    occurred_at = datetime(2026, 7, 16, 20, 0, tzinfo=UTC)
    sequences = tuple(
        EvaluationSequence(
            sequence_id=f"external-contract-fixture-{index:04d}",
            observations=(
                RecordedObservation(
                    observation_id=f"external-contract-fixture-{index:04d}:0",
                    source_kind="synthetic",
                    provenance_ref="external-interface-contract-fixture",
                    features=(1.0 if index % 2 == 0 else -1.0, 0.0),
                    occurred_at=occurred_at,
                ),
                RecordedObservation(
                    observation_id=f"external-contract-fixture-{index:04d}:1",
                    source_kind="synthetic",
                    provenance_ref="external-interface-contract-fixture",
                    features=(1.0 if index % 2 == 0 else -1.0, 0.0),
                    occurred_at=occurred_at,
                ),
            ),
            expected_label="positive" if index % 2 == 0 else "negative",
        )
        for index in range(512)
    )
    return EvaluationDataset(
        role="hidden_test",
        artifact_digest=evaluation_sequence_digest(sequences),
        sequences=sequences,
    )


def test_hidden_evaluator_identity_is_explicit_and_independent() -> None:
    with pytest.raises(ValidationError):
        IndependentEvaluatorIdentity(
            evaluator_id="implementer:self",
            artifact_provider_id="external-provider",
            evaluation_protocol_digest="b" * 64,
        )


def test_external_hidden_interface_returns_measurement_not_gate_claim() -> None:
    evaluator = IndependentEvaluatorIdentity(
        evaluator_id="independent:contract-test",
        artifact_provider_id="external-provider",
        evaluation_protocol_digest="b" * 64,
    )
    report = evaluate_hidden_dataset(
        active_model=_model(),
        dataset=_external_contract_fixture(),
        evaluator=evaluator,
        majority_label="positive",
    )

    assert report.independent_evaluator_id == "independent:contract-test"
    assert report.claim_status == "independent_hidden_result_requires_gate_review"
    assert report.evaluation_gates_passed == ()
    assert report.recognition_gates_passed == ()
