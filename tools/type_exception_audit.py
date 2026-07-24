"""Audit controlled mypy ignores and typing casts.

The allowlist is intentionally empty at foundation. Any future exception must
be listed in ``type-exceptions.toml`` with an exact location and rationale.
"""

from __future__ import annotations

import ast
import re
import sys
import tokenize
import tomllib
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "type-exceptions.toml"
SCAN_ROOTS = (ROOT / "src", ROOT / "tests", ROOT / "tools")
IGNORE_PATTERN = re.compile(r"#\s*type:\s*ignore(?P<codes>\[[^\]]+\])?")


@dataclass(frozen=True, slots=True)
class Finding:
    """A type-safety exception found in repository Python code."""

    path: str
    line: int
    kind: str
    code: str | None = None


@dataclass(frozen=True, slots=True)
class AllowedException:
    """A reviewed type-safety exception from the repository allowlist."""

    path: str
    line: int
    kind: str
    rationale: str
    code: str | None = None


def _relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _python_files() -> list[Path]:
    return sorted(path for root in SCAN_ROOTS for path in root.rglob("*.py"))


def _cast_findings(path: Path, tree: ast.AST) -> list[Finding]:
    cast_names = {"cast"}
    typing_modules = {"typing", "typing_extensions"}
    typing_aliases = set(typing_modules)

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module in typing_modules:
            cast_names.update(
                imported.asname or imported.name
                for imported in node.names
                if imported.name == "cast"
            )
        elif isinstance(node, ast.Import):
            typing_aliases.update(
                imported.asname or imported.name
                for imported in node.names
                if imported.name in typing_modules
            )

    def is_cast_reference(node: ast.AST) -> bool:
        return (isinstance(node, ast.Name) and node.id in cast_names) or (
            isinstance(node, ast.Attribute)
            and node.attr == "cast"
            and isinstance(node.value, ast.Name)
            and node.value.id in typing_aliases
        )

    changed = True
    while changed:
        changed = False
        for node in ast.walk(tree):
            target_names: list[str] = []
            value: ast.AST | None = None
            if isinstance(node, ast.Assign):
                value = node.value
                target_names.extend(
                    target.id for target in node.targets if isinstance(target, ast.Name)
                )
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                value = node.value
                target_names.append(node.target.id)

            if value is None or not target_names or not is_cast_reference(value):
                continue

            for name in target_names:
                if name not in cast_names:
                    cast_names.add(name)
                    changed = True

    findings: list[Finding] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if is_cast_reference(node.func):
            findings.append(Finding(_relative(path), node.lineno, "cast"))
    return findings


def _ignore_findings(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    with path.open("rb") as stream:
        for token in tokenize.tokenize(stream.readline):
            if token.type != tokenize.COMMENT:
                continue
            match = IGNORE_PATTERN.search(token.string)
            if match is None:
                continue
            codes = match.group("codes")
            code = codes[1:-1].strip() if codes is not None else None
            findings.append(Finding(_relative(path), token.start[0], "type-ignore", code))
    return findings


def collect_findings() -> list[Finding]:
    """Return every controlled type exception in scanned repository code."""

    findings: list[Finding] = []
    for path in _python_files():
        source = path.read_text(encoding="utf-8")
        findings.extend(_cast_findings(path, ast.parse(source, filename=str(path))))
        findings.extend(_ignore_findings(path))
    return sorted(findings, key=lambda finding: (finding.path, finding.line, finding.kind))


def _load_allowlist() -> tuple[int, int, set[AllowedException]]:
    with CONFIG_PATH.open("rb") as stream:
        config = tomllib.load(stream)
    if config.get("schema_version") != 1:
        raise ValueError("type-exceptions.toml must use schema_version = 1")

    raw_exceptions = config.get("exceptions", [])
    if not isinstance(raw_exceptions, list):
        raise TypeError("exceptions must be an array of tables")

    allowed: set[AllowedException] = set()
    for item in raw_exceptions:
        if not isinstance(item, dict):
            raise TypeError("each exception must be a table")
        rationale = item.get("rationale")
        if not isinstance(rationale, str) or len(rationale.strip()) < 10:
            raise ValueError("every exception requires a meaningful rationale")
        allowed.add(
            AllowedException(
                path=str(item["path"]),
                line=int(item["line"]),
                kind=str(item["kind"]),
                code=str(item["code"]) if "code" in item else None,
                rationale=rationale.strip(),
            )
        )

    return int(config["max_type_ignores"]), int(config["max_casts"]), allowed


def audit() -> tuple[int, list[str]]:
    """Return the finding count and policy violations."""

    max_ignores, max_casts, allowed = _load_allowlist()
    findings = collect_findings()
    violations: list[str] = []

    ignore_count = sum(finding.kind == "type-ignore" for finding in findings)
    cast_count = sum(finding.kind == "cast" for finding in findings)
    if ignore_count > max_ignores:
        violations.append(f"type-ignore count {ignore_count} exceeds maximum {max_ignores}")
    if cast_count > max_casts:
        violations.append(f"cast count {cast_count} exceeds maximum {max_casts}")

    allowed_keys = {(item.path, item.line, item.kind, item.code) for item in allowed}
    finding_keys = {(item.path, item.line, item.kind, item.code) for item in findings}
    for finding in findings:
        key = (finding.path, finding.line, finding.kind, finding.code)
        if finding.kind == "type-ignore" and finding.code is None:
            violations.append(f"{finding.path}:{finding.line}: type-ignore requires an error code")
        if key not in allowed_keys:
            violations.append(
                f"{finding.path}:{finding.line}: unapproved {finding.kind}"
                + (f"[{finding.code}]" if finding.code else "")
            )

    for item in allowed:
        key = (item.path, item.line, item.kind, item.code)
        if key not in finding_keys:
            violations.append(f"stale allowlist entry: {item.path}:{item.line} {item.kind}")

    return len(findings), violations


def main() -> int:
    """Run the audit and return a process exit code."""

    finding_count, violations = audit()
    print(f"type-exception findings: {finding_count}")
    for violation in violations:
        print(f"ERROR: {violation}", file=sys.stderr)
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main())
