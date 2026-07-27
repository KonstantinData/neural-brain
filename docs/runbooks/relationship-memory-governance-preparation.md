# Relationship Memory Governance Preparation Runbook

## Stop boundary

This preparation runbook neither receives real personal data nor retrieves a
signal, executes Dreaming, or authorizes a runtime. Stop and escalate if scope,
purpose, provenance, classification, review independence, freshness, retention,
correction lineage, or deletion state is unknown, stale, conflicting, or
prohibited.

## Service-managed requests

After future regular tenant onboarding the service is default enabled, with no
customer self-service configuration or disable control. The developer/service
owner handles customer requests only after documented contract, purpose, and
technical checks. Data-subject access, correction, and deletion requests enter
an auditable service-managed intake and response path; never a dashboard or
direct-store path.

## Candidate review handoff

This is a preparation checklist for a future separately authorized workflow;
it is not an executable review or Memory transition procedure.

1. For any future productive Tenant data path, confirm the ADR-019 identity
   anchor before reading or reviewing a candidate: the connection uses the
   Tenant-bound Runtime login and Tenant-specific connection pool; PostgreSQL
   resolves the authoritative Tenant from protected state keyed by immutable
   `session_user`; and the expected active Tenant, database target, and
   credential revision match the pool generation. A mismatch denies the
   operation and invalidates the connection. `current_user`, writable settings,
   candidate content, and request payloads are not identity anchors.
2. Confirm that authenticated Area scope, and any narrower Project or Session
   scope, resolve as subordinate lineage below the database-bound Tenant and
   come from the Protected Control Plane rather than the candidate payload.
3. Confirm the declared purpose, provenance, permitted signal type,
   classification, freshness, retention, review state, and correction lineage.
   Unknown, stale, conflicting, scope-mismatched, purpose-mismatched, or
   prohibited content stops the review and is not used.
4. Record the candidate as inactive and non-retrievable. A future Candidate
   Proposer may submit it only to the Memory Transition Gate and may not write,
   activate, promote, or approve it directly.
5. Require an independent future Reviewer to submit a bounded disposition
   request to the Memory Transition Gate. The Reviewer cannot replace
   authenticated scope, widen purpose, create authority, or approve their own
   candidate.

The Memory Transition Gate remains the sole future writer of protected memory
state. Every protected review, correction or supersession, expiry, deletion-
pending, and deletion-complete disposition is a typed request to that Gate. The
Gate may commit a disposition only with an authenticated actor, immutable
Tenant and Area scope plus required subordinate lineage, verified authority,
applicable policy, and atomic audit evidence. Missing, stale, conflicting, or
payload-derived actor, scope, authority, policy, or audit state denies the
transition.

## Correction, retention, and deletion handoff

- A correction is a provenance-bearing successor candidate with preserved
  lineage. Suspend use while facts conflict; never overwrite a signal in place
  or let a proposer self-approve the successor. Only the Memory Transition Gate
  may commit the protected correction or supersession disposition.
- At expiry, missing review, or uncertain legal-hold state, make the signal
  unavailable. A future retention action must follow a separately accepted
  schedule and preserve required audit evidence without retaining prohibited
  payload content. Only the Gate may commit the protected expiry or
  unavailable disposition.
- On a future deletion request, the Gate must first commit the protected
  deletion-pending or unavailable disposition. A downstream deletion
  reconciler may then process source records, derivatives, summaries, indexes,
  embeddings, caches, replicas, and eligible backup handling from that
  committed intent. The reconciler cannot write protected memory state or mark
  deletion complete; it submits reconciliation evidence, after which only the
  Gate may commit a protected deletion-complete disposition.
- Escalate prohibited content, cross-scope evidence, unresolved correction,
  uncertain legal hold, deletion residue, or unavailable audit evidence to the
  future accountable privacy and Protected Control Plane owners. Escalation
  never authorizes use, a retry, or a protected transition.

## Non-use under uncertainty

Use `deny_and_do_not_use`. Do not widen scope, infer purpose, use stale data,
substitute a cache, or ask a Planner or Dreaming worker to repair the result.
A future deletion suspends use and requires reconciliation of source,
derivatives, indexes, embeddings, caches, replicas, and eligible backup
handling. Position 3 is a future separately authorized technical enforcement
package; it does not activate schema, Gate, retrieval, Planner, or Dreaming.
