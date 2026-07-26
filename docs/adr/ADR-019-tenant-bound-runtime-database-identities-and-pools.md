# ADR-019: Tenant-Bound Runtime Database Identities and Connection Pools

- Status: Accepted
- Date: 2026-07-26
- Decision owner: Konstantin Milonas
- Notion source: https://app.notion.com/p/3a91c1ac5ec0813d8fb5fab270b14801
- Notion page ID: `3a91c1ac-5ec0-813d-8fb5-fab270b14801`
- Authority: current
- Theme: scope_and_isolation
- Applies to stages: NB-0, NB-1, NB-2, NB-3, NB-4, NB-5, NB-6, NB-7, NB-8
- Supersedes: none
- Superseded by: none
- Amends: ADR-002, ADR-003, ADR-005, ADR-013, ADR-015, ADR-016, ADR-018
- Amended by: none

## Context

The tenant-isolation evidence in PR #24 proved that PostgreSQL row-level
security, forced row-level security, restricted Runtime roles, and gate-owned
access correctly deny direct table access, foreign scope, and invalid authority
under the context presented to the database.

That evidence also exposed a boundary the database could not prove. A shared
Runtime database login carried no PostgreSQL-verifiable evidence of which OIDC
Principal or Tenant the application had authenticated earlier. An application
fault could therefore present a fully valid foreign Principal and Tenant
combination through writable session settings. PostgreSQL would correctly
authorize that combination because it had no independent Tenant identity to
compare against.

RLS cannot by itself repair an identity source that is supplied by the same
Runtime it is intended to constrain. A production boundary for customer data
therefore requires a Tenant identity anchored below application-supplied
context.

## Decision

For productive customer data, every Company/Tenant has exactly one
Tenant-bound Runtime database login identity and one dedicated Tenant-specific
connection pool. A Runtime database login is bound to exactly one Tenant in
protected PostgreSQL state. An established connection inherits that immutable
Tenant identity and may never switch Tenant for its lifetime.

PostgreSQL derives the connection's authoritative Tenant from protected state
keyed by `session_user`, or by an equivalently immutable authenticated session
identity if the connection mechanism changes. `current_user` is not an identity
anchor because `SET ROLE` and security-definer execution can change it.
Application-writable GUC values are not identity anchors.

Runtime-supplied scope may only narrow the database-bound identity:

- a supplied `tenant_id` must equal the Tenant bound to `session_user`;
- Area, Project, and Session values must resolve below that bound Tenant;
- missing, unknown, disabled, expired, or conflicting identity and scope fail
  closed before protected data is read or changed; and
- an OIDC Tenant claim may select the initial Tenant pool only after signature,
  issuer, audience, time, and claim-shape validation completes; it cannot change
  the Tenant of an established connection or bypass the database binding; and
- request payload, unverified claim data, model output, tool output, memory
  content, or writable GUC can never select another Tenant.

The OIDC consumer is the current untrusted-edge adapter. Its validated signed
Tenant claim and database-resolved Principal form the trusted routing context
used to choose the initial pool. Repository methods that accept a
`RuntimeContext` directly are trusted internal APIs, not public authentication
surfaces; batch or service adapters must authenticate and bind equivalent
context before calling them. Workload- or channel-bound routing attestation is
compatible later hardening, but is not part of FND-06 and requires a separate
accepted decision before becoming mandatory.

RLS and `FORCE ROW LEVEL SECURITY` remain mandatory on protected tables. They
are defense in depth and enforce row scope, but they are not the sole Tenant
boundary. Gate functions, authority checks, immutable catalog lineage,
restricted privileges, and audit remain mandatory.

Shared cross-Tenant Runtime database logins and shared cross-Tenant connection
pools are prohibited for productive customer data. General cryptographic
context attestation is explicitly outside this decision and is not required to
implement the accepted Tenant-bound identity model.

Owner, migration, provisioner, backup, restore, and break-glass identities are
not Runtime identities. They remain separate, least-privileged, explicitly
authorized, time-bounded where applicable, and independently audited. They may
not be used as application Runtime credentials.

## Connection and Pool Contract

- Pool ownership is keyed by immutable `tenant_id`; a pool cannot accept a
  request for another Tenant.
- Every connection is authenticated with the Runtime login bound to the pool's
  Tenant.
- Acquisition verifies through `session_user` that the expected active Tenant,
  database target, and credential revision match the pool generation before any
  protected operation.
- A Tenant mismatch invalidates and evicts the connection; it is never repaired
  by changing a GUC or role.
- Pool reset, retry, reconnect, failover, rotation, and worker reuse preserve
  the same Tenant binding.
- Credentials, pool handles, and connections cannot be cached or reused under a
  cross-Tenant key.
- Credential rotation and revocation close or evict affected connections so an
  old authenticated session cannot outlive the authorized credential state.

## Deployment Compatibility

This decision does not mandate a separate PostgreSQL cluster, deployment,
database, or schema for each Tenant. A shared deployment remains permitted only
when every Runtime identity and pool is Tenant-bound as specified here and all
RLS, FORCE, privilege, gate, catalog, audit, backup, restore, and operational
controls remain effective.

A later dedicated database or deployment per Company remains compatible with
this decision. Deployment consolidation may not weaken the Tenant-bound Runtime
identity contract.

## Consequences

- Provisioning, deprovisioning, credential rotation and revocation, pool
  eviction, and protected login-to-Tenant mapping become release-critical.
- Database gates and RLS policies must derive Tenant authority from immutable
  session identity and reject mismatched application context.
- OIDC Principal resolution and `principal_scope_bindings` authority checks
  remain mandatory; Tenant-bound database identity does not replace actor or
  capability authorization.
- Tenant-specific credentials and pool topology become protected operational
  configuration with secret-custody, monitoring, incident-response, migration,
  rollback, and recovery requirements.
- Backup and restore evidence must preserve or explicitly remap Tenant
  association without making a Runtime identity cross-Tenant.
- A shared cross-Tenant Runtime credential, cross-Tenant pool reuse, or a path
  that permits a connection to change Tenant is a release stop for productive
  customer data.
- Existing single shared Runtime credentials require a guarded migration and
  cannot remain as a production compatibility fallback.

## Invariants and Constraints

- One Runtime database login identity maps to exactly one active Tenant.
- One Runtime connection pool serves exactly one Tenant.
- One established Runtime connection has one immutable Tenant identity.
- PostgreSQL anchors Tenant identity in `session_user`, not `current_user` or a
  writable GUC.
- Runtime context may narrow Area, Project, Session, role, and capability; it
  may never expand or replace the database-bound Tenant.
- RLS and FORCE remain enabled on every protected table.
- The Tenant-bound identity does not grant Principal authority; current,
  enabled, unexpired bindings and operation-specific capabilities remain
  required.
- Runtime credentials cannot be owner, migration, provisioner, backup, restore,
  superuser, or `BYPASSRLS` credentials.
- Unknown or conflicting Tenant identity, lineage, role, scope, authority,
  credential, connection, or pool state is denied by default.

## Rejected Alternatives

### Shared Runtime login plus writable Tenant GUC

Rejected because the application could select a different fully valid Tenant
context and the database would have no independent Tenant identity against
which to reject it.

### RLS as the only Tenant boundary

Rejected because RLS can enforce only the identity and scope inputs available
to its policies. RLS and FORCE remain required defense in depth.

### General cryptographic context attestation

Not selected. Tenant-bound database logins and pools provide the required
database-visible Tenant anchor with lower protocol and operational complexity.
A future attestation design would require a separate accepted ADR.

### Mandatory database or deployment per Tenant

Not required by this decision. Physical separation is compatible and may be
selected later, but distinct Tenant-bound Runtime identities and pools are the
minimum accepted database Runtime boundary.

## Relationship to Earlier Decisions

- ADR-002 is amended by making authenticated Runtime scope database-anchored at
  the Tenant dimension.
- ADR-003 is amended by making Tenant-bound Runtime roles, pools, and their
  lifecycle part of the authoritative PostgreSQL ledger boundary.
- ADR-005 is amended by making shared cross-Tenant Runtime database identity a
  non-configurable Security Floor prohibition for productive customer data.
- ADR-013 is amended by requiring Tenant-specific Psycopg pools and immutable
  connection Tenant identity while preserving explicit short transactions.
- ADR-015 remains Memory Core subsystem authority and is strengthened by this
  database-enforced Tenant identity boundary.
- ADR-016 retains the hierarchy catalog and RLS scope model; this decision adds
  the immutable session-login anchor beneath Runtime-supplied scope.
- ADR-018 remains the complete product-boundary decision; this decision
  strengthens its Protected Control Plane identity and scope contract.

No earlier ADR is superseded. ADR-018 remains the current governing product
decision.

## Validation

Implementation evidence must prove:

- provisioning creates distinct NOINHERIT/NOBYPASSRLS Runtime logins bound to
  exactly one Tenant;
- a real Tenant-A login cannot read or write Tenant-B data through direct SQL,
  any gate, forged GUCs, valid foreign Principal values, role changes, pool
  reuse, retry, or stale connection state;
- a connection cannot change Tenant and mismatched pool acquisition fails
  closed and evicts the connection;
- each checkout matches the expected database target and credential revision,
  so a stale secret or incorrectly restored route cannot pass as the current
  pool generation;
- OIDC Principal resolution and missing, expired, disabled, or insufficient
  authority continue to deny correctly;
- RLS and FORCE guards cover every protected table;
- credential rotation, revocation, migration, rollback, backup, restore, and
  incident procedures preserve the Tenant binding; and
- focused PostgreSQL integration tests, the complete quality gate, and an
  independent security review pass before the release stop is removed.
