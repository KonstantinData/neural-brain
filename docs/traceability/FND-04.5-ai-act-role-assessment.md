# FND-04.5 AI Act Role Assessment Evidence

## Implementation Evidence

- Task ID: `FND-04.5`
- Objective: Define a neutral, evidence-backed and fail-closed per-deployment
  template for possible EU AI Act operator-role assessment.
- Acceptance criteria:
  - [x] A deployment-specific template requires immutable artifact, operating
    entity, brand, availability, authority-over-use, territorial, supplier,
    applicable-law, and role-analysis evidence.
  - [x] Repository and public metadata are explicitly insufficient for a
    deployment, market-placement, branding, operator, applicability, or role
    conclusion.
  - [x] Missing, unknown, stale, scope-mismatched, or unverified facts block
    the deployment-specific release decision and have no allow outcome.
  - [x] Deterministic architecture tests protect the evidence requirements and
    prohibit automatic legal, role, authority, release, or capability claims.
- Governing ADRs and normative sources: `docs/adr/ADR-001-product-neutral-platform-boundary.md`,
  `docs/adr/ADR-005-hard-security-floor-and-bounded-policy.md`,
  `docs/adr/ADR-018-complete-cognitive-system.md`,
  `docs/architecture/architecture-directive-v4.0.md`, and
  `docs/architecture/neural-brain-recognition-standard.md`.
- External legal reference: Regulation (EU) 2024/1689, Article 3, via
  `https://eur-lex.europa.eu/eli/reg/2024/1689/oj`; it is a reference for
  qualified review, not a repository legal conclusion.
- Changed artifacts: `docs/architecture/contracts/ai-act-role-assessment-v1.json`,
  `docs/governance/ai-act-role-assessment-v1.md`,
  `tests/architecture/test_ai_act_role_assessment_contract.py`, and traceability
  indexes.
- Migrations: none; this task adds no runtime state, deployment path,
  authorization, policy activation, or external effect.
- Verification: recorded after branch quality checks complete.
- Security and privacy impact: blocks unproven deployment-specific release
  assertions; it adds no authority, role assignment, compliance claim, personal
  data processing, or external-effect capability.
- Open risks: no concrete deployment facts, operator evidence, branded market
  availability, or qualified legal review record exists in this repository.
