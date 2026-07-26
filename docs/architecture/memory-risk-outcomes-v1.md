# Memory Risk Outcomes v1

## Purpose

This contract gives Memory Core intake, retrieval, disclosure, promotion,
correction, retention, and deletion one risk vocabulary and one fail-closed
result vocabulary. It implements S1-02.2 without claiming that later lifecycle
operations are released.

## Vocabulary

- Risk: `low`, `elevated`, `high`, `critical`.
- Outcome: `allow`, `deny`, `defer`. Only `allow` may admit an operation.
- Required facts: authenticated immutable scope, provenance, purpose, and the
  lifecycle gate applicable to the request.

The v1 decision is deterministic and has no policy, approval, caller override,
or scope-replacement input. Missing required facts always produce `deny`.

## Current stage boundary

Only gated Memory Core intake can return `allow`. Retrieval, disclosure,
promotion, correction, retention, and deletion are represented so later gates
share the same vocabulary, but return `deny` until their own stage-specific
implementation and evidence exist. A later configurable policy may further
narrow outcomes; it may never turn a Security Floor denial into `allow`.

## Traceability

Implementation: `neural_brain.security.memory_risk`.
Automated evidence: `tests/unit/test_memory_risk.py`.
Authority: ADR-005 as amended by ADR-018, Architecture Directive v4.0, and the
early Memory Core stage boundary.
