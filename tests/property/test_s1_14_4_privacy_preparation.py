"""Property evidence that preparation cannot authorize protected mutation."""

from datetime import UTC, datetime, timedelta

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from neural_brain.privacy import (
    Article10Status,
    DecisionPointStatus,
    EvidenceReference,
    MinorDataStatus,
    PersonalDataStatus,
    PolicyState,
    PreparationPolicyStateMachine,
    PreparationPrivacyEvaluator,
    PreparedStorageMetadata,
    PrivacyActivationNotAuthorizedError,
    PrivacyDecisionOutcome,
    PrivacyPreparationInput,
    ProtectedDataClassification,
    SpecialCategoryStatus,
    SubjectReferenceKind,
)

NOW = datetime(2026, 7, 28, 8, 0, tzinfo=UTC)


@st.composite
def _classifications(draw: st.DrawFn) -> ProtectedDataClassification:
    special = draw(st.sampled_from(list(SpecialCategoryStatus)))
    return ProtectedDataClassification(
        classification_id="class-1",
        classification_version=1,
        subject_artifact_digest="b" * 64,
        personal_data_status=draw(st.sampled_from(list(PersonalDataStatus))),
        special_category_status=special,
        article_10_status=draw(st.sampled_from(list(Article10Status))),
        minor_data_status=draw(st.sampled_from(list(MinorDataStatus))),
        article_9_category_codes=("health_data",)
        if special is SpecialCategoryStatus.ARTICLE_9
        else (),
        evidence_references=(
            EvidenceReference(
                evidence_id="evidence-1",
                evidence_version=1,
                evidence_digest="a" * 64,
                source_reference="review-package",
                valid_until=NOW + timedelta(days=30),
            ),
        ),
        contradiction_detected=draw(st.booleans()),
    )


def _metadata() -> PreparedStorageMetadata:
    evidence = EvidenceReference(
        evidence_id="evidence-1",
        evidence_version=1,
        evidence_digest="a" * 64,
        source_reference="review-package",
        valid_until=NOW + timedelta(days=30),
    )
    return PreparedStorageMetadata(
        schema_version="protected-storage-preparation-v1",
        data_object_type_id="observation",
        data_object_type_version=1,
        processing_activity_id="memory-intake",
        processing_activity_version=1,
        purpose_id="purpose-1",
        purpose_version=1,
        article_6_evidence_ref=evidence,
        additional_condition_evidence_ref=evidence,
        subject_category_id="data-subject-category-1",
        subject_category_version=1,
        subject_reference_kind=SubjectReferenceKind.SUBJECT,
        subject_reference_token="subject-token",
        source_id="source-1",
        source_version=1,
        source_digest="a" * 64,
        retention_rule_id="retention-1",
        retention_rule_version=1,
        technical_classification="restricted",
        privacy_data_class_id="class-1",
        privacy_data_class_version=1,
        protection_requirements_id="protection-1",
        protection_requirements_version=1,
        protection_requirements_digest="b" * 64,
        policy_id="policy-1",
        policy_version=1,
        policy_digest="b" * 64,
        approval_refs=(evidence,),
        evidence_refs=(evidence,),
        evidence_set_digest="a" * 64,
    )


@settings(max_examples=2_000, deadline=None)
@given(
    classification=_classifications(),
    state=st.sampled_from(list(PolicyState)),
    statuses=st.lists(st.sampled_from(list(DecisionPointStatus)), min_size=1, max_size=8).map(
        tuple
    ),
    evidence_complete=st.booleans(),
    conflict=st.booleans(),
)
def test_every_generated_preparation_result_is_non_authorizing(
    classification: ProtectedDataClassification,
    state: PolicyState,
    statuses: tuple[DecisionPointStatus, ...],
    evidence_complete: bool,
    conflict: bool,
) -> None:
    request = PrivacyPreparationInput(
        classification=classification,
        metadata=_metadata(),
        policy_state=state,
        decision_point_statuses=statuses,
        evidence_complete=evidence_complete,
        policy_conflict=conflict,
        policy_valid_until=NOW + timedelta(days=30),
    )

    decision = PreparationPrivacyEvaluator().evaluate(request, evaluated_at=NOW)

    assert decision.outcome is not PrivacyDecisionOutcome.ALLOW
    assert decision.runtime_enabled is False
    assert decision.mutation_authorized is False


@settings(max_examples=200, deadline=None)
@given(current_state=st.sampled_from(list(PolicyState)))
def test_no_generated_transition_can_enter_active(current_state: PolicyState) -> None:
    with pytest.raises(PrivacyActivationNotAuthorizedError):
        PreparationPolicyStateMachine().transition(
            current_state=current_state,
            target_state=PolicyState.ACTIVE,
            reason="generated-activation-attempt",
        )
