# Protected Ledger Backup and Point-in-Time Recovery

## Scope and readiness boundary

This target operating contract covers backup and point-in-time recovery (PITR)
of the PostgreSQL authoritative protected ledger. It is governed by ADR-003,
ADR-018, ADR-019, and
[`protected-ledger-backup-recovery-v1.json`](../architecture/contracts/protected-ledger-backup-recovery-v1.json).

It is not an executable deployment procedure and is not evidence that a backup
target, WAL archive, encryption, credential, retention schedule, RPO/RTO,
restore environment, or restore test exists. Do not admit productive data or
claim recovery readiness from this document alone.

The Memory Core is a protected subsystem of the product-neutral Neural Brain.
Backup and recovery protect the ledger and evidence; they do not authorize a
Cognitive Plane component, model, planner, consumer, or general application
role to write protected state or cause an external effect.

## Required separation of duties

| Activity | Required role | Prohibited shortcut |
| --- | --- | --- |
| Backup and WAL archive operation | Restricted backup operator | Runtime, model, or general application access |
| Encryption-key use and lifecycle | Separate key custodian | Storage administrator alone decrypting material |
| Isolated restore execution | Separate recovery operator | Restoring into a serving database |
| Restore acceptance | Independent witness | Tool exit or self-report as proof |
| Service cutover or incident resolution | Authorized recovery decision owner | Automatic or model-controlled cutover |

All access is deployment-specific, least-privilege, time-bounded, audited, and
reviewed. Credentials, DSNs, encryption keys, tokens, and live data must never
be recorded in this repository, Notion, logs, PR text, or test output.

## Preflight gate

Before a backup configuration, a restore test, or a recovery cutover, record
and independently verify:

1. the scoped ledger target and authoritative source identity;
2. approved backup cadence, WAL archive-latency threshold, retention, legal
   hold, deletion-propagation, jurisdiction, RPO, RTO, monitoring, and alert
   thresholds;
3. separate backup, key-custody, restore, witness, and recovery-decision
   identities;
4. encrypted-at-rest and encrypted-in-transit configuration, immutable-storage
   protection, secret-free manifest format, and cryptographic integrity checks;
5. an isolated non-serving restore environment with no production cutover path;
6. migration and release-artifact compatibility, including the protected
   ledger's RLS, `FORCE ROW LEVEL SECURITY`, Gate-only-writer, audit, and
   reconciliation requirements.

Any unknown, missing, stale, scope-mismatched, or contradictory item blocks the
operation. There is no fallback to a shared credential, unencrypted archive,
unverified backup, or another Tenant's resource.

## Backup eligibility procedure

1. Resolve the authoritative PostgreSQL ledger target from trusted operations
   context; never from a request, prompt, model response, or user-supplied DSN.
2. Create or select a base backup through the restricted backup operation and
   retain continuous WAL coverage for the defined recovery interval.
3. Encrypt backup and WAL material in transit and at rest through the approved
   deployment control. Keep encryption-key custody separate from storage and
   runtime credentials.
4. Produce immutable, secret-free evidence containing backup identity, source
   identity, base-backup boundary, WAL coverage, manifest digest, encryption
   control reference, retention/hold state, actor, timestamps, and result.
5. Independently verify manifest completeness and digests. A storage success
   response alone is not eligibility evidence.
6. Mark the backup eligible only after every recorded check passes. Missing WAL,
   a bad digest, an unverified encryption control, or ambiguous result is a
   release stop and must be reconciled rather than blindly retried.

## Isolated restore-test procedure

1. Obtain an authorized, scoped restore-test request identifying recovery target,
   test window, independent witness, acceptance criteria, and isolated
   non-serving destination.
2. Verify base-backup manifest, digest, source identity, key-custody path, WAL
   continuity, retention/hold state, and exact recovery target before movement.
3. Restore only to the isolated destination. Do not attach it to serving pools,
   external effectors, production credentials, or a cutover route.
4. Validate migration/release compatibility and recovered ledger invariants:
   scope lineage, RLS and `FORCE ROW LEVEL SECURITY`, Gate-only writes,
   immutable audit continuity, and reconciliation readiness.
5. Measure actual data-loss window and elapsed restoration time against approved
   RPO/RTO. A database process starting is not proof of success.
6. The independent witness records the result against every acceptance criterion.
   Missing, ambiguous, or failed results are `indeterminate` or failed, block
   cutover, and require authoritative reconciliation.
7. Revoke temporary access, remove restore-test material under approved policy,
   clean the isolated environment, and preserve secret-free immutable evidence.

## Recovery and cutover gate

Production recovery is separate from a restore test. Cutover needs an accepted,
authorized recovery procedure plus current evidence for the exact incident,
scope, recovery target, backup/WAL coverage, RPO/RTO measurement, independent
verification, audit continuity, reconciliation, and required approval. It never
replaces the Goal, Action, Memory, or Model Promotion Gate.

Do not overwrite a serving ledger, switch an endpoint, release resources, or
retry an ambiguous effect until authoritative reconciliation concludes. The
runtime remains not-ready while reconciliation or audit continuity is incomplete.

## Retention, legal hold, and deletion propagation

Evaluate each backup against approved retention, legal hold, deletion
propagation, incident evidence, and recovery obligation. A primary-ledger
deletion does not establish deletion completion while retained backup material
remains. Before destructive expiry, independently verify no hold or recovery
obligation remains, revoke associated key material through separate custody,
and record immutable secret-free destruction evidence. Unknown retention, hold,
deletion, or key state blocks destructive expiry.

## Required evidence and release stops

Retain secret-free immutable evidence for backup creation, WAL coverage,
integrity verification, access reviews, restore-test results, RPO/RTO
measurement, retention/hold evaluation, destruction, exceptions, and incident
reconciliation. No productive admission or cutover is permitted with missing
encrypted backup/PITR coverage, unmeasured RPO/RTO, missing restore test,
missing access or key separation, failed audit/reconciliation validation, or an
open retention/hold/deletion issue. These stops are not waived by a tool,
operator self-report, or model output.
