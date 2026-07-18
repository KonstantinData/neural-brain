from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
GOVERNANCE_DIR = ROOT / "docs" / "governance"
PROFILE_PATH = GOVERNANCE_DIR / "engineering-source-profile.json"


def load_profile() -> dict[str, Any]:
    value: object = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_engineering_source_profile_is_repo_scoped_and_not_runtime_scoped() -> None:
    profile = load_profile()

    assert profile["document_type"] == "engineering_source_profile"
    assert profile["repository"] == "KonstantinData/neural-brain"
    assert profile["governed_layer"] == "engineering_knowledge_base"
    assert "development_agents" in profile["applies_to"]
    assert "review_agents" in profile["applies_to"]
    assert "product_runtime" in profile["does_not_apply_to"]
    assert "runtime_rag" in profile["does_not_apply_to"]


def test_engineering_source_profile_has_no_product_runtime_effects() -> None:
    non_effects = load_profile()["runtime_non_effects"]

    assert non_effects
    assert all(value is False for value in non_effects.values())
    for denied_effect in (
        "creates_product_web_search",
        "creates_product_source_crawler",
        "creates_product_rag",
        "creates_product_knowledge_store",
        "allows_runtime_external_research",
        "allows_engineering_sources_to_be_ingested_into_product_memory",
        "automatically_changes_product_behavior",
        "automatically_changes_adrs",
    ):
        assert denied_effect in non_effects


def test_knowledge_layers_keep_repository_engineering_and_product_separate() -> None:
    layers = {layer["id"]: layer for layer in load_profile()["knowledge_layers"]}

    assert set(layers) == {
        "repository_evidence",
        "engineering_knowledge_base",
        "product_knowledge_and_data",
    }
    assert layers["repository_evidence"]["governed_by_this_profile"] is False
    assert layers["engineering_knowledge_base"]["governed_by_this_profile"] is True
    assert layers["product_knowledge_and_data"]["governed_by_this_profile"] is False
    assert layers["repository_evidence"]["authority"] == "durable_technical_source_of_truth"
    assert layers["engineering_knowledge_base"]["authority"] == "engineering_review_input"


def test_source_categories_cover_current_engineering_specialisms() -> None:
    profile = load_profile()
    categories = {category["id"]: category for category in profile["source_categories"]}

    expected_categories = {
        "repository_current_state",
        "language_and_runtime",
        "dependencies_and_frameworks",
        "security_and_privacy",
        "ci_cd_and_operations",
        "architecture_and_cognitive_evaluation",
    }
    assert set(categories) == expected_categories
    assert all(category["allowed_sources"] for category in categories.values())
    assert all(category["quality_rules"] for category in categories.values())

    for role, required_categories in profile["role_coverage"].items():
        assert required_categories, role
        assert set(required_categories) <= expected_categories
        assert "repository_current_state" in required_categories


def test_governance_docs_publish_the_boundary_and_profile() -> None:
    governance = (GOVERNANCE_DIR / "engineering-source-governance.md").read_text(encoding="utf-8")
    index = (GOVERNANCE_DIR / "README.md").read_text(encoding="utf-8")
    root_readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "Out of scope: Product runtime" in governance
    assert "product RAG system" in governance
    assert "engineering-source-profile.json" in governance
    assert "Engineering source governance" in index
    assert "Engineering source governance" in root_readme
