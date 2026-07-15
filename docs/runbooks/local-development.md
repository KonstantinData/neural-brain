# Local Development Environment

## Purpose

FND-01.6 provides isolated local PostgreSQL development and test services. The
environment is a Foundation reproducibility baseline, not the final Stage 1
PostgreSQL version decision required by S1-03.1.

The image is pinned to the multi-platform digest for the official PostgreSQL
18.4 Bookworm image. Development and test data use separate containers, ports,
users, databases, and named volumes.

## Prerequisites

- Docker Desktop with Docker Compose v2
- uv; repository commands bootstrap the required uv 0.11.28 release

No password or connection secret is stored in Git. The first command creates
random local credentials in `.local/dev.env`, which is ignored by Git. Commands
must not print this file or its values. The generated file is restricted to the
current operating-system user (`FullControl` with inheritance disabled on
Windows; mode `0600` on POSIX systems).

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
checks PostgreSQL 18.4, exercises explicit commit and rollback transaction
blocks, and proves each probe returns to idle transaction status. It never
prints credentials.

## Reset Only Disposable Test Data

```powershell
.\tools\dev.ps1 reset-test
```

The command fails closed unless the configured database name ends in `_test`.
It also requires the expected Docker Compose project and service-volume ownership
labels before it removes the fixed `neural-brain-postgres-test-data` volume. It
then recreates the test service without stopping or deleting the development
volume.

## Status and Shutdown

```powershell
.\tools\dev.ps1 status
.\tools\dev.ps1 down
```

`down` stops the services but preserves both data volumes. No command in this
runbook purges development data.

## Transaction Safety

Application code must use the ADR-013 contract:

```text
autocommit=True
+ explicit connection.transaction() blocks
```

No database transaction may span a model, tool, network, or other unbounded
external call. The local environment does not weaken database roles, transition
gates, audit atomicity, or scope isolation planned for Stage 1.
