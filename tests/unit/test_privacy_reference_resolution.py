"""Negative binding evidence for fail-closed privacy-reference composition."""

from datetime import UTC, datetime, timedelta
from typing import Literal

import pytest

from neural_brain.privacy import (
    DecisionPointStatus,
    EvidenceContradictionStatus,
    EvidenceReviewerTreatment,
    GovernanceApprovalReference,
    GovernanceDigestedReference,
    GovernanceEvidenceReference,
    GovernanceScope,
    PolicyResolutionContext,
    PreparationReferenceResolver,
    PrivacyReferenceMismatchError,
    ResolvedApprovalBinding,
    ResolvedEvidenceBinding,
)

NOW = datetime(2026, 7, 28, 12, 0, tzinfo=UTC)
DIGEST_A = "a" * 64
DIGEST_B = "b" * 64


def _scope(*, project_id: str = "project-1") -> GovernanceScope:
    return GovernanceScope(tenant_id="tenant-1", area_id="area-1", project_id=project_id)


def _context() -> PolicyResolutionContext:
    return PolicyResolutionContext(
        scope=_scope(),
        policy_digest=DIGEST_A,
        evidence_manifest_digest=DIGEST_B,
        authority_snapshot_digest=DIGEST_A,
        required_independence_evidence_ref=_digested_ref("independence-1"),
    )


def _digested_ref(reference_id: str, *, digest: str = DIGEST_A) -> GovernanceDigestedReference:
    return GovernanceDigestedReference(
        reference_id=reference_id, reference_version=1, reference_digest=digest
    )


def _evidence_ref(*, digest: str = DIGEST_A) -> GovernanceEvidenceReference:
    return GovernanceEvidenceReference(
        record_contract="privacy-evidence-record-v1",
        evidence_id="evidence-1",
        evidence_version=1,
        evidence_digest=digest,
    )


def _evidence_record(
    *,
    scope: GovernanceScope | None = None,
    digest: str = DIGEST_A,
    treatment: EvidenceReviewerTreatment = EvidenceReviewerTreatment.QUALIFIED_ACCEPTED,
    contradiction: EvidenceContradictionStatus = EvidenceContradictionStatus.NONE,
    valid_from: datetime | None = None,
    valid_until: datetime | None = None,
) -> ResolvedEvidenceBinding:
    return ResolvedEvidenceBinding(
        evidence_id="evidence-1",
        evidence_version=1,
        evidence_digest=digest,
        scope=scope or _scope(),
        reviewer_treatment=treatment,
        contradiction_status=contradiction,
        valid_from=valid_from or NOW - timedelta(days=1),
        valid_until=valid_until or NOW + timedelta(days=1),
    )


def _approval_ref(
    *,
    role: Literal[
        "accountable_owner", "privacy_reviewer", "legal_reviewer", "independent_reviewer"
    ] = "privacy_reviewer",
    digest: str = DIGEST_B,
    qualified_role_binding: GovernanceDigestedReference | None = None,
) -> GovernanceApprovalReference:
    return GovernanceApprovalReference(
        record_contract="privacy-approval-record-v1",
        review_role=role,
        reviewer_id="reviewer-1",
        approval_id="approval-1",
        approval_digest=digest,
        qualified_role_binding=qualified_role_binding or _digested_ref("qualified-role-1"),
    )


def _approval_record(
    *,
    scope: GovernanceScope | None = None,
    approval_digest: str = DIGEST_B,
    approval_type: Literal[
        "accountable_owner", "privacy_reviewer", "legal_reviewer", "independent_reviewer"
    ] = "privacy_reviewer",
    decision_status: DecisionPointStatus = DecisionPointStatus.DECIDED,
    approved_at: datetime | None = None,
    valid_until: datetime | None = None,
    policy_digest: str = DIGEST_A,
    evidence_manifest_digest: str = DIGEST_B,
    authority_snapshot_digest: str = DIGEST_A,
    qualified_role_binding: GovernanceDigestedReference | None = None,
    independence_evidence_ref: GovernanceDigestedReference | None = None,
) -> ResolvedApprovalBinding:
    return ResolvedApprovalBinding(
        approval_id="approval-1",
        approval_type=approval_type,
        approval_digest=approval_digest,
        policy_digest=policy_digest,
        evidence_manifest_digest=evidence_manifest_digest,
        actor_id="reviewer-1",
        authority_snapshot_digest=authority_snapshot_digest,
        qualified_role_binding=qualified_role_binding or _digested_ref("qualified-role-1"),
        scope=scope or _scope(),
        decision_status=decision_status,
        approved_at=approved_at or NOW - timedelta(days=1),
        valid_until=valid_until or NOW + timedelta(days=1),
        independence_evidence_ref=independence_evidence_ref or _digested_ref("independence-1"),
    )


def _validate(
    *,
    context: PolicyResolutionContext | None = None,
    evidence_ref: GovernanceEvidenceReference | None = None,
    evidence_record: ResolvedEvidenceBinding | None = None,
    approval_ref: GovernanceApprovalReference | None = None,
    approval_record: ResolvedApprovalBinding | None = None,
) -> None:
    PreparationReferenceResolver().validate(
        context=context or _context(),
        evidence_ref=evidence_ref or _evidence_ref(),
        evidence_record=evidence_record or _evidence_record(),
        approval_ref=approval_ref or _approval_ref(),
        approval_record=approval_record or _approval_record(),
        evaluated_at=NOW,
    )


def test_resolver_accepts_exact_current_qualified_bindings_only() -> None:
    _validate()


@pytest.mark.parametrize(
    "evidence_record",
    [
        _evidence_record(scope=_scope(project_id="other-project")),
        _evidence_record(digest=DIGEST_B),
        _evidence_record(treatment=EvidenceReviewerTreatment.REJECTED),
        _evidence_record(treatment=EvidenceReviewerTreatment.PENDING_REVIEW),
        _evidence_record(treatment=EvidenceReviewerTreatment.QUALIFIED_NOT_APPLICABLE),
        _evidence_record(contradiction=EvidenceContradictionStatus.CONFLICT),
        _evidence_record(contradiction=EvidenceContradictionStatus.UNKNOWN),
        _evidence_record(valid_until=NOW),
        _evidence_record(valid_from=NOW - timedelta(days=2), valid_until=NOW - timedelta(days=1)),
    ],
)
def test_resolver_rejects_validly_shaped_mismatched_or_nonqualifying_evidence(
    evidence_record: ResolvedEvidenceBinding,
) -> None:
    with pytest.raises(PrivacyReferenceMismatchError, match="evidence binding mismatch"):
        _validate(evidence_record=evidence_record)


@pytest.mark.parametrize(
    "approval_ref,approval_record",
    [
        (_approval_ref(role="legal_reviewer"), _approval_record()),
        (_approval_ref(digest=DIGEST_A), _approval_record()),
        (_approval_ref(), _approval_record(approval_digest=DIGEST_A)),
        (_approval_ref(), _approval_record(scope=_scope(project_id="other-project"))),
        (_approval_ref(), _approval_record(approval_type="legal_reviewer")),
        (_approval_ref(), _approval_record(decision_status=DecisionPointStatus.PENDING_OWNER)),
        (_approval_ref(), _approval_record(decision_status=DecisionPointStatus.REJECTED)),
        (_approval_ref(), _approval_record(decision_status=DecisionPointStatus.OUT_OF_SCOPE)),
        (_approval_ref(), _approval_record(valid_until=NOW)),
        (
            _approval_ref(),
            _approval_record(
                approved_at=NOW - timedelta(days=2), valid_until=NOW - timedelta(days=1)
            ),
        ),
        (_approval_ref(), _approval_record(policy_digest=DIGEST_B)),
        (_approval_ref(), _approval_record(evidence_manifest_digest=DIGEST_A)),
        (_approval_ref(), _approval_record(authority_snapshot_digest=DIGEST_B)),
        (_approval_ref(), _approval_record(qualified_role_binding=_digested_ref("other-role"))),
        (
            _approval_ref(),
            _approval_record(independence_evidence_ref=_digested_ref("other-independence")),
        ),
    ],
)
def test_resolver_rejects_validly_shaped_mismatched_or_non_decided_approval(
    approval_ref: GovernanceApprovalReference,
    approval_record: ResolvedApprovalBinding,
) -> None:
    with pytest.raises(PrivacyReferenceMismatchError, match="approval binding mismatch"):
        _validate(approval_ref=approval_ref, approval_record=approval_record)


def test_qualified_not_applicable_evidence_never_substitutes_for_out_of_scope_approval() -> None:
    with pytest.raises(PrivacyReferenceMismatchError, match="evidence binding mismatch"):
        _validate(
            evidence_record=_evidence_record(
                treatment=EvidenceReviewerTreatment.QUALIFIED_NOT_APPLICABLE
            ),
            approval_record=_approval_record(decision_status=DecisionPointStatus.OUT_OF_SCOPE),
        )


def test_resolver_rejects_future_dated_evidence_or_approval() -> None:
    with pytest.raises(PrivacyReferenceMismatchError, match="evidence binding mismatch"):
        _validate(evidence_record=_evidence_record(valid_from=NOW + timedelta(seconds=1)))

    with pytest.raises(PrivacyReferenceMismatchError, match="approval binding mismatch"):
        _validate(approval_record=_approval_record(approved_at=NOW + timedelta(seconds=1)))
