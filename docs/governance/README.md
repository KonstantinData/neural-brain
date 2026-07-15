# Repository Governance

This directory contains the versioned desired repository-governance state for
Neural Brain. The normative contract is
[`repository-policy.json`](repository-policy.json).

The contract requires task branches under `codex/`, Conventional Commit
headers, pull-request review, blocking quality checks, CODEOWNERS review, and
additional independence evidence for memory separation-of-duties-sensitive
changes.
Unknown or unverifiable governance state fails closed.

`@KonstantinData` and `@KonstantinCondata` are the declared code owners. Each
account must retain accepted repository write access. A pending invitation or
read-only access does not establish CODEOWNER eligibility. For any change, the
approval must come from an eligible owner who is distinct from the author and
latest pusher.

## External enforcement boundary

Repository files define the desired state; GitHub enforces it externally. The
current `main` branch protection was configured and verified against this
contract. The sanitized proof, evidence digest, and mandatory re-verification
conditions are recorded in
[`github-settings-evidence.md`](github-settings-evidence.md). Any unknown or
drifted live setting is a fail-closed merge condition.

Changes to this directory are themselves separation-of-duties-sensitive and
require the review defined by the policy. The policy protects Brain-owned memory
boundaries; it does not assign goals, planning, tool execution, or autonomous
behavior to Neural Brain.
