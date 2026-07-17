"""Offline training and immutable provenance tests for EVAL-01 NB-1 v3."""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

import neural_brain.cognition as cognition
from neural_brain.cognition.training import (
    OfflineTrainingBundle,
    TrainingDataset,
    generate_training_dataset,
    train_offline,
)
from tools.train_nb1_workspace import (
    HISTORICAL_ARTIFACT_SHA256,
    _sha256_text_file,
)

ROOT = Path(__file__).resolve().parents[2]
DIGEST_A = "a" * 64
DIGEST_B = "b" * 64
DIGEST_C = "c" * 64


def trained_bundle() -> OfflineTrainingBundle:
    """Create one deterministic train-only development candidate."""
    return train_offline(
        dataset=generate_training_dataset(),
        training_code_digest=DIGEST_A,
        contract_digest=DIGEST_B,
        environment_digest=DIGEST_C,
    )


def test_offline_grid_search_is_deterministic_and_discloses_every_attempt() -> None:
    first = trained_bundle()
    second = trained_bundle()

    assert first == second
    provenance = first.training_provenance
    assert len(provenance.attempted_candidates) == 27
    assert provenance.selected_candidate_index == 0
    assert provenance.attempted_candidates[0].accuracy == 1.0
    assert provenance.dataset_role == "train"
    assert provenance.runtime_training_surface is False
    assert first.active_model_promoted is False


def test_training_dataset_is_train_only_and_carries_public_split_provenance() -> None:
    dataset = generate_training_dataset()
    payload = dataset.model_dump(mode="json")

    assert payload["role"] == "train"
    assert payload["seed"] == 1931
    assert payload["generator_contract"] == "nb1-serial-context-generator-v2"
    payload["role"] = "development"
    with pytest.raises(ValidationError):
        TrainingDataset.model_validate(payload)


def test_productive_cognition_package_exposes_no_runtime_training_surface() -> None:
    assert not hasattr(cognition, "train_offline")
    assert not hasattr(cognition, "generate_training_dataset")


def test_parameter_training_and_manifest_tampering_is_rejected() -> None:
    bundle = trained_bundle()
    payload = bundle.model_dump(mode="json")
    payload["parameter_artifact"]["parameters"]["bias"] = 0.5
    with pytest.raises(ValidationError, match="parameter artifact digest"):
        OfflineTrainingBundle.model_validate_json(json.dumps(payload))

    payload = bundle.model_dump(mode="json")
    payload["training_provenance"]["dataset_digest"] = "d" * 64
    with pytest.raises(ValidationError, match="training provenance digest"):
        OfflineTrainingBundle.model_validate_json(json.dumps(payload))

    payload = bundle.model_dump(mode="json")
    payload["model_manifest"]["code_digest"] = "e" * 64
    with pytest.raises(ValidationError, match="manifest code digest"):
        OfflineTrainingBundle.model_validate_json(json.dumps(payload))


def test_checked_in_artifact_is_non_hidden_non_promoted_and_self_verifying() -> None:
    path = (
        ROOT
        / "docs"
        / "architecture"
        / "evaluations"
        / "artifacts"
        / "nb1-v1-offline-training-bundle.json"
    )
    document = json.loads(path.read_text(encoding="utf-8"))
    bundle = OfflineTrainingBundle.model_validate_json(json.dumps(document["bundle"]))

    assert document["dataset_manifest"]["role"] == "train"
    assert document["claim_boundary"] == {
        "active_model_promoted": False,
        "evaluation_gates_passed": [],
        "hidden_data_included": False,
        "recognition_gates_passed": [],
        "stage_release_authorized": False,
    }
    assert bundle.evaluation_gates_passed == ()
    assert bundle.recognition_gates_passed == ()
    assert bundle.stage_release_authorized is False


def test_checked_in_historical_artifact_matches_its_frozen_digest() -> None:
    path = (
        ROOT
        / "docs"
        / "architecture"
        / "evaluations"
        / "artifacts"
        / "nb1-v1-offline-training-bundle.json"
    )

    assert _sha256_text_file(path) == HISTORICAL_ARTIFACT_SHA256


def test_repository_text_digests_ignore_checkout_line_endings(tmp_path: Path) -> None:
    lf_path = tmp_path / "lf.txt"
    crlf_path = tmp_path / "crlf.txt"
    lf_path.write_bytes(b"first\nsecond\n")
    crlf_path.write_bytes(b"first\r\nsecond\r\n")

    assert _sha256_text_file(lf_path) == _sha256_text_file(crlf_path)
