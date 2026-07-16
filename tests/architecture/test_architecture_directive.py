from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).parents[2]
CURRENT_DIRECTIVE = REPOSITORY_ROOT / "docs" / "architecture" / "architecture-directive-v4.0.md"
V3_DIRECTIVE = REPOSITORY_ROOT / "docs" / "architecture" / "architecture-directive-v3.0.md"
V2_DIRECTIVE = REPOSITORY_ROOT / "docs" / "architecture" / "architecture-directive-v2.0.md"
V1_DIRECTIVE = REPOSITORY_ROOT / "docs" / "architecture" / "architecture-directive-v1.1.md"


@pytest.fixture(scope="module")
def directive_text() -> str:
    return CURRENT_DIRECTIVE.read_text(encoding="utf-8")


def test_v4_directive_declares_complete_cognitive_system_target(directive_text: str) -> None:
    assert "# Neural Brain Architecture Directive v4.0" in directive_text
    assert "- Status: Normative complete cognitive-system target baseline" in directive_text
    assert "- Governing decision: ADR-018" in directive_text
    assert "integrated, protected\nperception-cognition-action-learning loop" in directive_text
    assert "The current implementation is an early Memory Core foundation" in directive_text


def test_earlier_directives_are_preserved_as_superseded_history() -> None:
    v3 = V3_DIRECTIVE.read_text(encoding="utf-8")
    v2 = V2_DIRECTIVE.read_text(encoding="utf-8")
    v1 = V1_DIRECTIVE.read_text(encoding="utf-8")
    assert "- Status: Superseded by Architecture Directive v4.0 and ADR-018" in v3
    assert "- Historical scope: protected Memory Core subsystem" in v3
    assert "- Status: Superseded by Architecture Directive v3.0" in v2
    assert "- Status: Superseded by Architecture Directives v2.0 and v3.0" in v1


@pytest.mark.parametrize(
    "required_section",
    [
        "## 2. Two-plane architecture",
        "## 3. Identity, scope, and authority",
        "## 4. Neural cognitive substrate",
        "## 5. Protected cognitive cycle",
        "## 6. Perception, attention, and workspace",
        "## 7. Memory Core",
        "## 8. World, self, and value models",
        "## 9. Goals, executive control, planning, and action selection",
        "## 10. Continual learning and model promotion",
        "## 11. Metacognition and corrigibility",
        "## 12. Delivery stages",
        "## 13. Evaluation and release evidence",
        "## 14. Global release stops",
        "## 15. Traceability and architecture change",
    ],
)
def test_v4_contains_required_complete_system_sections(
    directive_text: str, required_section: str
) -> None:
    assert required_section in directive_text


def test_v4_preserves_protected_two_plane_separation(directive_text: str) -> None:
    normalized = " ".join(directive_text.split())
    assert "The Cognitive Plane proposes and learns" in normalized
    assert "The Protected Control Plane decides whether protected state may change" in normalized
    assert "Cognitive capability does not create authority" in normalized
    assert "Neither component writes protected state or invokes tools directly" in normalized


def test_v4_defines_the_closed_cognitive_cycle(directive_text: str) -> None:
    rows = [
        "observation admission",
        "perceptual inference and binding",
        "attention competition",
        "workspace broadcast and working-memory update",
        "world/self/value belief update",
        "planning and action selection",
        "post-action observation",
        "prediction-error and metacognitive update",
    ]
    offsets = [directive_text.index(row) for row in rows]
    assert offsets == sorted(offsets)
    assert "Executor success is not goal success" in directive_text


def test_v4_preserves_memory_core_as_a_protected_subsystem(directive_text: str) -> None:
    normalized = " ".join(directive_text.split())
    assert "The Memory Transition Gate remains the sole writer" in normalized
    assert "Dreaming remains Area-local offline candidate production" in normalized
    assert "It cannot activate a candidate, mutate an active model, call a tool" in normalized


def test_v4_defines_ordered_full_system_delivery(directive_text: str) -> None:
    rows = [f"| NB-{number} " for number in range(9)]
    offsets = [directive_text.index(row) for row in rows]
    assert offsets == sorted(offsets)
    assert "The label `Neural Brain Candidate` is prohibited before NB-6" in directive_text
    assert "Production autonomy is a separate deployment approval" in directive_text


def test_v4_requires_guarded_continual_learning(directive_text: str) -> None:
    normalized = " ".join(directive_text.split())
    assert "The active runtime never mutates its own productive model in place" in normalized
    assert "independent approval for risky changes" in normalized
    assert "atomic activation and a tested rollback target" in normalized
    assert "never self-modifiable" in normalized


def test_v4_keeps_recognition_claims_bounded(directive_text: str) -> None:
    normalized = " ".join(directive_text.lower().split())
    for prohibited_claim in (
        "consciousness",
        "sentience",
        "subjective experience",
        "human equivalence",
        "neurophysiological fidelity",
    ):
        assert prohibited_claim in normalized
