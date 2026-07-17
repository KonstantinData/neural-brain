"""First safe serial Neural Brain cognition slice."""

from neural_brain.cognition.adapters import (
    ActiveCognitiveModel,
    FixedWorkspaceProvider,
    MemoryServiceCognitiveGate,
    model_manifest_digest,
    workspace_parameter_digest,
)
from neural_brain.cognition.errors import (
    CognitiveCheckpointUnavailableError,
    CognitiveRuntimeError,
    CognitiveScopeError,
    StaleCognitiveCheckpointError,
    UnknownNeuralModelError,
)
from neural_brain.cognition.evaluation import (
    EvaluationDataset,
    EvaluationSequence,
    Nb1EvaluationReport,
    evaluate_dataset,
    evaluation_sequence_digest,
)
from neural_brain.cognition.hidden_contract import (
    CandidateEvaluationBundle,
    PredictionBatch,
    PredictionRecord,
    UnlabeledEvaluationBatch,
    UnlabeledEvaluationObservation,
    UnlabeledEvaluationSequence,
    predict_full_mechanism,
)
from neural_brain.cognition.hidden_evidence import (
    Ed25519SignedEvidenceEnvelope,
    HiddenEvaluationEvidencePayload,
    HiddenEvidenceVerificationOutcome,
    verify_signed_hidden_evidence,
)
from neural_brain.cognition.models import (
    ActiveCognitiveModelEvidence,
    ActiveCognitiveModelManifest,
    AttentionDecision,
    CognitiveAuditEvidence,
    CognitiveCheckpoint,
    CognitiveCycleRequest,
    CognitiveCycleResult,
    CognitiveTransitionEnvelope,
    InternalGoalProposal,
    InternalPlanProposal,
    MetacognitiveAssessment,
    NeuralWorkspaceParameters,
    RecordedObservation,
)
from neural_brain.cognition.service import CognitiveCycleService
from neural_brain.cognition.workspace import NeuralWorkspace

__all__ = [
    "ActiveCognitiveModel",
    "ActiveCognitiveModelEvidence",
    "ActiveCognitiveModelManifest",
    "AttentionDecision",
    "CandidateEvaluationBundle",
    "CognitiveAuditEvidence",
    "CognitiveCheckpoint",
    "CognitiveCheckpointUnavailableError",
    "CognitiveCycleRequest",
    "CognitiveCycleResult",
    "CognitiveCycleService",
    "CognitiveRuntimeError",
    "CognitiveScopeError",
    "CognitiveTransitionEnvelope",
    "Ed25519SignedEvidenceEnvelope",
    "EvaluationDataset",
    "EvaluationSequence",
    "FixedWorkspaceProvider",
    "HiddenEvaluationEvidencePayload",
    "HiddenEvidenceVerificationOutcome",
    "InternalGoalProposal",
    "InternalPlanProposal",
    "MemoryServiceCognitiveGate",
    "MetacognitiveAssessment",
    "Nb1EvaluationReport",
    "NeuralWorkspace",
    "NeuralWorkspaceParameters",
    "PredictionBatch",
    "PredictionRecord",
    "RecordedObservation",
    "StaleCognitiveCheckpointError",
    "UnknownNeuralModelError",
    "UnlabeledEvaluationBatch",
    "UnlabeledEvaluationObservation",
    "UnlabeledEvaluationSequence",
    "evaluate_dataset",
    "evaluation_sequence_digest",
    "model_manifest_digest",
    "predict_full_mechanism",
    "verify_signed_hidden_evidence",
    "workspace_parameter_digest",
]
