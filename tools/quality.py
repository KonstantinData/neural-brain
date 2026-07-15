"""Run the deterministic repository quality gate from the locked environment."""

from __future__ import annotations

import platform
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCKED_ARGUMENT = "--locked"
LOCKED_QUALITY_COMMAND = (
    "uv",
    "run",
    "--locked",
    "--all-groups",
    "python",
    "tools/quality.py",
    LOCKED_ARGUMENT,
)
COMMANDS: tuple[tuple[str, ...], ...] = (
    (sys.executable, "-m", "ruff", "format", "--check", "."),
    (sys.executable, "-m", "ruff", "check", "."),
    (sys.executable, "-m", "mypy"),
    (sys.executable, "tools/type_exception_audit.py"),
    (sys.executable, "-m", "pytest"),
)


def _validate_invocation(arguments: Sequence[str]) -> bool:
    if tuple(arguments) == (LOCKED_ARGUMENT,):
        return True
    command = " ".join(LOCKED_QUALITY_COMMAND)
    print(
        f"ERROR: quality gate must be invoked exactly as: {command}",
        file=sys.stderr,
    )
    return False


def _validate_runtime() -> bool:
    if platform.python_implementation() != "CPython" or sys.version_info[:2] != (3, 14):
        print("ERROR: quality gate requires CPython 3.14", file=sys.stderr)
        return False
    if not sys._is_gil_enabled():
        print("ERROR: quality gate requires the GIL-enabled CPython build", file=sys.stderr)
        return False
    return True


def main(arguments: Sequence[str] | None = None) -> int:
    """Run every quality command and fail on the first subprocess error."""

    effective_arguments = sys.argv[1:] if arguments is None else arguments
    if not _validate_invocation(effective_arguments) or not _validate_runtime():
        return 2

    for command in COMMANDS:
        print(f"==> {' '.join(command)}", flush=True)
        subprocess.run(command, cwd=ROOT, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
