# Memory Core Production-Readiness Ledger

## Scope

This ledger tracks the real gaps between the current protected Memory Core and
the first production-usable milestone. A green local demonstration does not
make the service, authentication model, operations, or complete Memory Core
production-ready.

Active coordination record:
[`Ship first production-usable authenticated Memory Core slice`](https://www.notion.so/3a71c1ac5ec081c98f09ca72dcbcd838).
Isolation evidence record:
[`Harden runtime principal binding and prove tenant isolation`](https://www.notion.so/3a91c1ac5ec081caa0bac06ad5be1647).
Open identity-boundary decision:
[`Decide database-bound Tenant identity or context attestation`](https://www.notion.so/3a91c1ac5ec0814ab44bee4ca23d9a94).

## Current State

| Readiness item | State | Repository evidence | Next production gap |
| --- | --- | --- | --- |
| Runnable entrypoint | Authenticated library, local demo, and installable artifacts available | `tools/dev.ps1 memory-demo`; `neural_brain.consumer.OidcMemoryCoreConsumer`; `uv build --offline`; unit and live PostgreSQL tests | Deploy an application runtime separately from the library. |
| Deployment/runtime | Reproducible library distribution available | `uv_build`; offline sdist/wheel test; `compose.yaml`; `tools/dev.ps1` | Deploy an application runtime separately from its database and decide whether each Tenant requires a database-bound credential or accepted context attestation. |
| Tenant isolation | Database table and gate controls proven; production identity-to-database binding remains open | `tests/database/test_tenant_isolation_contract.py` proves RLS plus FORCE on every memory table, direct-access denial for a real runtime login through every effective role, cross-Tenant and cross-Area row hiding, forged Tenant/Area-claim denial, and missing, expired, or disabled authority denial | The shared runtime login authenticates the service, not an OIDC Principal. Before real customer data, either accept the trusted-runtime boundary explicitly or implement an accepted tenant/principal-bound database identity or attestation contract. |
| Config and secrets | OIDC library configuration available | Random ignored `.local/dev.env`, operator-mounted public JWKS, issuer/audience validation, redacted failures | Define deployed secret injection, JWKS rotation, and issuer revocation operations. |
| Observability/logging | Partial | Atomic `memory_audit.events`, secret-free demo result output, and structured local PostgreSQL verification | Add deployed health/readiness, structured logs, metrics, audit query, and alerting. |
| Error handling | Partial | Typed fail-closed domain errors, documented recovery actions, and a secret-free stable JSON error envelope from `tools/dev.ps1 memory-demo` | Expose equivalent safe errors from a separately deployed application runtime. |
| Data migration | Local forward path available | Advisory lock, per-migration transaction, ordered SHA-256 ledger, drift denial, and structured disposable fresh/upgrade validation evidence | Prove production upgrade orchestration and compatibility windows. |
| Migration rollback | Local evidence available; production release stop remains | `tools/dev.ps1 backup-restore -VerifyMigrationRollback` backs up first, applies a generated disposable post-backup probe, replaces only that generated database from the archive, and proves the pre-upgrade migration ledger count | Define production upgrade orchestration, backup custody, compatibility windows, reconciliation, approval, and an independently witnessed recovery drill. |
| Backup/restore | Local evidence available; production release stop remains | `tools/dev.ps1 backup-restore`; owner-restricted Git-ignored custom archive plus SHA-256 manifest; disposable PostgreSQL restore drill verifies the immutable migration ledger | Define production backup storage, encryption, retention, RPO/RTO, reconciliation, schedule, alerting, and an independently witnessed restore drill. |
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
evidence now uses a real `NOINHERIT`, `NOBYPASSRLS` login and proves that every
current `memory_core` and `memory_audit` table has both RLS and FORCE enabled.
The read gate hides a Tenant B row from Tenant A, rejects a Tenant A Principal
paired with Tenant B scope, applies the equivalent checks across Areas, permits
the valid Tenant B and Area B Principals, and rejects missing, expired, or
disabled authority. Live evidence also proves repeatable installation and
fail-closed checksum drift.

## Explicit Non-Claims

- The local OIDC issuer and in-memory signing key are not production identity
  infrastructure.
- The local Compose stack is not a production deployment.
- The consumer library is not an HTTP service endpoint and does not fetch JWKS
  keys over the network.
- The shared PostgreSQL runtime login does not authenticate an individual OIDC
  Principal. PostgreSQL can validate the current Principal-to-scope authority,
  but it cannot infer that a different Principal was authenticated earlier in
  the application process. Passing a fully authorized Tenant B Principal and
  Tenant B scope is therefore legitimate at the database boundary, not a
  detectable spoof. Cross-Tenant containment after trusted-runtime compromise
  requires a separately accepted database-identity or attestation design.
- A buildable wheel is not a hosted runtime, a registry publication, or a
  deployment rollout.
- The demonstrated Memory Core slice does not complete MS-1, NB-1, or any
  Neural Brain recognition gate.
- No external effect, Dreaming execution, model promotion, or cognition-stage
  capability is added or authorized.
