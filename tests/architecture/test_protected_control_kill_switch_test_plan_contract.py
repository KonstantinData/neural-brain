"""Deterministic checks for the S1-02.5 preregistered evidence-plan draft."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
PLAN_PATH = (
    ROOT / "docs" / "architecture" / "contracts" / "protected-control-kill-switch-test-plan-v1.json"
)
DECISION_PATH = (
    ROOT / "docs" / "architecture" / "protected-control-kill-switch-scope-resolution-decision-v1.md"
)


def _plan() -> dict[str, object]:
    loaded: object = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def test_plan_is_non_authorizing_and_preregisters_case_evidence() -> None:
    plan = _plan()
    assert plan["status"] == "proposed_not_accepted_not_runtime_authorization"
    assert plan["task"] == "S1-02.5"
    assert plan["required_lineage"] == [
        "brain_id",
        "tenant_id",
        "area_id",
        "project_id",
        "session_id",
    ]
    boundary = plan["authority_boundary"]
    assert isinstance(boundary, dict)
    assert boundary["default_on_missing_evidence"] == "deny_or_stop_and_escalate"
    assert (
        boundary["stage_boundary"] == "NB-5 controlled sandbox and later; NB-1 remains effect-free"
    )
    exclusions = plan["explicit_exclusions"]
    assert isinstance(exclusions, list)
    assert "runtime implementation" in exclusions
    assert "test execution claim" in exclusions
    result_schema = plan["result_schema"]
    assert isinstance(result_schema, dict)
    assert result_schema["required_immutable_artifact_refs"] == [
        "contract_artifact_ref",
        "implementation_artifact_ref",
        "environment_artifact_ref",
        "fault_injection_artifact_ref",
        "ledger_artifact_ref",
    ]
    assert "Missing, mutable, unverifiable, or lineage-mismatched" in result_schema["binding_rule"]


def test_plan_covers_positive_negative_race_failure_and_recovery_paths() -> None:
    plan = _plan()
    cases = plan["cases"]
    assert isinstance(cases, list)
    assert all(isinstance(case, dict) for case in cases)
    rows = [case for case in cases if isinstance(case, dict)]
    assert {str(case["case_id"]) for case in rows} == {
        "KS-PT-001",
        "KS-PT-002",
        "KS-PT-003",
        "KS-PT-004",
        "KS-PT-005",
        "KS-NT-001",
        "KS-NT-002",
        "KS-RT-001",
        "KS-RT-002",
        "KS-FT-001",
        "KS-FT-002",
        "KS-FT-003",
        "KS-RC-001",
    }
    required = {
        "case_id",
        "category",
        "transition_or_interface",
        "preconditions",
        "trace_or_interleaving",
        "expected_state_oracle",
        "expected_audit_oracle",
        "expected_claim_oracle",
        "evidence_owner",
        "evidence_stage",
    }
    for case in rows:
        assert required <= set(case)
        assert case["preconditions"]
        assert case["trace_or_interleaving"]
    categories = {str(case["category"]) for case in rows}
    assert {
        "positive_transition",
        "negative_scope_authority",
        "negative_separation",
        "race_cas_idempotency",
        "race_revocation_in_flight",
        "crash_restart_audit_failure",
        "partition_stale_fence",
        "stale_checkpoint_crash_restart",
        "recovery_rollback",
    } <= categories
    coverage = plan["permitted_transition_coverage"]
    assert isinstance(coverage, list)
    assert all(isinstance(row, dict) for row in coverage)
    coverage_rows = [row for row in coverage if isinstance(row, dict)]
    assert {str(row["transition"]) for row in coverage_rows} == {
        "enabled->drain",
        "enabled->disabled",
        "drain->disabled",
        "drain->recovery",
        "disabled->recovery",
        "recovery->enabled",
        "recovery->disabled",
    }
    for row in coverage_rows:
        case_ids = row["coverage_case_ids"]
        assert isinstance(case_ids, list)
        assert set(case_ids) <= {str(case["case_id"]) for case in rows}
    by_transition = {str(row["transition"]): row for row in coverage_rows}
    by_case_id = {str(case["case_id"]): case for case in rows}
    for transition, row in by_transition.items():
        for case_id in row["coverage_case_ids"]:
            case = by_case_id[case_id]
            assert transition in str(case["transition_or_interface"])
    assert by_transition["recovery->disabled"]["coverage_mode"] == (
        "specified_automatic_failure_transition"
    )
    assert by_transition["enabled->disabled"]["coverage_case_ids"] == [
        "KS-PT-003",
        "KS-RT-001",
    ]
    drain_recovery = by_case_id["KS-PT-005"]
    assert drain_recovery["preconditions"] == [
        "authenticated complete lineage",
        "current drain revision",
        "drain quiescence",
        "no unresolved effect, fence, audit, credential, or scope ambiguity",
        "independently approved incident recovery",
    ]


def test_scope_resolution_matrix_remains_unaccepted_and_fail_closed() -> None:
    decision = DECISION_PATH.read_text(encoding="utf-8")
    assert "Status: Unaccepted decision preparation; not runtime authorization" in decision
    assert "It does not choose an option" in decision
    assert "Brain -> Tenant -> Area -> Project -> Session" in decision
    for decision_name in (
        "Control-scope granularity",
        "State ownership and persistence",
        "Credential-revocation binding",
        "Recovery authority and quorum",
        "Scope-wide effect containment",
        "Audit and lineage representation",
    ):
        assert decision_name in decision
    assert "Deny transitions and do not implement persistence or routing." in decision
    assert "Recovery never reaches enabled." in decision
