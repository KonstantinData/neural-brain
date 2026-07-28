"""Exact, non-authorizing comparison of resolved governance references."""

from datetime import datetime

from neural_brain.privacy.errors import PrivacyReferenceMismatchError
from neural_brain.privacy.models import (
    DecisionPointStatus,
    GovernanceApprovalReference,
    GovernanceEvidenceReference,
    PolicyResolutionContext,
    ResolvedApprovalBinding,
    ResolvedEvidenceBinding,
)


class PreparationReferenceResolver:
    """Reject cross-record mismatch without producing a policy decision or authority."""

    def validate(
        self,
        *,
        context: PolicyResolutionContext,
        evidence_ref: GovernanceEvidenceReference,
        evidence_record: ResolvedEvidenceBinding,
        approval_ref: GovernanceApprovalReference,
        approval_record: ResolvedApprovalBinding,
        evaluated_at: datetime,
    ) -> None:
        """Return only on exact binding; success remains non-authorizing."""
        if evaluated_at.tzinfo is None or evaluated_at.utcoffset() is None:
            raise ValueError("evaluated_at must include a timezone offset")
        if (
            evidence_ref.evidence_id != evidence_record.evidence_id
            or evidence_ref.evidence_version != evidence_record.evidence_version
            or evidence_ref.evidence_digest != evidence_record.evidence_digest
            or evidence_record.scope != context.scope
        ):
            raise PrivacyReferenceMismatchError("resolved privacy evidence binding mismatch")
        if (
            approval_ref.approval_id != approval_record.approval_id
            or approval_ref.approval_digest != approval_record.approval_digest
            or approval_ref.review_role != approval_record.approval_type
            or approval_ref.reviewer_id != approval_record.actor_id
            or approval_record.scope != context.scope
            or approval_record.policy_digest != context.policy_digest
            or approval_record.evidence_manifest_digest != context.evidence_manifest_digest
            or approval_record.decision_status is not DecisionPointStatus.DECIDED
            or evaluated_at >= approval_record.valid_until
        ):
            raise PrivacyReferenceMismatchError("resolved privacy approval binding mismatch")
