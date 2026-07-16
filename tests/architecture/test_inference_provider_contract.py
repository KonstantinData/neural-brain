import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
PATH = ROOT / "docs" / "architecture" / "contracts" / "inference-provider.json"


def _map(value: object) -> dict[str, object]:
    assert isinstance(value, dict)
    return value


def _strings(value: object) -> list[str]:
    assert isinstance(value, list)
    assert all(isinstance(item, str) for item in value)
    return [item for item in value if isinstance(item, str)]


def _contract() -> dict[str, object]:
    return _map(json.loads(PATH.read_text(encoding="utf-8")))


def test_inference_port_is_limited_to_memory_functions() -> None:
    port = _map(_contract()["internal_port"])
    assert port["id"] == "MemoryInferencePort"
    allowed = " ".join(_strings(port["allowed_functions"])).lower()
    assert "memory" in allowed or "retrieval" in allowed
    denied = set(_strings(port["non_functions"]))
    assert {
        "goal creation or lifecycle management",
        "planning",
        "tool or adapter execution",
        "external effects",
        "action-intent creation or lifecycle management",
        "direct protected memory mutation",
        "independent candidate promotion",
    } <= denied
    assert port["output_trust"] == "untrusted"


def test_only_local_ollama_adapter_is_approved() -> None:
    adapters = _contract()["approved_adapters"]
    assert isinstance(adapters, list)
    assert adapters == [
        {
            "adapter_id": "ollama_local",
            "provider": "ollama",
            "deployment_boundary": "local_non_public",
            "enabled_only_when_deployment_approval_is_complete": True,
        }
    ]


def test_inference_cannot_retrieve_write_or_promote_memory() -> None:
    boundary = _map(_contract()["memory_boundary"])
    assert boundary["adapter_initiated_retrieval"] == "denied"
    assert boundary["adapter_direct_memory_write"] == "denied"
    assert boundary["adapter_direct_candidate_promotion"] == "denied"
    assert boundary["model_output_may_define_scope_actor_or_governance"] is False
    assert boundary["ms_1_persistent_output"] == "inactive_non_retrievable_candidate_only"


def test_provider_failure_is_fail_closed_without_fallback() -> None:
    failure = _map(_contract()["failure_behavior"])
    assert failure["default"] == "fail_closed"
    assert failure["automatic_provider_switch"] == "denied"
    assert failure["automatic_model_switch"] == "denied"
    assert failure["automatic_cloud_fallback"] == "denied"
