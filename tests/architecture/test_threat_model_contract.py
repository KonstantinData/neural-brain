import re
from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).parents[2]
THREAT_MODEL_PATH = REPOSITORY_ROOT / "docs" / "architecture" / "threat-model.md"

CATALOG_ROW = re.compile(r"^\| (?P<identifier>(?:A|TB|T|M|V)-\d{2}) \| (?P<body>.+) \|$")
REFERENCE = re.compile(r"\b(?:A|TB|T|M|V)-\d{2}\b")


@pytest.fixture(scope="module")
def threat_model_text() -> str:
    return THREAT_MODEL_PATH.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def catalog_rows(threat_model_text: str) -> dict[str, str]:
    rows: dict[str, str] = {}
    for line in threat_model_text.splitlines():
        match = CATALOG_ROW.match(line)
        if match is None:
            continue
        identifier = match.group("identifier")
        assert identifier not in rows, f"duplicate catalog ID: {identifier}"
        rows[identifier] = match.group("body")
    return rows


def _ids(rows: dict[str, str], prefix: str) -> set[str]:
    return {identifier for identifier in rows if identifier.startswith(prefix)}


def test_catalog_identifiers_are_unique_and_complete(
    catalog_rows: dict[str, str],
) -> None:
    assert _ids(catalog_rows, "A-") == {f"A-{number:02d}" for number in range(1, 16)}
    assert _ids(catalog_rows, "TB-") == {f"TB-{number:02d}" for number in range(1, 13)}
    assert _ids(catalog_rows, "T-") == {f"T-{number:02d}" for number in range(1, 22)}
    assert _ids(catalog_rows, "M-") == {f"M-{number:02d}" for number in range(1, 16)}
    assert _ids(catalog_rows, "V-") == {f"V-{number:02d}" for number in range(1, 16)}


def test_every_threat_has_asset_mitigation_and_verification_references(
    catalog_rows: dict[str, str],
) -> None:
    for threat_id in sorted(_ids(catalog_rows, "T-")):
        references = set(REFERENCE.findall(catalog_rows[threat_id]))
        assert any(reference.startswith("A-") for reference in references), threat_id
        assert any(reference.startswith("M-") for reference in references), threat_id
        assert any(reference.startswith("V-") for reference in references), threat_id
        assert references <= set(catalog_rows), f"{threat_id} has an unknown reference"


def test_product_boundary_is_memory_only(threat_model_text: str) -> None:
    normalized = " ".join(threat_model_text.split())
    assert "Neural Brain is a memory system." in normalized
    assert (
        "It does not pursue goals, create plans, execute tools, dispatch actions, verify task "
        "completion, schedule agents, or operate autonomously."
    ) in normalized
    assert (
        "External consumers, local inference, retrieval, indexers, and background workers cannot mutate protected memory directly."
        in normalized
    )
    assert (
        "A memory result is context, not a command, approval, factual guarantee, plan, tool instruction, or proof of downstream task completion."
        in normalized
    )


@pytest.mark.parametrize(
    ("threat_id", "required_terms"),
    [
        ("T-01", ("tenant", "Area identifier", "scope")),
        ("T-02", ("prompt injection", "poisoning", "model output")),
        ("T-03", ("source metadata", "provenance", "transformations")),
        ("T-04", ("crosses Areas", "caching", "conversation reuse")),
        ("T-06", ("self-promotes", "candidate", "rollback")),
        ("T-08", ("stale evidence", "freshness", "consumer")),
        ("T-09", ("deletion", "embeddings", "backups")),
        ("T-10", ("Index", "PostgreSQL", "alternate truth")),
        ("T-12", ("OpenAI", "cloud API", "automatic fallback")),
        ("T-14", ("restore", "ready", "reconciled")),
        ("T-16", ("command", "plan", "task completion")),
    ],
)
def test_required_memory_threat_is_explicit(
    catalog_rows: dict[str, str],
    threat_id: str,
    required_terms: tuple[str, ...],
) -> None:
    story = catalog_rows[threat_id].lower()
    for term in required_terms:
        assert term.lower() in story


def test_trust_boundaries_cover_memory_service_components(
    catalog_rows: dict[str, str],
) -> None:
    boundary_text = " ".join(
        body for identifier, body in catalog_rows.items() if identifier.startswith("TB-")
    ).lower()
    for term in (
        "authenticated memory port",
        "source registry",
        "memory gate",
        "promotion authority",
        "retrieval result",
        "derived indexes",
        "local inference",
        "postgresql",
        "retention or deletion",
        "another area",
        "backup or restore",
    ):
        assert term in boundary_text


def test_release_stops_cover_memory_specific_failures(threat_model_text: str) -> None:
    release_stops = threat_model_text.split("## Release Stops", maxsplit=1)[1].split(
        "## Severity Calibration", maxsplit=1
    )[0]
    normalized = " ".join(release_stops.split()).lower()
    for term in (
        "cross-tenant or cross-area",
        "outside the memory gate",
        "candidate can become active",
        "openai",
        "correction, retention, legal hold, anonymization, or deletion",
        "index or cache",
        "startup or restore",
        "planner, goal owner, action dispatcher",
    ):
        assert term in normalized


def test_tenant_root_conflict_is_not_silently_resolved(threat_model_text: str) -> None:
    normalized = " ".join(threat_model_text.split())
    assert "remains a separate unresolved architecture question" in normalized
    assert "neither creates a sentinel Area nor introduces an exception" in normalized


def test_model_is_a_required_control_baseline_not_implementation_claim(
    threat_model_text: str,
) -> None:
    normalized = " ".join(threat_model_text.split())
    assert "does not claim those controls are implemented" in normalized
    assert "authorize productive processing" in normalized
    assert "security certification" in normalized
    assert "Baseline: ADR-015 memory-system boundary" in normalized
