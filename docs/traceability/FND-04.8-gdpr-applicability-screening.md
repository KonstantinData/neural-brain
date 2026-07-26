# FND-04.8 GDPR Applicability Screening Evidence

## Implementation Evidence

- Task ID: `FND-04.8`
- Objective: Define a versioned, deterministic, and fail-closed evidence
  template for qualified deployment-specific GDPR applicability,
  special-category, automated-decision, and DPIA screening.
- Acceptance criteria:
  - [x] The template records qualified-review-only applicable-article
    candidates, risk triggers, required assessments, verified evidence
    references, and release blockers.
  - [x] The template requires immutable artifact and authenticated scope
    evidence, accountable owner, qualified reviewer and date, rationale,
    assessment evidence, and reassessment triggers.
  - [x] Missing, unknown, stale, contradictory, scope-mismatched, or
    unqualified facts block a deployment-specific release decision.
  - [x] Deterministic tests prohibit legal, DPIA, authority, processing,
    release, or runtime-enablement claims.
- Governing ADRs and normative sources:
  `docs/adr/ADR-001-product-neutral-platform-boundary.md`,
  `docs/adr/ADR-005-hard-security-floor-and-bounded-policy.md`,
  `docs/adr/ADR-018-complete-cognitive-system.md`,
  `docs/architecture/architecture-directive-v4.0.md`, and
  `docs/architecture/neural-brain-recognition-standard.md`.
- External legal reference: Regulation (EU) 2016/679, Articles 2, 3, 5, 6, 9,
  10, 13, 14, 22, 25, 30, 32, 35, and 44, via
  `https://eur-lex.europa.eu/eli/reg/2016/679/oj`; this reference is for
  qualified review only, not a repository legal conclusion.
- Changed artifacts:
  `docs/architecture/contracts/gdpr-applicability-screening-v1.json`,
  `docs/governance/gdpr-applicability-screening-v1.md`,
  `tests/architecture/test_gdpr_applicability_screening_contract.py`, and
  contract/traceability indexes.
- Migrations: none; the task adds no runtime state, authority, processing path,
  policy activation, external effect, or release decision.
- Verification: recorded after branch quality checks complete.
- Security and privacy impact: preserves fail-closed screening evidence and
  release blockers; it adds no authority, legal conclusion, personal-data
  processing, or external-effect capability.
- Open risks: no concrete processing facts or qualified review record exists in
  this repository; this is intentional and remains a release blocker.
