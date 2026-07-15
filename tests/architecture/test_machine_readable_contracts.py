import json
from pathlib import Path
from typing import Any

import pytest

REPOSITORY_ROOT = Path(__file__).parents[2]
CONTRACT_DIRECTORY = REPOSITORY_ROOT / "docs" / "architecture" / "contracts"


def _load_contract(name: str) -> dict[str, Any]:
    with (CONTRACT_DIRECTORY / name).open(encoding="utf-8") as contract_file:
        loaded: object = json.load(contract_file)
    assert isinstance(loaded, dict)
    return loaded


@pytest.fixture(scope="module")
def envelopes() -> dict[str, Any]:
    return _load_contract("envelopes.json")


@pytest.fixture(scope="module")
def capabilities() -> dict[str, Any]:
    return _load_contract("stage-capabilities.json")


def test_persistent_envelope_header_requires_trusted_context(envelopes: dict[str, Any]) -> None:
    header = envelopes["$defs"]["PersistentEnvelopeHeader"]
    required = set(header["required"])
    assert {"scope", "actor", "trace", "governance", "provenance"} <= required
    assert header["x-direct-persistence"] == "forbidden"


def test_scope_context_requires_tenant_area_and_project_ancestry(
    envelopes: dict[str, Any],
) -> None:
    scope = envelopes["$defs"]["ScopeContext"]
    assert set(scope["required"]) == {"scope_level", "tenant_id", "area_id"}
    conditions = {
        item["if"]["properties"]["scope_level"]["const"]: item["then"] for item in scope["allOf"]
    }
    assert conditions["project"]["required"] == ["project_id"]
    assert conditions["session"]["required"] == ["project_id", "session_id"]
    assert conditions["goal"]["required"] == ["project_id", "session_id", "goal_id"]
    assert scope["x-trust-source"] == "authenticated_runtime_context"
    assert scope["x-immutable"] is True


def test_actor_and_trace_are_immutable_and_trusted(envelopes: dict[str, Any]) -> None:
    definitions = envelopes["$defs"]
    actor = definitions["ActorContext"]
    trace = definitions["TraceContext"]
    assert actor["x-trust-source"] == "authenticated_runtime_context"
    assert actor["x-immutable"] is True
    assert set(actor["required"]) == {
        "principal_id",
        "principal_kind",
        "runtime_component_id",
    }
    assert trace["x-trust-source"] == "trusted_ingress_or_transition_gate"
    assert trace["x-immutable"] is True
    assert set(trace["required"]) == {"correlation_id", "causation_id"}


def test_envelopes_close_unknown_fields_and_do_not_assert_achievement(
    envelopes: dict[str, Any],
) -> None:
    definitions = envelopes["$defs"]
    for name in ("EvidenceEnvelope", "ArtifactEnvelope"):
        assert definitions[name]["unevaluatedProperties"] is False
    evidence_text = json.dumps(definitions["EvidenceEnvelope"]).lower()
    assert "evidence does not contain an achieved" in evidence_text
    assert '"achieved"' not in evidence_text


def test_security_sensitive_format_choices_are_explicitly_deferred(
    envelopes: dict[str, Any],
) -> None:
    deferred = {
        decision["id"]: decision["status"] for decision in envelopes["x-deferred-decisions"]
    }
    assert deferred["identifier_encoding_and_generation"] == "deferred_requires_accepted_adr"
    assert deferred["digest_algorithm_and_value_encoding"] == (
        "deferred_requires_accepted_security_adr"
    )
    assert deferred["signatures_and_canonical_bytes"] == ("deferred_requires_accepted_security_adr")


def test_stage_capabilities_are_cumulative_and_complete(capabilities: dict[str, Any]) -> None:
    stages = capabilities["semantics"]["stage_order"]
    assert stages == ["stage_1", "stage_2", "stage_3", "stage_4"]
    assert capabilities["semantics"]["cumulative"] is True
    for capability in capabilities["capabilities"]:
        availability = capability["availability"]
        assert list(availability) == stages
        minimum_index = stages.index(capability["minimum_stage"])
        assert all(availability[stage] == "denied" for stage in stages[:minimum_index])
        assert all(availability[stage] == "allowed" for stage in stages[minimum_index:])


def test_stage_one_denies_every_later_capability(capabilities: dict[str, Any]) -> None:
    later_capabilities = [
        capability
        for capability in capabilities["capabilities"]
        if capability["minimum_stage"] != "stage_1"
    ]
    assert later_capabilities
    assert all(
        capability["availability"]["stage_1"] == "denied" for capability in later_capabilities
    )
    assert capabilities["request_enforcement"]["stage_1"]["rule"].startswith(
        "Every known Stage 2 through Stage 4"
    )
    assert capabilities["request_enforcement"]["unknown_operation"]["result"] == "denied"


def test_later_capability_denial_occurs_before_side_effects(
    capabilities: dict[str, Any],
) -> None:
    deny_before = set(capabilities["request_enforcement"]["known_operation"]["deny_before"])
    assert {
        "transition_gate_execution",
        "protected_state_mutation",
        "dispatch_journal_creation",
        "adapter_invocation",
        "external_effect",
        "later_stage_memory_read_or_write",
    } <= deny_before


def test_stage_boundaries_preserve_serial_dispatch_and_inactive_candidates(
    capabilities: dict[str, Any],
) -> None:
    indexed = {capability["id"]: capability for capability in capabilities["capabilities"]}
    assert indexed["runtime.generalized_distributed_outbox"]["minimum_stage"] == "stage_4"
    assert indexed["runtime.distributed_execution_ownership"]["minimum_stage"] == "stage_4"
    assert indexed["memory.controlled_learning"]["minimum_stage"] == "stage_3"
    assert capabilities["candidate_semantics"]["stage_1"]["active"] is False
    assert capabilities["candidate_semantics"]["stage_1"]["promotion"] == "denied"
    assert capabilities["candidate_semantics"]["stage_2"]["promotion"] == "denied"
