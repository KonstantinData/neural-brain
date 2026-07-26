# FND-04.7 AI Act Risk-Classification Assessment Evidence

## Implementation Evidence

- Task ID: `FND-04.7`
- Objective: Define a versioned, deterministic, and fail-closed assessment
  template for qualified, deployment-specific EU AI Act risk-classification
  review.
- Acceptance criteria:
  - [x] The template records review-only prohibited, high-risk, transparency,
    and other/minimal-risk candidate categories, with Article 5 review before
    Article 6/Annex I, Annex III, and Article 50 evidence.
  - [x] A per-deployment record requires immutable artifact and scope evidence,
    accountable owner, qualified reviewer and date, current rationale, controls,
    evidence expiry, reassessment triggers, and independent release reference.
  - [x] Missing, unknown, stale, contradictory, scope-mismatched, or
    unqualified evidence blocks the deployment-specific release decision; a
    qualified prohibition conclusion is non-overridable.
  - [x] Deterministic tests prohibit automatic legal, real-deployment
    classification, authority, release, or runtime-enablement claims.
- Governing ADRs and normative sources:
  `docs/adr/ADR-001-product-neutral-platform-boundary.md`,
  `docs/adr/ADR-005-hard-security-floor-and-bounded-policy.md`,
  `docs/adr/ADR-018-complete-cognitive-system.md`,
  `docs/architecture/architecture-directive-v4.0.md`, and
  `docs/architecture/neural-brain-recognition-standard.md`.
- External legal reference: Regulation (EU) 2024/1689, Articles 5, 6, and 50
  and Annexes I and III, via `https://eur-lex.europa.eu/eli/reg/2024/1689/oj`;
  this reference is for qualified review only, not a repository legal conclusion.
- Changed artifacts:
  `docs/architecture/contracts/ai-act-risk-classification-assessment-v1.json`,
  `docs/governance/ai-act-risk-classification-assessment-v1.md`,
  `tests/architecture/test_ai_act_risk_classification_assessment_contract.py`,
  and contract/traceability indexes.
- Migrations: none; the task adds no runtime state, authority, deployment path,
  policy activation, external effect, or release decision.
- Verification: recorded after branch quality checks complete.
- Security and privacy impact: preserves fail-closed review and a non-overridable
  prohibition stop; it adds no authority, legal conclusion, personal-data
  processing, or external-effect capability.
- Open risks: no concrete deployment facts or qualified review record exists in
  this repository; this is intentional and remains a release blocker.
