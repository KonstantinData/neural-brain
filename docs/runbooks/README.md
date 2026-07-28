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
- [`special-category-data-runtime-enforcement.md`](special-category-data-runtime-enforcement.md)
  defines preparation and future operating steps for S1-14.4/S1-11.2 while
  stopping before any unauthorized activation or protected write.
- [`special-category-data-incident-revocation-and-recovery.md`](special-category-data-incident-revocation-and-recovery.md)
  defines a preparation-only incident, suspension, revocation, reconciliation,
  and restore overlay; it neither operates a runtime nor proves recovery.
- [`relationship-memory-governance-preparation.md`](relationship-memory-governance-preparation.md)
  records only future service-managed request and non-use boundaries; it is not
  a runtime operating procedure.
- [`nb1-independent-evaluation-preparation.md`](nb1-independent-evaluation-preparation.md)
  defines preparation-only external EVAL-01 v4 custody, freeze, registry,
  ledger, signing, and review steps; it authorizes no evaluation or release.
- [`protected-control-kill-switch.md`](protected-control-kill-switch.md)
  defines a proposed target review procedure for a future Protected Control
  Plane kill switch; it is not an operational shutdown or recovery procedure.
- [`future-deployment-subject-export-readiness.md`](future-deployment-subject-export-readiness.md)
  defines category-only future deployment export-readiness review steps; it
  does not discover, access, process, export, or disclose personal data.
- [`nb1-candidate-freeze-lifecycle.md`](nb1-candidate-freeze-lifecycle.md)
  defines preparation-only candidate-freeze submission, verification,
  invalidation, and external handoff; it does not create a candidate or release.
