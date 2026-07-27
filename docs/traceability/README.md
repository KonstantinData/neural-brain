# Implementation Traceability

This directory defines how Neural Brain work is linked from an
approved task to versioned implementation and independently reviewable
evidence. Notion is the coordination ledger; repository artifacts remain the
durable technical source of truth.

## Evidence Chain

Every completed main task and subtask must provide an unbroken chain:

```text
Notion task ID
  -> accepted requirement and acceptance criteria
  -> relevant repository ADRs and contracts
  -> branch and commit or pull request
  -> changed code, migrations, configuration, and documentation
  -> baselines, ablations, automated tests, evaluation, and exact commands
  -> recorded results, limitations, risks, and follow-ups
```

Links do not replace evidence. A task is complete only when the referenced
repository state satisfies each acceptance criterion and the recorded commands
have actually run against that state.

## Stable References

Use the following identifiers consistently:

- The Notion `Task ID`, such as `NB-1`, and the full task URL.
- Repository-relative file paths for code, contracts, migrations, tests, and
  documentation.
- ADR identifiers in the form `ADR-NNN`.
- A Git commit SHA and pull-request URL once they exist. Before a commit exists,
  identify the task branch and state explicitly that the evidence is from the
  working tree.
- Exact test or verification commands plus their result. Never write `passed`
  for a command that was not executed.

Do not use mutable branch names as the only completion evidence. Do not copy
secrets, credentials, personal data, or sensitive memory payloads into an
evidence record. External consumer task or goal identifiers may appear only as
non-authoritative correlation metadata and never as proof of Brain scope,
authority, or transition state.

## Evidence Record

Use this structure in the task's Notion completion update or, when the evidence
is extensive or release-critical, in a versioned file under this directory:

```markdown
## Implementation Evidence

- Task ID: `NB-...`
- Task URL: `https://...`
- Objective: ...
- Acceptance criteria:
  - [x] Criterion with an objective repository or test reference
- Branch: `codex/...`
- Commit: `<full SHA>` or `working tree; no commit yet`
- Pull request: `<URL>` or `not created`
- ADRs and contracts:
  - `docs/adr/ADR-...md`
- Changed artifacts:
  - `path`: reason
- Migrations:
  - `path` or `none`
- Tests executed:
  - `exact command`: `passed | failed`
- Verification result: `passed | failed | blocked`
- Security and privacy impact: ...
- Documentation updated:
  - `path`
- Open risks: `none` or ...
- Blocked follow-ups: `none` or task URL and unblock condition
- Verified at: `<ISO-8601 timestamp with offset>`
```

The checkbox is an assertion backed by its adjacent evidence, not a substitute
for a test. Failed or unexecuted checks remain explicit and prevent completion
when they are required by the acceptance criteria.

## Versioned Evidence Records

- [`../architecture/ledger-conventions-v1.md`](../architecture/ledger-conventions-v1.md):
  S1-03.1 normative representation conventions with architecture-test evidence.
- [`FND-01-foundation-baseline.md`](FND-01-foundation-baseline.md): historical
  PR #1 Foundation baseline evidence and remediation mapping.
- [`neural-brain-capability-matrix.md`](neural-brain-capability-matrix.md):
  current capability-to-evidence matrix for the Foundation and first NB-1
  implementation slice.
- [`memory-core-production-readiness.md`](memory-core-production-readiness.md):
  current operator-readiness gaps and verified progress for the first deployable
  Memory Core milestone.
- [`requirement-to-test-catalog-v1.json`](requirement-to-test-catalog-v1.json):
  bounded, versioned mapping from active normative release-stop and Memory Core
  transition requirements to concrete tests. It records explicit N/A entries
  for target-only capabilities and is not a global implementation or release
  claim.
- [`FND-04.2-intended-purpose.md`](FND-04.2-intended-purpose.md): stable
  intended-purpose and future-deployment assessment-template evidence; it does
  not make a deployment, legal, or compliance determination.
- [`FND-04.3-prohibited-unsupported-uses.md`](FND-04.3-prohibited-unsupported-uses.md):
  deterministic, fail-closed prohibited and unsupported-use classification;
  it has no authorization or activation outcome.
- [`S1-15.3-security-floor-governance.md`](S1-15.3-security-floor-governance.md):
  maps immutable prohibited-use constraints to non-overridable Security Floor
  governance rules and bounds required human review for sensitive or high-risk
  candidate cases; it adds no legal classification, authority, or runtime path.
- [`FND-04.5-ai-act-role-assessment.md`](FND-04.5-ai-act-role-assessment.md):
  deployment-specific EU AI Act operator-role assessment template; it is
  evidence input only and fails closed without verified deployment facts and
  qualified review.
- [`FND-04.4-gdpr-role-assessment.md`](FND-04.4-gdpr-role-assessment.md):
  deployment-specific GDPR role-assessment evidence input; it names the
  concrete fact and qualified-review blocker, and neither makes a role
  conclusion nor enables processing, deployment, or release.
- [`FND-04.6-use-case-scope-intake.md`](FND-04.6-use-case-scope-intake.md):
  pre-production use-case and scope intake for future deployments; it is
  evidence input only, fails closed, and cannot supply trusted runtime context,
  authority, release, or enablement.
- [`FND-04.7-ai-act-risk-classification.md`](FND-04.7-ai-act-risk-classification.md):
  qualified-review input for a future deployment-specific EU AI Act risk
  classification; it fails closed and neither classifies a real deployment nor
  authorizes authority, release, or enablement.
- [`S1-15.1-ai-act-obligation-matrix.md`](S1-15.1-ai-act-obligation-matrix.md):
  versioned, fail-closed provider, deployer, model-supplier, downstream-actor,
  and non-applicability obligation evidence matrix; it has no legal, authority,
  model/deployment, release, or runtime-enablement outcome.
- [`FND-04.8-gdpr-applicability-screening.md`](FND-04.8-gdpr-applicability-screening.md):
  qualified-review input for future deployment-specific GDPR applicability,
  special-category, automated-decision, and DPIA screening; it records article
  candidates, risk triggers, assessments, evidence, and release blockers but
  cannot determine lawfulness or authorize processing, release, or enablement.
- [`FND-04.9-compliance-raci.md`](FND-04.9-compliance-raci.md): qualified-review
  input for future deployment-specific provider, deployer, privacy, security,
  product, incident, release, approval-authority, independence, and escalation
  governance; it fails closed and cannot assign a real role, grant authority,
  approve release, or bypass a Protected Control Plane gate.
- [`FND-04.10-reassessment-triggers.md`](FND-04.10-reassessment-triggers.md):
  fail-closed reported-change intake and linked reassessment-work template for
  future legal, guidance, model, supplier, purpose, data, and deployment
  changes; it neither polls sources nor decides law, release, authority, or
  runtime behavior.
- [`FND-04.11-compliance-release-decision.md`](FND-04.11-compliance-release-decision.md):
  signed-evidence record template for a separately governed compliance-release
  decision; it requires current scope-matched GDPR and EU AI Act evidence or
  qualified non-applicability bases and cannot authorize runtime enablement.
- [`S1-15.2-ai-literacy-competence-evidence.md`](S1-15.2-ai-literacy-competence-evidence.md):
  versioned, product-neutral AI-literacy curriculum, de-identified competence
  evidence, and refresh-cycle template; it makes no real-person, HR, legal,
  authority, release, or runtime claim.
- [`S1-14.1-ropa-evidence-intake.md`](S1-14.1-ropa-evidence-intake.md):
  deployment-specific record-of-processing-activities evidence intake with
  immutable authenticated Tenant and Area scope references; it stores only
  categories and references, fails closed, and cannot create processing,
  authority, release, or runtime outcomes.
- [`S1-14.2-personal-data-flow-register.md`](S1-14.2-personal-data-flow-register.md):
  product-neutral, category-only source-to-recipient data-flow evidence with
  immutable scope, transfer-boundary, retention, safeguard, and provenance
  references; it fails closed and cannot disclose, transfer, process, or
  authorize data at runtime.
- [`S1-14.3-article-6-legal-basis-evidence-intake.md`](S1-14.3-article-6-legal-basis-evidence-intake.md):
  immutable scope/purpose/activity-bound Article 6 legal-basis, necessity, and
  proportionality evidence intake for qualified review only; unknown,
  non-applicability, conflict, and external facts fail closed and cannot create
  legal, authority, processing, release, or runtime outcomes.
- [`S1-06.5-approval-claims-blocker.md`](S1-06.5-approval-claims-blocker.md):
  current, Gate-owned approval-claim prerequisite and verification boundary;
  it records a blocker and does not implement approval consumption.
- [`S1-06.6-separation-of-duties-blocker.md`](S1-06.6-separation-of-duties-blocker.md):
  authenticated, Gate-owned separation-decision prerequisite for candidate
  promotion, retrieval assessment, incident resolution, and future action roles;
  it records a blocker and does not implement a role or approval channel.
- [`S1-03.2-migration-reconciliation.md`](S1-03.2-migration-reconciliation.md):
  Foundation reconciliation from clean-database migration validation to
  least-privilege Runtime-role DDL and direct-write denial evidence; it adds no
  runtime capability.
- [`S1-03.3-core-schema-reconciliation.md`](S1-03.3-core-schema-reconciliation.md):
  MS-1 Memory Core source/observation, checkpoint, transition, provenance,
  lifecycle-boundary, and recovery mapping; it introduces no schema or early
  Goal, Action, or external-effect capability.
- [`S1-03.6-audit-atomicity-reconciliation.md`](S1-03.6-audit-atomicity-reconciliation.md):
  Foundation reconciliation proving that an injected audit failure rolls back
  the entire protected Memory transition and leaves unrelated scoped evidence
  intact.
- [`FND-ENT-02-goal-gate-adr-revalidation.md`](FND-ENT-02-goal-gate-adr-revalidation.md):
  historical Goal Gate ADR disposition and the proposed, fail-closed NB-1
  replacement boundary; it is not an accepted ADR or runtime authorization.
- [`FND-ENT-03-nb45-action-prerequisites.md`](FND-ENT-03-nb45-action-prerequisites.md):
  historical Action, preparation, dispatch, and reconciliation disposition plus
  the blocked, fail-closed NB-4/NB-5 Action Gate prerequisite boundary; it is
  not an accepted ADR or runtime authorization.
- [`S1-15.6-model-inference-inventory.md`](S1-15.6-model-inference-inventory.md):
  immutable, fail-closed model and inference-boundary inventory evidence; it
  records current absence and cannot activate, deploy, promote, or authorize a
  model or inference provider.
- [`S1-13.5-protected-ledger-backup-pitr.md`](S1-13.5-protected-ledger-backup-pitr.md):
  target-only protected-ledger backup, WAL/PITR, retention, custody, isolated
  restore-test, and release-stop evidence; it makes no deployed backup or
  recovery-readiness claim.

## Reconciliation Rules

Before a pull request or final handoff:

1. Compare the active Notion task and every inline or separate subtask with the
   complete repository diff.
2. Verify that accepted ADRs are synchronized to versioned records before their
   dependent implementation is treated as authorized.
3. Confirm that each changed cognitive or memory behavior, schema, operation,
   claim, or safety invariant has corresponding tests, evaluation, and durable
   documentation.
4. Record exact commands and results from the integrated branch, not only from
   isolated contributor work.
5. Keep incomplete, blocked, or deferred work visible as a separate Notion issue
   or backlog item with a named unblock condition.
6. Set `Done` and `Completed At` only after all acceptance criteria and required
   checks pass.

## Source Boundaries

- Code, tests, migrations, executable configuration, ADRs, contracts, and
  runbooks live in Git.
- Task status, ownership, timestamps, coordination notes, and links to evidence
  live in Notion.
- Exchange Room discussions remain non-normative until accepted and synchronized
  through the appropriate ADR, issue, or backlog workflow.
- Conflicting evidence blocks completion; it is never resolved by choosing the
  more convenient source silently.
