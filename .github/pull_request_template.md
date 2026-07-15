## Notion task

- Task ID and link:
- Owner:
- Started at:
- Acceptance criteria covered:

## Scope and invariants

- Work area: Neural Brain
- Memory scope and provenance affected:
- Protected memory state affected:
- Relevant ADRs and contracts:
- Stage boundary:

## Change summary

- Implemented:
- Failure and recovery paths:
- Documentation impact:
- Migrations:

## Security, privacy, and runtime separation

- [ ] Scope and actor come only from authenticated runtime context.
- [ ] Unknown inputs and undeclared behavior fail closed.
- [ ] Protected memory state remains writable only through the Memory Gate.
- [ ] Memory producer/gate, consumer/assessor, and candidate/promoter boundaries remain intact.
- [ ] External task or goal identifiers remain non-authoritative correlation metadata.
- [ ] No secret, credential, token, or live personal data is included.
- [ ] Security and privacy impact is documented, including `none` with rationale.

## Verification evidence

- Formatting:
- Lint:
- Strict type checking and exception audit:
- Tests, including negative and recovery coverage:
- Migration or environment checks:
- Independent verification:
- Checks not executed and reason:

## Separation-of-duties review

- [ ] This change is not separation-of-duties-sensitive.
- [ ] This change is sensitive and has an approving CODEOWNER distinct from the author and latest pusher.
- [ ] The independent verification reviewer did not implement the evidence reviewed.
- [ ] Policy activation is not approved solely by the policy author.
- [ ] Runtime separation boundaries affected by this change were explicitly assessed.

Reviewer identities and independence evidence:

## Delivery

- [ ] Branch matches `codex/` policy.
- [ ] Commit and pull-request titles follow Conventional Commits.
- [ ] All required checks pass.
- [ ] Conversations are resolved and approval covers the latest push.
- [ ] No direct or unreviewed delivery to `main` is requested.
