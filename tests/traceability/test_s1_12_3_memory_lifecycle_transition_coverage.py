"""Regression evidence for the bounded S1-12.3 Memory lifecycle inventory."""

import ast
from pathlib import Path

ROOT = Path(__file__).parents[2]
EVIDENCE = (
    ROOT / "docs" / "traceability" / "S1-12.3-memory-lifecycle-transition-coverage.md"
).read_text(encoding="utf-8")
SERVICE = (ROOT / "src" / "neural_brain" / "memory" / "service.py").read_text(encoding="utf-8")
DATABASE_TESTS = (ROOT / "tests" / "database" / "test_stage1_memory_kernel.py").read_text(
    encoding="utf-8"
)
UNIT_TESTS = (ROOT / "tests" / "unit" / "test_memory_service.py").read_text(encoding="utf-8")
HARNESS_TESTS = (ROOT / "tests" / "foundation" / "test_deterministic_memory_harness.py").read_text(
    encoding="utf-8"
)
ADAPTER_TESTS = (ROOT / "tests" / "database" / "test_postgres_memory_repository.py").read_text(
    encoding="utf-8"
)


def _service_method_names() -> set[str]:
    tree = ast.parse(SERVICE)
    memory_service = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.ClassDef) and node.name == "MemoryService"
    )
    return {
        node.name
        for node in memory_service.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def test_s1_12_3_keeps_one_current_memory_mutation_entrypoint() -> None:
    """No later lifecycle writer is hidden behind the MS-1 service surface."""

    methods = _service_method_names()
    assert "record_observation_and_checkpoint" in methods
    assert {"promote_candidate", "delete_or_anonymize", "quarantine", "rollback"}.isdisjoint(
        methods
    )
    assert "commit_memory_cycle" in SERVICE
    assert "_repository.commit_memory_cycle" in SERVICE
    assert "Memory Transition Gate" in EVIDENCE
    assert "only implemented protected mutation" in EVIDENCE


def test_s1_12_3_covers_current_gate_scope_audit_rollback_and_replay_boundaries() -> None:
    """The inventory names live and deterministic evidence for every current boundary."""

    for test_name in (
        "test_gate_commits_observation_working_context_checkpoint_and_audit_atomically",
        "test_runtime_role_cannot_mutate_protected_tables_directly",
        "test_checkpoint_readback_is_scope_and_session_checked",
        "test_stale_version_and_changed_replay_fail_without_partial_state",
        "test_concurrent_duplicate_request_cannot_double_commit",
        "test_audit_failure_rolls_back_the_complete_transition",
    ):
        assert test_name in DATABASE_TESTS
        assert test_name in EVIDENCE
    for test_name in (
        "test_untrusted_requests_reject_actor_and_scope_fields",
        "test_checkpoint_is_invisible_outside_authenticated_context",
        "test_atomic_failure_leaves_no_partial_cycle",
    ):
        assert test_name in UNIT_TESTS
        assert test_name in EVIDENCE
    for test_name in (
        "test_failpoint_leaves_no_partial_persistent_memory_or_audit_state",
        "test_persistent_fixture_is_scoped_idempotent_and_rejects_cross_scope_read",
        "test_scripted_untrusted_adapter_response_cannot_widen_authenticated_scope",
    ):
        assert test_name in HARNESS_TESTS
        assert test_name in EVIDENCE


def test_s1_12_3_keeps_dreaming_and_later_lifecycle_states_explicitly_unavailable() -> None:
    """A coverage inventory must not turn target operations into implemented behavior."""

    assert "Dreaming is unavailable" in SERVICE
    assert "Not enabled" in EVIDENCE
    for test_name in (
        "test_dreaming_is_unavailable_without_calling_repository_or_mutating_state",
        "test_postgres_repository_rejects_dreaming_before_opening_a_connection",
    ):
        assert test_name in UNIT_TESTS
        assert test_name in EVIDENCE
    assert "test_psycopg_adapter_rejects_dreaming_without_persisting_any_output" in ADAPTER_TESTS
    assert "N/A / not implemented" in EVIDENCE
    for operation in (
        "memory.propose_candidate",
        "memory.persist_episode_or_claim",
        "memory.retrieve",
        "memory.delete_or_anonymize",
        "memory.promote_candidate",
        "memory.activate_dreaming_successor",
        "memory.quarantine_or_rollback",
    ):
        assert operation in EVIDENCE
