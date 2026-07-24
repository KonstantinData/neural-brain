# Local Development Environment

## Purpose

The local environment provides isolated PostgreSQL development and test
services for the completed Memory Core foundation and the first MS-1 memory
kernel. It runs the protected hierarchy, observation, Working Memory,
checkpoint and audit migrations, protected NB-1 cognitive checkpoint evidence,
plus a reserved, non-executable Dreaming schema; it is not a
production-ready deployment.

The image is pinned to the multi-platform digest for the official PostgreSQL
18.4 Bookworm image. Development and test data use separate containers, ports,
users, databases, and named volumes. The Docker Compose project name is derived
from the canonical repository path and stored in `.local/dev.env`, so separate
local worktrees do not share the same disposable test volume by default.

## Prerequisites

- Docker Desktop with Docker Compose v2
- uv; repository commands bootstrap the required uv 0.11.28 release

No password or connection secret is stored in Git. The first command creates
random local credentials in `.local/dev.env`, which is ignored by Git. Commands
must not print this file or its values. The generated file is restricted to the
current operating-system user (`FullControl` with inheritance disabled on
Windows; mode `0600` on POSIX systems). The file contains a random local
PostgreSQL bootstrap password plus separate non-superuser development and test
role credentials.

## Start Dependencies

From the repository root:

```powershell
.\tools\dev.ps1 up
```

This starts both databases and waits for their health checks:

- development: `127.0.0.1:55432`, database `neural_brain_dev`
- test: `127.0.0.1:55433`, database `neural_brain_test`

Both ports bind only to loopback. Host authentication uses SCRAM-SHA-256.

## Verify Connections and Transaction Mode

```powershell
.\tools\dev.ps1 verify
```

Verification connects through synchronous Psycopg 3 with `autocommit=True`,
checks PostgreSQL 18.4, rejects superuser application/test roles, exercises
explicit commit and rollback transaction blocks with transaction-scoped
session settings, and proves each probe returns to idle transaction status. It
never prints credentials.

## Run the Local Memory Core Slice

From a clean checkout with Docker Desktop running:

```powershell
.\tools\dev.ps1 memory-demo
```

The command normally completes in under ten minutes and performs one bounded
local workflow:

1. generate owner-protected random local database credentials if absent;
2. start the loopback-only PostgreSQL 18.4 development service;
3. create or harden the fixed `NOLOGIN` Memory Core roles;
4. apply pending repository migrations one transaction at a time while holding
   an installation advisory lock;
5. reject any applied migration whose name or SHA-256 digest differs from the
   current checkout;
6. keep database ownership on the fixed `NOLOGIN` owner and grant the local
   non-superuser login only connection plus Memory Gate ingest/read access;
7. provision the fixed local demo hierarchy and Principal binding through the
   authenticated administrative provisioning gate with append-only audit
   evidence;
8. commit one observation, Working Memory version, checkpoint, transition
   receipt, and audit event through `MemoryService` and the protected PostgreSQL
   gate; and
9. read the checkpoint back through the reader gate and print only non-secret
   result identifiers and booleans.

Success output is one JSON object containing `"status": "passed"`,
`"working_memory_version": 1`, `"audit_committed": true`, and
`"checkpoint_readback": true`. The command accepts no principal, Tenant, Area,
Project, or Session override. Errors print only the exception class; DSNs and
credentials are never included.

The persistent migration ledger is stored in the protected
`neural_brain_install.schema_migrations` table. If product schemas exist without
that ledger, or an applied checksum differs, installation fails closed instead
of adopting or rewriting the database. This first operator slice has no
downgrade command. Preserve the development volume and restore from a verified
backup if rollback is required; production backup and restore remain a release
stop.

The fixed local OIDC Principal is not a production identity provider. The
entrypoint creates an in-memory RSA key and a signed RS256 token for the fixed
demo issuer and scope, resolves the subject to a pre-provisioned database
principal, and the database independently checks its authority. No private key
or bearer token is written to disk or printed. Do not expose the local database
port beyond loopback or use this demo as a production service.

## Reset Only Disposable Test Data

```powershell
.\tools\dev.ps1 reset-test
```

The command fails closed unless the configured database name ends in `_test`.
It also requires the expected Docker Compose project and service-volume ownership
labels before it stops the test container, removes it, or removes the
worktree-specific test volume. It then recreates the test service without
stopping or deleting the development volume.

## Status and Shutdown

```powershell
.\tools\dev.ps1 status
.\tools\dev.ps1 down
```

`down` stops the services but preserves both data volumes. No command in this
runbook purges development data.

## Memory Transaction Safety

Application code must use the ADR-013 contract:

```text
autocommit=True
+ explicit connection.transaction() blocks
```

No database transaction may span local model inference, a consumer callback, a
network request, or another unbounded external call. The local environment does
not weaken database roles, the Memory Gate, provenance and audit atomicity, or
scope isolation. The MS-1 role bootstrap, forward-migration validation, and
live database tests are also enforced in CI. Retention and deletion controls
remain a later MS-1 implementation block.

Migration `0004` keeps cognitive persistence inside the Memory Transition Gate.
The runtime adapter has execute access only to the dedicated gate functions and
never receives direct table-write permission. With a guarded disposable
PostgreSQL 18 administrative DSN set, run the focused recovery evidence with:

```powershell
uv run --locked --all-groups pytest tests/database/test_postgres_cognitive_repository.py
```

The suite proves transaction rollback, restart/readback consistency, CAS,
idempotency, corruption denial, and authenticated scope isolation. Do not place
the DSN in command history, documentation, or repository files.

## Dreaming Availability

Dreaming is fail-closed unavailable at the current maturity. The
`neural_brain_dreamer` role has no execute privilege on the reserved database
function, and both the application service and PostgreSQL adapter reject calls
before persistence. This is intentional: a persistent Area lease, immutable
input snapshot, and independent validation gate do not yet exist. Do not grant
execute permission or treat the reserved schema as a runnable dry-run path.
