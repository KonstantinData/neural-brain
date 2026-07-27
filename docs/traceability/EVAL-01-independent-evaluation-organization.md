# EVAL-01 Independent Evaluation Organization Traceability

## Objective

Define the external role separation, decision ownership, matrix evidence, deputy controls, handoffs, and escalation paths required before a future independent EVAL-01 v4 hidden evaluation. This repository slice creates no appointment, authority, candidate, hidden artifact, evaluation, gate result, release, recognition, runtime behavior, or external effect.

## Normative sources

- ADR-018: protected cognitive-system boundary, independent evidence, and no claim before gates pass.
- `docs/architecture/architecture-directive-v4.0.md`: independent Protected Control Plane, deny-by-default authority, and evidence boundaries.
- `docs/architecture/neural-brain-recognition-standard.md`: non-compensatory independent recognition evidence.
- `docs/architecture/contracts/nb1-hidden-evaluation.json`: existing hidden-evaluation and signed-evidence boundary.
- `docs/architecture/contracts/nb1-independent-evaluation-preparation-v1.json`: candidate freeze, hidden custody, ledger, registry, signature, workflow, and B1–B3 preparation requirements.

## Requirement-to-artifact mapping

| Requirement | Versioned artifact | Automated evidence | External evidence still required |
| --- | --- | --- | --- |
| All nine requested responsibilities have responsibilities, rights, prohibitions, independence, conflicts, escalation, deputy, handoff, and evidence requirements; v4 binds Hidden Dataset Provider as an evaluator-only logical duty | `docs/architecture/contracts/nb1-independent-evaluation-organization-v1.json` `roles`, `v4_custody_binding`, and `common_role_requirements` | `tests/architecture/test_nb1_independent_evaluation_organization_contract.py` | Appointment and independently attested identities, mandates, qualifications, scope, and conflicts for separately appointable roles; evaluator custody attestation |
| RACI, approval, review, deputy, escalation, and decision matrices are complete | Contract `matrices` | Contract test asserts all matrices and required decision boundaries | Accepted external governance operation and records |
| Release and recognition cannot arise from EVAL-01 preparation | Contract `scope`, role prohibitions, and `fail_closed`; governance checklist | Contract test asserts preparation-only flags and separate authority | Separate complete gate evidence and authenticated decision mandates |
| Organizational blockers are exact and actionable | Governance `External blockers` and contract `fail_closed` | Contract test asserts fail-closed states | Authority appointments and external evidence completion |

## Acceptance criteria

- [x] The nine requested future responsibilities and their constraints are explicit and machine-readable; v4 correctly keeps Hidden Dataset Provider as evaluator-only logical duty.
- [x] RACI, approval, review, deputy, escalation, and decision matrices are versioned and test-covered.
- [x] The contract fails closed for unappointed identities, conflicts, missing handoffs, and unclear decisions.
- [x] Preparation-only boundaries exclude authority, release, recognition, runtime, and external effects.
- [ ] Role appointment, organizational independence, custody, external registry operation, and mandates are proven. These require external decisions and evidence.

## Verification record

The controller integrates this slice only after an independent read-only review and records combined quality gates, commit, and Notion coordination evidence. External operations must not be represented as completed merely because this preparation contract exists.
