# NB-1 and EVAL-01 Independent Architecture Review — 2026-08-16

- Status: Review recommendation; non-authorizing
- Notion task: `Independent architecture review — EVAL-01 v4.1 and NB-1 revalidations`
- Governing sources: ADR-018 and Architecture Directive v4.0
- Reviewed proposals: EVAL-01 v4.1 clarification, v4.1 baseline-ceiling
  evidence rule, external independent-evaluation operating package, NB-1
  metacognition revalidation, and NB-1 model-manifest registry revalidation

## Review boundary

This review does not accept or amend an ADR, approve a candidate, create or
access hidden material, appoint an evaluator, create a registry or key, pass a
gate, authorize a migration, claim an NB-1 exit, or activate NB-2. Current
unknown or conflicting evidence remains a release stop.

## Reconciled decision recommendations

| Proposal | Recommendation | Required decision-owner action |
| --- | --- | --- |
| EVAL-01 v4.1 clarification | **Revise** | Reject `0.750000` and replace the proposal with one complete successor protocol; do not accept it together with the ceiling rule as written. |
| v4.1 baseline-ceiling evidence rule | **Accept only its rejection of `0.750000`; otherwise revise** | Approve a separate public-calibration protocol only after its sampling, statistical decision, and successor-specification rules are complete. |
| External independent-evaluation operating package | **Revise** | Keep v4 explicitly blocked and bind every operational step to the ID and digest of a later accepted successor. |
| NB-1 metacognition revalidation | **Revise, then decide** | Preserve its gap finding, but decide complete internal `defer`/`stop` semantics before implementation. |
| Trusted model-manifest registry revalidation | **Revise, then decide with priority** | Decide protected writer authority, scope, lifecycle, and atomicity before any schema or runtime package. |

## Blocking findings

1. The v4.1 clarification fixes a `0.750000` ceiling, but the ceiling package
   correctly rejects it: a full-model accuracy of `0.800000` leaves only the
   point lift `0.050000`, while v4 requires the lower 95% confidence bound to
   exceed that lift. The two proposals cannot be accepted together.
2. The clarification applies a baseline result while generating an individual
   sequence, although accuracy exists only for a completed artifact. This is
   baseline-conditioned rejection sampling and conflicts with the proposed
   one-complete-artifact check.
3. The clarification has seven baselines; the ceiling rule has eight, adding a
   parameter-matched recurrent non-neural comparator. One successor must bind
   exactly one complete baseline set, selection rule, artifact check, and
   receipt contract.
4. Frozen v4 contains a custody conflict: its specification assigns the hidden
   provider duty to the independent evaluator, while generator, runbook, and
   evidence surfaces retain separate-provider fields. No v4 or v4.1 hidden
   handoff is admissible until a complete, digest-bound successor replaces or
   guards every affected surface.
5. The ceiling panel is not yet reproducible: its IID seed source, commitment
   time, failure policy, target quantity, correlation/discordance bands,
   bootstrap generation, simultaneous-interval method, and boundary decisions
   remain unspecified. Its `C_panel` is not by itself a hidden-artifact ceiling.
6. `defer` and `stop` have no accepted selection, audit, expiry, checkpoint,
   recovery, or replay semantics. They remain internal proposals; calibration
   claims stay NB-6 evidence.
7. Current PostgreSQL checkpoint handling trusts only the training-artifact
   digest from a process-local mapping; remaining model provenance is caller
   supplied. The registry proposal identifies a material trust gap, but has not
   decided its bootstrap writer, Tenant/Area catalog scope, lifecycle authority,
   direct-DML denial design, or atomic binding/checkpoint/audit transaction.
8. `docs/architecture/delivery-roadmap.md` still calls EVAL-01 v3 frozen,
   contrary to the current v4 evaluation and work-package records. Correcting
   this without changing the rejected-v3 history is a separate documentation
   consistency task.

## Non-compensatory gates

- No candidate, freeze, hidden attachment, evaluator appointment, external
  operation, or gate review before one accepted, executable successor binds the
  generator, all baselines, public calibration, custody migration, and receipt.
- No statistical ceiling before precommitted public seed provenance, a complete
  append-only attempt ledger, all reports (including failures), deterministic
  power protocol, and independent reproduction.
- No `defer` or `stop` implementation before an accepted internal-only contract;
  neither may cause a Goal/Action transition, kill-switch activation, external
  effect, or bypass independent safety supervision.
- No model-manifest migration or integration before an accepted ADR fixes the
  database writer/gate authority, scope, RLS and role model, lifecycle,
  revocation, recovery, audit, and serializable fence semantics.
- No item above establishes NB-1 exit, release, recognition, runtime activation,
  or NB-2 authorization. Later evidence cannot compensate for an earlier unknown
  or failed gate.

## Required decision and integration order

1. **DOC-01:** correct the v3/v4 roadmap inconsistency as a documentation-only
   task; retain v3 as rejected immutable history and v4 as frozen but blocked.
2. **D-MMR:** decide a complete model-manifest registry ADR. Only then authorize
   **MMR-A — schema and authority**, followed strictly by gate integration,
   runtime adapter, operations/recovery, and independent DB/concurrency proof.
3. **D-META:** decide the internal metacognition amendment. Only then authorize
   an effect-free NB-1.5 `defer`/`stop` implementation with scope, audit,
   expiry, recovery, and replay tests.
4. **D-EVAL-CAL:** reject the current clarification as an executable candidate
   protocol and decide a separate public-calibration successor. Only then
   authorize **CAL-01 — public generator and calibration-contract
   implementation**, with no candidate, freeze, hidden material, or external
   roles.
5. **D-EVAL-SPEC:** after CAL-01 publication and independent reproduction,
   decide one final EVAL-01 successor that fixes the exact ceiling, full baseline
   set, receipt bindings, and custody migration.
6. Rewrite the external operating package to that successor ID and digest. Only
   after separate external role/registry attestations, a reviewer-accepted public
   freeze receipt, and a preregistered external run plan may hidden commitment,
   scoring, and later gate review be considered as distinct decisions.

## Verification

- `uv run pytest -q tests/architecture`: `416 passed` on the review base.
- The five proposal-specific structural suites: `19 passed` in total.

These checks establish document and claim-boundary regression only. They do
not prove executable generation, statistical validity, organizational
independence, hidden-data custody, database authorization, or stage evidence.
