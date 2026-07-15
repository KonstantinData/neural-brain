import json
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[2]
PATH = ROOT / "docs" / "architecture" / "contracts" / "ledger-invariants.json"


def _map(value: object) -> dict[str, object]:
    assert isinstance(value, dict)
    return value


def _list(value: object) -> list[object]:
    assert isinstance(value, list)
    return value


def _strings(value: object) -> list[str]:
    values = _list(value)
    assert all(isinstance(item, str) for item in values)
    return [item for item in values if isinstance(item, str)]


@pytest.fixture(scope="module")
def contract() -> dict[str, object]:
    with PATH.open(encoding="utf-8") as source:
        return _map(json.load(source))


def test_transition_record_has_complete_immutable_scope_and_causation(
    contract: dict[str, object],
) -> None:
    record = _map(contract["transition_record"])
    required = set(_strings(record["required_immutable_fields"]))
    assert {
        "tenant_id",
        "area_id",
        "project_id",
        "session_id",
        "goal_id",
        "aggregate_id",
        "contract_id",
        "contract_version",
        "transition_id",
        "transition_request_id",
        "source_state",
        "target_state",
        "expected_state_version",
        "new_state_version",
        "request_actor_principal_id",
        "writer_component_id",
        "correlation_id",
        "causation_id",
        "audit_event_type",
    } == required
    assert "transition gate database role" in str(record["writer_rule"])
    assert "one PostgreSQL transaction or all roll back" in str(record["atomicity"])
    assert "unique within immutable scope and aggregate" in str(record["replay_key"])
    assert "exactly one monotone new_state_version" in str(record["concurrency"])


def test_status_registries_are_closed_disjoint_and_nonempty(contract: dict[str, object]) -> None:
    registries = _map(contract["status_registries"])
    assert set(registries) == {
        "execution_attempt",
        "approval_claim",
        "budget_reservation",
        "resource_ownership_record",
        "recovery_work_item",
        "external_effect_disposition",
        "protected_transition_record",
        "startup_recovery_marker",
    }
    for registry in registries.values():
        statuses = _map(registry)
        blocking = _strings(statuses["blocking"])
        terminal = _strings(statuses["terminal"])
        assert blocking and terminal
        assert len(blocking) == len(set(blocking))
        assert len(terminal) == len(set(terminal))
        assert set(blocking).isdisjoint(terminal)


def test_ledger_invariant_registry_is_exact(contract: dict[str, object]) -> None:
    invariants = [_map(item) for item in _list(contract["invariants"])]
    assert {str(item["id"]): str(item["rule"]) for item in invariants} == {
        "LI-001": "budget_non_negative",
        "LI-002": "approval_single_consumption",
        "LI-003": "resource_conflict_exclusion",
        "LI-004": "unresolved_effect_holds_resources",
        "LI-005": "attempt_number_monotone",
        "LI-006": "persist_before_dispatch",
        "LI-007": "audit_failure_rolls_back",
        "LI-008": "reconciliation_before_ready",
        "LI-009": "unknown_status_fails_closed",
    }
    assertions = {str(item["rule"]): str(item["assertion"]) for item in invariants}
    assert "cannot produce a negative" in assertions["budget_non_negative"]
    assert "consumed exactly once" in assertions["approval_single_consumption"]
    assert (
        "remain held while an external effect is possible"
        in assertions["unresolved_effect_holds_resources"]
    )
    assert "durable before adapter invocation" in assertions["persist_before_dispatch"]
    assert "rolls back the protected transition" in assertions["audit_failure_rolls_back"]
    assert "remain not-ready" in assertions["reconciliation_before_ready"]
    assert "blocks quiescence" in assertions["unknown_status_fails_closed"]


def test_fencing_and_crash_rules_preserve_unknown_effects(contract: dict[str, object]) -> None:
    fencing = _map(contract["fencing"])
    assert "gates every new external effect" in str(fencing["stage_1_local_runtime_fence"])
    assert "stale executor fence" in str(fencing["recovery_context"])
    assert "Deferred to Stage 4" in str(fencing["stage_4_distributed_ownership_fence"])
    crash = str(contract["crash_rule"])
    assert "attempt record alone cannot prove" in crash
    assert "indeterminate effect" in crash
    assert "prohibits automatic retry" in crash


def test_unknown_ledger_state_is_always_blocking(contract: dict[str, object]) -> None:
    deny = _map(contract["default_deny"])
    assert deny == {
        "unknown_field_or_reference": "deny_and_audit",
        "unknown_status": "treat_as_blocking",
        "scope_mismatch": "deny_and_audit",
        "audit_failure": "rollback_and_deny",
    }
