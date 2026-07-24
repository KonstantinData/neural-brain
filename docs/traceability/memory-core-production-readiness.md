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
| Runnable entrypoint | Local slice available | `tools/dev.ps1 memory-demo`; `tools/memory_demo.py`; unit and live PostgreSQL tests | Ship a stable authenticated consumer API, CLI, or service endpoint. |
| Deployment/runtime | Local PostgreSQL slice available | `compose.yaml`; `tools/dev.ps1`; clean-database round-trip test | Package and deploy the application runtime separately from its database. |
| Config and secrets | Local-only controls | Random ignored `.local/dev.env`, owner-only ACL/mode, loopback binding, redacted CLI failures | Define production secret injection, rotation, and revocation. |
| Observability/logging | Partial | Atomic `memory_audit.events` and secret-free result output | Add health/readiness, structured logs, metrics, audit query, and alerting. |
| Error handling | Partial | Typed fail-closed domain errors; checksum and ambiguous-state rejection; nonzero CLI exit | Define stable operator error codes and recovery actions. |
| Data migration | Local forward path available | Advisory lock, per-migration transaction, ordered SHA-256 ledger, drift denial | Prove production upgrade orchestration and compatibility windows. |
| Migration rollback | Open | No downgrade command; runbook refuses silent adoption or rewrite | Define backup-before-upgrade, restore, and rollback evidence. |
| Backup/restore | Open release stop | No verified backup or restore workflow | Implement scheduled backup, restore drill, reconciliation, and evidence. |
| LICENSE | Open immediate item | Repository has no `LICENSE` | Owner must select and add the intended license. |
| `SECURITY.md` | Open immediate item | Repository has no vulnerability-reporting policy | Owner must define the private reporting and response path. |

## Proven Local Behavior

The operator entrypoint uses a fixed local Principal and scope; callers cannot
submit trusted identity or hierarchy values. It creates or hardens fixed
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

- The local fixed context is not production authentication.
- The local Compose stack is not a production deployment.
- Checkpoint readback does not provide direct Observation or current Working
  Memory read APIs.
- The demonstrated Memory Core slice does not complete MS-1, NB-1, or any
  Neural Brain recognition gate.
- No external effect, Dreaming execution, model promotion, or cognition-stage
  capability is added or authorized.
