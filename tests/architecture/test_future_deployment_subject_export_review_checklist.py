"""Evidence for the category-only future subject-export review checklist."""

from pathlib import Path

ROOT = Path(__file__).parents[2]
CHECKLIST_PATH = (
    ROOT / "docs" / "governance" / "future-deployment-subject-export-review-checklist-v1.md"
)


def test_review_checklist_is_category_only_and_fail_closed() -> None:
    checklist = CHECKLIST_PATH.read_text(encoding="utf-8")
    required_terms = {
        "snapshots",
        "all eleven matrix rows",
        "retention, archive, backup, and recovery",
        "lifecycle-specific evidence",
        "qualified independent privacy reviewer",
        "scope-bound qualified-review disposition",
        "never infer an allow outcome",
    }
    assert all(term in checklist for term in required_terms)
    prohibited = {
        "no data inventory",
        "discovery",
        "access",
        "processing",
        "export",
        "runtime capability",
        "authority",
        "approval",
        "release outcome",
    }
    assert all(term in checklist for term in prohibited)
