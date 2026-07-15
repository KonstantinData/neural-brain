# Security Scanning and Dependency Review

## Purpose

The `Security` workflow is a required, fail-closed pull-request check. It scans
the complete Git history for credentials and verifies the locked Python supply
chain, known vulnerabilities, package licenses, immutable GitHub Action
references, and least-privilege workflow configuration.

The workflow uses only the read-only `contents` permission. Checkout never
persists credentials, security jobs do not consume repository or organization
secrets, and external Actions are pinned to reviewed full commit SHAs.

## Blocking Thresholds

The following conditions fail the workflow and block merge:

- any credential detected by the default Gitleaks rules anywhere in Git
  history;
- any secret-scan error or inability to inspect the complete history;
- any known vulnerability reported by the exact pinned `pip-audit` version;
- a stale, inconsistent, or non-reproducible `uv.lock`;
- any dependency with a missing, unknown, explicitly prohibited, or unreviewed
  license string;
- a mutable, unknown, or unapproved GitHub Action reference;
- a checkout that persists credentials;
- a workflow permission with write scope;
- a repository or organization secret reference in security CI; or
- removal or weakening of required hash, strict-audit, lock, or scanner flags.

The vulnerability threshold is deliberately stricter than “critical”: every
known vulnerability reported for the complete locked production and development
graph blocks merge. Scanner errors fail the check rather than producing a clean
result.

## Pins and Integrity

- `uv lock --check` proves that `uv.lock` agrees with project metadata.
- `uv sync --frozen --all-groups --no-editable` proves clean reconstruction
  without modifying the lock.
- `uv export --frozen --all-groups` produces the complete pinned graph with
  hashes for `pip-audit`.
- `pip-audit` runs with hashes, without dependency resolution, and in strict
  mode.
- Security tools have exact versions or immutable source revisions in
  `.github/security-policy.json`.
- The local policy validator confirms that workflow references still match the
  reviewed pins.

Pin updates are normal dependency-maintenance changes. Review the upstream
release and changelog, resolve the new immutable commit or exact package
version, update the workflow and policy together, execute all repository gates,
and record the evidence in the tracked task. Never change a pin only to silence
a finding.

## Credential Finding Response

1. Stop the merge. Do not copy the detected value into an issue, log, Notion,
   chat, fixture, or documentation.
2. Treat the credential as compromised and revoke or rotate it at its
   authoritative provider.
3. Determine its scope and inspect provider audit evidence for misuse.
4. Remove the value from the branch and, when it exists in reachable history,
   coordinate a reviewed history rewrite. Rotation is required even if history
   is rewritten.
5. Re-run the complete-history scan and document only redacted evidence.

## False Positives and Exceptions

There are no inline bypasses, broad path exclusions, vulnerability ignores, or
license wildcards in the baseline. A finding remains blocking until it is fixed
or a narrowly scoped exception is reviewed.

An exception requires a separate tracked issue containing the scanner and rule
identifier, affected package or exact non-secret fingerprint, technical
rationale, risk owner, compensating control, expiry date, and removal condition.
Never include a suspected credential value. Two-person review is required for a
change to `.github/gitleaks.toml`, `.github/security-policy.json`, or blocking
workflow arguments. The exception must match the smallest possible rule,
package, version, path, or fingerprint and must expire. Broad directories,
generic entropy suppression, `continue-on-error`, and weakening a scanner exit
code are prohibited.

Unknown licenses are not classified locally by guess. Confirm the upstream
package metadata and license text, obtain the required legal review, and add
only the exact reviewed license representation. A vulnerability exception must
be removed on upgrade or no later than its expiry, whichever occurs first.

## Local Verification

After synchronizing the frozen environment, run:

```text
uv run --frozen python tools/security_policy.py workflow \
  --workflow .github/workflows/security.yml \
  --policy .github/security-policy.json

uvx --from pip-licenses==5.5.5 pip-licenses \
  --python=.venv/Scripts/python.exe \
  --from=mixed --format=json --output-file=.local/licenses.json

uv run --frozen python tools/security_policy.py licenses \
  --inventory .local/licenses.json \
  --policy .github/security-policy.json
```

Use `.venv/bin/python` instead of `.venv/Scripts/python.exe` on Unix. Local
Gitleaks execution is optional developer feedback; the authoritative check is
the clean GitHub runner scanning complete history with the pinned revision.
