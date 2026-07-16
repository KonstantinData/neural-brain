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
    IndependentEvaluatorIdentity,
    Nb1EvaluationReport,
    evaluate_dataset,
    evaluate_hidden_dataset,
    evaluation_sequence_digest,
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
    "CognitiveAuditEvidence",
    "CognitiveCheckpoint",
    "CognitiveCheckpointUnavailableError",
    "CognitiveCycleRequest",
    "CognitiveCycleResult",
    "CognitiveCycleService",
    "CognitiveRuntimeError",
    "CognitiveScopeError",
    "CognitiveTransitionEnvelope",
    "EvaluationDataset",
    "EvaluationSequence",
    "FixedWorkspaceProvider",
    "IndependentEvaluatorIdentity",
    "InternalGoalProposal",
    "InternalPlanProposal",
    "MemoryServiceCognitiveGate",
    "MetacognitiveAssessment",
    "Nb1EvaluationReport",
    "NeuralWorkspace",
    "NeuralWorkspaceParameters",
    "RecordedObservation",
    "StaleCognitiveCheckpointError",
    "UnknownNeuralModelError",
    "evaluate_dataset",
    "evaluate_hidden_dataset",
    "evaluation_sequence_digest",
    "model_manifest_digest",
    "workspace_parameter_digest",
]
