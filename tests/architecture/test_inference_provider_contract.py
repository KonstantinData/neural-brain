import ast
import json
import tomllib
from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).parents[2]
CONTRACT_PATH = REPOSITORY_ROOT / "docs" / "architecture" / "contracts" / "inference-provider.json"

FORBIDDEN_RUNTIME_MODULES = {
    "anthropic",
    "cohere",
    "google.generativeai",
    "openai",
}
FORBIDDEN_DIRECT_DEPENDENCIES = {"anthropic", "cohere", "google-generativeai", "openai"}


def _mapping(value: object) -> dict[str, object]:
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
def inference_contract() -> dict[str, object]:
    loaded: object
    with CONTRACT_PATH.open(encoding="utf-8") as contract_file:
        loaded = json.load(contract_file)
    return _mapping(loaded)


def test_only_local_ollama_adapter_is_approved(
    inference_contract: dict[str, object],
) -> None:
    adapters = _list(inference_contract["approved_adapters"])
    assert len(adapters) == 1
    adapter = _mapping(adapters[0])
    assert adapter == {
        "adapter_id": "ollama_local",
        "provider": "ollama",
        "deployment_boundary": "local_non_public",
        "enabled_only_when_deployment_approval_is_complete": True,
    }


def test_deployment_binds_local_endpoint_and_exact_model_identity(
    inference_contract: dict[str, object],
) -> None:
    configuration = _mapping(inference_contract["deployment_configuration"])
    assert configuration["request_override"] == "denied"
    required_fields = _mapping(configuration["required_fields"])
    assert {
        "adapter_id",
        "endpoint",
        "model_id",
        "model_version",
        "model_digest",
        "request_timeout_ms",
        "inference_budget_ref",
        "logging_policy_ref",
    } <= set(required_fields)

    assert _mapping(required_fields["adapter_id"])["approved_value"] == "ollama_local"
    endpoint_constraints = " ".join(
        _strings(_mapping(required_fields["endpoint"])["constraints"])
    ).lower()
    assert "exact" in endpoint_constraints
    assert "local" in endpoint_constraints
    assert "non-public" in endpoint_constraints
    assert "not accepted from a request" in endpoint_constraints

    for field in ("model_id", "model_version", "model_digest"):
        model_field = _mapping(required_fields[field])
        assert model_field["required"] is True
        assert model_field["value_status"] == "deployment_bound_approval_required"
    assert _mapping(required_fields["model_digest"])["exact_match_required"] is True
    assert configuration["concrete_values_selected_by_this_contract"] is False


def test_readiness_requires_exact_identity_controls_and_no_external_provider(
    inference_contract: dict[str, object],
) -> None:
    readiness = _mapping(inference_contract["readiness_gate"])
    assert readiness["default"] == "not_ready"
    assert {
        "approved_adapter_identity_matches",
        "approved_local_endpoint_matches",
        "service_is_reachable",
        "model_id_matches",
        "model_version_matches",
        "model_digest_matches",
        "timeout_is_valid",
        "budget_enforcement_is_available",
        "payload_minimized_logging_is_active",
        "egress_controls_are_active",
        "external_provider_configuration_is_absent",
    } == set(_strings(readiness["all_required"]))
    assert {
        "process_alive",
        "port_open",
        "http_success",
        "model_name_or_tag_without_verified_digest",
    } == set(_strings(readiness["insufficient_evidence"]))


def test_inference_fails_closed_without_provider_or_model_fallback(
    inference_contract: dict[str, object],
) -> None:
    behavior = _mapping(inference_contract["failure_behavior"])
    assert behavior["default"] == "fail_closed"
    assert behavior["automatic_provider_switch"] == "denied"
    assert behavior["automatic_model_switch"] == "denied"
    assert behavior["automatic_cloud_fallback"] == "denied"
    assert behavior["api_key_fallback"] == "denied"
    assert {
        "service_unavailable",
        "unapproved_endpoint",
        "model_missing",
        "model_identity_missing",
        "model_identity_mismatch",
        "model_digest_unverifiable",
        "timeout_invalid_or_expired",
        "budget_missing_unverifiable_or_exhausted",
        "egress_control_unavailable",
        "logging_control_unavailable",
        "external_provider_or_fallback_configuration_present",
    } == set(_strings(behavior["conditions"]))
    assert "same approved local endpoint" in str(behavior["retry"])
    assert "exact model identity" in str(behavior["retry"])


def test_egress_credentials_and_provider_configuration_are_default_deny(
    inference_contract: dict[str, object],
) -> None:
    egress = _mapping(inference_contract["egress_control"])
    assert egress["default"] == "deny"
    assert egress["allowed_destination"] == "exact_approved_local_ollama_endpoint_only"
    assert egress["public_network_egress"] == "denied"
    assert egress["external_provider_egress"] == "denied"
    assert egress["control_failure"] == "fail_closed"

    credentials = _mapping(inference_contract["credential_boundary"])
    assert credentials["inference_api_key_required"] is False
    assert credentials["cloud_provider_credentials"] == "denied"
    assert credentials["provider_fallback_credentials"] == "configuration_error"

    configuration = _mapping(inference_contract["deployment_configuration"])
    forbidden = set(_strings(configuration["forbidden_fields_and_configuration"]))
    assert {
        "openai_api_key",
        "openai_base_url",
        "openai_model",
        "cloud_provider_credentials",
        "fallback_provider",
        "fallback_model",
        "automatic_cloud_fallback",
        "public_inference_endpoint",
    } <= forbidden


def test_request_context_cannot_cross_scope_or_reuse_inference_state(
    inference_contract: dict[str, object],
) -> None:
    controls = _mapping(inference_contract["request_controls"])
    assert controls["cross_area_context"] == "denied"
    assert controls["server_side_conversation_reuse"] == "denied"
    assert controls["prompt_assembly"] == "request_scoped"
    assert controls["cross_scope_batching"] == "denied"
    assert controls["cross_scope_prompt_or_response_cache"] == "denied"
    assert controls["raw_working_memory_cross_area"] == "denied"
    assert controls["secrets_and_credentials"] == "denied"


def test_logging_excludes_sensitive_payloads_by_default(
    inference_contract: dict[str, object],
) -> None:
    logging = _mapping(inference_contract["logging"])
    assert logging["mode"] == "payload_minimized"
    assert {"prompt_body", "response_body", "raw_working_memory", "raw_audit_payload"} <= set(
        _strings(logging["excluded_by_default"])
    )
    assert {"secrets", "credentials", "api_keys"} == set(_strings(logging["always_denied"]))


def test_future_provider_requires_architecture_and_security_changes(
    inference_contract: dict[str, object],
) -> None:
    future = _mapping(inference_contract["future_provider_rule"])
    assert future["configuration_only_enablement"] == "denied"
    assert {
        "separate_accepted_adr",
        "explicitly_approved_adapter",
        "updated_egress_policy",
        "threat_and_privacy_assessment",
        "updated_normative_contract",
        "automated_safety_and_acceptance_tests",
    } == set(_strings(future["required_before_support"]))


def test_repository_has_no_direct_external_model_provider_dependency() -> None:
    with (REPOSITORY_ROOT / "pyproject.toml").open("rb") as project_file:
        project = tomllib.load(project_file)
    dependencies = project["project"]["dependencies"]
    assert isinstance(dependencies, list)
    normalized = {
        str(dependency)
        .split("[", maxsplit=1)[0]
        .split("=", maxsplit=1)[0]
        .split(">", maxsplit=1)[0]
        .lower()
        for dependency in dependencies
    }
    assert normalized.isdisjoint(FORBIDDEN_DIRECT_DEPENDENCIES)


def test_runtime_python_has_no_external_model_provider_import() -> None:
    imported_modules: set[str] = set()
    for source_root in (REPOSITORY_ROOT / "src", REPOSITORY_ROOT / "tools"):
        for path in source_root.rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported_modules.update(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module is not None:
                    imported_modules.add(node.module)

    forbidden_imports = {
        imported
        for imported in imported_modules
        if any(
            imported == forbidden or imported.startswith(f"{forbidden}.")
            for forbidden in FORBIDDEN_RUNTIME_MODULES
        )
    }
    assert forbidden_imports == set()
