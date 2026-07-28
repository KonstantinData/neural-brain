"""Strict non-authorizing models for S1-14.4 and S1-11.2 preparation."""

from datetime import datetime
from enum import StrEnum
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

type PrivacyOpaqueId = Annotated[str, Field(strict=True, min_length=1, max_length=128)]
type PrivacyVersion = Annotated[int, Field(strict=True, ge=1)]
type Sha256Digest = Annotated[str, Field(strict=True, pattern=r"^[0-9a-f]{64}$")]


class PrivacyDecisionOutcome(StrEnum):
    """Target decision vocabulary; ``ALLOW`` is reserved and unreachable here."""

    ALLOW = "ALLOW"
    DENY = "DENY"
    REQUIRE_HUMAN_REVIEW = "REQUIRE_HUMAN_REVIEW"
    REQUIRE_ADDITIONAL_EVIDENCE = "REQUIRE_ADDITIONAL_EVIDENCE"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"
    CONFLICT = "CONFLICT"
    UNKNOWN = "UNKNOWN"


class DecisionPointStatus(StrEnum):
    """External decision-package status without inferred approval."""

    DECIDED = "DECIDED"
    PENDING_OWNER = "PENDING_OWNER"
    PENDING_PRIVACY_REVIEW = "PENDING_PRIVACY_REVIEW"
    PENDING_LEGAL_REVIEW = "PENDING_LEGAL_REVIEW"
    REJECTED = "REJECTED"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"


class EvidenceReviewerTreatment(StrEnum):
    """Qualified disposition of a resolved evidence record."""

    QUALIFIED_ACCEPTED = "qualified_accepted"
    QUALIFIED_NOT_APPLICABLE = "qualified_not_applicable"
    REJECTED = "rejected"
    PENDING_REVIEW = "pending_review"


class EvidenceContradictionStatus(StrEnum):
    """Whether qualified evidence reconciliation found a contradiction."""

    NONE = "none"
    CONFLICT = "conflict"
    UNKNOWN = "unknown"


class PolicyState(StrEnum):
    """Proposed policy lifecycle vocabulary."""

    DRAFT = "DRAFT"
    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"
    REJECTED = "REJECTED"
    SUPERSEDED = "SUPERSEDED"


class PersonalDataStatus(StrEnum):
    """Orthogonal personal-data classification axis."""

    NON_PERSONAL = "NON_PERSONAL"
    PERSONAL = "PERSONAL"
    PSEUDONYMIZED_PERSONAL = "PSEUDONYMIZED_PERSONAL"
    ANONYMIZED_VERIFIED = "ANONYMIZED_VERIFIED"
    UNKNOWN = "UNKNOWN"


class SpecialCategoryStatus(StrEnum):
    """Article 9 applicability axis without a legal conclusion."""

    NOT_APPLICABLE = "NOT_APPLICABLE"
    ARTICLE_9 = "ARTICLE_9"
    UNKNOWN = "UNKNOWN"


class Article10Status(StrEnum):
    """Article 10 evidence axis, kept separate from Article 9."""

    NOT_APPLICABLE = "NOT_APPLICABLE"
    ARTICLE_10 = "ARTICLE_10"
    UNKNOWN = "UNKNOWN"


class MinorDataStatus(StrEnum):
    """Minor-data evidence axis."""

    NO = "NO"
    YES = "YES"
    UNKNOWN = "UNKNOWN"


class SubjectReferenceKind(StrEnum):
    """Pseudonymous subject-binding shape."""

    SUBJECT = "SUBJECT"
    GROUP = "GROUP"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    UNKNOWN = "UNKNOWN"


class StrictPrivacyModel(BaseModel):
    """Reject coercion, mutation, and undeclared fields at preparation boundaries."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class EvidenceReference(StrictPrivacyModel):
    """Immutable secret-free evidence reference; raw evidence is never embedded."""

    evidence_id: PrivacyOpaqueId
    evidence_version: PrivacyVersion
    evidence_digest: Sha256Digest
    source_reference: PrivacyOpaqueId
    valid_until: datetime

    @model_validator(mode="after")
    def valid_until_is_timezone_aware(self) -> Self:
        """Reject process-local timestamps at the policy boundary."""
        if self.valid_until.tzinfo is None or self.valid_until.utcoffset() is None:
            raise ValueError("valid_until must include a timezone offset")
        return self


class GovernanceScope(StrictPrivacyModel):
    """Authenticated-scope-shaped value used only for exact preparation comparison."""

    tenant_id: PrivacyOpaqueId
    area_id: PrivacyOpaqueId
    project_id: PrivacyOpaqueId


class GovernanceEvidenceReference(StrictPrivacyModel):
    """Typed compact reference to a resolved privacy evidence record."""

    record_contract: Literal["privacy-evidence-record-v1"]
    evidence_id: PrivacyOpaqueId
    evidence_version: PrivacyVersion
    evidence_digest: Sha256Digest


class GovernanceDigestedReference(StrictPrivacyModel):
    """Compact immutable reference used for trusted approval bindings."""

    reference_id: PrivacyOpaqueId
    reference_version: PrivacyVersion
    reference_digest: Sha256Digest


class ResolvedEvidenceBinding(StrictPrivacyModel):
    """Fields required to compare one resolved evidence record fail closed."""

    evidence_id: PrivacyOpaqueId
    evidence_version: PrivacyVersion
    evidence_digest: Sha256Digest
    scope: GovernanceScope
    reviewer_treatment: EvidenceReviewerTreatment
    contradiction_status: EvidenceContradictionStatus
    valid_from: datetime
    valid_until: datetime

    @model_validator(mode="after")
    def validity_window_is_timezone_aware(self) -> Self:
        """Reject ambiguous or inverted evidence validity windows."""
        if any(
            timestamp.tzinfo is None or timestamp.utcoffset() is None
            for timestamp in (self.valid_from, self.valid_until)
        ):
            raise ValueError("evidence validity window must include timezone offsets")
        if self.valid_from >= self.valid_until:
            raise ValueError("evidence valid_from must be before valid_until")
        return self


class GovernanceApprovalReference(StrictPrivacyModel):
    """Typed compact reference to a resolved privacy approval record."""

    record_contract: Literal["privacy-approval-record-v1"]
    review_role: Literal[
        "accountable_owner", "privacy_reviewer", "legal_reviewer", "independent_reviewer"
    ]
    reviewer_id: PrivacyOpaqueId
    approval_id: PrivacyOpaqueId
    approval_digest: Sha256Digest
    qualified_role_binding: GovernanceDigestedReference


class ResolvedApprovalBinding(StrictPrivacyModel):
    """Fields required to compare one resolved approval record fail closed."""

    approval_id: PrivacyOpaqueId
    approval_type: Literal[
        "accountable_owner", "privacy_reviewer", "legal_reviewer", "independent_reviewer"
    ]
    approval_digest: Sha256Digest
    policy_digest: Sha256Digest
    evidence_manifest_digest: Sha256Digest
    actor_id: PrivacyOpaqueId
    authority_snapshot_digest: Sha256Digest
    qualified_role_binding: GovernanceDigestedReference
    scope: GovernanceScope
    decision_status: DecisionPointStatus
    approved_at: datetime
    valid_until: datetime
    independence_evidence_ref: GovernanceDigestedReference

    @model_validator(mode="after")
    def validity_window_is_timezone_aware(self) -> Self:
        """Reject ambiguous or inverted approval validity windows."""
        if any(
            timestamp.tzinfo is None or timestamp.utcoffset() is None
            for timestamp in (self.approved_at, self.valid_until)
        ):
            raise ValueError("approval validity window must include timezone offsets")
        if self.approved_at >= self.valid_until:
            raise ValueError("approval approved_at must be before valid_until")
        return self


class PolicyResolutionContext(StrictPrivacyModel):
    """Trusted comparison context; it is not caller-supplied runtime authority."""

    scope: GovernanceScope
    policy_digest: Sha256Digest
    evidence_manifest_digest: Sha256Digest
    authority_snapshot_digest: Sha256Digest
    required_independence_evidence_ref: GovernanceDigestedReference


class ProtectedDataClassification(StrictPrivacyModel):
    """Versioned classification evidence, distinct from protection handling class."""

    classification_id: PrivacyOpaqueId
    classification_version: PrivacyVersion
    subject_artifact_digest: Sha256Digest
    personal_data_status: PersonalDataStatus
    special_category_status: SpecialCategoryStatus
    article_10_status: Article10Status
    minor_data_status: MinorDataStatus
    article_9_category_codes: tuple[PrivacyOpaqueId, ...] = ()
    evidence_references: Annotated[
        tuple[EvidenceReference, ...], Field(min_length=1, max_length=64)
    ]
    contradiction_detected: bool = False

    @model_validator(mode="after")
    def article_9_codes_match_axis(self) -> Self:
        """Require category codes only when the Article 9 axis is affirmative."""
        if (
            self.special_category_status is SpecialCategoryStatus.ARTICLE_9
            and not self.article_9_category_codes
        ):
            raise ValueError("ARTICLE_9 requires at least one category code")
        if (
            self.special_category_status is not SpecialCategoryStatus.ARTICLE_9
            and self.article_9_category_codes
        ):
            raise ValueError("Article 9 category codes require ARTICLE_9 status")
        return self


class PreparedStorageMetadata(StrictPrivacyModel):
    """S1-11.2 preflight references without trusted scope or a legal decision."""

    schema_version: Literal["protected-storage-preparation-v1"]
    data_object_type_id: PrivacyOpaqueId
    data_object_type_version: PrivacyVersion
    processing_activity_id: PrivacyOpaqueId
    processing_activity_version: PrivacyVersion
    purpose_id: PrivacyOpaqueId
    purpose_version: PrivacyVersion
    article_6_evidence_ref: EvidenceReference
    additional_condition_evidence_ref: EvidenceReference | None
    subject_category_id: PrivacyOpaqueId
    subject_category_version: PrivacyVersion
    subject_reference_kind: SubjectReferenceKind
    subject_reference_token: PrivacyOpaqueId | None = None
    source_id: PrivacyOpaqueId
    source_version: PrivacyVersion
    source_digest: Sha256Digest
    retention_rule_id: PrivacyOpaqueId
    retention_rule_version: PrivacyVersion
    technical_classification: Literal["public", "internal", "confidential", "restricted"]
    privacy_data_class_id: PrivacyOpaqueId
    privacy_data_class_version: PrivacyVersion
    protection_requirements_id: PrivacyOpaqueId
    protection_requirements_version: PrivacyVersion
    protection_requirements_digest: Sha256Digest
    policy_id: PrivacyOpaqueId
    policy_version: PrivacyVersion
    policy_digest: Sha256Digest
    approval_refs: Annotated[tuple[EvidenceReference, ...], Field(min_length=1, max_length=16)]
    evidence_refs: Annotated[tuple[EvidenceReference, ...], Field(min_length=1, max_length=64)]
    evidence_set_digest: Sha256Digest

    @model_validator(mode="after")
    def subject_reference_matches_kind(self) -> Self:
        """Keep unknown or not-applicable references non-identifying."""
        requires_token = self.subject_reference_kind in {
            SubjectReferenceKind.SUBJECT,
            SubjectReferenceKind.GROUP,
        }
        if requires_token and self.subject_reference_token is None:
            raise ValueError("subject or group reference requires a token")
        if not requires_token and self.subject_reference_token is not None:
            raise ValueError("unknown or not-applicable subject reference cannot carry a token")
        return self


class PrivacyPreparationInput(StrictPrivacyModel):
    """Inputs that may classify why preparation remains non-authorizing."""

    classification: ProtectedDataClassification
    metadata: PreparedStorageMetadata
    policy_state: PolicyState
    decision_point_statuses: Annotated[
        tuple[DecisionPointStatus, ...], Field(min_length=1, max_length=64)
    ]
    evidence_complete: bool
    policy_conflict: bool = False
    policy_valid_until: datetime

    @model_validator(mode="after")
    def policy_valid_until_is_timezone_aware(self) -> Self:
        """Reject ambiguous policy-expiry input."""
        if self.policy_valid_until.tzinfo is None or self.policy_valid_until.utcoffset() is None:
            raise ValueError("policy_valid_until must include a timezone offset")
        return self


class PrivacyPreparationDecision(StrictPrivacyModel):
    """A fail-closed preparation result that can never authorize mutation."""

    outcome: PrivacyDecisionOutcome
    reason_codes: Annotated[tuple[PrivacyOpaqueId, ...], Field(min_length=1)]
    runtime_enabled: Literal[False] = False
    mutation_authorized: Literal[False] = False

    @model_validator(mode="after")
    def allow_is_unrepresentable(self) -> Self:
        """Reserve ALLOW for a future accepted implementation, never this package."""
        if self.outcome is PrivacyDecisionOutcome.ALLOW:
            raise ValueError("ALLOW is not authorized in the preparation package")
        return self


class PreparedPolicyTransition(StrictPrivacyModel):
    """One non-activating lifecycle transition proposal."""

    from_state: PolicyState
    to_state: PolicyState
    transition_reason: PrivacyOpaqueId
    runtime_activated: Literal[False] = False
