# ADR-019 Routing-Attestation Evaluation

- Status: Evaluated and deferred; not an accepted architecture decision
- Backlog item: NB-275
- Evaluated against: ADR-018, Architecture Directive v4.0, Neural Brain Recognition Standard, and ADR-019
- Applies to: Protected Control Plane identity-routing hardening
- Does not apply to: FND-06 acceptance, release-stop removal, or Neural Brain recognition

## Decision boundary

ADR-019 is the authoritative source boundary for this evaluation. It says that
the OIDC consumer is the untrusted-edge adapter, that its fully validated
signed Tenant claim and database-resolved Principal select only the initial
Tenant pool, and that an established connection cannot change Tenant. Its
explicitly reserved boundary is: "Workload- or channel-bound routing
attestation is compatible later hardening, but is not part of FND-06 and
requires a separate accepted decision before becoming mandatory."

Therefore this document does not amend ADR-019 and does not make an
attestation mechanism mandatory. The existing database-visible invariant stays
the required boundary: one restricted Runtime login and one dedicated pool per
Tenant, with protected `session_user` mapping as the Tenant anchor. OIDC
validation, Principal authority, immutable hierarchy lineage, gates, RLS,
`FORCE ROW LEVEL SECURITY`, audit, and secret lifecycle remain separately
required controls.

## Concrete attack-path assessment

| Candidate signal | Spoofing or confused-deputy path | What ADR-019 already denies | Residual value and decision |
| --- | --- | --- | --- |
| OIDC Tenant claim | A request, host header, prompt, worker message, or stale cache tries to route a valid Tenant A token to Tenant B. | Signature, issuer, audience, time, and claim-shape validation precede initial pool selection; the pool, `session_user`, and protected mapping must match before protected access. | A signed claim is necessary routing input, not proof that a particular workload performed the routing. Keep the present validation contract; no new attestation requirement. |
| Workload identity | A compromised or incorrectly authorized worker obtains a valid Tenant A token or routing request and acts as a confused deputy for a foreign pool. | A foreign-pool route fails before protected operations because a Tenant-bound pool and `session_user` cannot be relabeled to the claim or request Tenant. Principal authorization remains independent. | Workload identity could bind a deployment identity to the edge adapter, but it adds operational issuer, lifecycle, and revocation dependencies. Defer pending a concrete multi-workload threat and deployment model. |
| mTLS or channel binding | A token or routing assertion is replayed over a different TLS channel, proxy hop, or worker. | Replay cannot change a connection's immutable database Tenant; foreign routing and writable-context substitution fail closed. | Channel binding can reduce bearer-token replay at the edge, but it neither replaces the database identity anchor nor proves Principal authority. Defer; it is not justified as a current FND-06 control. |
| Gateway assertion | A gateway forwards an unsigned, stale, audience-confused, or tenant-relabeled assertion to a downstream worker. | Gateway data is untrusted until the OIDC adapter validates the signed claim and the database verifies the Tenant-bound pool identity. | A future assertion format must have audience, issuer, expiry, nonce/replay, workload subject, Tenant binding, key rotation, and audit semantics. No gateway assertion is accepted today. |
| Dedicated database routing | DNS, service discovery, failover, restore, or a pool key points Tenant A traffic at Tenant B's target or credential revision. | Checkout must match expected active Tenant, database target, and credential revision; mismatch evicts the connection and cannot fall back to a shared credential. | The database/pool contract covers this path. Additional route attestation is deferred until deployment evidence shows a residual path not closed by that verification. |

## Security and architecture conclusion

The evaluated mechanisms are defense-in-depth candidates, not authority
sources. None may derive scope from a prompt, request payload, model output,
tool output, memory content, writable GUC, or a gateway assertion that has not
passed an accepted verification contract. None may grant Principal capability,
write protected state outside its Transition Gate, or authorize an external
effect. This preserves the ADR-018 two-plane separation: cognitive capability
does not create authority.

The current decision is to **defer** workload- or channel-bound routing
attestation. The repository has no accepted protocol, workload issuer trust
model, deployment topology, key custody design, replay semantics, lifecycle
operator, or held-out adversarial evidence sufficient to make such an
attestation a reliable protected-control input. Adding one prematurely would
create a second, underspecified identity source and could weaken the
fail-closed ADR-019 boundary.

This deferral makes **no FND-06 or release-gate change**. FND-06 remains bound
to the accepted Tenant-login/pool implementation and its integration,
lifecycle, independent-review, and production-readiness evidence. This
evaluation neither removes a release stop nor establishes any Neural Brain
recognition or delivery-stage claim.

## Exact trigger for a future ADR

A new ADR is required before routing attestation becomes mandatory. It may be
proposed only when all of the following are concrete and versioned:

1. A deployed multi-workload or multi-hop routing path has a demonstrated
   residual spoofing or confused-deputy risk that persists after ADR-019 pool
   checkout verification, `session_user` binding, and OIDC validation.
2. The proposed protocol names its trusted issuer(s), workload subject,
   audience, Tenant binding, expiry, nonce or replay protection, mTLS/channel
   binding semantics where used, key custody and rotation, revocation, failure
   behavior, audit records, and privacy/data-class limits.
3. The contract proves that an invalid, stale, replayed, audience-confused,
   workload-confused, channel-confused, or Tenant-confused assertion fails
   closed without shared-pool fallback, scope expansion, or protected access.
4. Independent adversarial tests prove the protocol does not bypass OIDC
   Principal resolution, database-bound Tenant identity, authority bindings,
   gates, RLS/FORCE, audit, or credential/pool lifecycle controls.
5. The proposed control has an accountable operator and recovery/runbook
   evidence for issuer outage, key compromise, proxy termination, rotation,
   revocation, restore, failover, and reconciliation.

Until that ADR is accepted and its evidence gates are specified, this document
is an evaluation record only; its deferred controls cannot be treated as
implemented, required, or a substitute for the ADR-019 contract.
