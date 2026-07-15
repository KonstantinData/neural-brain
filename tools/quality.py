"""Run the deterministic local quality gate from the locked environment."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMMANDS: tuple[tuple[str, ...], ...] = (
    ("ruff", "format", "--check", "."),
    ("ruff", "check", "."),
    ("mypy",),
    (sys.executable, "tools/type_exception_audit.py"),
    ("pytest",),
)


def main() -> int:
    """Run every quality command and fail on the first error."""

    for command in COMMANDS:
        print(f"==> {' '.join(command)}", flush=True)
        subprocess.run(command, cwd=ROOT, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
