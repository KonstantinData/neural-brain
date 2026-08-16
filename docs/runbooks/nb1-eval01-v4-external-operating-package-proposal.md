# NB-1 EVAL-01 v4 External Operating Package Proposal

- Status: Proposed; pending accepted architecture clarification
- Scope: External preparation workflow only for `EVAL-01.NB-1.safe-serial-cognition.v4`
- Authority: None. This package neither appoints an actor nor authorizes an
  artifact, evaluation, gate decision, stage exit, release, runtime, external
  effect, or NB-2 work.

## Purpose and current block

This package converts the existing v4 preparation, organization, freeze, and
artifact-manifest contracts into an exact external owner/action checklist. It
does not repair their active custody conflict. Frozen v4 says that
`hidden_dataset_provider` is a logical custody duty performed by the
`independent_evaluator_only`. Inherited generator, runbook, and executable
evidence surfaces instead expect a separate provider organization.

The latter route is a proposed replacement only. It is not an EVAL-01 v4
operating path until the Architecture Decision Owner accepts an ADR-018/v4
clarification. No participant may resolve that conflict by changing frozen v4
text, self-attestation, a subagent, a branch, a worktree, a repository role, or
an identifier prefix.

## Exact owner/action checklist

| Order | Owner | Required action and evidence | Fail-closed outcome |
| --- | --- | --- | --- |
| 1 | Architecture Decision Owner | Accept, reject, or otherwise dispose of the unresolved public-artifact-generation, baseline-definition, and inherited separate-provider questions through an ADR-018/v4 clarification. This package defines neither evaluation criteria nor values. | Without an accepted disposition: no v4 candidate freeze, hidden attachment, or external operation. |
| 2 | Designated Independent-Review Authority | Externally appoint and attest evaluator, reviewer, registry custodian, key custodian, audit owner, release authority, and recognition authority. Attest identity, organization, reporting line, qualification, mandate, conflict, validity, deputy, and handoff. | No external appointment/separation evidence: independent evaluation blocked. |
| 3 | Independent Reviewer / Registry Custodian | Accept frozen v4 specification/protocol and reviewer-controlled registries for identities, attestations, candidate freezes, hidden commitments, public keys, validity, and revocation. | Unknown, expired, revoked, self-supplied, mismatched, or unverifiable record: evidence inadmissible. |
| 4 | Implementation Owner + Independent Reviewer | Submit and recompute a clean, committed public-only candidate plus complete canonical v4 freeze receipt and manifests. | Missing binding or post-freeze change: candidate inadmissible; hidden attachment blocked. |
| 5 | Independent Evaluator | As the sole v4 hidden custodian, create and seal the hidden artifact outside the repository and record a non-disclosing pre-run commitment. The reviewer checks completeness only. | Any transfer or disclosure into the implementation trust domain, or a separate-provider v4 route: evaluation invalid. |
| 6 | Independent Evaluator | Run frozen candidate, evaluator-owned baselines, and ablations in fresh, read-only, network-disabled, bounded, effect-free processes. Finalize every completed, failed, aborted, crashed, duplicate, and missing-output attempt in the append-only ledger. | Missing/rewritten ledger entry or unknown execution condition: evidence inadmissible. |
| 7 | Independent Evaluator + Key Custodian | Release only permitted aggregate canonical-JSON evidence with SHA-256 bindings and a detached Ed25519 signature from a trusted, non-revoked key. | Hidden material, private key, signing token, or per-sequence outcome exposure: evidence inadmissible. |
| 8 | Independent Reviewer | Verify receipt, registries, role attestations, key status, signature, ledger continuity, contamination, hard failures, resource results, and claim boundary. | Any unknown, stale, contradictory, contaminated, unsigned, revoked, or incomplete item: evidence inadmissible. |
| 9 | Separately Authorized Evaluation-Gate Reviewer | Review admissible evidence using the accepted gate process. | No signature, aggregate score, preparation step, or reviewer recommendation automatically passes G0/G1, exits NB-1, releases anything, recognizes Neural Brain, enables runtime, or activates NB-2. |

## Proposed replacement boundary

Until an accepted clarification changes it, the only proposed v4 custody model
is:

```text
hidden_dataset_provider = logical duty
custodian_evaluator_id = independent_evaluator_id
separate provider identity, organization, registry record, or transfer = denied
```

The legacy `provider` / `provider_id` terms remain historical implementation
inputs, not authority to run v4. A successor must be accepted before any
corresponding runtime or evidence-schema change is made.

## External evidence package

The reviewer must receive only references and permitted aggregate material:

- externally attested appointment, separation, custody, conflict, and key
  records;
- accepted specification/protocol, freeze receipt, hidden commitment, registry,
  key-status, and revocation references;
- complete append-only-ledger commitment, aggregate baseline/ablation results,
  confidence intervals, resource and contamination reports, hard-failure
  results, and detached signature;
- an explicit claim boundary stating that the package does not itself pass a
  gate, stage, release, recognition, runtime, external effect, or NB-2.

Seeds, hidden examples, labels, latent metadata, provider/evaluator private
implementation details, signing keys/tokens, and raw per-sequence correctness
are excluded from this repository, the implementation owner, and aggregate
reports.

## Repository verification and traceability

The machine-readable proposal is
[`nb1-eval01-v4-external-operating-package-proposal-v1.json`](../architecture/contracts/nb1-eval01-v4-external-operating-package-proposal-v1.json).
Its structural regression test proves only that this proposal remains
non-authorizing, v4 sole-custody, and fail-closed. It is not an independent
appointment, signature validation, evaluation, or gate-review result.

See [`EVAL-01-external-operating-package-proposal.md`](../traceability/EVAL-01-external-operating-package-proposal.md)
for the requirement-to-test and external-evidence mapping.
