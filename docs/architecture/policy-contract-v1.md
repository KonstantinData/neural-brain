# Policy Contract v1

## Status

S1-02.3 implements a strict, canonical, expiry-bound policy document and
compiler. It is deliberately narrower than the future policy decision and
activation system.

## Document contract

The document has fixed schema version `policy-v1`, stable `policy_id`,
timezone-aware `expires_at`, an operation allow-list, and a data-classification
allow-list. Unknown fields and duplicate values are rejected. Canonical bytes
are sorted-key compact JSON and their SHA-256 digest is retained by the compiled
policy.

## Non-overridable boundary

The compiler rejects an expired policy and any operation other than the only
currently released operation, gated Memory Core intake. A policy may later
narrow admission further, but cannot turn the Security Floor's denial of
retrieval, disclosure, promotion, correction, retention, deletion, action, or
model promotion into an allow.

## Traceability

Implementation: `neural_brain.security.policy`.
Evidence: `tests/unit/test_policy_contract.py`.
Authority: ADR-005 as amended by ADR-018, Architecture Directive v4.0, and the
merged Security Floor and risk-outcome contracts.
