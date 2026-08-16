# NB-1 Database-Authoritative Model-Manifest Registry ADR-018 Revalidation Proposal v1

- Status: Proposed prerequisite; not accepted and not runtime authorization
- Task: P1 NB-1 active-model provenance gap
- Governing target: ADR-003, ADR-005, ADR-016, ADR-018, ADR-019, and Architecture Directive v4.0
- Delivery boundary: NB-1 protected provenance preparation only

## Purpose and authority

This proposal addresses a verified P1 gap in the effect-free NB-1 cognitive
checkpoint path. `PostgresCognitiveRepository` currently resolves only a
training-artifact digest from a process-local model-to-digest mapping. The
remaining active-model provenance is accepted in the caller-supplied transition
envelope and is then written as checkpoint and audit evidence. This permits a
syntactically valid but substituted parameter, code, contract, or evaluation
digest to be persisted when its training digest still matches the local map.

This is not an accepted ADR. It does not amend, reactivate, or replace an
accepted decision, and it authorizes no migration, registry, runtime path,
model activation, candidate evaluation, or NB-1 stage exit. An accepted
replacement by the authorized architecture owner is required before any
successor package may begin.

## Proposed decision

After acceptance, PostgreSQL shall be the authoritative source for immutable
active-model provenance used by the cognitive checkpoint gate. The Learning and
Model Promotion Gate is the sole writer of protected manifest and runtime
binding state. Registration is distinct from activation: recording a manifest
does not make it active, promoted, evaluatively accepted, deployable, or
authorized.

### Immutable manifest registry

The future registry records a canonical, content-addressed manifest version.
At a minimum, the protected record binds its immutable identity and digest to
the complete active-model evidence currently represented by the NB-1 model
manifest: model version, parameter digest, training-artifact digest,
training-code digest, contract digest, and evaluation-spec digest. It also
records its declared schema/profile version, immutable artifact and lineage
references, creation decision reference, and lifecycle state.

The accepted implementation must define the exact canonicalization and
collision rules before storing a record. Unknown schema/profile, malformed or
noncanonical digest, duplicate identity with a different digest, unknown
lineage, or incomplete evidence is denied. A caller-provided envelope may name
an immutable manifest identity only; it cannot supply, repair, select, or
override the evidence resolved from PostgreSQL.

### Protected runtime binding and scope

A separately protected runtime binding selects exactly one manifest version
for an authenticated operational scope and includes a monotonically increasing
binding/fence epoch. Every binding must carry immutable authenticated Tenant
and Area scope, with Project and Session when the binding is narrower. The
cognitive gate must resolve the binding in its own transaction, lock the
authoritative binding and manifest, and reject unknown, stale, revoked,
expired, scope-incompatible, or envelope-mismatched state.

A catalog-level manifest is not itself an authority grant and never creates
implicit cross-Tenant or cross-Area reuse. The accepted ADR must make any
permitted reuse explicit and preserve the ADR-016 and ADR-019 scope and
database-identity boundary.

### Gate, audit, revocation, recovery, and concurrency rules

The future cognitive gate writes only database-derived manifest identity,
manifest digest, binding identity, and binding epoch into checkpoint and audit
evidence. It must not persist caller-supplied parallel provenance as trusted
evidence. All registry, binding, activation, suspension, and revocation events
are append-only; an existing manifest or event is neither updated nor deleted.
Revocation blocks new cognitive commits immediately after its committed event.

The cognitive runtime, caller, general application roles, and evaluation roles
may read no more than the gate needs and may not register, bind, activate,
suspend, revoke, promote, or directly mutate a manifest. A safety or operations
actor may request an emergency withdrawal only through the defined protected
gate; that request does not become a state change by itself.

Checkpoint recovery may retain historic provenance for audit, but must not
resume or silently retarget a checkpoint whose resolved manifest or binding is
missing, corrupted, scope-incompatible, digest-mismatched, revoked, or
unreconciled after restore. Backup and restore readiness requires registry,
binding, revocation, and audit continuity to reconcile before the cognitive
gate is ready. Concurrent bind, revoke, and checkpoint transactions must
serialize so a commit either records one complete, current binding epoch or
fails closed; no commit may cross a revocation boundary unnoticed.

## Candidate-evaluation custody boundary

This runtime provenance registry is not the EVAL-01 v4 candidate-freeze,
reviewer, key, or hidden-material registry. It must not store hidden seeds,
examples, labels, scores, thresholds, evaluator keys, evaluator identity,
independence assertions, custody attestations, evaluation acceptance, promotion
approval, release outcome, or a claim that a candidate passed a gate. It cannot
substitute for the reviewer-controlled registry, independent evaluator custody,
or external attestations required by EVAL-01 v4.

At most, a future protected manifest may contain an opaque immutable reference
to separately admissible evidence. Resolving that reference does not interpret
it, grant authority, promote a candidate, or make the model active. Candidate
evaluation custody and active-runtime provenance remain separate domains with
separate roles, stores, audit chains, and acceptance gates.

## Required authorized disposition

Before implementation, the authorized architecture owner must accept, replace,
or reject this proposal. An accepted ADR must specify:

1. the exact manifest schema, canonicalization profile, immutable identity,
   versioning, collision, lineage, retention, and deletion semantics;
2. the exact database ownership, `SECURITY DEFINER` boundary, roles, grants,
   RLS/FORCE behavior, gate API, audit chain, and independently controlled
   emergency-revocation request path;
3. lifecycle states and valid append-only transitions for registration,
   binding, activation, suspension, revocation, recovery, and reconciliation;
4. scope placement and explicit reuse semantics consistent with authenticated
   Tenant-bound database identity; and
5. the complete positive, negative, authority, scope, audit-failure,
   crash-boundary, recovery, backup/restore, revocation, and concurrency test
   matrix without turning evaluation preparation into runtime authority.

## Successor implementation packages and exclusions

After acceptance, the work must be split into non-overlapping packages:

| Package | Permitted scope after acceptance | Explicitly excluded |
| --- | --- | --- |
| A — Schema and authority | PostgreSQL registry, binding/event schema, append-only protections, roles, grants, RLS/FORCE, migration checks | runtime adapter, candidate evaluation, model promotion decision |
| B — Gate integration | Registry-gate API, atomic gate-side manifest resolution, binding fence, DB-derived audit evidence | caller trust map, activation policy, external effects |
| C — Runtime adapter | Typed manifest reference port and removal of local provenance as a trust anchor | direct registry mutation, fallback to caller evidence, online learning |
| D — Operations and recovery | Revocation, reconciliation, backup/restore, incident and recovery runbooks | self-certification, evaluation custody, release authorization |
| E — Independent verification evidence | Database integration, adversarial authorization, audit, recovery, and concurrency test evidence | hidden data access, independent-party fabrication, NB-1 stage exit |

No migration or runtime implementation is authorized by this proposal. No
candidate is created or evaluated; no hidden data is created, accessed, or
stored; no independent party is appointed or claimed; no model is promoted or
activated; no NB-2 capability is enabled; and no stage, release, recognition,
or production-readiness claim is made.

## Required test evidence after acceptance

The accepted implementation must add and pass tests that prove at least:

1. each individual caller-provided provenance-field substitution, manifest
   identity/version swap, unknown manifest, malformed/collision digest, stale
   binding, and scope mismatch is rejected by PostgreSQL;
2. direct DML and every non-gate role are denied, while the named protected
   writer alone can record permitted lifecycle events;
3. registry registration never activates or promotes a model, and checkpoint
   audit evidence is wholly DB-derived rather than copied from the caller;
4. audit write failure rolls back the checkpoint transition; revocation,
   suspension, and recovery failures fail closed without retargeting;
5. backup/restore with missing, corrupt, divergent, or unreconciled registry,
   binding, revocation, or audit-chain state blocks readiness; and
6. concurrent checkpoint, bind, and revoke operations are atomic, fenced, and
   serializable at the chosen binding epoch.

The deterministic documentation test for this proposal validates only its
fail-closed boundary and planned evidence. It is not a migration check,
database test, runtime authorization, independent evaluation, recognition, or
release evidence.
