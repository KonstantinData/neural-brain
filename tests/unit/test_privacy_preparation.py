"""Unit evidence for the non-authorizing privacy preparation boundary."""

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from neural_brain.privacy import (
    Article10Status,
    DecisionPointStatus,
    EvidenceReference,
    InvalidPolicyTransitionError,
    MinorDataStatus,
    PersonalDataStatus,
    PolicyState,
    PreparationPolicyStateMachine,
    PreparationPrivacyEvaluator,
    PreparedStorageMetadata,
    PrivacyActivationNotAuthorizedError,
    PrivacyDecisionOutcome,
    PrivacyPreparationDecision,
    PrivacyPreparationInput,
    ProtectedDataClassification,
    SpecialCategoryStatus,
    SubjectReferenceKind,
)

NOW = datetime(2026, 7, 28, 8, 0, tzinfo=UTC)
DIGEST_A = "a" * 64
DIGEST_B = "b" * 64


def _evidence(*, valid_until: datetime | None = None) -> EvidenceReference:
    return EvidenceReference(
        evidence_id="evidence-1",
        evidence_version=1,
        evidence_digest=DIGEST_A,
        source_reference="qualified-review-package",
        valid_until=valid_until or NOW + timedelta(days=30),
    )


def _classification(
    *,
    personal: PersonalDataStatus = PersonalDataStatus.PERSONAL,
    special: SpecialCategoryStatus = SpecialCategoryStatus.ARTICLE_9,
    article_10: Article10Status = Article10Status.NOT_APPLICABLE,
    minor: MinorDataStatus = MinorDataStatus.NO,
    contradiction: bool = False,
    valid_until: datetime | None = None,
) -> ProtectedDataClassification:
    return ProtectedDataClassification(
        classification_id="class-1",
        classification_version=1,
        subject_artifact_digest=DIGEST_B,
        personal_data_status=personal,
        special_category_status=special,
        article_10_status=article_10,
        minor_data_status=minor,
        article_9_category_codes=("health_data",)
        if special is SpecialCategoryStatus.ARTICLE_9
        else (),
        evidence_references=(_evidence(valid_until=valid_until),),
        contradiction_detected=contradiction,
    )


def _metadata(
    *,
    subject_kind: SubjectReferenceKind = SubjectReferenceKind.SUBJECT,
    additional_condition: bool = True,
    evidence_valid_until: datetime | None = None,
) -> PreparedStorageMetadata:
    evidence = _evidence(valid_until=evidence_valid_until)
    return PreparedStorageMetadata(
        schema_version="protected-storage-preparation-v1",
        data_object_type_id="observation",
        data_object_type_version=1,
        processing_activity_id="memory-intake",
        processing_activity_version=1,
        purpose_id="purpose-1",
        purpose_version=1,
        article_6_evidence_ref=evidence,
        additional_condition_evidence_ref=evidence if additional_condition else None,
        subject_category_id="data-subject-category-1",
        subject_category_version=1,
        subject_reference_kind=subject_kind,
        subject_reference_token="subject-token"
        if subject_kind in {SubjectReferenceKind.SUBJECT, SubjectReferenceKind.GROUP}
        else None,
        source_id="source-1",
        source_version=1,
        source_digest=DIGEST_A,
        retention_rule_id="retention-1",
        retention_rule_version=1,
        technical_classification="restricted",
        privacy_data_class_id="class-1",
        privacy_data_class_version=1,
        protection_requirements_id="protection-1",
        protection_requirements_version=1,
        protection_requirements_digest=DIGEST_B,
        policy_id="policy-1",
        policy_version=1,
        policy_digest=DIGEST_B,
        approval_refs=(evidence,),
        evidence_refs=(evidence,),
        evidence_set_digest=DIGEST_A,
    )


def _request(
    *,
    classification: ProtectedDataClassification | None = None,
    metadata: PreparedStorageMetadata | None = None,
    policy_state: PolicyState = PolicyState.APPROVED,
    statuses: tuple[DecisionPointStatus, ...] = (DecisionPointStatus.DECIDED,),
    evidence_complete: bool = True,
    policy_conflict: bool = False,
    policy_valid_until: datetime | None = None,
) -> PrivacyPreparationInput:
    return PrivacyPreparationInput(
        classification=classification or _classification(),
        metadata=metadata or _metadata(),
        policy_state=policy_state,
        decision_point_statuses=statuses,
        evidence_complete=evidence_complete,
        policy_conflict=policy_conflict,
        policy_valid_until=policy_valid_until or NOW + timedelta(days=30),
    )


@pytest.mark.parametrize(
    ("case_input", "expected"),
    [
        (_request(policy_conflict=True), PrivacyDecisionOutcome.CONFLICT),
        (
            _request(
                classification=_classification(
                    personal=PersonalDataStatus.NON_PERSONAL,
                    special=SpecialCategoryStatus.ARTICLE_9,
                )
            ),
            PrivacyDecisionOutcome.CONFLICT,
        ),
        (
            _request(
                classification=_classification(
                    personal=PersonalDataStatus.UNKNOWN,
                    special=SpecialCategoryStatus.UNKNOWN,
                )
            ),
            PrivacyDecisionOutcome.UNKNOWN,
        ),
        (_request(policy_state=PolicyState.REVOKED), PrivacyDecisionOutcome.REVOKED),
        (
            _request(policy_valid_until=NOW - timedelta(seconds=1)),
            PrivacyDecisionOutcome.EXPIRED,
        ),
        (
            _request(evidence_complete=False),
            PrivacyDecisionOutcome.REQUIRE_ADDITIONAL_EVIDENCE,
        ),
        (
            _request(metadata=_metadata(additional_condition=False)),
            PrivacyDecisionOutcome.REQUIRE_ADDITIONAL_EVIDENCE,
        ),
        (
            _request(metadata=_metadata(evidence_valid_until=NOW - timedelta(seconds=1))),
            PrivacyDecisionOutcome.EXPIRED,
        ),
        (
            _request(statuses=(DecisionPointStatus.PENDING_OWNER,)),
            PrivacyDecisionOutcome.REQUIRE_ADDITIONAL_EVIDENCE,
        ),
        (
            _request(statuses=(DecisionPointStatus.PENDING_PRIVACY_REVIEW,)),
            PrivacyDecisionOutcome.REQUIRE_HUMAN_REVIEW,
        ),
        (
            _request(statuses=(DecisionPointStatus.PENDING_LEGAL_REVIEW,)),
            PrivacyDecisionOutcome.REQUIRE_HUMAN_REVIEW,
        ),
        (
            _request(statuses=(DecisionPointStatus.REJECTED,)),
            PrivacyDecisionOutcome.DENY,
        ),
        (
            _request(statuses=(DecisionPointStatus.OUT_OF_SCOPE,)),
            PrivacyDecisionOutcome.DENY,
        ),
    ],
)
def test_preparation_evaluator_classifies_blockers_without_authorizing(
    case_input: PrivacyPreparationInput, expected: PrivacyDecisionOutcome
) -> None:
    decision = PreparationPrivacyEvaluator().evaluate(case_input, evaluated_at=NOW)

    assert decision.outcome is expected
    assert decision.runtime_enabled is False
    assert decision.mutation_authorized is False


def test_complete_approved_input_still_denies_runtime_activation() -> None:
    decision = PreparationPrivacyEvaluator().evaluate(_request(), evaluated_at=NOW)

    assert decision == PrivacyPreparationDecision(
        outcome=PrivacyDecisionOutcome.DENY,
        reason_codes=("runtime_activation_not_authorized",),
    )


def test_reserved_allow_decision_cannot_be_constructed() -> None:
    with pytest.raises(ValidationError, match="ALLOW is not authorized"):
        PrivacyPreparationDecision(
            outcome=PrivacyDecisionOutcome.ALLOW,
            reason_codes=("forged_allow",),
        )


def test_untrusted_metadata_has_no_identity_scope_or_decision_fields() -> None:
    fields = set(PreparedStorageMetadata.model_fields)

    assert fields.isdisjoint(
        {
            "actor_id",
            "tenant_id",
            "area_id",
            "project_id",
            "session_id",
            "decision",
            "outcome",
            "approval",
        }
    )


def test_strict_metadata_rejects_unknown_fields() -> None:
    document = _metadata().model_dump(mode="python")
    document["tenant_id"] = "payload-tenant"

    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        PreparedStorageMetadata.model_validate(document)


def test_prepared_metadata_versions_are_strict_positive_integers() -> None:
    document = _metadata().model_dump(mode="python")
    document["policy_version"] = "1"

    with pytest.raises(ValidationError, match="valid integer"):
        PreparedStorageMetadata.model_validate(document)

    document["policy_version"] = 0
    with pytest.raises(ValidationError, match="greater than or equal to 1"):
        PreparedStorageMetadata.model_validate(document)


def test_subject_reference_shape_is_fail_closed() -> None:
    document = _metadata().model_dump(mode="python")
    document["subject_reference_kind"] = SubjectReferenceKind.UNKNOWN

    with pytest.raises(ValidationError, match="cannot carry a token"):
        PreparedStorageMetadata.model_validate(document)


def test_preparation_state_machine_allows_review_but_never_activation() -> None:
    machine = PreparationPolicyStateMachine()

    review = machine.transition(
        current_state=PolicyState.DRAFT,
        target_state=PolicyState.PENDING_REVIEW,
        reason="submit-for-review",
    )
    approved = machine.transition(
        current_state=PolicyState.PENDING_REVIEW,
        target_state=PolicyState.APPROVED,
        reason="external-decisions-recorded",
    )

    assert review.runtime_activated is False
    assert approved.runtime_activated is False
    with pytest.raises(PrivacyActivationNotAuthorizedError):
        machine.transition(
            current_state=PolicyState.APPROVED,
            target_state=PolicyState.ACTIVE,
            reason="attempted-activation",
        )


def test_terminal_policy_state_cannot_transition() -> None:
    with pytest.raises(InvalidPolicyTransitionError):
        PreparationPolicyStateMachine().transition(
            current_state=PolicyState.REVOKED,
            target_state=PolicyState.PENDING_REVIEW,
            reason="invalid-reactivation",
        )
