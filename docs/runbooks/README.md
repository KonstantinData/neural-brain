# Runbooks

This directory contains operational, recovery, incident, backup, restore, and
release procedures for implemented Neural Brain capabilities.

Runbooks must be executable by their intended operators, avoid secrets, and
identify safety gates that may not be bypassed.

Runbooks must preserve the boundary between the Cognitive Plane and the
independent Protected Control Plane. Planning and action selection never confer
authority; tool execution, effect recovery, shutdown, and promotion require
their accepted gates and may not be documented as model-controlled shortcuts.

- [`release-artifacts.md`](release-artifacts.md) defines deterministic release
  evidence, SBOM generation, and GitHub OIDC artifact attestation.
- [`memory-core-oidc-consumer.md`](memory-core-oidc-consumer.md) deploys the
  authenticated Memory Core consumer library and its externally managed OIDC
  configuration.
- [`tenant-database-operations.md`](tenant-database-operations.md) defines the
  target ADR-019 operating contract for Tenant-bound database credentials,
  dedicated pools, provisioning, rotation, revocation, recovery, and migration
  without claiming production readiness.
- [`protected-ledger-backup-recovery.md`](protected-ledger-backup-recovery.md)
  defines target-only backup, WAL/PITR, retention, custody, and isolated
  restore-test procedure; it does not prove a deployed recovery capability.
- [`relationship-memory-governance-preparation.md`](relationship-memory-governance-preparation.md)
  records only future service-managed request and non-use boundaries; it is not
  a runtime operating procedure.
