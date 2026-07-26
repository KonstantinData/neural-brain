"""Non-overridable runtime security boundaries."""

from neural_brain.security.activation import (
    IndependentPolicyApproval,
    PolicyActivationDeniedError,
    PolicyRegressionEvidence,
    authorize_policy_activation,
)
from neural_brain.security.authority import (
    MEMORY_AUTHORITY_CONTRACT_VERSION,
    GrantStatus,
    MemoryAuthorityDeniedError,
    MemoryAuthorityGrant,
    MemoryAuthoritySnapshot,
    TrustedMemoryAuthorityRequest,
    authorize_memory_authority,
)
from neural_brain.security.envelopes import TrustSurface, UntrustedPayloadEnvelope
from neural_brain.security.floor import (
    SECURITY_FLOOR_VERSION,
    MemoryOperation,
    SecurityFloorDeniedError,
    authorize_memory_operation,
)
from neural_brain.security.memory_approval import (
    MEMORY_OPERATION_APPROVAL_CONTRACT_VERSION,
    MemoryOperationApproval,
    MemoryOperationApprovalDeniedError,
    validate_memory_operation_approval_evidence,
)
from neural_brain.security.memory_request_evidence import (
    MemoryRequestEvidenceDeniedError,
    validate_memory_request_evidence,
)
from neural_brain.security.memory_risk import (
    MEMORY_RISK_CONTRACT_VERSION,
    MemoryLifecycleOperation,
    MemoryRiskClass,
    MemoryRiskDecision,
    MemoryRiskOutcome,
    MemoryRiskRequest,
    decide_memory_risk,
)
from neural_brain.security.policy import (
    POLICY_SCHEMA_VERSION,
    CompiledPolicy,
    PolicyCompilationError,
    PolicyDocument,
    canonical_policy_json,
    compile_policy,
)

__all__ = [
    "MEMORY_AUTHORITY_CONTRACT_VERSION",
    "MEMORY_OPERATION_APPROVAL_CONTRACT_VERSION",
    "MEMORY_RISK_CONTRACT_VERSION",
    "POLICY_SCHEMA_VERSION",
    "SECURITY_FLOOR_VERSION",
    "CompiledPolicy",
    "GrantStatus",
    "IndependentPolicyApproval",
    "MemoryAuthorityDeniedError",
    "MemoryAuthorityGrant",
    "MemoryAuthoritySnapshot",
    "MemoryLifecycleOperation",
    "MemoryOperation",
    "MemoryOperationApproval",
    "MemoryOperationApprovalDeniedError",
    "MemoryRequestEvidenceDeniedError",
    "MemoryRiskClass",
    "MemoryRiskDecision",
    "MemoryRiskOutcome",
    "MemoryRiskRequest",
    "PolicyActivationDeniedError",
    "PolicyCompilationError",
    "PolicyDocument",
    "PolicyRegressionEvidence",
    "SecurityFloorDeniedError",
    "TrustSurface",
    "TrustedMemoryAuthorityRequest",
    "UntrustedPayloadEnvelope",
    "authorize_memory_authority",
    "authorize_memory_operation",
    "authorize_policy_activation",
    "canonical_policy_json",
    "compile_policy",
    "decide_memory_risk",
    "validate_memory_operation_approval_evidence",
    "validate_memory_request_evidence",
]
