# Tenant-Bound Database Operations

## Scope and readiness boundary

This runbook defines the required operating contract for ADR-019 and FND-06.
It applies to the target deployment model in which one PostgreSQL installation
may host multiple Tenants, while every Tenant uses a dedicated database login
and a dedicated connection pool. It also defines the migration seam to a later
one-Company-per-database or one-Company-per-instance topology.

This document is not production authorization. Operators must not admit real
customer data until the implementation, live PostgreSQL tests, independent
security review, production secret store, backup custody, restore evidence,
RPO/RTO, monitoring, and all other release stops in the production-readiness
ledger are complete.

The mandatory invariant is:

```text
trusted request Tenant
    == pool Tenant
    == database login Tenant
    == database-bound Tenant
and checkout database target + credential revision
    == pool database target + credential revision
```

A mismatch, unknown mapping, unavailable secret, failed reset, stale credential,
or incomplete lifecycle operation fails closed. No common customer-data runtime
login or cross-Tenant fallback pool is permitted.

## Roles and responsibilities

| Responsibility | Required owner | Prohibited shortcut |
| --- | --- | --- |
| Tenant catalog approval | Authorized platform operator | Runtime self-registration |
| Database role creation and mapping | Restricted provisioner | Application-admin SQL or manual production SQL |
| Secret generation and storage | Provisioner plus approved secret store | Passwords in repository, Notion, logs, command history, CI output, or PR text |
| Pool creation and eviction | Runtime control plane | Request-selected DSN or common fallback pool |
| Rotation and revocation | Credential operator | Password replacement without draining and terminating old sessions |
| Backup and restore | Recovery operator with independent witness | Restoring directly into a serving database |
| Incident containment | Incident commander or Safety Supervisor | Cognitive-plane or model-controlled recovery |

The provisioner, migration owner, and runtime must use separate credentials.
Tenant runtime logins are `NOSUPERUSER`, `NOBYPASSRLS`, preferably
`NOINHERIT`, own no tables or schemas, have no schema `CREATE`, and cannot
become another Tenant's role. Privileged administration credentials never enter
runtime pools.

## Secret store and naming

Use a deployment-approved secret store with encryption at rest, access audit,
versioning, explicit workload identity, and immediate revocation. A recommended
logical name is:

```text
neural-brain/tenants/<tenant_id>/database/runtime
```

The secret value contains only the connection material required by the
deployment. Store non-secret routing metadata separately, including the stable
Tenant ID, database endpoint identifier, database name, credential version,
creation time, and rotation state. Do not use a Company display name as an
authorization key.

Secret access is limited to the provisioner, the exact Tenant runtime workload,
the rotation controller, and audited break-glass recovery. A workload may read
only its Tenant secret. Secret values, DSNs, passwords, bearer tokens, and
private keys must never appear in repository files, Notion, audit payloads,
metrics, traces, test output, exception chains, or pull-request descriptions.

## Credential generation

1. Resolve the canonical Tenant from an authorized provisioning request.
2. Generate a unique role name from an opaque, collision-resistant Tenant role
   identifier. Do not embed unescaped customer-supplied text in SQL identifiers.
3. Generate a cryptographically random credential with at least 256 bits of
   entropy, or obtain an equivalent credential from the secret store. Never ask
   an operator to invent a password.
4. Create the Tenant login and database-to-Tenant mapping through the restricted
   provisioner. Set `NOSUPERUSER`, `NOBYPASSRLS`, `NOCREATEDB`, `NOCREATEROLE`,
   `NOREPLICATION`, no ownership, and only the exact connection and gate grants.
5. Write the credential to the secret store without logging its value.
6. Verify the catalog, membership, ownership, schema privileges, cross-Tenant
   role denial, and bound-Tenant lookup using a fresh connection as that login.
7. Activate routing only after both the database and secret-store evidence pass.

Database DDL and secret-store writes do not form one atomic transaction. Model
provisioning as a fail-closed workflow: an incomplete Tenant is never routable;
on failure, revoke login, terminate any sessions, remove grants and mapping,
revoke the secret version, and record a secret-free failure result. A retry must
prove that it does not add or widen privileges.

## Tenant provisioning

The controlled provisioning operation must produce an auditable, secret-free
result containing the request ID, Tenant ID, role identifier, credential
version identifier, database target identifier, exact policy/configuration
version, verification results, actor, timestamps, and final state.

Required sequence:

1. create or validate the Tenant catalog record;
2. create the Tenant login and any controlled non-login gate memberships;
3. create the secret version without exposing it;
4. atomically bind `session_user` to exactly one Tenant and append the lifecycle
   event through the protected database function;
5. explicitly revoke `PUBLIC`, schema creation, direct table access, and
   unrelated function execution;
6. verify role attributes, membership graph, ownership, grants, binding, RLS,
   `FORCE ROW LEVEL SECURITY`, and positive Tenant-local gate access;
7. verify foreign-Tenant read, write, context assertion, and role assumption
   denial;
8. mark the Tenant routable and create its pool only after every check passes.

Existing provisioning is idempotent only when the catalog identity, database
binding, role attributes, grants, and secret metadata match the requested
configuration. Any drift is an error requiring reconciliation; it must not be
silently accepted or repaired by granting broader access.

## Tenant-specific pool lifecycle

### Pool key and creation

The trusted resolver selects a pool from authenticated routing context, never
from a request body, prompt, model response, host header, tool output, memory
content, or an unverified claim. The current OIDC adapter may use its signed
Tenant claim only after issuer, audience, signature, time, and claim validation
has completed. After checkout, neither that claim nor a directly constructed
internal `RuntimeContext` can replace the database-bound Tenant. The internal
pool key must include at least:

```text
(tenant_id, database_endpoint_id, database_name, credential_version)
```

Each pool is created with exactly one Tenant credential. A pool object and each
connection it owns retain immutable Tenant metadata for their full lifetime.
The resolver must not mutate an existing pool into another Tenant pool.

Secret lookup failure, unknown Tenant, mapping mismatch, capacity exhaustion,
or pool creation failure returns a stable fail-closed error. There is no shared
pool, default Tenant, last-known cross-Tenant credential, or retry with another
Tenant's connection.

### Connection checkout and return

On every checkout, call the protected database-identity lookup keyed by
`session_user` and verify its Tenant, current database target, and credential
revision against the pool generation.
Set only narrower Area, Project, Session, and Principal transaction context.
Tenant context may narrow authorization but can never change or expand the
database-bound Tenant.

Before return, complete or roll back the transaction and run the pool's trusted
session-reset hook. Reset role and session settings, close cursors, release
advisory locks, clear notifications and temporary application state, and verify
the bound Tenant again. `DISCARD ALL` or equivalent cleanup must run only where
the driver and transaction state permit it. Any reset or verification failure
closes the physical connection; it is never returned to the pool.

### Limits and eviction

The deployment must define and test:

- maximum resident Tenant pools;
- maximum connections per Tenant and globally;
- idle pool lifetime and connection maximum age;
- request queue limit and timeout;
- least-recently-used or equivalent deterministic eviction;
- protected capacity for recovery and administration;
- credential maximum age and rotation deadline.

These values are deployment-specific and currently remain production release
evidence, not repository defaults. Eviction drains only the selected Tenant
pool, closes every physical connection, removes cached secret material, and
records secret-free evidence. Capacity pressure must reject or evict safely;
it must never combine Tenants or select a common fallback.

## Credential rotation

ADR-019 permits exactly one active Runtime login per Tenant. Rotation therefore
changes that login's credential revision; it does not create a second active
Tenant login. Use a fail-closed, Tenant-scoped maintenance window:

1. generate a pending replacement secret version without exposing its value;
2. stop new routing to the Tenant and drain or close its old pool;
3. change the login credential and increment its protected credential revision
   in one authorized database operation;
4. terminate every remaining session for that Tenant login, because password
   change alone does not end existing authenticated connections;
5. verify the pending secret with a fresh isolated connection, including the
   protected Tenant binding and exact credential revision;
6. create a new pool keyed by the new credential revision and resume routing;
7. disable or delete the old secret version;
8. prove that the old credential fails and no other Tenant pool changed;
9. close the rotation record with independent evidence.

If verification fails after the database credential changes, keep the Tenant
offline and issue another controlled revision. Do not route back to an old
session or use another Tenant or a shared runtime credential as rollback.

## Revocation and emergency rotation

For planned revocation, stop new routing, drain the Tenant pool, set the login
to `NOLOGIN` or drop it as appropriate, revoke memberships and connection
rights, terminate remaining sessions, revoke the secret, and verify denial with
a fresh client.

For suspected credential compromise, do not wait for graceful drain:

1. disable routing for the affected Tenant;
2. revoke login and terminate all sessions for the exact compromised role;
3. evict every pool entry using its credential version;
4. revoke the secret version and issue a new independently verified credential;
5. preserve database, secret-store, routing, and audit evidence;
6. review access, role changes, denied Tenant mismatches, exports, backup access,
   and operator actions for the exposure window;
7. restore service only after containment and authorization review.

The expected blast radius of a compromised Tenant runtime credential is that
Tenant's permitted database operations. This claim holds only when role
membership, database mapping, pool routing, RLS, and gate controls are intact.
Compromise of the provisioner, migration role, PostgreSQL superuser, secret
store administrator, host, or backup custody is outside that containment claim
and requires broader incident response.

## Deprovisioning

Deprovisioning is a governed lifecycle, not immediate data deletion:

1. authorize and record the customer termination or suspension decision;
2. disable request and job routing;
3. drain and close all Tenant pools;
4. revoke login, terminate sessions, revoke grants and memberships, and remove
   the active database mapping;
5. revoke every live secret version;
6. verify that old credentials and role assumptions fail;
7. apply retention, legal hold, export, deletion, and backup-expiry policy;
8. retain only minimal non-secret audit evidence permitted by policy.

Do not drop Tenant data, roles, or backup material while legal hold, authorized
export, incident evidence, or verified deletion propagation remains unresolved.

## Monitoring and telemetry

Emit structured, secret-free signals for:

- active and idle pools, connections, queue depth, checkout latency, and
  evictions by opaque Tenant reference;
- pool-to-login and login-to-Tenant verification failures;
- secret lookup, expiry, revocation, and rotation state;
- denied cross-Tenant context assertions and role assumptions;
- direct-table and schema-creation denial;
- provisioning and deprovisioning state, rollback, and drift;
- unexpected role attributes, memberships, ownership, or grants;
- long-lived connections that exceed credential or pool lifetime;
- backup/restore Tenant-mapping verification and reconciliation state.

Alerts must not include DSNs, credentials, bearer tokens, private keys, memory
content, or raw customer identifiers. Unknown telemetry state cannot be used as
evidence of isolation or readiness.

## Backup and restore mapping

On a shared PostgreSQL database, a physical or whole-database backup may contain
multiple Tenants even though runtime credentials are Tenant-bound. Tenant
credentials therefore do not make backup custody Tenant-specific.

Every backup manifest must bind the database target, migration ledger, Tenant
catalog snapshot, tenant-role mapping version, policy version, encryption key
reference, creation time, retention class, and integrity digest. It must never
contain a runtime password. Restore only into an isolated, non-serving target.
Before traffic, verify migrations, RLS and FORCE, policies, role attributes,
role-to-Tenant mappings, secret versions, audit continuity, retention/deletion
state, and cross-Tenant negative tests. Quarantine any ambiguous mapping.

Production backup storage, encryption, retention, schedule, alerting, RPO/RTO,
external custody, per-Tenant recovery semantics, and an independently witnessed
restore drill remain release stops. The local generic restore drill does not
close them.

## Migration to one database or instance per Company

The pool resolver must treat host, port, database, and credential version as
trusted routing metadata rather than global constants. To move one Tenant:

1. provision the target database or instance with the same protected contracts;
2. create a new Tenant-bound credential and secret on the target;
3. quiesce or fence writes for the Tenant;
4. export and restore through an approved, Tenant-complete migration process;
5. verify counts, digests, provenance, lifecycle state, audit continuity,
   policies, bindings, and negative isolation tests;
6. atomically switch only that Tenant's routing metadata and pool;
7. retain rollback fencing until reconciliation and acceptance complete;
8. deprovision the old route and data under retention policy.

The runtime contract remains `Tenant -> trusted database target -> dedicated
credential -> dedicated pool`; only the target metadata changes. A migration
must never temporarily route two Tenants through one credential or allow both
old and new writers without an accepted replication and reconciliation design.

## Audit evidence and production gate

Provisioning, rotation, revocation, pool eviction, deprovisioning, restore, and
migration evidence must identify the authorized actor, request, Tenant, role
identifier, credential version identifier, configuration/policy version,
timestamps, checks, result, and failure handling without storing secret values.

Before production approval, independently verify at minimum:

- two real restricted Tenant logins and two Tenant pools;
- positive same-Tenant read/write and denied foreign-Tenant read/write;
- denied foreign role assumption and context assertion;
- safe pool reset, eviction, exhaustion, and missing-secret behavior;
- idempotent provisioning and complete partial-failure cleanup;
- rotation, old-credential denial, emergency revocation, and deprovisioning;
- catalog guards for role attributes, ownership, grants, mappings, RLS, FORCE,
  policy predicates, and `SECURITY DEFINER` search paths;
- production backup custody, RPO/RTO, independently witnessed restore, and
  Tenant-mapping reconciliation;
- independent security review with no unresolved critical or high findings.

Until all applicable evidence exists, the system remains not approved for real
customer data.
