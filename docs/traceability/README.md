# Implementation Traceability

This directory defines how Neural Brain work is linked from an approved task to
versioned implementation and independently reviewable evidence. Notion is the
coordination ledger; repository artifacts remain the durable technical source
of truth.

## Evidence Chain

Every completed main task and subtask must provide an unbroken chain:

```text
Notion task ID
  -> accepted requirement and acceptance criteria
  -> relevant repository ADRs and contracts
  -> branch and commit or pull request
  -> changed code, migrations, configuration, and documentation
  -> automated tests and exact verification commands
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
secrets, credentials, personal data, or sensitive runtime payloads into an
evidence record.

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

## Reconciliation Rules

Before a pull request or final handoff:

1. Compare the active Notion task and every inline or separate subtask with the
   complete repository diff.
2. Verify that accepted ADRs are synchronized to versioned records before their
   dependent implementation is treated as authorized.
3. Confirm that each changed behavior, schema, operation, or safety invariant has
   corresponding tests and durable documentation.
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
