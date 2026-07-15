"""Executable evidence for ADR-013's CPython runtime contract."""

from __future__ import annotations

import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_runtime_is_cpython_314_with_gil() -> None:
    assert platform.python_implementation() == "CPython"
    assert sys.version_info[:2] == (3, 14)
    assert sys._is_gil_enabled()


def test_runtime_pin_requests_standard_cpython_variant() -> None:
    runtime_request = (ROOT / ".python-version").read_text(encoding="utf-8").strip()
    assert runtime_request == "cpython-3.14.6"
    assert not runtime_request.endswith("t")
