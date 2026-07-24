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

## ADR authority validation

The ADR cleanup guard checks that `docs/adr/` has a continuous decision
sequence, a matching `adr-authority.json` inventory, a canonical `STATUS.md`,
indexed records, valid status metadata, uniform authority headers, required
decision sections, and reciprocal supersession or amendment references:

```text
python tools/validate_adrs.py
```

The same validator is exercised by `tests/architecture/test_accepted_adrs.py`.

## NB-1 offline training evidence

The bounded EVAL-01 v3 grid search is an offline evidence builder, not a runtime
training or promotion interface. Verify the checked-in non-hidden artifact with:

```text
uv run --locked --all-groups python tools/train_nb1_workspace.py --check
```

Generation without `--check` requires a new, explicitly versioned output path and uses only the preregistered public training split
and rewrites the deterministic development-candidate bundle. It never reads a
hidden artifact, promotes a model, or marks an evaluation gate as passed.

## NB-1 external evaluator handoff

Candidate export is currently blocked. The only checked-in model is bound to
rejected EVAL-01 v3, and the command fails closed for that digest. After a
replacement specification, generator, versioned training artifact, and
candidate are frozen, this interface can export a label-free freeze receipt to
evaluator-controlled storage:

```text
uv run --locked --all-groups python tools/export_nb1_evaluation_candidate.py --frozen-at 2026-07-17T10:00:00+02:00 --output <external-path>/candidate.json
```

The export contains no hidden data and is not a passing evaluation artifact.
The external evaluator keeps hidden seed, labels, scoring implementation,
detailed correctness, attempts ledger, and Ed25519 private key outside this
repository. Signed evidence is accepted only against reviewer-supplied trusted
candidate, specification, and public-key registries and still requires an
independent gate review. Historical EVAL-01 v3 is rejected and must not be
placed in an accepted-specification registry.
