# ADR-013: CPython 3.14 GIL Runtime and Engineering Toolchain

- Status: Accepted
- Date: 2026-07-15
- Decision owner: Konstantin Milonas
- Notion record: https://app.notion.com/p/39e1c1ac5ec081049f97e82c17f6b120
- Related task: FND-01.5
- Authority: current
- Theme: runtime_and_inference
- Applies to stages: NB-0, NB-1, NB-2, NB-3, NB-4, NB-5, NB-6, NB-7, NB-8
- Supersedes: none
- Superseded by: none
- Amends: none
- Amended by: ADR-015, ADR-018

## Amendment by ADR-018

The selected toolchain currently implements the synchronous Memory Core. It is
also the default engineering baseline for the complete cognitive system, but
this ADR does not validate the neural substrate, concurrency model, numerical
stack, accelerator runtime, simulator, or distributed execution required by
later NB stages. Those choices require measured evidence and, where they alter
the runtime boundary, a further ADR. Cognitive components remain separated from
protected gates, execution, verification, and model promotion.

## Amendment by ADR-015

The selected toolchain implements a synchronous memory runtime. References in
the original rationale to a cognitive agent loop, planner, executor, verifier,
Goal or Action gates, tool execution, or goal completion are superseded. The
runtime validation boundary terminates in a typed memory policy and transition
boundary. External-agent runtime responsibilities are not part of this ADR.

## Context

Neural Brain needs a reproducible greenfield runtime for the serial Stage 1
memory lifecycle, PostgreSQL transaction safety, property-based transition
testing, model-assisted memory processing, and fail-closed validation of
untrusted inputs.

The runtime must preserve explicit consumer, inference, memory-policy, memory
transition, and persistence boundaries. Static typing is an engineering
control, not a substitute for runtime validation, authenticated identity,
authority, policy, or database constraints.

## Decision

Neural Brain uses:

- CPython 3.14 with the standard GIL-enabled runtime;
- uv for Python runtime, dependency, environment, and lockfile management;
- Ruff for formatting and linting;
- mypy in strict mode for static type checking;
- pytest for deterministic and integration tests;
- Hypothesis for property-based and rule-based state-machine tests;
- Pydantic v2 for runtime schema validation at untrusted boundaries; and
- Psycopg 3 for synchronous PostgreSQL access with explicit transaction control.

Stage 1 uses synchronous application and database flows. Asynchronous or
free-threaded execution requires a separate accepted ADR and may not be enabled
through configuration alone.

## CPython Runtime Contract

The runtime request must identify CPython 3.14 without the free-threaded `t`
variant. Repository checks must reject:

- another Python implementation;
- a Python minor version other than 3.14; or
- a runtime where the GIL is disabled.

The exact patch version is pinned in `.python-version` and updated through a
reviewed dependency-maintenance change.

## Static Type-Safety Contract

Mypy strict mode applies from the first module. In addition:

- implicit `Any` is prohibited;
- untyped third-party libraries are isolated behind typed adapters;
- `typing.cast()` and `# type: ignore[...]` are controlled exceptions;
- every ignore names a concrete mypy error code;
- every approved exception has a documented rationale; and
- the repository quality gate reports exception counts and rejects unapproved
  exceptions.

The repository starts with an empty exception allowlist. Adding an exception is
a reviewed change, never a local bypass.

## Runtime Trust Boundary

Every untrusted runtime payload follows this sequence:

```text
Untrusted input
-> Pydantic schema validation
-> Trust Envelope
-> typed domain object
-> memory policy and transition boundary
```

Untrusted inputs include request payloads, prompts, model responses, tool
outputs, integration messages, persisted payloads, and database reads whose
integrity is not already established by the current transaction and schema.

Schema validation does not determine principal, scope, roles, authority,
approval, policy, or kill-switch state. Those values come only from trusted,
authenticated runtime context.

## PostgreSQL Transaction Contract

Stage 1 uses the synchronous Psycopg API with:

```text
autocommit=True
+ explicit connection.transaction() blocks
```

The application must:

- make every transaction boundary visible in code;
- commit protected state mutation and its audit event in the same transaction;
- avoid implicit long-lived transactions and `idle in transaction` sessions;
- never hold a database transaction across a model, consumer, network, or other
  unbounded external call; and
- perform model or consumer work before or after the database transaction, never
  inside it.

These rules apply to the local Ollama adapter without granting it direct memory
write authority.

## Inference Provider Is Out of Scope

This decision does not select a model provider. A separate accepted inference
ADR must define local Ollama as the allowed provider and explicitly prohibit
OpenAI use and automatic cloud fallback before model inference is integrated.

## Alternatives Considered

### TypeScript

TypeScript offers strong compile-time contracts and model SDK support, but it
does not provide enough benefit for the current Python-oriented repository and
serial runtime to justify an additional ecosystem and runtime boundary.

### Rust

Rust offers stronger compile-time ownership and memory-safety guarantees, but
its additional model-integration and delivery cost is not justified for the
current serial Stage 1 architecture.

### Free-threaded CPython

Free-threaded CPython is rejected for Stage 1. It would expand concurrency and
extension-compatibility risk before the architecture introduces a scheduler or
distributed execution ownership.

## Consequences

- Runtime and dependencies are reproducible through reviewed pins and `uv.lock`.
- Strict typing and exception auditing make circumventions visible.
- Runtime validation is mandatory at every untrusted boundary.
- PostgreSQL transactions remain short, explicit, and auditable.
- CPU-bound scaling and asynchronous execution are deferred until justified by
  an accepted architecture decision.
- The model-provider decision remains independent and cannot be inferred from
  the Python stack.
