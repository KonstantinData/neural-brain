# Machine-readable Neural Brain contracts

These contracts implement the complete cognitive-system target established by
ADR-018 while retaining the governed Memory Core established by ADR-015 through
ADR-017.

## Complete-system contracts

- `system-boundary.json`: Cognitive Plane, Protected Control Plane, scope,
  target capabilities, Memory Core role, and non-claims.
- `cognitive-cycle.json`: typed serial cognitive-cycle order and invariants.
- `nb1-safe-serial-cognition.json`: first implementation-slice boundary for
  recorded or synthetic observations, bounded learned attention, a fixed-version
  recurrent workspace, internal proposals, deterministic checkpoints, and no
  external effects.
- `goal-transition-gate-v1.json`: bounded prerequisite contract for a future
  Goal Transition Gate. It binds a session-scoped aggregate, immutable
  authenticated scope and lineage, evidence references, and stage boundaries;
  it does not authorize a Goal runtime, migration, action, or external effect.
- `relationship-memory-signal-contract-v1.json`: proposed, fail-closed signal
  vocabulary for future Relationship Memory preparation; it creates no signal
  store, migration, runtime, retrieval, or processing authority.
- `action-transition-gate-v1.json`: bounded prerequisite contract for a future
  NB-5 Action Transition Gate. It separates NB-4 learning/consolidation from
  NB-5 action and does not authorize a runtime, migration, executor, dispatch,
  budget, resource, fence, sandbox, or external effect.
- `nb1-hidden-evaluation.json`: label-free candidate boundary, candidate freeze
  receipt, external evaluator custody, and signed evidence intake for EVAL-01 v4.
- `stage-capabilities.json`: cumulative NB-0 through NB-8 delivery contract.
- `recognition-gates.json`: all-required recognition criteria.
- `evaluation-gates.json`: ordered, non-compensatory G0 through G8 evidence.
- `release-stops.json`: non-waivable complete-system release stops.
- `intended-purpose.json`: stable product- and domain-neutral intended-purpose
  statement plus a versioned future-deployment assessment input. It neither
  authorizes a release nor supplies a legal or compliance conclusion.
- `gdpr-role-assessment-v1.json`: deployment-specific evidence-input template
  for controller, joint-controller, processor, subprocessor, and recipient
  relationships. It makes no role conclusion, processing authorization, or
  deployment/release decision.
- `gdpr-applicability-screening-v1.json`: neutral, per-deployment evidence
  template for qualified GDPR applicability, special-category,
  automated-decision, and DPIA screening. It records article candidates, risk
  triggers, required assessments, evidence, and release blockers only; it
  never determines lawfulness or authorizes processing or release.
- `article-6-legal-basis-evidence-intake-v1.json`: immutable,
  scope/purpose/activity-bound Article 6 legal-basis, necessity, and
  proportionality evidence intake for qualified review only. It records
  external-fact and non-applicability handling, fails closed, and never selects
  a legal basis, determines lawfulness, grants authority, or authorizes
  processing, release, or runtime enablement.
- `article-9-special-category-evidence-intake-v1.json`: documentation-only
  preparation for future scope-bound Article 9 and Article 10 evidence review.
  It defines candidate-evidence XOR qualified-N/A requirements but provides no
  instance validator, qualified review, authorization, enforcement, or release.
- `legitimate-interest-assessment-evidence-intake-v1.json`: immutable,
  documentation-only preparation for future scope-bound Article 6(1)(f)
  evidence review, including public-authority, vulnerability, objection, and
  direct-marketing controls. It provides no instance validator, balancing
  result, processing stop, legal conclusion, runtime authority, or release.
- `consent-evidence-intake-v1.json`: immutable,
  documentation-only preparation for future scope-bound consent evidence review
  under Articles 7, 8, and 9(2)(a). It provides no instance validator, consent
  determination, withdrawal workflow, processing stop, runtime authority, or
  release.
- `prohibited-unsupported-use-v1.json`: deterministic, fail-closed
  classification of immutable prohibited and currently unsupported uses. It has
  no allow, activation, or release outcome and never replaces the Security
  Floor, qualified legal review, authority, or required human approval.
- `ai-act-role-assessment-v1.json`: neutral, per-deployment evidence template
  for qualified EU AI Act operator-role review. It never assigns a role,
  determines applicability or lawfulness, or authorizes a release.
- `ai-act-risk-classification-assessment-v1.json`: neutral, per-deployment
  evidence template for qualified EU AI Act risk-classification review. It
  records prohibited, high-risk, transparency, and other/minimal-risk review
  inputs only; it never classifies a real deployment or authorizes a release.
- `ai-act-obligation-matrix-v1.json`: versioned, fail-closed evidence template
  for qualified provider, deployer, model-supplier, downstream-actor, and
  non-applicability obligation review. It never assigns a real role or
  obligation, approves a model or deployment, or authorizes a release.
- `gpai-provider-obligation-applicability-v1.json`: fail-closed evidence input
  for qualified review of a concrete distribution, modification, branding, or
  fine-tuning fact pattern. It never assigns GPAI-provider status, determines
  an Article 53 obligation, or authorizes a deployment, model, or runtime.
- `compliance-release-decision-v1.json`: fail-closed, signed-evidence record
  template for a separately governed compliance-release decision. It requires
  scope-matched qualified GDPR and EU AI Act findings or explicit qualified
  non-applicability bases, but it never signs, verifies, authorizes, enables,
  or releases a deployment.
- `protected-ledger-backup-recovery-v1.json`: target-only, fail-closed
  PostgreSQL protected-ledger backup, WAL/PITR, retention, key/access
  separation, restore-test, and release-stop contract. It configures no backup
  system and makes no recovery-readiness claim.
- `personal-data-flow-register-v1.json`: category-only, fail-closed evidence
  template for a proposed end-to-end personal-data flow and recipient
  relationship. It requires immutable scope-bound source, recipient, transfer,
  retention, safeguard, and provenance evidence but never routes, discloses,
  transfers, processes, or authorizes data at runtime.
- `data-object-catalogue-intake-v1.json`: category-only, fail-closed evidence
  intake for a proposed stored data-object type. It requires ownership, role,
  purpose, recipient, storage, transition, retention, rights, deletion, and
  RoPA evidence but cannot create a processing register or runtime path.

## Memory Core contracts

- `scope-catalog.json`: strict Brain-to-Session catalog lineage; Goal is a
  session-bound protected aggregate, not a catalog entry or isolation dimension.
- `envelopes.json`: authenticated memory requests and records.
- `memory-lifecycle.json`: Memory Gate operations and lifecycle.
- `memory-stage-capabilities.json`: cumulative, separately namespaced MS-0
  through MS-4 Memory Core maturity contract. These stages are not NB product
  stages and do not advance product maturity by themselves.
- `memory-release-stops.json`: retained non-waivable Memory Core-specific
  release stops under ADR-018.
- `ledger-invariants.json`: PostgreSQL, provenance, audit, isolation, and recovery.
- `dreaming.json`: Area-local offline Dreaming and inactive candidates.
- `inference-provider.json`: bounded local Ollama memory-processing boundary.
- `model-inference-inventory-v1.json`: versioned, fail-closed evidence contract
  for any model or inference boundary. It requires immutable ID/version/digest,
  provenance, supplier, licence/model-card references, precision, context bound,
  and evaluation status; it does not activate, deploy, promote, or authorize a
  model or inference provider.

Historical Goal, Action Intent, dispatch, intent-purpose, and quiescence
contracts remain in Git history. ADR-018 does not reactivate them automatically;
each must be revalidated or replaced by its delivery task.

Preregistered evaluation specifications live under
`docs/architecture/evaluations/`. Their digest is frozen before the evaluated
runtime or evidence report is accepted.

Unknown scope, actor, authority, state, operation, model version, provenance,
freshness, data class, promotion, evaluation, or authorization state fails
closed. A schema may describe a later operation without authorizing it before
its stage and evidence gates pass.
