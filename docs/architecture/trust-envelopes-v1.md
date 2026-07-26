# Trust Envelopes v1

## Status

S1-02.6 adds a typed boundary for payloads arriving from the ingestion, model,
memory, and integration surfaces. It does not activate a new runtime capability
or make a payload authoritative.

## Boundary

The untrusted payload envelope carries only a declared surface, an opaque
payload schema identifier, and opaque payload content. Its strict schema rejects
unknown envelope fields. Payload maps cannot supply identity, scope, authority,
approval, policy, purpose, classification, retention, legal-hold, promotion,
or lifecycle values. Nested payload content remains opaque data, not trusted
control, and must be interpreted only through a future surface-specific gate.

Trusted identity, immutable scope, authority, policy, purpose, data class,
retention, legal hold, promotion, and protected state remain runtime- or
gate-derived. This preserves ADR-018 and Architecture Directive v4.0's rule
that prompts, observations, model output, memory content, tools, and request
payloads cannot define or expand trusted context.

## Traceability

Implementation: neural_brain.security.envelopes.
Automated evidence: tests/unit/test_trust_envelopes.py.
Foundation contract: docs/architecture/contracts/envelopes.json.
