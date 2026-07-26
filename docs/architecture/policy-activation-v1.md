# Policy activation v1

## Scope

This early Memory Core control-plane contract permits no implicit policy
activation. A compiled policy remains inactive until a regression result and a
four-eyes approval bind to its exact canonical policy digest.

## Fail-closed rules

- The invariant-suite result, approval, and candidate policy must share one
  immutable digest.
- The suite must pass and the approval must be issued after the suite result.
- The policy author and approver are distinct identities.
- Unknown fields, naive timestamps, mismatched evidence, expired policy, or
  self-approval deny activation.
- Activation evidence does not widen the Security Floor, create authority, or
  enable a later Neural Brain stage.

## Traceability

This contract implements S1-02.7 under ADR-018 and Architecture Directive v4.0
Sections 2, 3, 10, 13, and 14. Tests in `tests/unit/test_policy_activation.py`
cover positive admission and the matching negative paths.
