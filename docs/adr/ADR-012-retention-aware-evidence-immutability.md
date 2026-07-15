# ADR-012: Retention-Aware Evidence Immutability

- Status: Accepted
- Date: 2026-07-15
- Notion source: https://app.notion.com/p/39d1c1ac5ec081fa850afe7e90516111
- Notion page ID: `39d1c1ac-5ec0-81fa-850a-fe7e90516111`

## Amendment by ADR-015

This decision applies to all governed memory forms and their derivatives, not
only episodes and audit history. Claims, assessments, procedures, summaries,
embeddings, indexes, caches, and provenance-linked derivatives participate in
the authorized retention, deletion, anonymization, and audit path.

## Context

Append-only evidence requirements must coexist with privacy, retention, lawful
deletion, and anonymization obligations.

## Decision

Episodes and audit history are not silently rewritten. Corrections are appended.
Authorized retention or deletion processing may remove or anonymize content and
all of its derivatives while retaining non-reconstructive evidence that the
deletion occurred.

## Invariants and Constraints

- Existing episode and audit content is not silently rewritten.
- Corrections are new, appended evidence.
- Deletion or anonymization requires an authorized retention or deletion path.
- Deletion covers payloads, embeddings, caches, indexes, and derivatives.
- Retained deletion evidence must not reconstruct the removed content.
- Deletion processing is resumable and audited.

## Consequences

Deletion must propagate through payloads, embeddings, caches, indexes, and other
derivatives. The operation remains resumable and auditable without preserving a
reconstructive copy of content that was lawfully removed or anonymized.

## Relationship to the Architecture Directive

This decision specializes the architecture directive's audit, memory, privacy,
and retention requirements. Immutability protects evidence against silent
rewrites but does not mean indefinite retention beyond an authorized deletion or
anonymization obligation.
