import json
from pathlib import Path

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


def _contract() -> dict[str, object]:
    return _map(json.loads(PATH.read_text(encoding="utf-8")))


def test_transition_record_has_memory_scope_provenance_and_atomic_audit() -> None:
    record = _map(_contract()["transition_record"])
    required = set(_strings(record["required_immutable_fields"]))
    assert {"tenant_id", "area_id", "memory_record_id", "provenance_ref"} <= required
    assert {"goal_id", "action_intent_id", "execution_attempt_id"}.isdisjoint(required)
    assert "Memory Transition Gate" in str(record["writer_rule"])
    assert "one PostgreSQL transaction or all roll back" in str(record["atomicity"])


def test_memory_ledger_invariant_registry_is_exact() -> None:
    invariants = [_map(item) for item in _list(_contract()["invariants"])]
    assert {str(item["id"]): str(item["rule"]) for item in invariants} == {
        "MLI-001": "scope_immutable",
        "MLI-002": "provenance_preserved",
        "MLI-003": "gate_only_writer",
        "MLI-004": "audit_failure_rolls_back",
        "MLI-005": "inactive_candidates_not_retrievable",
        "MLI-006": "promotion_creates_version",
        "MLI-007": "freshness_visible",
        "MLI-008": "deletion_cascades",
        "MLI-009": "area_isolation",
        "MLI-010": "reconciliation_before_ready",
        "MLI-011": "unknown_state_fails_closed",
        "MLI-012": "catalog_lineage_typed",
        "MLI-013": "dreaming_cannot_activate_directly",
    }


def test_consumer_metadata_cannot_control_ledger() -> None:
    metadata = _map(_contract()["consumer_metadata"])
    assert metadata == {
        "storage": "optional opaque metadata",
        "authoritative": False,
        "foreign_key_to_consumer_domain": False,
        "may_affect_scope_or_actor": False,
    }


def test_unknown_state_and_failed_audit_fail_closed() -> None:
    deny = _map(_contract()["default_deny"])
    assert deny["unknown_lifecycle_state"] == "deny_and_audit"
    assert deny["unknown_freshness"] == "exclude_from_current_fact_and_require_reassessment"
    assert deny["scope_mismatch"] == "deny_and_audit"
    assert deny["provenance_missing_or_invalid"] == "deny_and_audit"
    assert deny["audit_failure"] == "rollback_and_deny"
    assert deny["reconciliation_incomplete"] == "not_ready"


def test_unknown_commit_outcome_requires_reconciliation() -> None:
    crash_rule = str(_contract()["crash_rule"])
    assert "authoritative memory ledger" in crash_rule
    assert "not blindly retried" in crash_rule
