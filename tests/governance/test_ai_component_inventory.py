from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INVENTORY = ROOT / "docs" / "governance" / "ai-component-inventory.md"


def load_inventory() -> str:
    return INVENTORY.read_text(encoding="utf-8")


def normalized_inventory() -> str:
    return " ".join(load_inventory().split())


def test_inventory_is_authoritative_full_system_and_fail_closed() -> None:
    inventory = normalized_inventory()

    assert "Authoritative repository inventory" in inventory
    assert "Cognitive Plane inventory" in inventory
    assert "Memory Core and Protected Control Plane inventory" in inventory
    assert "Models, datasets, adapters, integrations, data flow, and deployment" in inventory
    assert (
        "unknown component, version, provenance, evaluation state, owner, or risk control"
        in inventory
    )
    assert "denied for capability, deployment, or recognition claims" in inventory
    assert "The Memory Core is a protected subsystem, not the product boundary." in inventory


def test_inventory_has_every_required_architecture_and_asset_boundary() -> None:
    inventory = load_inventory()

    expected_records = {
        "CP-01",
        "CP-02",
        "CP-03",
        "CP-04",
        "CP-05",
        "CP-06",
        "CP-07",
        "CP-08",
        "CP-09",
        "MC-01",
        "MC-02",
        "MC-03",
        "PC-01",
        "PC-02",
        "PC-03",
        "PC-04",
        "PC-05",
        "PC-06",
        "PC-07",
        "AS-01",
        "AS-02",
        "AS-03",
        "AS-04",
        "AS-05",
        "AS-06",
        "AS-07",
    }
    assert all(f"| {record} |" in inventory for record in expected_records)
    assert (
        inventory.count(
            "| ID | Component and lifecycle | Current status | Owner and version/authority |"
        )
        == 2
    )
    assert "| ID | Asset or boundary | Current status | Owner and version/authority |" in inventory


def test_inventory_does_not_promote_target_or_ollama_to_current_capability() -> None:
    inventory = normalized_inventory()

    ollama_record = next(line for line in inventory.splitlines() if "| AS-03 |" in line)
    assert "target and **not deployed**" in ollama_record
    assert "no adapter implementation or approved model/deployment record exists" in ollama_record
    assert "local-only fail closed" in ollama_record
    assert (
        "Ollama may be recorded only as the future, local, non-public, untrusted inference boundary"
        in inventory
    )
    assert (
        "not a current adapter, model deployment, cloud fallback, or proof of neural cognition"
        in inventory
    )


def test_inventory_links_to_current_authority_and_real_repository_evidence() -> None:
    inventory = normalized_inventory()

    for authority in (
        "ADR-018",
        "Architecture Directive v4.0",
        "Neural Brain Recognition Standard",
        "recognition-gates.json",
        "system-boundary.json",
        "release-stops.json",
    ):
        assert authority in inventory

    for path in (
        "src/neural_brain/cognition/workspace.py",
        "src/neural_brain/memory/service.py",
        "src/neural_brain/security/floor.py",
        "migrations/0002_stage1_memory_kernel.sql",
        "tests/evaluation/test_nb1_safe_serial_cognition.py",
    ):
        assert (ROOT / path).is_file(), path
        assert f"`{path}`" in inventory


def test_governance_index_exposes_inventory_without_treating_it_as_authorization() -> None:
    index = (ROOT / "docs" / "governance" / "README.md").read_text(encoding="utf-8")

    assert "ai-component-inventory.md" in index
    assert "does not enable a capability" in index
    assert "approve a deployment" in index
    assert "establish Neural Brain recognition" in index
