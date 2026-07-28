# S1-14.4 and S1-11.2 Runtime Enforcement Test Strategy v1

## Status and purpose

This document defines the test architecture for the S1-14.4 privacy runtime
enforcement contract and its S1-11.2 protected-storage integration. It is a
technical preparation artifact. It does not determine lawfulness, approve a
special-category condition, activate processing, or prove that either backlog
item is implemented.

The repository currently provides documentation-only evidence intakes for
Article 6, Article 9, Article 10, consent, legitimate interests, data-object
cataloguing, and related deployment review. Those artifacts are not runtime
authorization. The current Memory Core stores a technical protection
classification and a free-form purpose, but it does not bind a protected write
to an accepted processing basis, an additional special condition, retention,
qualified review evidence, or an approved privacy-policy version.

The strategy therefore has two strictly separated test sets:

1. **Preparation tests**, which are permitted before authoritative approval and
   must prove that runtime activation is unavailable and no input can produce
   `ALLOW`.
2. **Post-authorization target tests**, which must not be implemented as passing
   runtime evidence until the normative contract, deployment scope, accountable
   owner decision, and required qualified privacy or legal review are accepted.

Passing preparation tests means only that the repository fails closed while the
authorization contract is incomplete. It is not evidence of operational
acceptance for S1-14.4 or S1-11.2.

## Test authority boundary

Repository code, migrations, accepted ADRs, and the accepted runtime contract
define executable behavior. Tests may verify those sources but may not invent
missing legal, organizational, or deployment decisions.

The candidate decision vocabulary is:

```text
ALLOW
DENY
REQUIRE_HUMAN_REVIEW
REQUIRE_ADDITIONAL_EVIDENCE
EXPIRED
REVOKED
CONFLICT
UNKNOWN
```

Only `ALLOW` may authorize a protected mutation. Before authoritative approval,
the evaluator is disabled and must never emit `ALLOW`; the exact mapping among
the remaining outcomes and reason codes is a contract decision, not a test
author decision.

The candidate policy lifecycle is:

```text
DRAFT
PENDING_REVIEW
APPROVED
ACTIVE
SUSPENDED
REVOKED
EXPIRED
REJECTED
SUPERSEDED
```

Before authoritative approval, no transition may reach `ACTIVE` and no test may
describe a simulated active policy as production authority.

## Phase A: preparation tests before authoritative approval

Preparation tests are allowed to validate schemas, strict types, immutable
bindings, disabled control surfaces, and fail-closed defaults. They must not
encode a positive processing rule or a deployment-specific `ALLOW` fixture.

### Proposed preparation test files

| Proposed path | Required preparation evidence |
| --- | --- |
| `tests/architecture/test_s1_14_4_runtime_enforcement_contract.py` | The draft contract declares `runtime_enabled=false`, lists every unresolved decision, identifies its owner and review status, contains the candidate outcomes and lifecycle states, and prohibits runtime or legal claims. |
| `tests/architecture/test_s1_11_2_runtime_integration_contract.py` | S1-11.2 may capture and validate metadata but cannot determine lawfulness, supply a missing condition, resolve a conflict, or write protected state without the S1-14.4 decision and owning mutation gate. |
| `tests/unit/test_privacy_processing_metadata.py` | Strict, frozen, extra-forbid schemas reject missing, unknown, contradictory, scope-widening, naive-time, non-versioned, or mutable metadata. This test does not declare which legal combination is sufficient. |
| `tests/unit/test_privacy_policy_disabled_evaluator.py` | The evaluator reports `runtime_enabled=false`; every input, including apparently complete input, returns a non-`ALLOW` outcome with an authorization-pending reason. Exceptions and unavailable dependencies also return no `ALLOW`. |
| `tests/property/test_s1_14_4_disabled_policy_state_machine.py` | Generated lifecycle sequences cannot reach `ACTIVE`; no sequence can store protected data; replay, field deletion, field mutation, clock advance, or scope substitution cannot broaden the disabled state. |
| `tests/traceability/test_s1_14_4_s1_11_2_runtime_traceability.py` | Every preparation claim maps to a versioned contract field and test. Operational criteria remain explicitly unfulfilled rather than being counted as implemented coverage. |

### Preparation invariants

1. `runtime_enabled` is exactly `false` while any required decision is not
   authoritatively decided.
2. The disabled evaluator has no `ALLOW` branch, configuration override,
   environment-variable override, caller override, or fallback allow-list.
3. Unknown or contradictory data classification is rejected before protected
   persistence.
4. Missing purpose, processing basis, required additional condition, retention,
   approval, safeguard, evidence, policy version, owner, or auditability cannot
   be compensated by another favorable field.
5. Request payloads, prompts, observations, model output, memory content, tool
   output, or catalogue labels cannot establish authenticated scope or trusted
   review evidence.
6. Draft evidence, evidence-intake completion, schema validity, and a passing
   test suite never activate a policy.
7. A disabled decision creates no protected mutation and cannot be reused as a
   future approval.
8. S1-11.2 metadata validation remains separate from S1-14.4 policy evaluation.
9. Existing Article 6, Article 9, Article 10, consent, and data-object catalogue
   preparation artifacts retain their explicit non-runtime boundary.
10. A generated model or deterministic test double is labelled as such and is
    never reported as PostgreSQL, migration, restore, or production evidence.

### Preparation property and state-machine model

The preparation state machine has an intentionally small oracle:

```text
contract_authorization = pending
runtime_enabled = false
active_policy = none
protected_mutation_count = 0
```

Generated operations should include schema validation, decision submission,
owner-review submission, qualified-review submission, evidence expiry,
evidence revocation, purpose change, classification change, policy-version
change, scope substitution, replay, activation attempt, and storage attempt.
After every generated step, all four oracle values must remain unchanged except
for non-authorizing draft evidence history. The model must not pretend to test
database roles, transaction atomicity, current authority, or a real reviewer.

## Phase B: post-authorization target tests

Post-authorization tests become implementable only after all of the following
are repository-visible and accepted for the exact deployment scope:

- the normative S1-14.4 runtime contract and machine-readable schema;
- supported jurisdictions, environments, data classes, purposes, processing
  bases, additional conditions, safeguards, retention rules, and exclusions;
- deterministic outcome and reason-code semantics;
- lifecycle transition roles and evidence requirements;
- accountable owner approval and required qualified privacy or legal review;
- policy/evidence custody, authenticity, validity, revocation, and version rules;
- S1-11.2 protected-record metadata and integration contract;
- database ownership, transaction, reconciliation, backup, and restore rules;
- closure of all Critical and High security, privacy, and architecture findings.

### Proposed post-authorization test files

| Proposed path | Required target evidence |
| --- | --- |
| `tests/unit/test_privacy_policy_evaluator.py` | Accepted positive and negative decision matrix, exact reason codes, time validity, policy selection, additional-condition rules, safeguards, retention, and approval requirements. |
| `tests/unit/test_privacy_policy_lifecycle.py` | Every accepted transition, rejected transition, authorized actor, evidence precondition, version rule, revocation rule, and terminal-state rule. |
| `tests/unit/test_s1_11_2_protected_record_metadata.py` | Every protected record carries the accepted classification, purpose, basis, additional condition when required, subject reference, source, retention, protection, policy version, approval, and evidence references. |
| `tests/property/test_s1_14_4_privacy_policy_properties.py` | Single-field mutation, incompleteness, determinism, digest binding, non-widening, expiry, revocation, conflict, and unknown-value properties over the accepted policy domain. |
| `tests/property/test_s1_14_4_privacy_enforcement_state_machine.py` | Generated policy lifecycle, decision, storage, suspension, revocation, expiry, supersession, purpose change, classification change, and reconciliation sequences. |
| `tests/integration/test_s1_11_2_privacy_gate_pipeline.py` | Application sequence is metadata validation, classification validation, S1-14.4 decision, owning mutation gate, then atomic storage and audit. Every non-`ALLOW` stops before repository mutation. |
| `tests/database/test_privacy_enforcement_gate.py` | Real PostgreSQL gate re-evaluates current policy and evidence immediately before commit and atomically binds decision, protected mutation, receipt, and audit. |
| `tests/database/test_privacy_enforcement_isolation.py` | Runtime roles cannot directly read or mutate policy, evidence, decision, audit, or protected data tables; RLS and immutable login-to-Tenant binding prevent cross-scope reuse. |
| `tests/database/test_privacy_enforcement_concurrency.py` | Revocation versus storage, supersession versus storage, duplicate request, stale policy cache, and conflicting policy-version races have one serializable, fail-closed outcome. |
| `tests/database/test_privacy_enforcement_failures.py` | Database, decision persistence, audit, protected mutation, timeout, process interruption, corrupt evidence, and ambiguous commit failures cannot produce an unaudited protected mutation or blind retry. |
| `tests/migrations/test_privacy_enforcement_schema.py` | New tables, columns, constraints, indexes, triggers, functions, ownership, grants, RLS, `FORCE ROW LEVEL SECURITY`, safe `SECURITY DEFINER` search paths, and no general-role writes. |
| `tests/database/test_privacy_enforcement_upgrade.py` | Fresh and previous-schema upgrades converge; legacy or partially classified rows are blocked or quarantined according to the accepted migration contract and are never permissively backfilled. |
| `tests/e2e/test_s1_11_2_protected_storage.py` | Authenticated request through S1-11.2, S1-14.4, PostgreSQL mutation, audit, receipt, and readback for accepted positive cases and all critical negative cases. |
| `tests/database/test_privacy_policy_restore_reconciliation.py` | An isolated restore cannot serve or reactivate stale approvals; current revocation, expiry, policy version, scope, audit continuity, and readiness must reconcile before any protected processing. |

### Post-authorization decision properties

The pure evaluator must prove at least these properties over the accepted
domain:

- no incomplete metadata set returns `ALLOW`;
- no unknown or contradictory data class returns `ALLOW`;
- an accepted general processing basis cannot compensate for a missing required
  additional special condition;
- expired, revoked, suspended, rejected, or superseded evidence never returns
  `ALLOW`;
- a purpose, classification, jurisdiction, environment, scope, policy version,
  evidence, safeguard, retention, approval, actor, or protected-payload digest
  change invalidates a prior decision;
- an authority or approval can narrow but never widen authenticated scope;
- the same canonical inputs and policy version produce the same outcome and
  reason codes;
- changing any protected input changes the canonical binding digest;
- cached decisions are valid only for their exact binding and current validity
  interval;
- only an accepted `ACTIVE` immutable policy version can participate in an
  `ALLOW` decision.

The property suite should use a bounded pull-request profile and a larger
scheduled profile only after runtime profiling establishes a deterministic time
budget. Trace count is evidence metadata, not a substitute for domain coverage,
state coverage, or live database tests.

### Post-authorization state-machine invariants

The generated state machine should model immutable policy versions, policy
lifecycle, approvals, evidence validity, authenticated scope, decisions,
protected records, audit events, receipts, retention actions, and a controllable
clock. Its invariants are:

1. Every protected record references exactly one committed `ALLOW` decision.
2. The decision binding exactly matches actor, Tenant, Area, Project, Session,
   operation, resource, data classification, purpose, processing basis,
   additional condition, safeguards, retention, policy version, evidence,
   authority, approval, and protected-payload digest as required by the accepted
   contract.
3. Every committed protected mutation has its decision event, mutation receipt,
   and audit evidence in the same authoritative transaction.
4. Every non-`ALLOW` outcome leaves protected state unchanged.
5. A denied, rolled-back, or indeterminate operation cannot be represented as a
   successful record.
6. `REVOKED`, `EXPIRED`, `REJECTED`, and `SUPERSEDED` never transition directly
   to `ACTIVE`; reactivation requires a new accepted immutable version where the
   contract permits it.
7. A purpose or classification change invalidates prior authorization and
   triggers the accepted stop, block, deletion, or review workflow.
8. Scope and authority never widen through derivation, replay, cache, restore,
   or retry.
9. Repeated execution is deterministic and idempotent for an exact request;
   changed-payload replay is denied.
10. Audit and receipt cardinality remain consistent with committed mutations and
    separately required denial events.

### Live PostgreSQL fixtures

Extend the disposable PostgreSQL 18 fixture pattern in `tests/database/conftest.py`
without weakening its generated database-name guard, redacted DSN handling, or
least-privilege runtime identities. Proposed shared fixtures belong in:

- `tests/support/privacy_enforcement_fixtures.py` for frozen clocks, accepted
  policy/evidence factories, canonical digests, authenticated scope, and
  single-defect negative cases;
- `tests/support/privacy_enforcement_harness.py` for deterministic pure-model
  state and explicit failpoints;
- `tests/database/conftest.py` for disposable PostgreSQL policy, evidence,
  reviewer, decision, retention, and runtime-role records once their schemas are
  accepted.

Required fixture families are:

- one accepted ordinary-personal-data case;
- one accepted special-category case with its exact additional condition and
  safeguards;
- an Article 10 case only if the accepted scope supports it;
- one defect per required field;
- unknown, contradictory, stale, expired, revoked, suspended, rejected, and
  superseded records;
- wrong Tenant, Area, Project, Session, purpose, jurisdiction, environment,
  policy version, actor, reviewer role, evidence digest, and payload digest;
- reused evidence outside its exact scope;
- concurrent activation, revocation, supersession, and storage barriers;
- legacy rows with no accepted classification or authorization binding;
- restored rows carrying policy state older than the authoritative revocation or
  supersession watermark.

Fixtures must use synthetic category-level values and opaque references. They
must not contain real personal data, special-category values, criminal-offence
data, legal advice, credentials, or production evidence.

### PostgreSQL and failure-injection expectations

The live gate must prove the preferred transaction sequence:

```text
authenticated scope
-> strict metadata and classification validation
-> load current immutable policy and evidence
-> deterministic decision
-> append decision/audit intent as required
-> protected mutation, receipt, and audit
-> atomic commit
```

Failure injection must cover at least:

- policy/evidence lookup failure;
- database unavailability and statement timeout;
- decision-record insertion failure;
- audit insertion or hash-chain failure;
- protected mutation failure;
- receipt insertion failure;
- process interruption before commit;
- stale cache and policy-version mismatch;
- concurrent revocation or supersession;
- corrupted or digest-mismatched evidence;
- partial migration failure;
- restore of stale approval or policy state;
- loss of the client response around commit.

Failures before commit must roll back all transaction-owned artifacts. A lost
response after a possible commit must enter the accepted indeterminate and
reconciliation path; it must not trigger a blind retry. A network-partition test
is meaningful only if the accepted architecture contains a remote policy or
evidence service. An in-process or PostgreSQL-resident evaluator should instead
test repository unavailability, timeout, stale state, and transaction failure.

### Migration tests

The existing migration validator must continue to prove:

- contiguous forward-only migration files;
- no top-level transaction control inside a migration;
- PostgreSQL 18 execution;
- equal security- and behavior-relevant schema digests for fresh and
  previous-schema upgrade paths;
- redacted, secret-free validation output.

Privacy-specific migration tests additionally must prove:

- no default legal basis, special condition, purpose, approval, retention rule,
  or `ALLOW` decision is invented for legacy rows;
- unknown legacy state is blocked or quarantined exactly as the accepted
  migration contract specifies;
- the migration cannot leave a serving runtime with a partially installed gate;
- protected tables have immutable scope columns, RLS, forced RLS, restrictive
  privileges, and gate-only writers;
- migration failure rolls back the affected migration and does not weaken the
  previous gate;
- policy versions, decision bindings, evidence references, audit records, and
  receipts preserve canonical digests and referential integrity;
- rollback of a deployment uses a separately accepted forward remediation or
  reconciliation path rather than destructive schema downgrade assumptions.

### End-to-end and restore tests

The S1-11.2 end-to-end suite must use the real application service and the real
disposable PostgreSQL gate. A valid accepted case must demonstrate metadata
capture, S1-14.4 decision, atomic storage, decision/audit evidence, receipt, and
scope-bound readback. Each negative case must demonstrate the exact blocking
outcome and absence of protected mutation.

Restore testing is post-authorization and post-recovery-implementation evidence.
A `pg_dump` or database start alone cannot prove operational recovery. The
isolated restore test must begin non-serving, reconcile current revocation,
expiry, supersession, scope lineage, migration version, RLS, gate ownership,
audit continuity, retention, and deletion state, and remain not-ready on any
unknown or conflict. Only the separately governed recovery decision may permit
cutover.

## Verification gates

The gates are ordered and non-compensatory.

### Gate T0: preparation contract shape

- Draft machine-readable schemas parse and reject unknown fields.
- Every unresolved decision has an owner, evidence requirement, status, and
  acceptance criterion.
- `runtime_enabled=false` and the non-runtime claim boundary are explicit.

### Gate T1: disabled runtime

- Disabled evaluator tests pass for every generated input.
- Activation is unavailable.
- Protected mutation count remains zero.
- No positive `ALLOW` fixture exists.

Passing T0 and T1 permits only technical preparation.

### Gate T2: authoritative contract acceptance

- Exact contract version, deployment scope, owners, qualified reviews,
  restrictions, and revalidation date are accepted and repository-visible.
- Critical and High contract findings are closed.
- Positive test vectors are derived from, and traceable to, the accepted
  contract rather than authored independently.

### Gate T3: pure evaluator and lifecycle

- Unit, table-driven negative, property, and state-machine tests pass.
- Exact reason codes and transition roles match the accepted contract.
- Determinism, expiry, revocation, conflict, non-widening, and digest binding are
  proven without runtime mocks being reported as database evidence.

### Gate T4: migration and database boundary

- Fresh and upgrade migrations pass on PostgreSQL 18.
- Role, privilege, RLS, forced-RLS, function ownership, safe search path, and
  direct-bypass tests pass.
- Legacy data is blocked or reconciled without permissive defaults.

### Gate T5: atomic runtime enforcement

- Positive and negative live PostgreSQL tests pass.
- Decision, mutation, receipt, and audit atomicity is proven.
- TOCTOU, replay, concurrent revocation, failure injection, and reconciliation
  tests pass.

### Gate T6: S1-11.2 integration

- Every protected storage path invokes S1-14.4 immediately before commit.
- No alternate repository or direct SQL path bypasses the gate.
- End-to-end positive, negative, scope, retention, expiry, and revocation tests
  pass.

### Gate T7: recovery and release evidence

- Isolated restore and stale-approval reconciliation tests pass where recovery
  is in deployment scope.
- Independent Security, Privacy, and Architecture reviews have no open Critical
  or High findings.
- Required CI checks, independent review, traceability, runbooks, and release
  evidence are current for the exact commit.

Only T0 and T1 are available before authoritative approval. Failure of any later
gate blocks the affected implementation, release, or completion claim.

## CI requirements

Preparation tests should run in the existing locked quality workflow because
they require no external service and must remain deterministic. They must not be
skipped conditionally.

After authoritative approval, CI should provide a distinct required privacy
runtime job, for example in a proposed
`.github/workflows/privacy-runtime.yml`, with:

- pinned CPython, uv, dependencies, Actions, and PostgreSQL 18 image;
- locked environment synchronization;
- contract, unit, property, and state-machine tests;
- migration validation before runtime tests;
- a generated disposable database and mandatory `MIGRATION_ADMIN_DSN`;
- live PostgreSQL positive, negative, isolation, concurrency, and failure tests;
- explicit failure if a required live test is skipped;
- secret-free artifacts containing contract version, migration plan digest,
  schema digests, test identifiers, result counts, and commit SHA;
- a timeout budget based on measured runtime, not by reducing invariant or
  negative-path coverage;
- no production credentials, personal data, reviewer evidence payloads, or legal
  documents in fixtures or artifacts.

Restore/PITR evidence should run in a separate isolated, non-serving scheduled
or explicitly dispatched job only after an accepted operational recovery
contract exists. It must not be represented by a mocked restore in the pull
request quality job.

Required checks must distinguish:

1. static contract preparation;
2. pure evaluator and property evidence;
3. PostgreSQL migration and enforcement evidence;
4. end-to-end protected-storage evidence;
5. restore and reconciliation evidence, where applicable.

A green static or pure-model job cannot compensate for a missing live database,
integration, restore, approval, or independent-review gate.

## Claim limits

This strategy does not establish:

- a legal opinion or general finding of lawful processing;
- an Article 6 basis, Article 9 condition, Article 10 authorization, consent
  validity, legitimate-interest conclusion, or safeguard sufficiency;
- authorization for a jurisdiction, purpose, Tenant, Area, Project, Session,
  environment, data class, recipient, processor, transfer, or retention rule;
- an authenticated reviewer, accountable owner, authority grant, approval, or
  release decision;
- a runtime policy, active evaluator, protected mutation gate, migration,
  deployment, backup, restore, deletion process, or incident process;
- production readiness, recovery readiness, completion of S1-14.4, or
  completion of S1-11.2;
- that passing schema, unit, property, state-machine, mocked integration, or
  deterministic-harness tests proves PostgreSQL enforcement or operational
  behavior;
- transferability of a future accepted decision to another scope, purpose,
  policy version, evidence set, artifact, environment, or jurisdiction.

Until the authoritative contract and reviews satisfy Gate T2, the only valid
runtime conclusion is: authorization is unavailable, `runtime_enabled=false`,
no decision may be `ALLOW`, and protected processing remains blocked.
