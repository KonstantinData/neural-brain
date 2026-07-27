"""Deterministic evidence for the non-authorizing S1-02.5 contract draft."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
CONTRACT_PATH = (
    ROOT / "docs" / "architecture" / "contracts" / "protected-control-kill-switch-v1.json"
)
GOVERNANCE_PATH = ROOT / "docs" / "governance" / "protected-control-kill-switch-v1.md"
RUNBOOK_PATH = ROOT / "docs" / "runbooks" / "protected-control-kill-switch.md"
TRACEABILITY_PATH = ROOT / "docs" / "traceability" / "S1-02.5-protected-control-kill-switch.md"


def _contract() -> dict[str, object]:
    loaded: object = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _strings(value: object) -> set[str]:
    assert isinstance(value, list)
    assert all(isinstance(item, str) for item in value)
    return set(value)


def test_kill_switch_is_a_non_authorizing_adr_018_prerequisite() -> None:
    contract = _contract()
    assert contract["contract_id"] == "neural-brain.protected-control-kill-switch"
    assert contract["status"] == "proposed_not_accepted_not_runtime_authorization"
    assert contract["governing_decisions"] == ["ADR-018", "ADR-019", "ADR-005"]
    assert contract["historical_input_requiring_revalidation"] == ["ADR-006"]
    assert "runtime component" in _strings(contract["explicit_exclusions"])
    assert "database schema or migration" in _strings(contract["explicit_exclusions"])


def test_state_machine_is_fail_closed_and_does_not_restore_enabled_implicitly() -> None:
    machine = _contract()["state_machine"]
    assert isinstance(machine, dict)
    assert machine["states"] == ["enabled", "drain", "disabled", "recovery"]
    assert machine["safe_default"] == "disabled"
    forbidden = _strings(machine["forbidden_transitions"])
    assert "enabled directly from disabled" in forbidden
    assert "any Brain-initiated enable or recovery" in forbidden
    assert "implicit restart restoration to enabled" in forbidden
    transitions = machine["permitted_transitions"]
    assert isinstance(transitions, list)
    assert all(isinstance(transition, dict) for transition in transitions)
    transition_rows = [transition for transition in transitions if isinstance(transition, dict)]
    assert {(str(row["from"]), str(row["to"])) for row in transition_rows} == {
        ("enabled", "drain"),
        ("enabled", "disabled"),
        ("drain", "disabled"),
        ("drain", "recovery"),
        ("disabled", "recovery"),
        ("recovery", "enabled"),
        ("recovery", "disabled"),
    }
    guards = " ".join(str(row["guard"]) for row in transition_rows)
    for required_guard in (
        "atomic audit",
        "fail closed",
        "no unresolved effect, fence, audit, credential, or scope ambiguity",
        "credential revocation/rotation evidence",
        "all release stops resolved",
        "automatic fail-closed transition",
    ):
        assert required_guard in guards


def test_authenticated_scope_and_separation_of_duties_are_required() -> None:
    contract = _contract()
    boundary = contract["authority_boundary"]
    assert isinstance(boundary, dict)
    assert (
        boundary["trusted_context_source"]
        == "authenticated_protected_control_plane_runtime_context"
    )
    assert boundary["default_on_unknown"] == "deny_or_stop_and_escalate"
    assert _strings(contract["immutable_scope"]) == {
        "brain_id",
        "tenant_id",
        "area_id",
        "project_id",
        "session_id",
        "operation_class",
        "control_scope_id",
    }
    lineage = contract["immutable_scope_lineage"]
    assert isinstance(lineage, dict)
    assert lineage["hierarchy"] == [
        "brain_id",
        "tenant_id",
        "area_id",
        "project_id",
        "session_id",
    ]
    assert lineage["source"] == "authenticated_protected_control_plane_runtime_context"
    assert lineage["default_on_unknown_or_mismatch"] == "deny_or_stop_and_escalate"
    assert "cannot establish, alter, infer, or repair lineage" in lineage["exclusion"]
    roles = contract["roles_and_separation_of_duties"]
    assert isinstance(roles, list)
    assert all(isinstance(role, dict) for role in roles)
    by_role = {str(role["role"]): role for role in roles if isinstance(role, dict)}
    assert set(by_role) == {
        "kill_operator",
        "independent_safety_supervisor",
        "credential_revoker",
        "incident_commander",
        "recovery_approver",
        "independent_reviewer",
    }
    assert "approve own recovery" in _strings(by_role["kill_operator"]["may_not"])
    assert "be controlled by Brain runtime" in _strings(
        by_role["independent_safety_supervisor"]["may_not"]
    )
    assert "enable operation" in _strings(by_role["credential_revoker"]["may_not"])
    assert "unilaterally re-enable" in _strings(by_role["incident_commander"]["may_not"])
    assert any(
        "sole verifier" in item for item in _strings(by_role["recovery_approver"]["may_not"])
    )
    assert any(
        "waive a Security Floor rule" in item
        for item in _strings(by_role["independent_reviewer"]["may_not"])
    )


def test_concurrency_failure_and_recovery_evidence_is_preregistered() -> None:
    contract = _contract()
    persisted = contract["future_persisted_evidence"]
    assert isinstance(persisted, dict)
    assert _strings(persisted["required_fields"]) == {
        "control_scope_id",
        "immutable_scope",
        "brain_id",
        "tenant_id",
        "area_id",
        "project_id",
        "session_id",
        "scope_lineage_hash",
        "state",
        "revision",
        "issued_at",
        "expires_at",
        "transition_id",
        "causation_id",
        "actor_identity",
        "actor_role",
        "authority_snapshot_ref",
        "policy_decision_ref",
        "approval_refs",
        "credential_revision_refs",
        "fence_refs",
        "reason_code",
        "audit_hash",
        "previous_audit_hash",
    }
    assert {
        "monotonic revision",
        "compare-and-swap precondition",
        "lineage binding checked against authenticated runtime context before persistence and every future enforcement boundary",
    } <= _strings(persisted["integrity"])
    failure_behavior = _strings(contract["enforcement_and_failure_behavior"])
    assert len(failure_behavior) == 7
    assert any("network partition" in item for item in failure_behavior)
    assert any("blindly retried" in item for item in failure_behavior)
    assert any("Every future Action and Goal admission" in item for item in failure_behavior)
    assert any("Credential revocation is scope-bound" in item for item in failure_behavior)
    assert any("On restart there is no implicit enabled state" in item for item in failure_behavior)
    assert any("Rollback means transition to disabled" in item for item in failure_behavior)
    tests = _strings(contract["required_future_test_evidence"])
    assert any("concurrency race" in item for item in tests)
    assert any("restart" in item for item in tests)
    assert any("credential revocation" in item for item in tests)
    interfaces = contract["gate_interfaces"]
    assert isinstance(interfaces, dict)
    assert set(interfaces) == {
        "action_transition_gate",
        "goal_transition_gate",
        "executor_and_sandbox",
        "audit_and_reconciliation",
        "security_floor",
    }
    assert "precommit, commit, dispatch" in interfaces["action_transition_gate"]
    assert "indeterminate effects" in interfaces["goal_transition_gate"]
    assert "before every effect boundary" in interfaces["executor_and_sandbox"]
    assert "Audit failure blocks admission" in interfaces["audit_and_reconciliation"]
    assert "may override a Security Floor prohibition" in interfaces["security_floor"]
    assert _strings(contract["explicit_exclusions"]) == {
        "runtime component",
        "database schema or migration",
        "protected-state writer",
        "credential revocation implementation",
        "executor or dispatch integration",
        "network control",
        "automatic recovery",
        "deployment or release authorization",
        "claim that a kill switch is implemented, safe, or effective",
    }
    blocker = contract["implementation_blocker"]
    assert isinstance(blocker, dict)
    assert blocker["decision_owner"] == "Neural Brain architecture decision owner"
    assert blocker["contract_owner"] == "Protected Control Plane architecture owner"
    assert _strings(blocker["required_approvals"]) == {
        "accepted ADR decision",
        "independent security and safety review",
        "qualified operational recovery ownership",
    }


def test_governance_runbook_and_traceability_preserve_the_blocker() -> None:
    governance = GOVERNANCE_PATH.read_text(encoding="utf-8")
    runbook = RUNBOOK_PATH.read_text(encoding="utf-8")
    traceability = TRACEABILITY_PATH.read_text(encoding="utf-8")
    assert "Proposed prerequisite; not accepted and not runtime authorization" in governance
    assert "unaccepted ADR-018 revalidation proposal must live" in governance
    assert "Do not use this document to operate an environment" in runbook
    assert "does not authorize runtime" in traceability
    assert "not prove a kill switch works" in traceability
    assert "runtime-dependent successor remains" in traceability
    assert "blocked." in traceability
