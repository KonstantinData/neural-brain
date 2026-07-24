# Memory Core Production-Readiness Ledger

## Scope

This ledger tracks the real gaps between the current protected Memory Core and
the first production-usable milestone. A green local demonstration does not
make the service, authentication model, operations, or complete Memory Core
production-ready.

Active coordination record:
[`Ship first production-usable authenticated Memory Core slice`](https://www.notion.so/3a71c1ac5ec081c98f09ca72dcbcd838).

## Current State

| Readiness item | State | Repository evidence | Next production gap |
| --- | --- | --- | --- |
| Runnable entrypoint | Authenticated library, local demo, and installable artifacts available | `tools/dev.ps1 memory-demo`; `neural_brain.consumer.OidcMemoryCoreConsumer`; `uv build --offline`; unit and live PostgreSQL tests | Deploy an application runtime separately from the library. |
| Deployment/runtime | Reproducible library distribution available | `uv_build`; offline sdist/wheel test; `compose.yaml`; `tools/dev.ps1` | Deploy an application runtime separately from its database. |
| Config and secrets | OIDC library configuration available | Random ignored `.local/dev.env`, operator-mounted public JWKS, issuer/audience validation, redacted failures | Define deployed secret injection, JWKS rotation, and issuer revocation operations. |
| Observability/logging | Partial | Atomic `memory_audit.events` and secret-free result output | Add health/readiness, structured logs, metrics, audit query, and alerting. |
| Error handling | Partial | Typed fail-closed domain errors, documented recovery actions, and a secret-free stable JSON error envelope from `tools/dev.ps1 memory-demo` | Expose equivalent safe errors from a separately deployed application runtime. |
| Data migration | Local forward path available | Advisory lock, per-migration transaction, ordered SHA-256 ledger, drift denial | Prove production upgrade orchestration and compatibility windows. |
| Migration rollback | Open | No downgrade command; runbook refuses silent adoption or rewrite | Define backup-before-upgrade, restore, and rollback evidence. |
| Backup/restore | Open release stop | No verified backup or restore workflow | Implement scheduled backup, restore drill, reconciliation, and evidence. |
| LICENSE | MIT license declared | `LICENSE`; package metadata; security-policy license inventory | Keep package metadata and released artifacts aligned with the license text. |
| `SECURITY.md` | Open immediate item | Repository has no vulnerability-reporting policy | Owner must define the private reporting and response path. |

## Proven Local Behavior

The operator entrypoint uses a fixed local OIDC Principal and scope; callers
cannot submit trusted identity or hierarchy values. It creates or hardens fixed
`NOLOGIN` database roles, keeps the database owned by the fixed non-login owner,
grants the local non-superuser login only connection plus ingest/read gate
membership, and provisions the local hierarchy plus authority binding through
an authenticated administrative gate with audit evidence. The audit actor is
the authenticated database administrator; the runtime Principal is the subject.

The existing protected Memory Gate then atomically commits one observation,
Working Memory version, checkpoint, transition receipt, and audit event. The
reader gate returns the same checkpoint inside authenticated session scope.
Direct runtime DML against protected catalog tables remains denied. Live test
evidence also proves repeatable installation and fail-closed checksum drift.

## Explicit Non-Claims

- The local OIDC issuer and in-memory signing key are not production identity
  infrastructure.
- The local Compose stack is not a production deployment.
- The consumer library is not an HTTP service endpoint and does not fetch JWKS
  keys over the network.
- A buildable wheel is not a hosted runtime, a registry publication, or a
  deployment rollout.
- The demonstrated Memory Core slice does not complete MS-1, NB-1, or any
  Neural Brain recognition gate.
- No external effect, Dreaming execution, model promotion, or cognition-stage
  capability is added or authorized.
