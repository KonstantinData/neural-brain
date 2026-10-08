# Policy Contract v1

## Status

S1-02.3 implements a strict, canonical, expiry-bound policy document and
compiler. Separate decision-record and activation-evidence validators are
implemented; protected policy activation remains a future runtime capability.
Compilation alone grants no authority and does not activate a policy.

## Document contract

The document has fixed schema version `policy-v1`, stable `policy_id`,
timezone-aware `expires_at`, an operation allow-list, and a data-classification
allow-list. Unknown fields and duplicate values are rejected. Canonical bytes
are sorted-key compact JSON and their SHA-256 digest is retained by the compiled
policy.

## Non-overridable boundary

The compiler rejects an expired policy and any operation other than gated
Memory Core intake, the only operation admitted by this v1 policy compiler.
The runtime Security Floor separately admits scoped `memory_ingest` and
`memory_read`; this compiler does not broaden that boundary or authorize
semantic retrieval. A policy may narrow admission further, but cannot turn a
Security Floor denial into an allow or enable disclosure, promotion,
correction, retention, deletion, action, or model promotion.

## Traceability

Implementation: `neural_brain.security.policy`.
Evidence: `tests/unit/test_policy_contract.py`.
Authority: ADR-005 as amended by ADR-018, Architecture Directive v4.0, and the
merged Security Floor and risk-outcome contracts.
