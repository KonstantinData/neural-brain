# NB-1 Independent Hidden Evaluation Runbook

- Status: evaluator handoff and evidence-intake procedure
- Scope: NB-1 mechanism evidence only
- Prohibited claim: this runbook cannot grant an evaluation, recognition, stage,
  release, production, or Neural Brain Candidate status

## Trust boundary

The implementer owns source code, public train/development data, and the frozen
candidate export. A separate artifact provider owns the hidden generator seed,
examples, labels, and pre-run commitment. A separate evaluator owns the scoring
runner, attempts ledger, aggregate report, and Ed25519 signing key. An
independent reviewer supplies accepted full candidate freeze receipts, exact
hidden commitments, specifications, identity attestations, and public-key
registries used by evidence intake.

A subagent, branch, worktree, process name, or `independent:*` string inside the
implementation trust domain does not satisfy this separation.

## Preconditions

1. The evaluation specification and generator contract are frozen before any
   hidden artifact is attached. The active replacement pair is
   `EVAL-01.NB-1.safe-serial-cognition.v4` and
   `nb1-serial-context-generator-v4`.
2. The source tree is committed and clean.
3. The model manifest, parameters, training artifact, candidate code, contract,
   lockfile, source commit, tree digest, fixed training-derived majority label,
   and freeze time are bound by the candidate bundle.
4. Provider, evaluator, implementation owner, and reviewer identities and key
   custody are recorded outside this repository.
5. Historical EVAL-01 v3 is absent from the accepted-specification registry.

Unknown or missing preconditions stop the run.

## Candidate export stop

There is currently no exportable v4 candidate. The checked-in model is bound
to rejected EVAL-01 v3. The export command fails closed for that digest and
may only become operational after a v4 public train/development artifact,
training artifact, model manifest, parameters, and candidate freeze receipt
have been generated and accepted.

When unblocked, the command must reject a dirty worktree. Its output may contain
learned parameters and public provenance but no hidden example, label, seed,
provider metadata, score, threshold decision, correctness result, or gate claim.

## External attachment and execution

The external provider commits the hidden artifact digest, generator contract,
split identity, sequence count, and timestamp before scoring. The candidate
receives only opaque run/sequence/observation identifiers and bounded unlabeled
feature sequences. It returns ordered predictions bound to the candidate,
input, and run digests.

The evaluator runs the full mechanism and independently owned reference
baselines/ablations in fresh, network-disabled, read-only candidate processes.
Every completed, failed, or aborted attempt is finalized in the append-only
attempt ledger. Crashes and missing outputs are failures, not invisible retries.

Detailed labels and per-sequence correctness stay sealed with the evaluator.
Only aggregate results, confidence intervals, contamination results, resource
measurements, failure disclosures, and immutable digests enter signed evidence.

## Signed evidence intake

Evidence uses canonical JSON, SHA-256, and a detached Ed25519 signature. The
reviewer calls `verify_signed_hidden_evidence` with five external registries:

- accepted specification ID to digest;
- accepted candidate bundle digest to the complete validated freeze receipt;
- accepted provider commitment ID to the exact canonical hidden commitment digest;
- evaluator/provider identity to the accepted attestation digest;
- evaluator signer ID to trusted Ed25519 public key.

Unknown candidate, specification, digest, signer, missing mode, attempt,
contamination result, failure result, resource result, signature, or prohibited
effect fails closed. Successful intake means only that the external aggregate
evidence is structurally complete, registry-bound, and signature-valid. A
separate independent gate review remains mandatory.

## Historical v3 stop

EVAL-01 v3 was rejected before hidden attachment. Its public generator has six
distinct feature/label patterns across 512 training sequences, making the
hidden example space enumerable by the implementer. Do not run, sign, accept,
or use v3 as held-out cognitive evidence. Retain its frozen files and rejection
record as immutable history.
