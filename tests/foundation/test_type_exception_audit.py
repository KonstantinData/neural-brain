"""Tests for the controlled type-exception quality gate."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tools.type_exception_audit import _cast_findings, audit

ROOT = Path(__file__).resolve().parents[2]


def test_repository_has_no_unapproved_type_exceptions() -> None:
    finding_count, violations = audit()
    assert finding_count == 0
    assert violations == []


@pytest.mark.parametrize(
    "source",
    [
        "from typing import cast as narrow\nnarrow(int, object())",
        "from typing import cast\nnarrow = cast\nnarrow(int, object())",
        "from typing import cast\nnarrow = cast\nagain = narrow\nagain(int, object())",
        "from typing import cast\nnarrow: object = cast\nnarrow(int, object())",
        "import typing\nnarrow = typing.cast\nnarrow(int, object())",
        "import typing as types\ntypes.cast(int, object())",
        "import typing_extensions\ntyping_extensions.cast(int, object())",
    ],
)
def test_cast_aliases_cannot_bypass_audit(source: str) -> None:
    findings = _cast_findings(ROOT / "tests" / "synthetic.py", ast.parse(source))
    assert len(findings) == 1
    assert findings[0].kind == "cast"
