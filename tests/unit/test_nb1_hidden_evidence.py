"""Signed external evidence intake tests for EVAL-01 NB-1 v3."""

import base64
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from pydantic import ValidationError

from neural_brain.cognition.adapters import model_manifest_digest, workspace_parameter_digest
from neural_brain.cognition.hidden_contract import (
    CandidateEvaluationBundle,
    candidate_evaluation_bundle_digest,
)
from neural_brain.cognition.hidden_evidence import (
    ConfidenceInterval,
    Ed25519SignedEvidenceEnvelope,
    HiddenEvaluationEvidencePayload,
    canonical_evidence_payload_bytes,
    evidence_payload_digest,
    hidden_artifact_commitment_digest,
    verify_signed_hidden_evidence,
)
from neural_brain.cognition.models import ActiveCognitiveModelManifest, NeuralWorkspaceParameters
from neural_brain.cognition.workspace import NeuralWorkspace

DIGEST_A = "a" * 64
DIGEST_B = "b" * 64
DIGEST_C = "c" * 64
DIGEST_D = "d" * 64
DIGEST_E = "e" * 64
DIGEST_F = "f" * 64
DIGEST_1 = "1" * 64
DIGEST_2 = "2" * 64
DIGEST_3 = "3" * 64
DIGEST_4 = "4" * 64
DIGEST_5 = "5" * 64
DIGEST_6 = "6" * 64
TEST_SPEC_ID = "EVAL-01.NB-1.contract-test.vNEXT"
TEST_SPEC_DIGEST = "a1" * 32
HISTORICAL_V3_ID = "EVAL-01.NB-1.safe-serial-cognition.v3"
HISTORICAL_V3_DIGEST = "3ac6d895d3f33b5d63c462471ca335d6d538cc379ae8eb3ad0611c81271b3fc8"
ACCEPTED_SPECS = {TEST_SPEC_ID: TEST_SPEC_DIGEST}
NOW = datetime(2026, 7, 17, 8, 0, tzinfo=UTC)
INPUT_BATCH_DIGEST = "bc" * 32
PREDICTION_BATCH_DIGEST = "cd" * 32
TRUSTED_ATTESTATIONS = {
    "independent:evaluator-one": DIGEST_A,
    "provider:hidden-lab": DIGEST_B,
}


def _candidate_bundle() -> CandidateEvaluationBundle:
    parameters = NeuralWorkspaceParameters(
        model_version="hidden-evidence-contract-test",
        training_provenance_ref=DIGEST_1,
        attention_logits=(4.0, -4.0),
        input_weights=(1.0, 1.0),
        recurrent_weight=1.5,
    )
    manifest = ActiveCognitiveModelManifest(
        model_version=parameters.model_version,
        parameter_digest=workspace_parameter_digest(NeuralWorkspace(parameters)),
        training_artifact_digest=DIGEST_1,
        code_digest=DIGEST_2,
        contract_digest=DIGEST_4,
        evaluation_spec_digest=TEST_SPEC_DIGEST,
    )
    manifest_digest = model_manifest_digest(manifest)
    frozen_at = NOW - timedelta(hours=1)
    artifact_digest = candidate_evaluation_bundle_digest(
        model_manifest=manifest,
        model_manifest_digest_value=manifest_digest,
        parameters=parameters,
        source_commit="1" * 40,
        source_tree_digest="7" * 64,
        training_code_digest=DIGEST_2,
        candidate_code_digest=DIGEST_3,
        evaluation_contract_digest=DIGEST_4,
        dependency_lock_digest=DIGEST_6,
        fixed_train_majority_label="positive",
        frozen_at=frozen_at,
    )
    return CandidateEvaluationBundle(
        artifact_digest=artifact_digest,
        source_commit="1" * 40,
        source_tree_digest="7" * 64,
        training_code_digest=DIGEST_2,
        candidate_code_digest=DIGEST_3,
        evaluation_contract_digest=DIGEST_4,
        dependency_lock_digest=DIGEST_6,
        fixed_train_majority_label="positive",
        frozen_at=frozen_at,
        model_manifest=manifest,
        model_manifest_digest=manifest_digest,
        parameters=parameters,
    )


def _accepted_candidate_bundles() -> dict[str, CandidateEvaluationBundle]:
    candidate = _candidate_bundle()
    return {candidate.artifact_digest: candidate}


def _interval(lower: float, upper: float) -> ConfidenceInterval:
    return ConfidenceInterval(lower=lower, upper=upper)


def _comparator(mode: str, *, correct: int = 384) -> dict[str, Any]:
    accuracy = correct / 512
    lift = 0.875 - accuracy
    return {
        "mode": mode,
        "correct": correct,
        "total": 512,
        "accuracy": accuracy,
        "accuracy_interval": {"lower": max(0.0, accuracy - 0.04), "upper": 0.80},
        "full_minus_comparator_lift": lift,
        "paired_lift_interval": {"lower": lift - 0.04, "upper": lift + 0.04},
        "bootstrap_replicates": 10000,
    }


def _payload_dict() -> dict[str, Any]:
    candidate = _candidate_bundle()
    return {
        "document_type": "nb1_independent_hidden_evaluation_evidence",
        "format_version": 1,
        "spec_id": TEST_SPEC_ID,
        "spec_digest": TEST_SPEC_DIGEST,
        "evaluator": {
            "evaluator_id": "independent:evaluator-one",
            "organization_id": "evaluation-lab",
            "implementation_owner_id": "neural-brain-team",
            "independent_from_implementation": True,
            "attestation_digest": DIGEST_A,
        },
        "provider": {
            "provider_id": "provider:hidden-lab",
            "organization_id": "artifact-lab",
            "implementation_owner_id": "neural-brain-team",
            "independent_from_implementation": True,
            "attestation_digest": DIGEST_B,
        },
        "hidden_artifact": {
            "commitment_id": "hidden-commitment-001",
            "provider_id": "provider:hidden-lab",
            "dataset_role": "hidden_test",
            "generator_contract": "nb1-serial-context-generator-contract-test-vnext",
            "split_id": "hidden-split-001",
            "artifact_digest": DIGEST_C,
            "sequence_count": 512,
            "committed_at": NOW,
            "seed_disclosed_to_implementer": False,
            "hidden_content_included": False,
        },
        "candidate_bundle_digest": candidate.artifact_digest,
        "candidate_frozen_at": candidate.frozen_at,
        "source_commit": candidate.source_commit,
        "source_tree_digest": candidate.source_tree_digest,
        "dependency_lock_digest": candidate.dependency_lock_digest,
        "candidate_code_digest": candidate.candidate_code_digest,
        "evaluation_contract_digest": candidate.evaluation_contract_digest,
        "fixed_train_majority_label": candidate.fixed_train_majority_label,
        "evaluation_protocol_digest": DIGEST_D,
        "model_manifest_digest": candidate.model_manifest_digest,
        "parameter_digest": candidate.model_manifest.parameter_digest,
        "training_artifact_digest": candidate.model_manifest.training_artifact_digest,
        "training_code_digest": candidate.training_code_digest,
        "runtime_code_digest": candidate.candidate_code_digest,
        "contract_digest": candidate.evaluation_contract_digest,
        "reported_run_id": "hidden-run-001",
        "input_batch_digest": INPUT_BATCH_DIGEST,
        "prediction_batch_digest": PREDICTION_BATCH_DIGEST,
        "evaluation_executable_digest": candidate.candidate_code_digest,
        "evaluation_mode": "full",
        "environment": {
            "environment_digest": DIGEST_5,
            "dependency_lock_digest": DIGEST_6,
            "source_tree_digest": "7" * 64,
            "evaluator_code_digest": "8" * 64,
            "python_version": "3.14.0",
            "runtime_id": "external-runtime-001",
        },
        "declared_attempt_count": 1,
        "run_attempts": (
            {
                "attempt_index": 0,
                "run_id": "hidden-run-001",
                "status": "completed",
                "selected_for_report": True,
                "started_at": NOW + timedelta(minutes=1),
                "completed_at": NOW + timedelta(minutes=2),
                "hidden_artifact_digest": DIGEST_C,
                "candidate_bundle_digest": candidate.artifact_digest,
                "input_batch_digest": INPUT_BATCH_DIGEST,
                "prediction_batch_digest": PREDICTION_BATCH_DIGEST,
                "executable_digest": candidate.candidate_code_digest,
                "evaluation_mode": "full",
                "fresh_process": True,
                "model_manifest_digest": candidate.model_manifest_digest,
                "evaluation_protocol_digest": DIGEST_D,
                "environment_digest": DIGEST_5,
                "all_inputs_verified": True,
                "hidden_data_exposed_to_implementer": False,
                "post_attachment_change_detected": False,
                "failure_summary_digest": None,
            },
        ),
        "contamination": {
            "report_digest": "9" * 64,
            "train_dataset_digest": DIGEST_A,
            "development_dataset_digest": DIGEST_B,
            "hidden_dataset_digest": DIGEST_C,
            "exact_duplicate_count": 0,
            "identifier_overlap_count": 0,
            "provenance_overlap_count": 0,
            "hidden_seed_leakage_detected": False,
            "hidden_access_by_implementer_detected": False,
            "post_attachment_change_detected": False,
            "all_attempts_disclosed": True,
            "checks_complete": True,
        },
        "resources": {
            "maximum_input_features": 2,
            "maximum_workspace_units": 1,
            "maximum_sequence_length": 8,
            "training_sequences": 512,
            "hidden_test_sequences": 512,
            "network_calls": 0,
            "external_effects": 0,
            "runtime_parameter_mutations": 0,
            "measurements_complete": True,
        },
        "failures": {
            "hard_safety_test_failures": 0,
            "external_effect_surface_failures": 0,
            "unknown_required_results": 0,
            "undisclosed_failures": 0,
            "disclosure_complete": True,
            "report_digest": "0" * 64,
        },
        "full_result": {
            "mode": "full",
            "correct": 448,
            "total": 512,
            "accuracy": 0.875,
            "accuracy_interval": {"lower": 0.84, "upper": 0.91},
        },
        "baseline_results": (
            _comparator("majority_class"),
            _comparator("seeded_random", correct=256),
            _comparator("stateless_last_observation"),
            _comparator("uniform_pooling"),
            _comparator("non_neural_finite_state"),
            _comparator("parameter_matched_stateless"),
        ),
        "ablation_results": (
            _comparator("uniform_feature_gate"),
            _comparator("zero_recurrent_weight"),
            _comparator("reset_workspace_state_each_step"),
        ),
        "evaluation_gates_passed": (),
        "recognition_gates_passed": (),
        "stage_release_authorized": False,
        "neural_brain_candidate_claimed": False,
        "claim_status": "independent_hidden_result_requires_gate_review",
    }


def _payload() -> HiddenEvaluationEvidencePayload:
    return HiddenEvaluationEvidencePayload.model_validate(_payload_dict())


def _accepted_hidden_commitments() -> dict[str, str]:
    commitment = _payload().hidden_artifact
    return {
        commitment.commitment_id: hidden_artifact_commitment_digest(commitment),
    }


def _signed_envelope(
    private_key: Ed25519PrivateKey, payload: HiddenEvaluationEvidencePayload | None = None
) -> Ed25519SignedEvidenceEnvelope:
    signed_payload = payload or _payload()
    signature = private_key.sign(canonical_evidence_payload_bytes(signed_payload))
    return Ed25519SignedEvidenceEnvelope(
        payload=signed_payload,
        payload_digest=evidence_payload_digest(signed_payload),
        signer_id=signed_payload.evaluator.evaluator_id,
        signature_base64=base64.b64encode(signature).decode(),
    )


def test_trusted_signature_accepts_evidence_but_never_passes_a_gate() -> None:
    private_key = Ed25519PrivateKey.generate()
    envelope = _signed_envelope(private_key)

    outcome = verify_signed_hidden_evidence(
        envelope=envelope,
        trusted_public_keys={envelope.signer_id: private_key.public_key()},
        accepted_spec_digests=ACCEPTED_SPECS,
        accepted_candidate_bundles=_accepted_candidate_bundles(),
        trusted_attestation_digests=TRUSTED_ATTESTATIONS,
        accepted_hidden_commitments=_accepted_hidden_commitments(),
    )

    assert outcome.evidence_accepted is True
    assert outcome.signature_valid is True
    assert outcome.evaluation_gates_passed == ()
    assert outcome.recognition_gates_passed == ()
    assert outcome.stage_release_authorized is False
    assert outcome.neural_brain_candidate_recognized is False
    assert outcome.claim_status == "verified_external_evidence_requires_independent_gate_review"


def test_historical_v3_is_rejected_even_with_a_valid_trusted_signature() -> None:
    document = _payload_dict()
    document["spec_id"] = HISTORICAL_V3_ID
    document["spec_digest"] = HISTORICAL_V3_DIGEST
    historical_payload = HiddenEvaluationEvidencePayload.model_validate(document)
    private_key = Ed25519PrivateKey.generate()
    envelope = _signed_envelope(private_key, historical_payload)

    outcome = verify_signed_hidden_evidence(
        envelope=envelope,
        trusted_public_keys={envelope.signer_id: private_key.public_key()},
        accepted_spec_digests=ACCEPTED_SPECS,
        accepted_candidate_bundles=_accepted_candidate_bundles(),
        trusted_attestation_digests=TRUSTED_ATTESTATIONS,
        accepted_hidden_commitments=_accepted_hidden_commitments(),
    )

    assert outcome.evidence_accepted is False
    assert outcome.signature_valid is True
    assert outcome.payload_digest_valid is True
    assert "unaccepted_spec_id" in outcome.reasons


def test_registered_spec_id_rejects_a_mismatched_digest() -> None:
    document = _payload_dict()
    document["spec_digest"] = DIGEST_F
    mismatched_payload = HiddenEvaluationEvidencePayload.model_validate(document)
    private_key = Ed25519PrivateKey.generate()
    envelope = _signed_envelope(private_key, mismatched_payload)

    outcome = verify_signed_hidden_evidence(
        envelope=envelope,
        trusted_public_keys={envelope.signer_id: private_key.public_key()},
        accepted_spec_digests=ACCEPTED_SPECS,
        accepted_candidate_bundles=_accepted_candidate_bundles(),
        trusted_attestation_digests=TRUSTED_ATTESTATIONS,
        accepted_hidden_commitments=_accepted_hidden_commitments(),
    )

    assert outcome.evidence_accepted is False
    assert outcome.signature_valid is True
    assert "accepted_spec_digest_mismatch" in outcome.reasons


def test_unknown_candidate_is_rejected_even_with_a_valid_trusted_signature() -> None:
    document = _payload_dict()
    unknown_candidate = "cd" * 32
    document["candidate_bundle_digest"] = unknown_candidate
    document["run_attempts"][0]["candidate_bundle_digest"] = unknown_candidate
    payload = HiddenEvaluationEvidencePayload.model_validate(document)
    private_key = Ed25519PrivateKey.generate()
    envelope = _signed_envelope(private_key, payload)

    outcome = verify_signed_hidden_evidence(
        envelope=envelope,
        trusted_public_keys={envelope.signer_id: private_key.public_key()},
        accepted_spec_digests=ACCEPTED_SPECS,
        accepted_candidate_bundles=_accepted_candidate_bundles(),
        trusted_attestation_digests=TRUSTED_ATTESTATIONS,
        accepted_hidden_commitments=_accepted_hidden_commitments(),
    )

    assert outcome.evidence_accepted is False
    assert outcome.signature_valid is True
    assert "unknown_candidate_bundle" in outcome.reasons


def test_candidate_registered_for_another_spec_is_rejected() -> None:
    document = _payload_dict()
    document["spec_digest"] = DIGEST_F
    payload = HiddenEvaluationEvidencePayload.model_validate(document)
    private_key = Ed25519PrivateKey.generate()
    envelope = _signed_envelope(private_key, payload)

    outcome = verify_signed_hidden_evidence(
        envelope=envelope,
        trusted_public_keys={envelope.signer_id: private_key.public_key()},
        accepted_spec_digests={TEST_SPEC_ID: DIGEST_F},
        accepted_candidate_bundles=_accepted_candidate_bundles(),
        trusted_attestation_digests=TRUSTED_ATTESTATIONS,
        accepted_hidden_commitments=_accepted_hidden_commitments(),
    )

    assert outcome.evidence_accepted is False
    assert outcome.signature_valid is True
    assert "candidate_spec_digest_mismatch" in outcome.reasons


def test_every_signed_freeze_receipt_binding_must_match_the_accepted_candidate() -> None:
    documents: list[dict[str, Any]] = []

    source_commit = _payload_dict()
    source_commit["source_commit"] = "2" * 40
    documents.append(source_commit)

    source_tree = _payload_dict()
    source_tree["source_tree_digest"] = DIGEST_F
    source_tree["environment"]["source_tree_digest"] = DIGEST_F
    documents.append(source_tree)

    lock = _payload_dict()
    lock["dependency_lock_digest"] = DIGEST_F
    lock["environment"]["dependency_lock_digest"] = DIGEST_F
    documents.append(lock)

    majority = _payload_dict()
    majority["fixed_train_majority_label"] = "negative"
    documents.append(majority)

    frozen_at = _payload_dict()
    frozen_at["candidate_frozen_at"] = NOW - timedelta(minutes=30)
    documents.append(frozen_at)

    training = _payload_dict()
    training["training_code_digest"] = DIGEST_F
    documents.append(training)

    candidate_code = _payload_dict()
    candidate_code["candidate_code_digest"] = DIGEST_F
    candidate_code["runtime_code_digest"] = DIGEST_F
    candidate_code["evaluation_executable_digest"] = DIGEST_F
    candidate_code["run_attempts"][0]["executable_digest"] = DIGEST_F
    documents.append(candidate_code)

    contract = _payload_dict()
    contract["evaluation_contract_digest"] = DIGEST_F
    contract["contract_digest"] = DIGEST_F
    documents.append(contract)

    for document in documents:
        payload = HiddenEvaluationEvidencePayload.model_validate(document)
        private_key = Ed25519PrivateKey.generate()
        envelope = _signed_envelope(private_key, payload)
        outcome = verify_signed_hidden_evidence(
            envelope=envelope,
            trusted_public_keys={envelope.signer_id: private_key.public_key()},
            accepted_spec_digests=ACCEPTED_SPECS,
            accepted_candidate_bundles=_accepted_candidate_bundles(),
            trusted_attestation_digests=TRUSTED_ATTESTATIONS,
            accepted_hidden_commitments=_accepted_hidden_commitments(),
        )
        assert outcome.signature_valid is True
        assert outcome.evidence_accepted is False
        assert "candidate_freeze_receipt_mismatch" in outcome.reasons


def test_candidate_must_be_frozen_strictly_before_hidden_commitment() -> None:
    document = _payload_dict()
    document["candidate_frozen_at"] = NOW

    with pytest.raises(ValidationError, match="strictly before"):
        HiddenEvaluationEvidencePayload.model_validate(document)


def test_selected_attempt_is_bound_to_run_input_prediction_executable_and_mode() -> None:
    cases = (
        ("reported_run_id", "another-run"),
        ("input_batch_digest", DIGEST_F),
        ("prediction_batch_digest", DIGEST_F),
        ("evaluation_executable_digest", DIGEST_F),
        ("evaluation_mode", "ablation"),
    )
    for field_name, value in cases:
        document = _payload_dict()
        document[field_name] = value
        with pytest.raises(ValidationError):
            HiddenEvaluationEvidencePayload.model_validate(document)


def test_reviewer_attestation_registry_is_mandatory_and_exact() -> None:
    private_key = Ed25519PrivateKey.generate()
    envelope = _signed_envelope(private_key)

    unknown = verify_signed_hidden_evidence(
        envelope=envelope,
        trusted_public_keys={envelope.signer_id: private_key.public_key()},
        accepted_spec_digests=ACCEPTED_SPECS,
        accepted_candidate_bundles=_accepted_candidate_bundles(),
        trusted_attestation_digests={},
        accepted_hidden_commitments=_accepted_hidden_commitments(),
    )
    assert unknown.evidence_accepted is False
    assert "unknown_evaluator_attestation" in unknown.reasons
    assert "unknown_provider_attestation" in unknown.reasons

    mismatched = verify_signed_hidden_evidence(
        envelope=envelope,
        trusted_public_keys={envelope.signer_id: private_key.public_key()},
        accepted_spec_digests=ACCEPTED_SPECS,
        accepted_candidate_bundles=_accepted_candidate_bundles(),
        trusted_attestation_digests={
            "independent:evaluator-one": DIGEST_F,
            "provider:hidden-lab": DIGEST_F,
        },
        accepted_hidden_commitments=_accepted_hidden_commitments(),
    )
    assert mismatched.evidence_accepted is False
    assert "evaluator_attestation_mismatch" in mismatched.reasons
    assert "provider_attestation_mismatch" in mismatched.reasons


def test_reviewer_hidden_commitment_custody_registry_is_mandatory_and_exact() -> None:
    private_key = Ed25519PrivateKey.generate()
    envelope = _signed_envelope(private_key)

    unknown = verify_signed_hidden_evidence(
        envelope=envelope,
        trusted_public_keys={envelope.signer_id: private_key.public_key()},
        accepted_spec_digests=ACCEPTED_SPECS,
        accepted_candidate_bundles=_accepted_candidate_bundles(),
        trusted_attestation_digests=TRUSTED_ATTESTATIONS,
        accepted_hidden_commitments={},
    )
    assert unknown.evidence_accepted is False
    assert unknown.signature_valid is True
    assert "unknown_hidden_artifact_commitment" in unknown.reasons

    mismatched = verify_signed_hidden_evidence(
        envelope=envelope,
        trusted_public_keys={envelope.signer_id: private_key.public_key()},
        accepted_spec_digests=ACCEPTED_SPECS,
        accepted_candidate_bundles=_accepted_candidate_bundles(),
        trusted_attestation_digests=TRUSTED_ATTESTATIONS,
        accepted_hidden_commitments={
            envelope.payload.hidden_artifact.commitment_id: DIGEST_F,
        },
    )
    assert mismatched.evidence_accepted is False
    assert mismatched.signature_valid is True
    assert "hidden_artifact_commitment_digest_mismatch" in mismatched.reasons


def test_unknown_signer_and_payload_digest_tampering_fail_closed() -> None:
    private_key = Ed25519PrivateKey.generate()
    envelope = _signed_envelope(private_key)
    tampered = envelope.model_copy(update={"payload_digest": "0" * 64})

    outcome = verify_signed_hidden_evidence(
        envelope=tampered,
        trusted_public_keys={},
        accepted_spec_digests=ACCEPTED_SPECS,
        accepted_candidate_bundles=_accepted_candidate_bundles(),
        trusted_attestation_digests=TRUSTED_ATTESTATIONS,
        accepted_hidden_commitments=_accepted_hidden_commitments(),
    )

    assert outcome.evidence_accepted is False
    assert outcome.trusted_signer is False
    assert outcome.payload_digest_valid is False
    assert "unknown_signer" in outcome.reasons
    assert "payload_digest_mismatch" in outcome.reasons


def test_signed_payload_tampering_invalidates_digest_and_signature() -> None:
    private_key = Ed25519PrivateKey.generate()
    envelope = _signed_envelope(private_key)
    tampered_payload = envelope.payload.model_copy(update={"model_manifest_digest": DIGEST_A})
    tampered = envelope.model_copy(update={"payload": tampered_payload})

    outcome = verify_signed_hidden_evidence(
        envelope=tampered,
        trusted_public_keys={envelope.signer_id: private_key.public_key()},
        accepted_spec_digests=ACCEPTED_SPECS,
        accepted_candidate_bundles=_accepted_candidate_bundles(),
        trusted_attestation_digests=TRUSTED_ATTESTATIONS,
        accepted_hidden_commitments=_accepted_hidden_commitments(),
    )

    assert outcome.evidence_accepted is False
    assert outcome.payload_digest_valid is False
    assert outcome.signature_valid is False


def test_invalid_detached_signature_fails_closed() -> None:
    private_key = Ed25519PrivateKey.generate()
    other_key = Ed25519PrivateKey.generate()
    envelope = _signed_envelope(private_key)

    outcome = verify_signed_hidden_evidence(
        envelope=envelope,
        trusted_public_keys={envelope.signer_id: other_key.public_key()},
        accepted_spec_digests=ACCEPTED_SPECS,
        accepted_candidate_bundles=_accepted_candidate_bundles(),
        trusted_attestation_digests=TRUSTED_ATTESTATIONS,
        accepted_hidden_commitments=_accepted_hidden_commitments(),
    )

    assert outcome.evidence_accepted is False
    assert outcome.signature_valid is False
    assert "invalid_signature" in outcome.reasons


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("resources", "network_calls"), 1),
        (("resources", "external_effects"), 1),
        (("failures", "hard_safety_test_failures"), 1),
        (("evaluation_gates_passed",), ["g1"]),
        (("stage_release_authorized",), True),
        (("neural_brain_candidate_claimed",), True),
    ],
)
def test_prohibited_results_and_self_claims_are_rejected(
    path: tuple[str, ...], value: object
) -> None:
    document = _payload_dict()
    target: Any = document
    for part in path[:-1]:
        target = target[part]
    target[path[-1]] = value

    with pytest.raises(ValidationError):
        HiddenEvaluationEvidencePayload.model_validate(document)


def test_missing_mode_and_incomplete_attempt_ledger_are_rejected() -> None:
    missing_mode = _payload_dict()
    missing_mode["baseline_results"] = missing_mode["baseline_results"][:-1]
    with pytest.raises(ValidationError, match="every required baseline"):
        HiddenEvaluationEvidencePayload.model_validate(missing_mode)

    incomplete_attempts = _payload_dict()
    incomplete_attempts["declared_attempt_count"] = 2
    with pytest.raises(ValidationError, match="attempt count"):
        HiddenEvaluationEvidencePayload.model_validate(incomplete_attempts)


def test_per_sequence_evidence_is_not_accepted() -> None:
    document = _payload_dict()
    document["full_result"]["per_sequence_correct"] = [True] * 512

    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        HiddenEvaluationEvidencePayload.model_validate(document)


def test_provider_evaluator_and_split_identity_must_remain_separate() -> None:
    document = _payload_dict()
    document["provider"]["organization_id"] = "evaluation-lab"
    with pytest.raises(ValidationError, match="must be separate"):
        HiddenEvaluationEvidencePayload.model_validate(document)


def test_failed_attempt_must_be_disclosed_and_cannot_supply_the_report() -> None:
    document = _payload_dict()
    attempt = document["run_attempts"][0]
    attempt["status"] = "failed"
    attempt["failure_summary_digest"] = DIGEST_6

    with pytest.raises(ValidationError, match="completed attempt"):
        HiddenEvaluationEvidencePayload.model_validate(document)


def test_run_attempt_cannot_precede_hidden_artifact_commitment() -> None:
    document = _payload_dict()
    document["run_attempts"][0]["started_at"] = NOW - timedelta(seconds=1)

    with pytest.raises(ValidationError, match="cannot precede"):
        HiddenEvaluationEvidencePayload.model_validate(document)


def test_run_attempt_must_use_the_payload_candidate_bundle() -> None:
    document = _payload_dict()
    document["run_attempts"][0]["candidate_bundle_digest"] = DIGEST_F

    with pytest.raises(ValidationError, match="candidate bundle digest mismatch"):
        HiddenEvaluationEvidencePayload.model_validate(document)


def test_helpers_create_stable_canonical_payload_identity() -> None:
    payload = _payload()

    assert canonical_evidence_payload_bytes(payload) == canonical_evidence_payload_bytes(payload)
    assert evidence_payload_digest(payload) == evidence_payload_digest(payload)
    assert hidden_artifact_commitment_digest(
        payload.hidden_artifact
    ) == hidden_artifact_commitment_digest(payload.hidden_artifact)
    assert _interval(0.1, 0.2).confidence_level == 0.95
