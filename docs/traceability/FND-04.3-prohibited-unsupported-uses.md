# FND-04.3 Prohibited and Unsupported Use Evidence

## Implementation Evidence

- Task ID: `FND-04.3`
- Objective: Provide a deterministic, versioned, product- and domain-neutral
  prohibited and unsupported use classification contract.
- Acceptance criteria:
  - [x] Immutable Security Floor and recognition prohibitions are explicitly
    classified as `prohibited` and non-overridable by policy or approval.
  - [x] Sensitive, high-impact, high-risk, unclassified, deployment-specific,
    and unproven-capability uses remain `unsupported` and disabled without a
    release or authorization outcome.
  - [x] The contract fails closed for unknown, missing, stale, scope-mismatched,
    or unaccepted inputs and makes no legal or lawfulness determination.
  - [x] Architecture tests prove the ordered fail-closed classification,
    immutable-prohibition semantics, non-authorization boundary, and required
    future controls.
- Governing ADRs and normative sources: `docs/adr/ADR-001-product-neutral-platform-boundary.md`,
  `docs/adr/ADR-005-hard-security-floor-and-bounded-policy.md`,
  `docs/adr/ADR-018-complete-cognitive-system.md`,
  `docs/architecture/architecture-directive-v4.0.md`, and
  `docs/architecture/neural-brain-recognition-standard.md`.
- Changed artifacts: `docs/architecture/contracts/prohibited-unsupported-use-v1.json`,
  `docs/governance/prohibited-unsupported-use-classification-v1.md`,
  `tests/architecture/test_prohibited_unsupported_use_contract.py`, and
  traceability indexes.
- Migrations: none; this task adds no runtime state, policy activation, or
  deployment path.
- Verification: recorded after branch quality checks complete.
- Security and privacy impact: records a fail-closed classification boundary;
  it adds neither authority, policy override, personal-data processing, nor
  external-effect capability.
- Open risks: the separately governed classification, qualified legal review,
  release evidence, and activation mechanisms are intentionally not implemented
  by this Foundation task.
