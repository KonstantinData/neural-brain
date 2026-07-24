"""Validate the ADR inventory, index, and decision-record files."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Final

ROOT: Final = Path(__file__).resolve().parents[1]
ADR_DIRECTORY: Final = ROOT / "docs" / "adr"
AUTHORITY_FILE: Final = ADR_DIRECTORY / "adr-authority.json"
INDEX_FILE: Final = ADR_DIRECTORY / "README.md"
STATUS_FILE: Final = ADR_DIRECTORY / "STATUS.md"
ADR_REFERENCE_PATTERN: Final = re.compile(r"\bADR-[0-9]{3}\b")
VALID_AUTHORITIES: Final = {"current", "retained_subsystem", "historical"}
REQUIRED_SECTIONS: Final = ("## Context", "## Decision", "## Consequences")


class AdrValidationError(Exception):
    """Raised when the ADR structure is internally inconsistent."""


def _load_inventory() -> list[dict[str, Any]]:
    payload = json.loads(AUTHORITY_FILE.read_text(encoding="utf-8"))
    records = payload.get("records")
    if not isinstance(records, list):
        raise AdrValidationError("adr-authority.json must contain a records list")
    return records


def _adr_files() -> list[Path]:
    return sorted(path for path in ADR_DIRECTORY.glob("ADR-*.md") if path.is_file())


def _line_value(text: str, key: str) -> str:
    prefix = f"- {key}: "
    for line in text.splitlines():
        if line.startswith(prefix):
            return line.removeprefix(prefix)
    raise AdrValidationError(f"missing metadata field: {key}")


def _list_value(values: list[str]) -> str:
    if not values:
        return "none"
    return ", ".join(values)


def _assert_known_references(record: dict[str, Any], known_ids: set[str]) -> None:
    for field in ("supersedes", "superseded_by", "amends", "amended_by"):
        references = record.get(field)
        if not isinstance(references, list):
            raise AdrValidationError(f"{record['id']} field {field} must be a list")
        unknown = sorted(reference for reference in references if reference not in known_ids)
        if unknown:
            raise AdrValidationError(f"{record['id']} field {field} has unknown ADRs: {unknown}")


def _assert_reciprocal_links(records: list[dict[str, Any]]) -> None:
    by_id = {record["id"]: record for record in records}
    for record in records:
        record_id = record["id"]
        for superseded_id in record["supersedes"]:
            target = by_id[superseded_id]
            if record_id not in target["superseded_by"]:
                raise AdrValidationError(
                    f"{record_id} supersedes {superseded_id}, but {superseded_id} does "
                    f"not list {record_id} in superseded_by"
                )
        for amended_id in record["amends"]:
            target = by_id[amended_id]
            if record_id not in target["amended_by"]:
                raise AdrValidationError(
                    f"{record_id} amends {amended_id}, but {amended_id} does not list "
                    f"{record_id} in amended_by"
                )


def _validate_inventory(records: list[dict[str, Any]], files: list[Path]) -> None:
    file_names = [path.name for path in files]
    record_files = [record.get("file") for record in records]
    if record_files != file_names:
        raise AdrValidationError("adr-authority.json records must match sorted ADR files")

    expected_ids = [f"ADR-{number:03d}" for number in range(1, len(files) + 1)]
    record_ids = [record.get("id") for record in records]
    if record_ids != expected_ids:
        raise AdrValidationError("ADR IDs must form a continuous sequence")

    known_ids = set(expected_ids)
    for record in records:
        if record.get("authority") not in VALID_AUTHORITIES:
            raise AdrValidationError(
                f"{record['id']} has invalid authority {record.get('authority')}"
            )
        if not isinstance(record.get("stage_scope"), list):
            raise AdrValidationError(f"{record['id']} stage_scope must be a list")
        _assert_known_references(record, known_ids)
    _assert_reciprocal_links(records)


def _validate_adr_file(record: dict[str, Any], known_ids: set[str]) -> None:
    path = ADR_DIRECTORY / record["file"]
    text = path.read_text(encoding="utf-8")
    adr_id = record["id"]

    if not text.startswith(f"# {adr_id}: {record['title']}"):
        raise AdrValidationError(f"{record['file']} heading does not match inventory")
    if _line_value(text, "Status") != record["status"]:
        raise AdrValidationError(f"{adr_id} status does not match inventory")
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", _line_value(text, "Date")):
        raise AdrValidationError(f"{adr_id} date must use YYYY-MM-DD")
    if _line_value(text, "Authority") != record["authority"]:
        raise AdrValidationError(f"{adr_id} authority does not match inventory")
    if _line_value(text, "Theme") != record["theme"]:
        raise AdrValidationError(f"{adr_id} theme does not match inventory")
    if _line_value(text, "Applies to stages") != _list_value(record["stage_scope"]):
        raise AdrValidationError(f"{adr_id} stage scope does not match inventory")
    for field, label in (
        ("supersedes", "Supersedes"),
        ("superseded_by", "Superseded by"),
        ("amends", "Amends"),
        ("amended_by", "Amended by"),
    ):
        if _line_value(text, label) != _list_value(record[field]):
            raise AdrValidationError(f"{adr_id} {label} does not match inventory")
    if "https://app.notion.com/p/" not in text:
        raise AdrValidationError(f"{adr_id} must link to its Notion decision record")
    for section in REQUIRED_SECTIONS:
        if section not in text:
            raise AdrValidationError(f"{adr_id} is missing {section}")

    references = set(ADR_REFERENCE_PATTERN.findall(text))
    unknown = sorted(reference for reference in references if reference not in known_ids)
    if unknown:
        raise AdrValidationError(f"{adr_id} references unknown ADRs: {unknown}")


def _validate_index(records: list[dict[str, Any]]) -> None:
    index = INDEX_FILE.read_text(encoding="utf-8")
    required_phrases = (
        "## Current Authority",
        "## Authority States",
        "## Thematic Map",
        "## Supersession Matrix",
        "## Decision Records",
        "ADR-018 governs the complete cognitive-system boundary",
        "continuous decision sequence from ADR-001 through\nADR-018",
    )
    for phrase in required_phrases:
        if phrase not in index:
            raise AdrValidationError(f"ADR index is missing required phrase: {phrase}")
    for record in records:
        expected_link = f"[{record['id']}]({record['file']})"
        if expected_link not in index:
            raise AdrValidationError(f"ADR index is missing {expected_link}")
    if "python tools/validate_adrs.py" not in index:
        raise AdrValidationError("ADR index must document the validator command")


def _validate_status(records: list[dict[str, Any]]) -> None:
    status = STATUS_FILE.read_text(encoding="utf-8")
    required_phrases = (
        "## Current Baseline",
        "## Clean Authority Model",
        "## Required Reading Order",
        "## Active Revalidation Queue",
        "## Maintenance Rule",
        "python tools/validate_adrs.py",
    )
    for phrase in required_phrases:
        if phrase not in status:
            raise AdrValidationError(f"ADR status is missing required phrase: {phrase}")
    for record in records:
        if record["id"] not in status:
            raise AdrValidationError(f"ADR status is missing {record['id']}")


def validate() -> None:
    """Validate ADR file sequence, inventory, index, and cross-links."""

    records = _load_inventory()
    files = _adr_files()
    _validate_inventory(records, files)
    known_ids = {record["id"] for record in records}
    for record in records:
        _validate_adr_file(record, known_ids)
    _validate_index(records)
    _validate_status(records)


def main() -> int:
    """CLI entry point for local and CI validation."""

    try:
        validate()
    except AdrValidationError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
