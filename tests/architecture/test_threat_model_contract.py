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
    assert _ids(catalog_rows, "A-") == {f"A-{number:02d}" for number in range(1, 17)}
    assert _ids(catalog_rows, "TB-") == {f"TB-{number:02d}" for number in range(1, 13)}
    assert _ids(catalog_rows, "T-") == {f"T-{number:02d}" for number in range(1, 28)}
    assert _ids(catalog_rows, "M-") == {f"M-{number:02d}" for number in range(1, 17)}
    assert _ids(catalog_rows, "V-") == {f"V-{number:02d}" for number in range(1, 16)}


def test_every_threat_reference_resolves_to_a_catalog_entry(
    catalog_rows: dict[str, str],
) -> None:
    for threat_id in sorted(_ids(catalog_rows, "T-")):
        references = set(REFERENCE.findall(catalog_rows[threat_id]))
        asset_refs = {reference for reference in references if reference.startswith("A-")}
        mitigation_refs = {reference for reference in references if reference.startswith("M-")}
        verification_refs = {reference for reference in references if reference.startswith("V-")}
        assert asset_refs, f"{threat_id} has no protected asset reference"
        assert mitigation_refs, f"{threat_id} has no mitigation reference"
        assert verification_refs, f"{threat_id} has no verification reference"
        assert references <= set(catalog_rows), f"{threat_id} contains an unknown reference"


@pytest.mark.parametrize(
    ("threat_id", "required_terms"),
    [
        ("T-02", ("Prompt injection", "model", "policy")),
        ("T-05", ("tool", "forged scope", "false success")),
        ("T-13", ("maintenance tool", "protected tables", "audit event")),
        ("T-01", ("principal", "tenant_id", "another scope")),
        ("T-06", ("planner", "Action Gate", "protected state")),
        ("T-16", ("memory candidates", "cross scopes", "Stage 2")),
        ("T-20", ("integration message", "crosses scope", "repeated processing")),
        ("T-11", ("external call", "dispatches twice", "blind retry")),
        ("T-21", ("manipulates", "approver", "unsafe decision")),
        ("T-22", ("Automation bias", "independent evidence", "review")),
        ("T-18", ("sensitive data", "secrets", "telemetry")),
        ("T-19", ("deletion", "derived artifacts", "backups")),
    ],
)
def test_required_foundation_threat_category_is_explicit(
    catalog_rows: dict[str, str],
    threat_id: str,
    required_terms: tuple[str, ...],
) -> None:
    story = catalog_rows[threat_id].lower()
    for term in required_terms:
        assert term.lower() in story


def test_t27_covers_cross_scope_cache_batch_and_conversation_reuse(
    catalog_rows: dict[str, str],
) -> None:
    story = catalog_rows["T-27"].lower()
    for term in (
        "conversation reuse",
        "caching",
        "batching",
        "working memory",
        "tenant",
        "area",
        "project",
        "session",
        "goal",
    ):
        assert term in story
    references = set(REFERENCE.findall(catalog_rows["T-27"]))
    assert {"A-02", "A-09", "A-13", "A-14"} <= references
    assert {"M-01", "M-03", "M-08", "M-12"} <= references
    assert {"V-02", "V-08", "V-10"} <= references


def test_inference_threat_requires_local_ollama_and_no_cloud_fallback(
    catalog_rows: dict[str, str],
) -> None:
    inference_threat = catalog_rows["T-04"].lower()
    assert "openai" in inference_threat
    assert "cloud api" in inference_threat
    assert "public endpoint" in inference_threat
    assert "automatic fallback" in inference_threat
    assert {"M-03", "M-12", "V-08", "V-15"} <= set(REFERENCE.findall(catalog_rows["T-04"]))


def test_fnd04_boundary_defers_use_case_and_regulatory_determinations(
    threat_model_text: str,
) -> None:
    normalized = " ".join(threat_model_text.split())
    assert (
        "FND-04 MUST extend this model for each concrete deployment and intended use." in normalized
    )
    assert (
        "This Foundation model makes no legal applicability or regulatory-role determination."
        in normalized
    )
    assert (
        "productive tenants, areas, personal-data processing, and real mutating tools remain disabled"
        in normalized
    )
    assert "## FND-04 Extension Requirements" in threat_model_text
    assert "Missing or inconclusive applicability evidence is a denial condition" in normalized


def test_model_declares_contract_evidence_not_implemented_control(
    threat_model_text: str,
) -> None:
    normalized = " ".join(threat_model_text.split())
    assert "does not claim that the controls are already implemented" in normalized
    assert "does not authorize productive processing" in normalized
    assert "is not a security certification" in normalized


def test_release_stops_cover_unmitigated_high_risk_and_external_inference(
    threat_model_text: str,
) -> None:
    normalized = " ".join(threat_model_text.split())
    assert (
        "inference can reach an external provider, OpenAI, an unapproved model, or automatic fallback"
        in normalized
    )
    assert (
        "A critical or high threat in this model lacks an implemented mitigation and objective verification evidence"
        in normalized
    )
