"""Machine-checkable preparation evidence for S1-14.4 runtime enforcement."""

from __future__ import annotations

import copy
import importlib
import json
from pathlib import Path
from typing import Protocol

import pytest

from neural_brain.privacy import (
    PolicyState,
    PreparationPolicyStateMachine,
    PreparedStorageMetadata,
)

ROOT = Path(__file__).parents[2]
CONTRACTS = ROOT / "docs" / "architecture" / "contracts"
DIGEST = "a" * 64
NOW = "2026-07-28T12:00:00Z"
LATER = "2026-08-28T12:00:00Z"

_jsonschema = importlib.import_module("jsonschema")
_validator_class = _jsonschema.Draft202012Validator
_format_checker = _jsonschema.FormatChecker
_validation_error = importlib.import_module("jsonschema.exceptions").ValidationError
assert isinstance(_validation_error, type) and issubclass(_validation_error, Exception)
VALIDATION_ERROR: type[Exception] = _validation_error


class _Validator(Protocol):
    def validate(self, instance: object) -> None: ...


def _document(name: str) -> dict[str, object]:
    loaded: object = json.loads((CONTRACTS / name).read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _validator(name: str) -> _Validator:
    schema = _document(name)
    _validator_class.check_schema(schema)
    validator: _Validator = _validator_class(schema, format_checker=_format_checker())
    return validator


def _ref(reference_id: str) -> dict[str, object]:
    return {"reference_id": reference_id, "reference_version": 1}


def _digested_ref(reference_id: str) -> dict[str, object]:
    return {**_ref(reference_id), "reference_digest": DIGEST}


def _evidence(evidence_id: str) -> dict[str, object]:
    return {
        "record_contract": "privacy-evidence-record-v1",
        "evidence_id": evidence_id,
        "evidence_version": 1,
        "evidence_digest": DIGEST,
    }


def _classification() -> dict[str, object]:
    return {
        "contract_version": "protected-data-classification-v1",
        "classification_schema_version": "1.0.0",
        "classification_id": "class.special.health",
        "classification_version": 1,
        "subject_kind": "observation",
        "subject_digest": DIGEST,
        "scope": {"tenant_id": "tenant-1", "area_id": "area-1", "project_id": "project-1"},
        "personal_data_status": "PSEUDONYMIZED_PERSONAL",
        "special_category_status": "ARTICLE_9",
        "article_9_category_ids": ["health_data"],
        "article_10_status": "NOT_APPLICABLE",
        "minor_data_status": "NO",
        "classification_evidence_refs": [_evidence("classification-evidence-1")],
        "source_and_provenance_refs": [_evidence("classification-source-1")],
        "automated_classifier": {"status": "not_used"},
        "qualified_reviewer_binding": _digested_ref("privacy-review-1"),
        "reviewed_at": NOW,
        "contradiction_status": "none",
        "evidence_manifest_digest": DIGEST,
        "classification_digest": DIGEST,
        "valid_from": NOW,
        "valid_until": LATER,
        "recorded_at": NOW,
    }


def _resolution(family: str, code: str) -> dict[str, object]:
    return {
        "requirement_family": family,
        "requirement_code": code,
        "resolution": "candidate_evidence",
        "evidence_refs": [_evidence(f"evidence-{code}")],
    }


def _approval(role: str) -> dict[str, object]:
    return {
        "record_contract": "privacy-approval-record-v1",
        "review_role": role,
        "reviewer_id": f"reviewer-{role}",
        "approval_id": f"approval-{role}",
        "approval_digest": DIGEST,
        "approved_at": NOW,
        "valid_until": LATER,
    }


def _privacy_evidence_record() -> dict[str, object]:
    return {
        "contract_version": "privacy-evidence-record-v1",
        "evidence_schema_version": "1.0.0",
        "evidence_id": "evidence-1",
        "evidence_version": 1,
        "evidence_digest": DIGEST,
        "evidence_type": "qualified-review-evidence",
        "source_reference": _digested_ref("source-1"),
        "source_provenance_refs": [_digested_ref("provenance-1")],
        "source_date": NOW,
        "retrieved_or_verified_at": NOW,
        "scope": {"tenant_id": "tenant-1", "area_id": "area-1", "project_id": "project-1"},
        "purpose": _digested_ref("purpose-1"),
        "processing_activity": _digested_ref("activity-1"),
        "jurisdiction_binding": _digested_ref("jurisdiction-1"),
        "reviewer_treatment": "qualified_accepted",
        "contradiction_status": "none",
        "valid_from": NOW,
        "valid_until": LATER,
        "reassessment_trigger_refs": [_digested_ref("reassessment-1")],
        "retention_and_deletion_class": _digested_ref("retention-deletion-1"),
        "canonical_record_digest": DIGEST,
    }


def _privacy_approval_record() -> dict[str, object]:
    return {
        "contract_version": "privacy-approval-record-v1",
        "approval_schema_version": "1.0.0",
        "approval_id": "approval-independent_reviewer",
        "approval_type": "independent_reviewer",
        "approval_digest": DIGEST,
        "policy_digest": DIGEST,
        "evidence_manifest_digest": DIGEST,
        "actor_id": "reviewer-independent_reviewer",
        "authority_snapshot_digest": DIGEST,
        "qualified_role_binding": _digested_ref("qualified-role-1"),
        "scope": {"tenant_id": "tenant-1", "area_id": "area-1", "project_id": "project-1"},
        "decision_status": "DECIDED",
        "rationale_and_constraint_refs": [_digested_ref("rationale-1")],
        "approved_at": NOW,
        "valid_until": LATER,
        "revalidation_trigger_refs": [_digested_ref("revalidation-1")],
        "independence_evidence_ref": _digested_ref("independence-1"),
    }


def _policy() -> dict[str, object]:
    return {
        "contract_version": "special-category-processing-policy-v1",
        "policy_schema_version": "1.0.0",
        "policy_id": "policy-1",
        "policy_version": 1,
        "predecessor_policy_digest": None,
        "policy_digest": DIGEST,
        "policy_author_id": "policy-author-1",
        "created_at": NOW,
        "initial_state": "DRAFT",
        "scope": {"tenant_id": "tenant-1", "area_id": "area-1", "project_id": "project-1"},
        "deployment": {"deployment_id": "deployment-1", "environment_id": "test"},
        "supported_system_ids": ["neural-brain-memory-core"],
        "controller_role_evidence_ref": _evidence("controller-role-1"),
        "processor_role_evidence_refs": [_evidence("processor-role-1")],
        "session_scope_rule": _digested_ref("session-scope-rule-1"),
        "jurisdiction_profile": _ref("jurisdiction-profile-1"),
        "jurisdiction_ids": ["jurisdiction-1"],
        "artifact": _digested_ref("artifact-1"),
        "purpose": _digested_ref("purpose-1"),
        "processing_activity": _digested_ref("activity-1"),
        "supported_operation_ids": ["memory.observe"],
        "excluded_operation_ids": ["memory.direct-write"],
        "supported_classification_predicates": [_digested_ref("classification-predicate-1")],
        "data_classification": _digested_ref("class.special.health"),
        "general_basis_evidence_binding": _digested_ref("article-6-binding-1"),
        "additional_condition_evidence_binding": _digested_ref("article-9-binding-1"),
        "article_10_disposition_binding": _digested_ref("article-10-disposition-1"),
        "consent_and_withdrawal_binding": _digested_ref("consent-withdrawal-1"),
        "safeguard_manifest_binding": _digested_ref("safeguard-manifest-1"),
        "minimization_rule_binding": _digested_ref("minimization-rule-1"),
        "access_rule_binding": _digested_ref("access-rule-1"),
        "rights_process_binding": _digested_ref("rights-process-1"),
        "rule_set": _digested_ref("rule-set-1"),
        "retention_policy": _digested_ref("retention-1"),
        "deletion_and_derivative_rule_binding": _digested_ref("deletion-rule-1"),
        "legal_hold_rule_binding": _digested_ref("legal-hold-rule-1"),
        "recipient_processor_location_bindings": [_digested_ref("recipient-location-1")],
        "transfer_rule_binding": _digested_ref("transfer-rule-1"),
        "incident_and_reassessment_bindings": [_digested_ref("incident-rule-1")],
        "protection_profile": _digested_ref("protection-1"),
        "accountable_owner_id": "owner-1",
        "requirement_resolutions": [
            _resolution("article_6_basis", "article-6-reviewed-basis"),
            _resolution("article_9_condition", "article-9-reviewed-condition"),
            _resolution("retention", "retention-current"),
            _resolution("safeguard", "safeguards-current"),
        ],
        "approval_evidence_refs": [
            _approval("accountable_owner"),
            _approval("privacy_reviewer"),
            _approval("legal_reviewer"),
            _approval("independent_reviewer"),
        ],
        "valid_from": NOW,
        "valid_until": LATER,
        "next_review_at": LATER,
        "unsupported_cases": ["unknown-or-unapproved-processing"],
        "evidence_manifest_digest": DIGEST,
        "approval_manifest_digest": DIGEST,
        "recorded_at": NOW,
    }


def _decision(outcome: str = "DENY") -> dict[str, object]:
    return {
        "contract_version": "special-category-decision-record-v1",
        "decision_schema_version": "1.0.0",
        "decision_id": "decision-1",
        "decision_digest": DIGEST,
        "transition_request_id": "request-1",
        "actor": {"principal_id": "principal-1", "runtime_component_id": "component-1"},
        "scope": {
            "tenant_id": "tenant-1",
            "area_id": "area-1",
            "project_id": "project-1",
            "session_id": "session-1",
        },
        "operation_id": "memory.observe",
        "protected_record_reference": {
            "record_kind": "observation",
            "record_id": "observation-1",
            "record_digest": DIGEST,
        },
        "subject_kind": "data-subject-reference",
        "subject_digest": DIGEST,
        "data_classification": _digested_ref("class.special.health"),
        "purpose": _digested_ref("purpose-1"),
        "processing_activity": _digested_ref("activity-1"),
        "general_basis_evidence_digest": DIGEST,
        "additional_condition_binding": {
            "disposition": "evidence",
            "binding_digest": DIGEST,
        },
        "safeguard_and_retention_manifest_digest": DIGEST,
        "processing_policy": _digested_ref("policy-1"),
        "policy_activation_event_id": "policy-activation-1",
        "rule_set": _digested_ref("rule-set-1"),
        "database_identity_generation": 1,
        "authority_snapshot_digest": DIGEST,
        "approval_set_digest": DIGEST,
        "approval_manifest_digest": DIGEST,
        "evidence_set_digest": DIGEST,
        "input_parameter_digest": DIGEST,
        "policy_state": "DRAFT",
        "outcome": outcome,
        "reason_codes": ["runtime-disabled"],
        "obligations": ["preserve-decision-evidence"],
        "required_review_roles": [
            "accountable_owner",
            "privacy_reviewer",
            "legal_reviewer",
            "independent_reviewer",
        ],
        "non_compensatory_gates_passed": False,
        "evaluator": {
            "component_id": "privacy-evaluator",
            "code_version": "preparation-v1",
            "model_version": "not-applicable",
        },
        "decided_at": NOW,
        "valid_until": LATER,
        "reusable": False,
        "downstream_action": "block",
        "mutation_and_audit_correlation": {
            "transaction_correlation_id": "transaction-1",
            "decision_event_id": "decision-event-1",
            "audit_event_id": "audit-event-1",
            "mutation_id": None,
        },
    }


def test_preparation_contract_cannot_claim_runtime_allow_authority() -> None:
    contract = _document("special-category-data-runtime-enforcement-v1.json")
    machine = _document("special-category-policy-state-machine-v1.json")
    assert contract["status"] == "proposed_non_authorizing_preparation"
    assert machine["status"] == "proposed_non_authorizing_preparation"
    boundary = contract["preparation_boundary"]
    assert isinstance(boundary, dict)
    assert boundary["runtime_enabled"] is False
    assert boundary["allow_authorized"] is False
    assert boundary["executable_migration_present"] is False
    assert contract["authorization_rule"] == (
        "Only ALLOW may be consumed by a protected mutation, but this preparation version "
        "cannot produce or authorize ALLOW because runtime_enabled and allow_authorized are false."
    )


def test_governing_adrs_are_current_and_historical_inputs_stay_separate() -> None:
    contract = _document("special-category-data-runtime-enforcement-v1.json")
    authority: object = json.loads(
        (ROOT / "docs" / "adr" / "adr-authority.json").read_text(encoding="utf-8")
    )
    assert isinstance(authority, dict)
    raw_records = authority["records"]
    assert isinstance(raw_records, list)
    records: dict[str, dict[str, object]] = {}
    for raw_record in raw_records:
        assert isinstance(raw_record, dict)
        record_id = raw_record.get("id")
        assert isinstance(record_id, str)
        records[record_id] = raw_record

    governing = contract["governing_decisions"]
    assert isinstance(governing, list)
    for decision_id in governing:
        assert isinstance(decision_id, str)
        assert records[decision_id]["authority"] in {"current", "retained_subsystem"}

    assert contract["historical_inputs_requiring_revalidation"] == ["ADR-004"]
    assert records["ADR-004"]["authority"] == "historical"


@pytest.mark.parametrize(
    "name",
    [
        "protected-data-classification-v1.schema.json",
        "privacy-evidence-record-v1.schema.json",
        "privacy-approval-record-v1.schema.json",
        "special-category-processing-policy-v1.schema.json",
        "special-category-decision-record-v1.schema.json",
    ],
)
def test_runtime_preparation_schemas_are_valid_draft_2020_12(name: str) -> None:
    schema = _document(name)
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    _validator_class.check_schema(schema)
    assert schema["additionalProperties"] is False


@pytest.mark.parametrize(
    "name",
    ["privacy-evidence-record-v1.schema.json", "privacy-approval-record-v1.schema.json"],
)
def test_resolved_governance_records_are_explicitly_non_authorizing(name: str) -> None:
    schema = _document(name)
    boundary = schema["x-neural-brain-preparation-boundary"]
    assert isinstance(boundary, dict)
    assert boundary["runtime_enabled"] is False
    assert boundary["allow_authorized"] is False
    assert boundary["composition_required"] is True


@pytest.mark.parametrize(
    "missing",
    [
        "source_provenance_refs",
        "scope",
        "purpose",
        "processing_activity",
        "jurisdiction_binding",
        "reviewer_treatment",
        "contradiction_status",
        "reassessment_trigger_refs",
        "retention_and_deletion_class",
        "canonical_record_digest",
    ],
)
def test_resolved_evidence_record_requires_complete_governance_metadata(missing: str) -> None:
    record = _privacy_evidence_record()
    del record[missing]
    with pytest.raises(VALIDATION_ERROR):
        _validator("privacy-evidence-record-v1.schema.json").validate(record)


@pytest.mark.parametrize(
    "missing",
    [
        "policy_digest",
        "evidence_manifest_digest",
        "actor_id",
        "authority_snapshot_digest",
        "qualified_role_binding",
        "scope",
        "decision_status",
        "rationale_and_constraint_refs",
        "revalidation_trigger_refs",
        "independence_evidence_ref",
    ],
)
def test_resolved_approval_record_requires_authority_scope_and_independence(
    missing: str,
) -> None:
    record = _privacy_approval_record()
    del record[missing]
    with pytest.raises(VALIDATION_ERROR):
        _validator("privacy-approval-record-v1.schema.json").validate(record)


def test_resolved_reference_bindings_match_policy_scope_and_digests() -> None:
    policy = _policy()
    evidence_record = _privacy_evidence_record()
    approval_record = _privacy_approval_record()
    evidence_ref = _evidence("evidence-1")
    approval_ref = _approval("independent_reviewer")

    assert evidence_ref["record_contract"] == evidence_record["contract_version"]
    assert evidence_ref["evidence_id"] == evidence_record["evidence_id"]
    assert evidence_ref["evidence_version"] == evidence_record["evidence_version"]
    assert evidence_ref["evidence_digest"] == evidence_record["evidence_digest"]
    assert evidence_record["scope"] == policy["scope"]
    assert approval_ref["record_contract"] == approval_record["contract_version"]
    assert approval_ref["approval_id"] == approval_record["approval_id"]
    assert approval_ref["approval_digest"] == approval_record["approval_digest"]
    assert approval_record["scope"] == policy["scope"]
    assert approval_record["policy_digest"] == policy["policy_digest"]
    assert approval_record["evidence_manifest_digest"] == policy["evidence_manifest_digest"]

    wrong_scope = copy.deepcopy(evidence_record)
    wrong_scope["scope"] = {
        "tenant_id": "tenant-other",
        "area_id": "area-1",
        "project_id": "project-1",
    }
    assert wrong_scope["scope"] != policy["scope"]

    wrong_digest = copy.deepcopy(approval_record)
    wrong_digest["approval_digest"] = "not-a-digest"
    with pytest.raises(VALIDATION_ERROR):
        _validator("privacy-approval-record-v1.schema.json").validate(wrong_digest)


def test_classification_represents_unknown_but_rejects_inconsistent_non_personal_values() -> None:
    validator = _validator("protected-data-classification-v1.schema.json")
    validator.validate(_classification())

    unknown = copy.deepcopy(_classification())
    unknown.update(
        personal_data_status="UNKNOWN",
        special_category_status="UNKNOWN",
        article_9_category_ids=[],
        article_10_status="UNKNOWN",
        minor_data_status="UNKNOWN",
        contradiction_status="unknown",
    )
    validator.validate(unknown)

    inconsistent = copy.deepcopy(_classification())
    inconsistent.update(
        personal_data_status="NON_PERSONAL",
        special_category_status="ARTICLE_9",
        article_9_category_ids=["health_data"],
    )
    with pytest.raises(VALIDATION_ERROR):
        validator.validate(inconsistent)


@pytest.mark.parametrize(
    "missing",
    [
        "subject_digest",
        "article_9_category_ids",
        "source_and_provenance_refs",
        "qualified_reviewer_binding",
        "contradiction_status",
        "evidence_manifest_digest",
        "classification_digest",
    ],
)
def test_classification_requires_review_provenance_and_digest_bindings(missing: str) -> None:
    document = _classification()
    del document[missing]
    with pytest.raises(VALIDATION_ERROR):
        _validator("protected-data-classification-v1.schema.json").validate(document)


def test_special_category_policy_requires_basis_condition_retention_safeguard_and_reviews() -> None:
    validator = _validator("special-category-processing-policy-v1.schema.json")
    validator.validate(_policy())

    no_article_9 = copy.deepcopy(_policy())
    resolutions = no_article_9["requirement_resolutions"]
    assert isinstance(resolutions, list)
    no_article_9["requirement_resolutions"] = [
        item for item in resolutions if item["requirement_family"] != "article_9_condition"
    ]
    with pytest.raises(VALIDATION_ERROR):
        validator.validate(no_article_9)

    incomplete_reviews = copy.deepcopy(_policy())
    incomplete_reviews["approval_evidence_refs"] = [_approval("accountable_owner")]
    with pytest.raises(VALIDATION_ERROR):
        validator.validate(incomplete_reviews)

    no_legal_review = copy.deepcopy(_policy())
    approvals = no_legal_review["approval_evidence_refs"]
    assert isinstance(approvals, list)
    no_legal_review["approval_evidence_refs"] = [
        item for item in approvals if item["review_role"] != "legal_reviewer"
    ]
    with pytest.raises(VALIDATION_ERROR):
        validator.validate(no_legal_review)


@pytest.mark.parametrize(
    "missing",
    [
        "controller_role_evidence_ref",
        "session_scope_rule",
        "supported_operation_ids",
        "rights_process_binding",
        "deletion_and_derivative_rule_binding",
        "legal_hold_rule_binding",
        "recipient_processor_location_bindings",
        "transfer_rule_binding",
        "incident_and_reassessment_bindings",
        "unsupported_cases",
        "evidence_manifest_digest",
        "approval_manifest_digest",
    ],
)
def test_policy_requires_complete_operational_governance_bindings(missing: str) -> None:
    document = _policy()
    del document[missing]
    with pytest.raises(VALIDATION_ERROR):
        _validator("special-category-processing-policy-v1.schema.json").validate(document)


def test_policy_resolution_xor_rejects_both_evidence_branches() -> None:
    validator = _validator("special-category-processing-policy-v1.schema.json")
    incoherent = copy.deepcopy(_policy())
    resolutions = incoherent["requirement_resolutions"]
    assert isinstance(resolutions, list)
    first = resolutions[0]
    assert isinstance(first, dict)
    first["qualified_not_applicable"] = {
        "reviewer_id": "reviewer-1",
        "reviewed_at": NOW,
        "rationale_evidence_refs": [_evidence("rationale-1")],
        "next_review_at": LATER,
    }
    with pytest.raises(VALIDATION_ERROR):
        validator.validate(incoherent)


def test_article_6_only_policy_accepts_one_qualified_article_9_not_applicable() -> None:
    validator = _validator("special-category-processing-policy-v1.schema.json")
    article_6_only = copy.deepcopy(_policy())
    resolutions = article_6_only["requirement_resolutions"]
    assert isinstance(resolutions, list)
    resolutions[:] = [
        item for item in resolutions if item["requirement_family"] != "article_9_condition"
    ]
    resolutions.append(
        {
            "requirement_family": "article_9_condition",
            "requirement_code": "article-9-not-applicable",
            "resolution": "qualified_not_applicable",
            "qualified_not_applicable": {
                "reviewer_id": "reviewer-1",
                "reviewed_at": NOW,
                "rationale_evidence_refs": [_evidence("article-9-na-rationale")],
                "next_review_at": LATER,
            },
        }
    )
    validator.validate(article_6_only)


def test_policy_rejects_distinct_conflicting_family_entries_and_retention_na() -> None:
    validator = _validator("special-category-processing-policy-v1.schema.json")

    conflicting_article_9 = copy.deepcopy(_policy())
    article_9_resolutions = conflicting_article_9["requirement_resolutions"]
    assert isinstance(article_9_resolutions, list)
    article_9_resolutions.append(
        {
            "requirement_family": "article_9_condition",
            "requirement_code": "article-9-not-applicable",
            "resolution": "qualified_not_applicable",
            "qualified_not_applicable": {
                "reviewer_id": "reviewer-1",
                "reviewed_at": NOW,
                "rationale_evidence_refs": [_evidence("rationale-1")],
                "next_review_at": LATER,
            },
        }
    )
    with pytest.raises(VALIDATION_ERROR):
        validator.validate(conflicting_article_9)

    retention_not_applicable = copy.deepcopy(_policy())
    retention_resolutions = retention_not_applicable["requirement_resolutions"]
    assert isinstance(retention_resolutions, list)
    retention_resolutions[:] = [
        item for item in retention_resolutions if item["requirement_family"] != "retention"
    ]
    retention_resolutions.append(
        {
            "requirement_family": "retention",
            "requirement_code": "retention-not-applicable",
            "resolution": "qualified_not_applicable",
            "qualified_not_applicable": {
                "reviewer_id": "reviewer-1",
                "reviewed_at": NOW,
                "rationale_evidence_refs": [_evidence("rationale-2")],
                "next_review_at": LATER,
            },
        }
    )
    with pytest.raises(VALIDATION_ERROR):
        validator.validate(retention_not_applicable)


def test_state_machine_has_no_terminal_reactivation_path() -> None:
    machine = _document("special-category-policy-state-machine-v1.json")
    assert machine["runtime_enabled"] is False
    terminal_states = machine["terminal_states"]
    assert isinstance(terminal_states, list)
    terminal = {str(item) for item in terminal_states}
    transitions = machine["transitions"]
    assert isinstance(transitions, list)
    assert not any(item["from"] in terminal for item in transitions)
    assert not any(item["from"] == "REVOKED" and item["to"] == "ACTIVE" for item in transitions)
    assert machine["unknown_transition_outcome"] == "DENY"


def test_python_preparation_graph_exactly_matches_machine_contract() -> None:
    contract = _document("special-category-policy-state-machine-v1.json")
    raw_transitions = contract["transitions"]
    assert isinstance(raw_transitions, list)
    expected = {state: set[PolicyState]() for state in PolicyState}
    for raw_transition in raw_transitions:
        assert isinstance(raw_transition, dict)
        from_state = raw_transition.get("from")
        to_state = raw_transition.get("to")
        assert isinstance(from_state, str)
        assert isinstance(to_state, str)
        expected[PolicyState(from_state)].add(PolicyState(to_state))

    helper = PreparationPolicyStateMachine()
    actual = {state: set(helper.allowed_targets(state)) for state in PolicyState}
    assert actual == expected


def test_python_prepared_metadata_matches_documented_preflight_field_set() -> None:
    assert set(PreparedStorageMetadata.model_fields) == {
        "schema_version",
        "data_object_type_id",
        "data_object_type_version",
        "processing_activity_id",
        "processing_activity_version",
        "purpose_id",
        "purpose_version",
        "article_6_evidence_ref",
        "additional_condition_evidence_ref",
        "subject_category_id",
        "subject_category_version",
        "subject_reference_kind",
        "subject_reference_token",
        "source_id",
        "source_version",
        "source_digest",
        "retention_rule_id",
        "retention_rule_version",
        "technical_classification",
        "privacy_data_class_id",
        "privacy_data_class_version",
        "protection_requirements_id",
        "protection_requirements_version",
        "protection_requirements_digest",
        "policy_id",
        "policy_version",
        "policy_digest",
        "approval_refs",
        "evidence_refs",
        "evidence_set_digest",
    }


def test_decision_schema_marks_target_shape_allow_as_non_authorizing() -> None:
    validator = _validator("special-category-decision-record-v1.schema.json")
    schema = _document("special-category-decision-record-v1.schema.json")
    boundary = schema["x-neural-brain-preparation-boundary"]
    assert isinstance(boundary, dict)
    assert boundary == {
        "runtime_enabled": False,
        "allow_authorized": False,
        "composition_required": True,
        "statement": (
            "This schema validates a future decision-record shape only. Structural ALLOW "
            "validity is not authority and may not be consumed without the separately accepted "
            "and active runtime composition."
        ),
    }
    validator.validate(_decision())

    invalid_deny = _decision()
    invalid_deny["downstream_action"] = "protected_mutation"
    with pytest.raises(VALIDATION_ERROR):
        validator.validate(invalid_deny)

    future_allow = _decision("ALLOW")
    future_allow.update(
        policy_state="ACTIVE",
        non_compensatory_gates_passed=True,
        downstream_action="protected_mutation",
        reason_codes=["all-gates-passed"],
    )
    correlation = future_allow["mutation_and_audit_correlation"]
    assert isinstance(correlation, dict)
    correlation["mutation_id"] = "mutation-1"
    validator.validate(future_allow)

    incomplete_allow = copy.deepcopy(future_allow)
    incomplete_allow["non_compensatory_gates_passed"] = False
    with pytest.raises(VALIDATION_ERROR):
        validator.validate(incomplete_allow)


@pytest.mark.parametrize(
    "missing",
    [
        "general_basis_evidence_digest",
        "additional_condition_binding",
        "subject_digest",
        "safeguard_and_retention_manifest_digest",
        "policy_activation_event_id",
        "input_parameter_digest",
        "database_identity_generation",
        "obligations",
        "required_review_roles",
        "mutation_and_audit_correlation",
    ],
)
def test_decision_requires_complete_input_review_and_audit_bindings(missing: str) -> None:
    document = _decision()
    del document[missing]
    with pytest.raises(VALIDATION_ERROR):
        _validator("special-category-decision-record-v1.schema.json").validate(document)


def test_decision_rejects_non_digest_subject_binding() -> None:
    document = _decision()
    document["subject_digest"] = "subject-reference-1"
    with pytest.raises(VALIDATION_ERROR):
        _validator("special-category-decision-record-v1.schema.json").validate(document)
