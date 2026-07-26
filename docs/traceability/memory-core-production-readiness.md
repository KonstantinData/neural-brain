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
Accepted identity-boundary decision:
[`ADR-019: Tenant-Bound Runtime Database Identities and Connection Pools`](../adr/ADR-019-tenant-bound-runtime-database-identities-and-pools.md).
The earlier decision issue is resolved by Tenant-bound credentials and pools;
general cryptographic context attestation is not selected.

NB-275 records the bounded evaluation of workload- or channel-bound routing
attestation in
[`ADR-019 Routing-Attestation Evaluation`](../governance/adr-019-routing-attestation-evaluation.md).
It defers that additional control pending a separate accepted ADR; it makes no
FND-06 or release-gate change and is not implementation or recognition evidence.

## Current State

| Readiness item | State | Repository evidence | Next production gap |
| --- | --- | --- | --- |
| Runnable entrypoint | Authenticated library, local demo, and installable artifacts available | `tools/dev.ps1 memory-demo`; `neural_brain.consumer.OidcMemoryCoreConsumer`; `uv build --offline`; unit and live PostgreSQL tests | Deploy an application runtime separately from the library. |
| Deployment/runtime | Tenant-bound target accepted; hosted Runtime remains open | `uv_build`; offline sdist/wheel test; `compose.yaml`; `tools/dev.ps1`; ADR-019 | Complete and prove the Tenant-to-pool resolver and dedicated pool lifecycle in a separately deployed application Runtime. No shared customer-data Runtime pool or login is permitted. |
| Tenant isolation | Repository implementation and live local evidence available; independent review and hosted proof remain | `tests/database/test_tenant_isolation_contract.py` proves RLS plus FORCE on every memory table, direct-access denial, Cross-Tenant read and commit-gate denial, forged valid foreign Principal/Tenant denial, fixed-role graph safety, and invalid authority denial; migration 0007 anchors Tenant in `session_user` | Complete independent review and reproduce the same contract in the hosted Runtime. Do not treat local evidence alone as production authorization. |
| Principal roles and service identities | Versioned MS-1 catalog migration implemented; live PostgreSQL proof pending guarded environment | `migrations/0008_principal_roles_and_service_identities.sql`; `tests/migrations/test_principal_roles_and_service_identities.py` | Run the complete live migration and adversarial authorization matrix with `MIGRATION_ADMIN_DSN`; Roles and Service Identities must never widen Principal scope or Memory Gate authority. |
| Tenant provisioning | Repository lifecycle implemented; production control plane not released | `tenant_provisioning.py`; migration 0007 protected lifecycle functions; `test_tenant_database_provisioning.py`; operations runbook | Integrate an approved production secret store and prove reconciliation, monitoring, operator authorization, and deployment procedures. |
| Tenant connection pools | Tenant resolver implemented; hosted pool operations not released | `tenant_pool.py`; unit and live repository tests prove immutable pool generations, no cached/shared fallback, Tenant/database/revision checkout binding, reset propagation, eviction, bounded cache, secret failure, and rotation isolation | Prove deployed global connection budgets, queue/timeout behavior, observability, workload secret access, failover, and restore routing. |
| Runtime Security Floor | Implemented minimum Memory Core boundary; not a general policy engine | `security/floor.py` admits only complete trusted session scope for Memory Core ingest/read; `test_security_floor.py` proves unknown and unreleased operations cannot be configured or overridden into admission | Add versioned policy documents, decision records, approval, obligations, expiry, activation, and independent review without weakening the fixed floor. |
| Config and secrets | Local OIDC configuration available; production Tenant secret custody remains open | Random ignored `.local/dev.env`, operator-mounted public JWKS, issuer/audience validation, redacted failures; Tenant secret naming and lifecycle contract in the operations runbook | Select and configure the production secret store, workload access policy, credential generation, rotation deadlines, emergency revocation, JWKS lifecycle, and secret-free audit/telemetry. |
| Observability/logging | Partial | Atomic `memory_audit.events`, secret-free demo result output, and structured local PostgreSQL verification | Add deployed health/readiness, structured logs, metrics, audit query, alerts, and Tenant-pool/credential lifecycle monitoring without customer identifiers or secrets. |
| Error handling | Partial | Typed fail-closed domain errors, documented recovery actions, and a secret-free stable JSON error envelope from `tools/dev.ps1 memory-demo` | Expose equivalent safe errors from a separately deployed application runtime. |
| Data migration | Local forward path available | Advisory lock, per-migration transaction, ordered SHA-256 ledger, drift denial, and structured disposable fresh/upgrade validation evidence | Prove production upgrade orchestration and compatibility windows. |
| Migration rollback | Local generic evidence available; production and Tenant-mapping release stops remain | `tools/dev.ps1 backup-restore -VerifyMigrationRollback` backs up first, applies a generated disposable post-backup probe, replaces only that generated database from the archive, and proves the pre-upgrade migration ledger count | Define production upgrade orchestration, backup custody, compatibility windows, Tenant-role and credential-revision reconciliation, approval, and an independently witnessed recovery drill. |
| Backup/restore | Local generic evidence available; production release stop remains | `tools/dev.ps1 backup-restore`; owner-restricted Git-ignored custom archive plus SHA-256 manifest; disposable PostgreSQL restore drill verifies the immutable migration ledger | Define production backup storage, encryption, retention, RPO/RTO, external custody, Tenant catalog and role-mapping manifests, per-Tenant recovery semantics, schedule, alerting, and an independently witnessed restore drill. |
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

The production-facing OIDC adapter may choose the initial Tenant pool from the
signed Tenant claim only after complete token validation. It resolves the
Principal from the database inside that Tenant-bound connection. Once acquired,
the protected database lookup independently verifies Tenant, database target,
and credential revision. Direct `RuntimeContext` construction remains a trusted
internal integration seam, not an untrusted authentication interface.

## FND-06 / ADR-019 Evidence Boundary

ADR-019 is accepted normative architecture. Migration 0007 and the Tenant
database operations runbook define repository implementation and operational
contracts, but neither document alone proves a deployed security boundary.

The FND-06 pull request may claim the Tenant-bound slice implemented only after
its integrated evidence proves all of the following with real restricted
PostgreSQL logins and the production-equivalent pool path:

- two Tenants have different Runtime logins and dedicated pool identities;
- `session_user` resolves to one protected active Tenant and writable context
  cannot replace it;
- same-Tenant reads and writes succeed while foreign reads, inserts, updates,
  deletes, context claims, functions, and role assumptions fail;
- RLS and FORCE policies, `WITH CHECK`, role attributes, ownership, grants,
  mappings, memberships, and secure `SECURITY DEFINER` search paths are guarded;
- pool creation, checkout, reset, eviction, limits, secret-load failure, and
  connection reuse remain Tenant-bound and fail closed;
- provisioning is idempotent and cleans partial failures; rotation terminates
  old sessions; revocation, emergency rotation, and deprovisioning deny old
  credentials; and
- migration validation, the full quality gate, and independent security review
  pass with no unresolved critical or high findings.

Even after that evidence passes, it removes only the database Runtime identity
gap. It does not approve real customer data while the hosted Runtime, production
secret store, observability, backup custody, restore, RPO/RTO, vulnerability
reporting, and other ledger release stops remain open.

## Explicit Non-Claims

- The local OIDC issuer and in-memory signing key are not production identity
  infrastructure.
- The local Compose stack is not a production deployment.
- The consumer library is not an HTTP service endpoint and does not fetch JWKS
  keys over the network.
- The historical shared PostgreSQL Runtime login does not authenticate an
  individual OIDC Principal and cannot prove which Tenant the application
  authenticated earlier. ADR-019 now prohibits that shared login for productive
  customer data. An accepted design and migration are not sufficient evidence:
  the final two-login/two-pool PostgreSQL and Runtime tests, lifecycle controls,
  deployed secret custody, and independent review must pass before this release
  stop can be removed.
- Tenant-bound database credentials constrain the Company blast radius; they do
  not replace OIDC Principal authentication, Principal-to-scope authority,
  Area/Project/Session checks, Memory Gates, RLS, FORCE, audit, or operational
  reconciliation.
- A shared-database backup may contain several Tenants. Tenant Runtime
  credentials do not provide Tenant-specific backup custody or close production
  backup, restore, external custody, RPO/RTO, and witnessed-drill requirements.
- A buildable wheel is not a hosted runtime, a registry publication, or a
  deployment rollout.
- The demonstrated Memory Core slice does not complete MS-1, NB-1, or any
  Neural Brain recognition gate.
- No external effect, Dreaming execution, model promotion, or cognition-stage
  capability is added or authorized.
