import re
from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).parents[2]
THREAT_MODEL_PATH = REPOSITORY_ROOT / "docs" / "architecture" / "threat-model.md"

CATALOG_ROW = re.compile(r"^\| (?P<identifier>(?:A|ACT|TB|T|M|V)-\d{2}) \| (?P<body>.+) \|$")
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
    assert _ids(catalog_rows, "A-") == {f"A-{number:02d}" for number in range(1, 24)}
    assert _ids(catalog_rows, "ACT-") == {f"ACT-{number:02d}" for number in range(1, 16)}
    assert _ids(catalog_rows, "TB-") == {f"TB-{number:02d}" for number in range(1, 22)}
    assert _ids(catalog_rows, "T-") == {f"T-{number:02d}" for number in range(1, 36)}
    assert _ids(catalog_rows, "M-") == {f"M-{number:02d}" for number in range(1, 26)}
    assert _ids(catalog_rows, "V-") == {f"V-{number:02d}" for number in range(1, 26)}


def test_every_threat_has_asset_mitigation_and_verification_references(
    catalog_rows: dict[str, str],
) -> None:
    for threat_id in sorted(_ids(catalog_rows, "T-")):
        references = set(REFERENCE.findall(catalog_rows[threat_id]))
        assert any(reference.startswith("A-") for reference in references), threat_id
        assert any(reference.startswith("M-") for reference in references), threat_id
        assert any(reference.startswith("V-") for reference in references), threat_id
        assert references <= set(catalog_rows), f"{threat_id} has an unknown reference"


def test_complete_system_assets_are_explicit_and_security_bearing(
    catalog_rows: dict[str, str],
) -> None:
    required_asset_terms = {
        "A-17": ("perceptual streams", "attention decisions", "neural workspace"),
        "A-18": ("world model", "self model", "value model", "uncertainty"),
        "A-19": ("goal and action state", "committed intents", "quiescence"),
        "A-20": ("authority snapshots", "approvals", "budgets", "runtime fences"),
        "A-21": ("planner decisions", "executor receipts", "verifier decisions"),
        "A-22": ("learning traces", "evaluation definitions", "active pointers"),
        "A-23": ("safety supervisor", "shutdown channels", "safe-recovery"),
    }
    for asset_id, required_terms in required_asset_terms.items():
        body = catalog_rows[asset_id].lower()
        for term in required_terms:
            assert term in body, f"{asset_id} is missing complete-system term {term!r}"


def test_complete_system_threats_reference_complete_system_assets(
    catalog_rows: dict[str, str],
) -> None:
    complete_system_assets = {f"A-{number:02d}" for number in range(17, 24)}
    referenced_assets: set[str] = set()

    for number in range(26, 36):
        threat_id = f"T-{number:02d}"
        threat_assets = {
            reference
            for reference in REFERENCE.findall(catalog_rows[threat_id])
            if reference.startswith("A-")
        }
        assert threat_assets & complete_system_assets, (
            f"{threat_id} must reference a complete-system asset"
        )
        referenced_assets.update(threat_assets)

    assert complete_system_assets <= referenced_assets


def test_product_boundary_is_complete_system_with_protected_memory_core(
    threat_model_text: str,
) -> None:
    normalized = " ".join(threat_model_text.split())
    assert (
        "Neural Brain targets an integrated perception-cognition-action-learning loop."
        in normalized
    )
    assert (
        "It owns cognitive proposals, protected Goal and Action lifecycles, and governed "
        "Memory Core and model-promotion state."
    ) in normalized
    assert (
        "External effects remain technically separated behind authenticated authority, policy, "
        "approval where required, sandboxing, fencing, independent verification, shutdown, "
        "reconciliation, and atomic audit." in normalized
    )
    assert "Cognitive capability does not create authority." in normalized
    assert "The inherited Memory Core threat model covers" in normalized


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
        ("T-26", ("model-generated input", "direct observation", "world model")),
        ("T-27", ("attention", "safety evidence", "supervisor commands")),
        ("T-28", ("planner", "action gate", "executor")),
        ("T-29", ("value model", "reward hacking", "specification gaming")),
        ("T-30", ("world model error", "imagined rollouts", "uncertainty")),
        ("T-31", ("executor success", "independent observation", "verification")),
        ("T-32", ("online learning", "independent promotion", "rollback")),
        ("T-33", ("dreaming", "privacy-leaking", "hidden tests")),
        ("T-34", ("credential revocation", "shutdown", "approver")),
        ("T-35", ("deceives", "self-replicates", "unobserved")),
    ],
)
def test_required_threat_is_explicit(
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


def test_complete_system_actor_separation_is_explicit(
    catalog_rows: dict[str, str],
) -> None:
    required_actor_terms = {
        "ACT-09": ("perception", "attention", "neural workspace", "safety channels"),
        "ACT-10": ("world model", "self model", "value model", "no authority"),
        "ACT-11": ("goal gate", "action gate", "sole writer", "runtime fence"),
        "ACT-12": ("bounded executor", "sandbox", "neither effect certainty"),
        "ACT-13": ("independent verifier", "separate from planner and executor"),
        "ACT-14": ("learning", "independent promoter", "cannot activate"),
        "ACT-15": ("safety supervisor", "outside the cognitive", "fails closed"),
    }
    for actor_id, required_terms in required_actor_terms.items():
        body = catalog_rows[actor_id].lower()
        for term in required_terms:
            assert term in body, f"{actor_id} is missing separation term {term!r}"


def test_trust_boundaries_cover_complete_cognitive_control_loop(
    catalog_rows: dict[str, str],
) -> None:
    required_boundary_terms = {
        "TB-14": ("admitted observation", "modality", "generated content"),
        "TB-15": ("attention", "neural workspace", "non-suppressible safety"),
        "TB-16": ("world, self, and value models", "cannot establish objectives"),
        "TB-17": ("goal and action gates", "authority", "runtime fence"),
        "TB-18": ("committed action intent", "bounded executor", "idempotency"),
        "TB-19": ("independent verification", "indeterminate", "quiescence"),
        "TB-20": ("learning candidate", "evaluation", "active model pointer"),
        "TB-21": ("independent safety supervisor", "kill switch", "fails closed"),
    }
    for boundary_id, required_terms in required_boundary_terms.items():
        body = catalog_rows[boundary_id].lower()
        for term in required_terms:
            assert term in body, f"{boundary_id} is missing complete-system boundary term {term!r}"


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
        "planner, model, memory core component, or skill",
    ):
        assert term in normalized


def test_release_stops_cover_complete_cognitive_system_failures(
    threat_model_text: str,
) -> None:
    release_stops = threat_model_text.split("## Release Stops", maxsplit=1)[1].split(
        "## Severity Calibration", maxsplit=1
    )[0]
    normalized = " ".join(release_stops.split()).lower()
    for term in (
        "model-generated content can be represented as direct observation",
        "an external effect lacks committed intent",
        "indeterminate` effect can be blindly retried",
        "goal success can be inferred from tool success",
        "active brain can modify its productive model",
        "learning activation lacks immutable provenance",
        "shutdown, credential revocation, independent monitoring",
        "failed or unknown cognitive, recognition, evaluation",
    ):
        assert term in normalized


def test_tenant_root_scope_and_dreaming_are_explicitly_governed(
    threat_model_text: str,
) -> None:
    normalized = " ".join(threat_model_text.split())
    assert "ADR-016 hierarchy scope" in normalized
    assert "ADR-017 governed Dreaming" in normalized
    assert "descendant `area_id` on Tenant" in normalized


def test_model_is_a_required_control_baseline_not_implementation_claim(
    threat_model_text: str,
) -> None:
    normalized = " ".join(threat_model_text.split())
    assert "does not claim those controls are implemented" in normalized
    assert "authorize productive processing" in normalized
    assert "security certification" in normalized
    assert "Related decisions: ADR-015, ADR-016, ADR-017, and ADR-018" in normalized
    assert "Version: 4.0" in normalized
