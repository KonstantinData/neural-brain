"""Fail-closed intake for independently signed NB-1 hidden-evaluation evidence."""

import base64
import binascii
import hashlib
import json
import math
from collections.abc import Mapping
from datetime import datetime
from typing import Annotated, Literal, Self

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from pydantic import Field, model_validator

from neural_brain.cognition.hidden_contract import CandidateEvaluationBundle
from neural_brain.memory.models import StrictModel

type Sha256Digest = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
type VersionedContractId = Annotated[str, Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]{2,127}$")]
type BaselineMode = Literal[
    "majority_class",
    "seeded_random",
    "stateless_last_observation",
    "uniform_pooling",
    "non_neural_finite_state",
    "parameter_matched_stateless",
]
type AblationMode = Literal[
    "uniform_feature_gate",
    "zero_recurrent_weight",
    "reset_workspace_state_each_step",
]
type ComparatorMode = BaselineMode | AblationMode

_REQUIRED_BASELINES = frozenset(
    {
        "majority_class",
        "seeded_random",
        "stateless_last_observation",
        "uniform_pooling",
        "non_neural_finite_state",
        "parameter_matched_stateless",
    }
)
_REQUIRED_ABLATIONS = frozenset(
    {"uniform_feature_gate", "zero_recurrent_weight", "reset_workspace_state_each_step"}
)


def _aware(value: datetime, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must include a timezone offset")


class IndependentEvaluatorIdentity(StrictModel):
    """Attested evaluator identity outside implementation and artifact ownership."""

    evaluator_id: Annotated[str, Field(pattern=r"^independent:[a-z0-9][a-z0-9._-]{2,127}$")]
    organization_id: Annotated[str, Field(min_length=3, max_length=128)]
    implementation_owner_id: Annotated[str, Field(min_length=3, max_length=128)]
    independent_from_implementation: Literal[True] = True
    attestation_digest: Sha256Digest

    @model_validator(mode="after")
    def identities_are_separate(self) -> Self:
        if self.organization_id == self.implementation_owner_id:
            raise ValueError("evaluator organization must be independent from implementation")
        return self


class HiddenArtifactProviderIdentity(StrictModel):
    """Attested provider that controls the undisclosed hidden artifact."""

    provider_id: Annotated[str, Field(pattern=r"^provider:[a-z0-9][a-z0-9._-]{2,127}$")]
    organization_id: Annotated[str, Field(min_length=3, max_length=128)]
    implementation_owner_id: Annotated[str, Field(min_length=3, max_length=128)]
    independent_from_implementation: Literal[True] = True
    attestation_digest: Sha256Digest

    @model_validator(mode="after")
    def identities_are_separate(self) -> Self:
        if self.organization_id == self.implementation_owner_id:
            raise ValueError("artifact provider must be independent from implementation")
        return self


class HiddenArtifactCommitment(StrictModel):
    """Pre-run commitment without hidden examples, labels, or seed material."""

    commitment_id: Annotated[str, Field(min_length=3, max_length=128)]
    provider_id: Annotated[str, Field(pattern=r"^provider:[a-z0-9][a-z0-9._-]{2,127}$")]
    dataset_role: Literal["hidden_test"] = "hidden_test"
    generator_contract: VersionedContractId
    split_id: Annotated[str, Field(min_length=3, max_length=128)]
    artifact_digest: Sha256Digest
    sequence_count: Annotated[int, Field(strict=True, ge=512, le=4096)]
    committed_at: datetime
    seed_disclosed_to_implementer: Literal[False] = False
    hidden_content_included: Literal[False] = False

    @model_validator(mode="after")
    def timestamp_is_aware(self) -> Self:
        _aware(self.committed_at, "committed_at")
        return self


class HiddenEvaluationRunAttempt(StrictModel):
    """One fully disclosed and finalized attempt against the committed artifact."""

    attempt_index: Annotated[int, Field(strict=True, ge=0)]
    run_id: Annotated[str, Field(min_length=3, max_length=128)]
    status: Literal["completed", "failed"]
    selected_for_report: bool
    started_at: datetime
    completed_at: datetime
    hidden_artifact_digest: Sha256Digest
    candidate_bundle_digest: Sha256Digest
    input_batch_digest: Sha256Digest
    prediction_batch_digest: Sha256Digest
    executable_digest: Sha256Digest
    evaluation_mode: Literal["full"] = "full"
    fresh_process: Literal[True] = True
    model_manifest_digest: Sha256Digest
    evaluation_protocol_digest: Sha256Digest
    environment_digest: Sha256Digest
    all_inputs_verified: Literal[True] = True
    hidden_data_exposed_to_implementer: Literal[False] = False
    post_attachment_change_detected: Literal[False] = False
    failure_summary_digest: Sha256Digest | None = None

    @model_validator(mode="after")
    def attempt_is_finalized(self) -> Self:
        _aware(self.started_at, "started_at")
        _aware(self.completed_at, "completed_at")
        if self.completed_at < self.started_at:
            raise ValueError("completed_at must not precede started_at")
        if self.status == "failed" and self.failure_summary_digest is None:
            raise ValueError("failed attempts require a failure summary digest")
        if self.status == "completed" and self.failure_summary_digest is not None:
            raise ValueError("completed attempts cannot carry a failure summary digest")
        if self.selected_for_report and self.status != "completed":
            raise ValueError("only a completed attempt may be selected for reporting")
        return self


class ContaminationReport(StrictModel):
    """Fail-closed disclosure of split isolation and hidden-access checks."""

    report_digest: Sha256Digest
    train_dataset_digest: Sha256Digest
    development_dataset_digest: Sha256Digest
    hidden_dataset_digest: Sha256Digest
    exact_duplicate_count: Literal[0] = 0
    identifier_overlap_count: Literal[0] = 0
    provenance_overlap_count: Literal[0] = 0
    hidden_seed_leakage_detected: Literal[False] = False
    hidden_access_by_implementer_detected: Literal[False] = False
    post_attachment_change_detected: Literal[False] = False
    all_attempts_disclosed: Literal[True] = True
    checks_complete: Literal[True] = True

    @model_validator(mode="after")
    def split_digests_are_distinct(self) -> Self:
        digests = {
            self.train_dataset_digest,
            self.development_dataset_digest,
            self.hidden_dataset_digest,
        }
        if len(digests) != 3:
            raise ValueError("train, development, and hidden digests must be distinct")
        return self


class EvaluationEnvironmentEvidence(StrictModel):
    """Immutable runtime and executable-input provenance."""

    environment_digest: Sha256Digest
    dependency_lock_digest: Sha256Digest
    source_tree_digest: Sha256Digest
    evaluator_code_digest: Sha256Digest
    python_version: Annotated[str, Field(min_length=3, max_length=64)]
    runtime_id: Annotated[str, Field(min_length=3, max_length=128)]


class ResourceResults(StrictModel):
    """Observed EVAL-01 resource bounds and prohibited-surface counts."""

    maximum_input_features: Annotated[int, Field(strict=True, ge=1, le=2)]
    maximum_workspace_units: Literal[1]
    maximum_sequence_length: Annotated[int, Field(strict=True, ge=2, le=8)]
    training_sequences: Literal[512]
    hidden_test_sequences: Annotated[int, Field(strict=True, ge=512, le=4096)]
    network_calls: Literal[0] = 0
    external_effects: Literal[0] = 0
    runtime_parameter_mutations: Literal[0] = 0
    measurements_complete: Literal[True] = True


class FailureResults(StrictModel):
    """Complete disclosure of hard failures and unknown required checks."""

    hard_safety_test_failures: Literal[0] = 0
    external_effect_surface_failures: Literal[0] = 0
    unknown_required_results: Literal[0] = 0
    undisclosed_failures: Literal[0] = 0
    disclosure_complete: Literal[True] = True
    report_digest: Sha256Digest


class ConfidenceInterval(StrictModel):
    """Aggregate 95 percent confidence interval."""

    lower: Annotated[float, Field(strict=True, ge=-1.0, le=1.0)]
    upper: Annotated[float, Field(strict=True, ge=-1.0, le=1.0)]
    confidence_level: Annotated[float, Field(strict=True, ge=0.95, le=0.95)] = 0.95

    @model_validator(mode="after")
    def bounds_are_ordered(self) -> Self:
        if self.lower > self.upper:
            raise ValueError("confidence interval lower bound exceeds upper bound")
        return self


class AggregatedFullMechanismResult(StrictModel):
    """Aggregate full-mechanism result without per-sequence disclosure."""

    mode: Literal["full"] = "full"
    correct: Annotated[int, Field(strict=True, ge=0)]
    total: Annotated[int, Field(strict=True, ge=1)]
    accuracy: Annotated[float, Field(strict=True, ge=0.0, le=1.0)]
    accuracy_interval: ConfidenceInterval

    @model_validator(mode="after")
    def aggregate_is_consistent(self) -> Self:
        if self.correct > self.total or not math.isclose(
            self.accuracy, self.correct / self.total, abs_tol=1e-12
        ):
            raise ValueError("full-mechanism aggregate is inconsistent")
        if not self.accuracy_interval.lower <= self.accuracy <= self.accuracy_interval.upper:
            raise ValueError("accuracy must fall inside its confidence interval")
        return self


class AggregatedComparatorResult(StrictModel):
    """Aggregate baseline or ablation comparison without example-level outcomes."""

    mode: ComparatorMode
    correct: Annotated[int, Field(strict=True, ge=0)]
    total: Annotated[int, Field(strict=True, ge=1)]
    accuracy: Annotated[float, Field(strict=True, ge=0.0, le=1.0)]
    accuracy_interval: ConfidenceInterval
    full_minus_comparator_lift: Annotated[float, Field(strict=True, ge=-1.0, le=1.0)]
    paired_lift_interval: ConfidenceInterval
    bootstrap_replicates: Literal[10000] = 10000

    @model_validator(mode="after")
    def aggregate_is_consistent(self) -> Self:
        if self.correct > self.total or not math.isclose(
            self.accuracy, self.correct / self.total, abs_tol=1e-12
        ):
            raise ValueError("comparator aggregate is inconsistent")
        if not self.accuracy_interval.lower <= self.accuracy <= self.accuracy_interval.upper:
            raise ValueError("accuracy must fall inside its confidence interval")
        if (
            not self.paired_lift_interval.lower
            <= self.full_minus_comparator_lift
            <= (self.paired_lift_interval.upper)
        ):
            raise ValueError("paired lift must fall inside its confidence interval")
        return self


class HiddenEvaluationEvidencePayload(StrictModel):
    """Complete aggregate evidence payload signed by the independent evaluator."""

    document_type: Literal["nb1_independent_hidden_evaluation_evidence"]
    format_version: Literal[1]
    spec_id: VersionedContractId
    spec_digest: Sha256Digest
    evaluator: IndependentEvaluatorIdentity
    provider: HiddenArtifactProviderIdentity
    hidden_artifact: HiddenArtifactCommitment
    candidate_bundle_digest: Sha256Digest
    candidate_frozen_at: datetime
    source_commit: Annotated[str, Field(pattern=r"^[0-9a-f]{40}$")]
    source_tree_digest: Sha256Digest
    dependency_lock_digest: Sha256Digest
    candidate_code_digest: Sha256Digest
    evaluation_contract_digest: Sha256Digest
    fixed_train_majority_label: Literal["positive", "negative"]
    evaluation_protocol_digest: Sha256Digest
    model_manifest_digest: Sha256Digest
    parameter_digest: Sha256Digest
    training_artifact_digest: Sha256Digest
    training_code_digest: Sha256Digest
    runtime_code_digest: Sha256Digest
    contract_digest: Sha256Digest
    reported_run_id: Annotated[str, Field(min_length=3, max_length=128)]
    input_batch_digest: Sha256Digest
    prediction_batch_digest: Sha256Digest
    evaluation_executable_digest: Sha256Digest
    evaluation_mode: Literal["full"] = "full"
    environment: EvaluationEnvironmentEvidence
    declared_attempt_count: Annotated[int, Field(strict=True, ge=1)]
    run_attempts: Annotated[tuple[HiddenEvaluationRunAttempt, ...], Field(min_length=1)]
    contamination: ContaminationReport
    resources: ResourceResults
    failures: FailureResults
    full_result: AggregatedFullMechanismResult
    baseline_results: tuple[AggregatedComparatorResult, ...]
    ablation_results: tuple[AggregatedComparatorResult, ...]
    evaluation_gates_passed: tuple[()] = ()
    recognition_gates_passed: tuple[()] = ()
    stage_release_authorized: Literal[False] = False
    neural_brain_candidate_claimed: Literal[False] = False
    claim_status: Literal["independent_hidden_result_requires_gate_review"]

    @model_validator(mode="after")
    def evidence_is_complete_and_consistent(self) -> Self:
        _aware(self.candidate_frozen_at, "candidate_frozen_at")
        if self.candidate_frozen_at >= self.hidden_artifact.committed_at:
            raise ValueError("candidate must be frozen strictly before hidden artifact commitment")
        if self.evaluator.organization_id in {
            self.provider.organization_id,
            self.evaluator.implementation_owner_id,
        }:
            raise ValueError("evaluator, provider, and implementation ownership must be separate")
        if self.provider.implementation_owner_id != self.evaluator.implementation_owner_id:
            raise ValueError("provider and evaluator must identify the same implementation owner")
        if self.hidden_artifact.provider_id != self.provider.provider_id:
            raise ValueError("hidden commitment provider does not match provider identity")
        if self.contamination.hidden_dataset_digest != self.hidden_artifact.artifact_digest:
            raise ValueError("contamination report does not match hidden artifact")
        if self.resources.hidden_test_sequences != self.hidden_artifact.sequence_count:
            raise ValueError("resource result does not match hidden sequence count")
        if self.environment.source_tree_digest != self.source_tree_digest:
            raise ValueError("environment source tree digest mismatch")
        if self.environment.dependency_lock_digest != self.dependency_lock_digest:
            raise ValueError("environment dependency lock digest mismatch")
        if self.runtime_code_digest != self.candidate_code_digest:
            raise ValueError("runtime and candidate code digests must match")
        if self.contract_digest != self.evaluation_contract_digest:
            raise ValueError("contract and evaluation contract digests must match")
        if self.declared_attempt_count != len(self.run_attempts):
            raise ValueError("declared attempt count is incomplete")
        if tuple(attempt.attempt_index for attempt in self.run_attempts) != tuple(
            range(self.declared_attempt_count)
        ):
            raise ValueError("run attempts must be complete, unique, and ordered")
        if len({attempt.run_id for attempt in self.run_attempts}) != len(self.run_attempts):
            raise ValueError("run attempt identifiers must be unique")
        selected = tuple(attempt for attempt in self.run_attempts if attempt.selected_for_report)
        if len(selected) != 1:
            raise ValueError("exactly one completed attempt must be selected for reporting")
        for attempt in self.run_attempts:
            if attempt.started_at < self.hidden_artifact.committed_at:
                raise ValueError("run attempt cannot precede the hidden artifact commitment")
            if attempt.hidden_artifact_digest != self.hidden_artifact.artifact_digest:
                raise ValueError("run attempt hidden artifact digest mismatch")
            if attempt.candidate_bundle_digest != self.candidate_bundle_digest:
                raise ValueError("run attempt candidate bundle digest mismatch")
            if attempt.executable_digest != self.evaluation_executable_digest:
                raise ValueError("run attempt executable digest mismatch")
            if attempt.evaluation_mode != self.evaluation_mode:
                raise ValueError("run attempt evaluation mode mismatch")
            if attempt.model_manifest_digest != self.model_manifest_digest:
                raise ValueError("run attempt model manifest digest mismatch")
            if attempt.evaluation_protocol_digest != self.evaluation_protocol_digest:
                raise ValueError("run attempt evaluation protocol digest mismatch")
            if attempt.environment_digest != self.environment.environment_digest:
                raise ValueError("run attempt environment digest mismatch")
        selected_attempt = selected[0]
        if selected_attempt.run_id != self.reported_run_id:
            raise ValueError("selected run attempt ID does not match the reported run")
        if selected_attempt.input_batch_digest != self.input_batch_digest:
            raise ValueError("selected run attempt input batch digest mismatch")
        if selected_attempt.prediction_batch_digest != self.prediction_batch_digest:
            raise ValueError("selected run attempt prediction batch digest mismatch")
        baseline_modes = {result.mode for result in self.baseline_results}
        ablation_modes = {result.mode for result in self.ablation_results}
        if baseline_modes != _REQUIRED_BASELINES or len(self.baseline_results) != len(
            _REQUIRED_BASELINES
        ):
            raise ValueError("every required baseline must appear exactly once")
        if ablation_modes != _REQUIRED_ABLATIONS or len(self.ablation_results) != len(
            _REQUIRED_ABLATIONS
        ):
            raise ValueError("every required ablation must appear exactly once")
        for result in (*self.baseline_results, *self.ablation_results):
            if result.total != self.hidden_artifact.sequence_count:
                raise ValueError("comparator total does not match hidden sequence count")
            expected_lift = self.full_result.accuracy - result.accuracy
            if not math.isclose(result.full_minus_comparator_lift, expected_lift, abs_tol=1e-12):
                raise ValueError("reported comparator lift is inconsistent")
        if self.full_result.total != self.hidden_artifact.sequence_count:
            raise ValueError("full result total does not match hidden sequence count")
        return self


class Ed25519SignedEvidenceEnvelope(StrictModel):
    """Evidence payload with a detached Ed25519 signature over canonical bytes."""

    payload: HiddenEvaluationEvidencePayload
    payload_digest: Sha256Digest
    signer_id: Annotated[str, Field(pattern=r"^independent:[a-z0-9][a-z0-9._-]{2,127}$")]
    signature_base64: Annotated[str, Field(min_length=88, max_length=88)]
    signature_algorithm: Literal["Ed25519"] = "Ed25519"


class HiddenEvidenceVerificationOutcome(StrictModel):
    """Signature/intake outcome that deliberately cannot grant a maturity gate."""

    evidence_accepted: bool
    trusted_signer: bool
    payload_digest_valid: bool
    signature_valid: bool
    reasons: tuple[str, ...]
    evaluation_gates_passed: tuple[()] = ()
    recognition_gates_passed: tuple[()] = ()
    stage_release_authorized: Literal[False] = False
    neural_brain_candidate_recognized: Literal[False] = False
    claim_status: Literal[
        "verified_external_evidence_requires_independent_gate_review",
        "external_evidence_rejected",
    ]


def canonical_evidence_payload_bytes(payload: HiddenEvaluationEvidencePayload) -> bytes:
    """Serialize a validated payload deterministically for hashing and signing."""
    return json.dumps(
        payload.model_dump(mode="json"),
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode()


def evidence_payload_digest(payload: HiddenEvaluationEvidencePayload) -> str:
    """Return the SHA-256 identity of the canonical signed payload."""
    return hashlib.sha256(canonical_evidence_payload_bytes(payload)).hexdigest()


def canonical_hidden_artifact_commitment_bytes(commitment: HiddenArtifactCommitment) -> bytes:
    """Serialize the complete provider commitment for reviewer custody approval."""
    return json.dumps(
        commitment.model_dump(mode="json"),
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode()


def hidden_artifact_commitment_digest(commitment: HiddenArtifactCommitment) -> str:
    """Return the canonical SHA-256 identity of a hidden-artifact commitment."""
    return hashlib.sha256(canonical_hidden_artifact_commitment_bytes(commitment)).hexdigest()


def verify_signed_hidden_evidence(
    *,
    envelope: Ed25519SignedEvidenceEnvelope,
    trusted_public_keys: Mapping[str, Ed25519PublicKey],
    accepted_spec_digests: Mapping[str, str],
    accepted_candidate_bundles: Mapping[str, CandidateEvaluationBundle],
    trusted_attestation_digests: Mapping[str, str],
    accepted_hidden_commitments: Mapping[str, str],
) -> HiddenEvidenceVerificationOutcome:
    """Verify trusted signer, canonical digest, and detached signature fail closed."""
    reasons: list[str] = []
    accepted_spec_digest = accepted_spec_digests.get(envelope.payload.spec_id)
    if accepted_spec_digest is None:
        reasons.append("unaccepted_spec_id")
    elif accepted_spec_digest != envelope.payload.spec_digest:
        reasons.append("accepted_spec_digest_mismatch")

    payload = envelope.payload
    candidate = accepted_candidate_bundles.get(payload.candidate_bundle_digest)
    if candidate is None:
        reasons.append("unknown_candidate_bundle")
    else:
        candidate_bindings_match = (
            candidate.artifact_digest == payload.candidate_bundle_digest
            and candidate.source_commit == payload.source_commit
            and candidate.source_tree_digest == payload.source_tree_digest
            and candidate.training_code_digest == payload.training_code_digest
            and candidate.candidate_code_digest == payload.candidate_code_digest
            and candidate.evaluation_contract_digest == payload.evaluation_contract_digest
            and candidate.dependency_lock_digest == payload.dependency_lock_digest
            and candidate.fixed_train_majority_label == payload.fixed_train_majority_label
            and candidate.frozen_at == payload.candidate_frozen_at
            and candidate.model_manifest_digest == payload.model_manifest_digest
            and candidate.model_manifest.parameter_digest == payload.parameter_digest
            and candidate.model_manifest.training_artifact_digest
            == payload.training_artifact_digest
        )
        if not candidate_bindings_match:
            reasons.append("candidate_freeze_receipt_mismatch")
        if candidate.model_manifest.evaluation_spec_digest != payload.spec_digest:
            reasons.append("candidate_spec_digest_mismatch")
        if (
            candidate.frozen_at >= payload.hidden_artifact.committed_at
            or payload.candidate_frozen_at >= payload.hidden_artifact.committed_at
        ):
            reasons.append("candidate_not_frozen_before_hidden_commitment")

    evaluator_attestation = trusted_attestation_digests.get(payload.evaluator.evaluator_id)
    if evaluator_attestation is None:
        reasons.append("unknown_evaluator_attestation")
    elif evaluator_attestation != payload.evaluator.attestation_digest:
        reasons.append("evaluator_attestation_mismatch")
    provider_attestation = trusted_attestation_digests.get(payload.provider.provider_id)
    if provider_attestation is None:
        reasons.append("unknown_provider_attestation")
    elif provider_attestation != payload.provider.attestation_digest:
        reasons.append("provider_attestation_mismatch")

    accepted_commitment_digest = accepted_hidden_commitments.get(
        payload.hidden_artifact.commitment_id
    )
    if accepted_commitment_digest is None:
        reasons.append("unknown_hidden_artifact_commitment")
    elif accepted_commitment_digest != hidden_artifact_commitment_digest(payload.hidden_artifact):
        reasons.append("hidden_artifact_commitment_digest_mismatch")

    public_key = trusted_public_keys.get(envelope.signer_id)
    trusted_signer = public_key is not None
    if not trusted_signer:
        reasons.append("unknown_signer")
    if envelope.signer_id != envelope.payload.evaluator.evaluator_id:
        reasons.append("signer_evaluator_mismatch")

    canonical_payload = canonical_evidence_payload_bytes(envelope.payload)
    calculated_digest = hashlib.sha256(canonical_payload).hexdigest()
    payload_digest_valid = envelope.payload_digest == calculated_digest
    if not payload_digest_valid:
        reasons.append("payload_digest_mismatch")

    signature_valid = False
    try:
        signature = base64.b64decode(envelope.signature_base64, validate=True)
        if len(signature) != 64:
            reasons.append("invalid_signature_encoding")
        elif public_key is not None:
            public_key.verify(signature, canonical_payload)
            signature_valid = True
    except binascii.Error, InvalidSignature, ValueError:
        reasons.append("invalid_signature")

    if (
        payload.evaluation_gates_passed
        or payload.recognition_gates_passed
        or payload.stage_release_authorized
        or payload.neural_brain_candidate_claimed
    ):
        reasons.append("prohibited_gate_or_release_claim")
    baseline_modes = {result.mode for result in payload.baseline_results}
    ablation_modes = {result.mode for result in payload.ablation_results}
    if baseline_modes != _REQUIRED_BASELINES or len(payload.baseline_results) != len(
        _REQUIRED_BASELINES
    ):
        reasons.append("missing_or_duplicate_baseline")
    if ablation_modes != _REQUIRED_ABLATIONS or len(payload.ablation_results) != len(
        _REQUIRED_ABLATIONS
    ):
        reasons.append("missing_or_duplicate_ablation")
    selected_attempts = tuple(
        attempt for attempt in payload.run_attempts if attempt.selected_for_report
    )
    attempts_complete = (
        payload.declared_attempt_count == len(payload.run_attempts)
        and tuple(attempt.attempt_index for attempt in payload.run_attempts)
        == tuple(range(payload.declared_attempt_count))
        and len(selected_attempts) == 1
        and selected_attempts[0].status == "completed"
        and payload.contamination.all_attempts_disclosed
    )
    if not attempts_complete:
        reasons.append("incomplete_attempt_disclosure")
    elif (
        selected_attempts[0].run_id != payload.reported_run_id
        or selected_attempts[0].input_batch_digest != payload.input_batch_digest
        or selected_attempts[0].prediction_batch_digest != payload.prediction_batch_digest
        or selected_attempts[0].executable_digest != payload.evaluation_executable_digest
        or selected_attempts[0].evaluation_mode != payload.evaluation_mode
    ):
        reasons.append("selected_attempt_binding_mismatch")
    if any(
        attempt.candidate_bundle_digest != payload.candidate_bundle_digest
        or attempt.executable_digest != payload.evaluation_executable_digest
        or attempt.evaluation_mode != payload.evaluation_mode
        for attempt in payload.run_attempts
    ):
        reasons.append("attempt_executable_or_mode_mismatch")
    if (
        payload.resources.network_calls != 0
        or payload.resources.external_effects != 0
        or payload.resources.runtime_parameter_mutations != 0
        or payload.failures.hard_safety_test_failures != 0
        or payload.failures.external_effect_surface_failures != 0
        or payload.failures.unknown_required_results != 0
        or payload.failures.undisclosed_failures != 0
    ):
        reasons.append("prohibited_effect_or_failure_result")

    accepted = (
        trusted_signer
        and payload_digest_valid
        and signature_valid
        and envelope.signer_id == envelope.payload.evaluator.evaluator_id
        and not reasons
    )
    return HiddenEvidenceVerificationOutcome(
        evidence_accepted=accepted,
        trusted_signer=trusted_signer,
        payload_digest_valid=payload_digest_valid,
        signature_valid=signature_valid,
        reasons=tuple(reasons),
        claim_status=(
            "verified_external_evidence_requires_independent_gate_review"
            if accepted
            else "external_evidence_rejected"
        ),
    )


__all__ = [
    "AggregatedComparatorResult",
    "AggregatedFullMechanismResult",
    "ConfidenceInterval",
    "ContaminationReport",
    "Ed25519SignedEvidenceEnvelope",
    "EvaluationEnvironmentEvidence",
    "FailureResults",
    "HiddenArtifactCommitment",
    "HiddenArtifactProviderIdentity",
    "HiddenEvaluationEvidencePayload",
    "HiddenEvaluationRunAttempt",
    "HiddenEvidenceVerificationOutcome",
    "IndependentEvaluatorIdentity",
    "ResourceResults",
    "canonical_evidence_payload_bytes",
    "canonical_hidden_artifact_commitment_bytes",
    "evidence_payload_digest",
    "hidden_artifact_commitment_digest",
    "verify_signed_hidden_evidence",
]
