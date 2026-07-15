# GitHub Repository Settings Evidence

## Current evidence status

- Repository: `KonstantinData/neural-brain`
- Protected branch: `main`
- Live configuration verified: **Yes**
- Verified at: `2026-07-15T10:42:23.8865025+02:00`
- Authority: explicit autonomous Neural Brain execution instruction dated
  2026-07-15
- Sanitized evidence SHA-256:
  `5aa5a7479a50c5b92e3cc10b9722eb210150308f24f2ca0ad5a383c0bb323419`
- Verification probe: PR #2 is technically mergeable but GitHub reports
  `mergeStateStatus=BLOCKED` and `reviewDecision=REVIEW_REQUIRED`.

## Verified live settings

- Strict required status checks: enabled
- Required checks: `quality`, `PostgreSQL 18 forward migrations`,
  `Secret history scan`, `Dependency, license, and workflow policy`, and
  `Build deterministic release evidence`
- Pull request and one approving review required
- Stale approvals dismissed; approval after latest push required
- CODEOWNERS review and conversation resolution required
- Administrator enforcement enabled
- Force pushes and deletion of `main` disabled

## Re-verification contract

Capture timestamped ruleset or branch-protection API output and verify all of
the following against `repository-policy.json`:

1. Pull requests are mandatory for `main`; direct and force pushes are denied.
2. Required approval, stale-approval dismissal, latest-push approval,
   CODEOWNERS, and conversation-resolution settings are enabled.
3. Every declared blocking check context is configured exactly.
4. Administrators cannot bypass the ruleset and `main` cannot be deleted.
5. Sensitive-path changes require CODEOWNERS review plus the independent
   separation-of-duties evidence recorded in the pull-request template.
6. A deliberately non-compliant pull request is reported as non-mergeable.
7. The captured evidence identifies the repository, branch, ruleset revision,
   actor, and exact verification time without exposing credentials or tokens.

Re-run this verification after any governance or required-check change. Do not
store authenticated API responses containing tokens, private repository
metadata, or other secrets in this repository.
