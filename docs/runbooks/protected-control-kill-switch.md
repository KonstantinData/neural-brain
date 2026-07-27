# Proposed Protected Control Plane Kill-Switch Review Runbook

- Status: Design-review runbook only; not an operational shutdown procedure
- Task: S1-02.5
- Authority: No runtime authority; dependent on a future accepted ADR

## Use boundary

Do not use this document to operate an environment. No accepted runtime,
credential-revocation path, control-state store, actor registry, deployment
mapping, or recovery authority exists in this repository. An incident must use
the separately authorized environment-specific incident process.

## Evidence package for architecture decision

The decision coordinator collects a versioned review package that includes:

1. the exact contract version and digest;
2. authenticated scope catalog and control-scope conflict rules;
3. named role/identity and separation-of-duties evidence, excluding secrets;
4. proposed PostgreSQL authorization, protected-state, audit, backup/restore,
   and break-glass design;
5. executor, sandbox, fence, credential, Goal Gate, Action Gate, verifier, and
   reconciliation interface specifications;
6. a preregistered positive, negative, failure, race, restart, partition, and
   recovery test plan;
7. independent security/safety review findings and disposition;
8. a release-stop register with owner, expiry, and exact unblocker for every
   unknown, disagreement, or untested property.

## Required review sequence

1. Verify that ADR-006 is classified as historical input and that the proposal
   does not reactivate it.
2. Verify that all control inputs originate in authenticated Protected Control
   Plane context and that unknown evidence fails closed.
3. Trace each state transition to an actor, guard, CAS revision, atomic audit,
   credential treatment, fence behavior, and recovery outcome.
4. Confirm that `drain`, `disabled`, restart, and partition cannot admit a new
   external effect and that ambiguous work remains `indeterminate` until
   authoritative reconciliation.
5. Confirm independent review and recovery approval are distinct from the
   triggering operator, credential revoker, executor, verifier, and Brain.
6. Record accept, replace, or reject decision in an authorized ADR. If any
   item is unknown, retain the affected release stop and do not authorize work.

## Future implementation readiness gate

After—not before—ADR acceptance, create separately owned packages for schema
and roles, transition gate, revocation integration, executor enforcement,
reconciliation, and independent verification. Each package needs an isolated
threat review and the contract's required test evidence. No package may assume
the work of another package is complete.
