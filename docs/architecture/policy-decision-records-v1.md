# Policy Decision Records v1

S1-02.4 adds immutable decision records that bind an outcome, reason codes,
obligations, required approver roles, and validity to one authenticated actor
and complete Tenant/Area/Project/Session scope plus authority, parameter,
checkpoint, and policy digests.

The record is non-authorizing: it cannot create missing authority, activate a
policy, or override the Security Floor. `is_valid_for` is false after expiry or
whenever any bound fact differs. Implementation is
`neural_brain.security.decision`; evidence is in
`tests/unit/test_policy_decision.py`.
