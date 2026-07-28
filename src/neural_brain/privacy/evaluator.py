"""Deterministic evaluator for non-authorizing privacy preparation."""

from datetime import datetime

from neural_brain.privacy.models import (
    Article10Status,
    DecisionPointStatus,
    MinorDataStatus,
    PersonalDataStatus,
    PolicyState,
    PrivacyDecisionOutcome,
    PrivacyPreparationDecision,
    PrivacyPreparationInput,
    ProtectedDataClassification,
    SpecialCategoryStatus,
    SubjectReferenceKind,
)


class PreparationPrivacyEvaluator:
    """Explain the blocking state while making ``ALLOW`` unreachable."""

    def evaluate(
        self, request: PrivacyPreparationInput, *, evaluated_at: datetime
    ) -> PrivacyPreparationDecision:
        """Return a deterministic non-authorizing result."""
        if evaluated_at.tzinfo is None or evaluated_at.utcoffset() is None:
            raise ValueError("evaluated_at must include a timezone offset")

        classification = request.classification
        if request.policy_conflict or classification.contradiction_detected:
            return self._decision(
                PrivacyDecisionOutcome.CONFLICT,
                "privacy_policy_or_classification_conflict",
            )

        if self._classification_conflicts(classification):
            return self._decision(
                PrivacyDecisionOutcome.CONFLICT,
                "privacy_classification_axes_conflict",
            )

        if self._contains_unknown(request):
            return self._decision(
                PrivacyDecisionOutcome.UNKNOWN,
                "privacy_classification_or_subject_reference_unknown",
            )

        if request.policy_state is PolicyState.REVOKED:
            return self._decision(PrivacyDecisionOutcome.REVOKED, "privacy_policy_revoked")

        metadata = request.metadata
        metadata_evidence = (
            metadata.article_6_evidence_ref,
            *(
                (metadata.additional_condition_evidence_ref,)
                if metadata.additional_condition_evidence_ref is not None
                else ()
            ),
            *metadata.approval_refs,
            *metadata.evidence_refs,
        )
        if (
            request.policy_state is PolicyState.EXPIRED
            or evaluated_at >= request.policy_valid_until
            or any(
                evaluated_at >= evidence.valid_until
                for evidence in classification.evidence_references
            )
            or any(evaluated_at >= evidence.valid_until for evidence in metadata_evidence)
        ):
            return self._decision(
                PrivacyDecisionOutcome.EXPIRED,
                "privacy_policy_or_evidence_expired",
            )

        statuses = set(request.decision_point_statuses)
        if DecisionPointStatus.REJECTED in statuses:
            return self._decision(PrivacyDecisionOutcome.DENY, "required_decision_rejected")

        additional_condition_required = (
            classification.special_category_status is SpecialCategoryStatus.ARTICLE_9
            or classification.article_10_status is Article10Status.ARTICLE_10
        )
        if (
            not request.evidence_complete
            or DecisionPointStatus.PENDING_OWNER in statuses
            or (
                additional_condition_required and metadata.additional_condition_evidence_ref is None
            )
        ):
            return self._decision(
                PrivacyDecisionOutcome.REQUIRE_ADDITIONAL_EVIDENCE,
                "required_evidence_or_owner_disposition_missing",
            )

        if statuses & {
            DecisionPointStatus.PENDING_PRIVACY_REVIEW,
            DecisionPointStatus.PENDING_LEGAL_REVIEW,
        }:
            return self._decision(
                PrivacyDecisionOutcome.REQUIRE_HUMAN_REVIEW,
                "qualified_privacy_or_legal_review_pending",
            )

        if DecisionPointStatus.OUT_OF_SCOPE in statuses:
            return self._decision(PrivacyDecisionOutcome.DENY, "required_decision_out_of_scope")

        return self._decision(
            PrivacyDecisionOutcome.DENY,
            "runtime_activation_not_authorized",
        )

    @staticmethod
    def _classification_conflicts(
        classification: ProtectedDataClassification,
    ) -> bool:
        non_personal = classification.personal_data_status in {
            PersonalDataStatus.NON_PERSONAL,
            PersonalDataStatus.ANONYMIZED_VERIFIED,
        }
        protected_axis_present = (
            classification.special_category_status is SpecialCategoryStatus.ARTICLE_9
            or classification.article_10_status is Article10Status.ARTICLE_10
            or classification.minor_data_status is MinorDataStatus.YES
        )
        return non_personal and protected_axis_present

    @staticmethod
    def _contains_unknown(request: PrivacyPreparationInput) -> bool:
        classification = request.classification
        return (
            classification.personal_data_status is PersonalDataStatus.UNKNOWN
            or classification.special_category_status is SpecialCategoryStatus.UNKNOWN
            or classification.article_10_status is Article10Status.UNKNOWN
            or classification.minor_data_status is MinorDataStatus.UNKNOWN
            or request.metadata.subject_reference_kind is SubjectReferenceKind.UNKNOWN
        )

    @staticmethod
    def _decision(outcome: PrivacyDecisionOutcome, reason_code: str) -> PrivacyPreparationDecision:
        return PrivacyPreparationDecision(
            outcome=outcome,
            reason_codes=(reason_code,),
        )
