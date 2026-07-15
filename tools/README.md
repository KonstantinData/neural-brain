# Tools

This directory contains guarded development, verification, migration, and
maintenance commands for the repository.

Tools must fail safely, require explicit scope where applicable, and must not
provide unrestricted mutation paths around protected state or audit controls.

## Locked quality gate

Local development and CI use the same commands and the same `uv.lock`. The
repository requires `uv` 0.11.28 through `pyproject.toml`; a different version
fails before dependency synchronization or test execution.

Run the complete gate from the repository root:

```text
uv python install
uv sync --locked --all-groups
uv run --locked --all-groups python tools/quality.py --locked
```

The final command is also the only quality command executed by the CI workflow.
It checks the GIL-enabled CPython 3.14 runtime, Ruff formatting, Ruff linting,
mypy strict mode, the controlled type-exception audit, and the complete pytest
suite. It stops at the first failed command. Invoking `tools/quality.py` without
the explicit locked-invocation guard is rejected; the guard does not replace
the required `uv --locked` option.
