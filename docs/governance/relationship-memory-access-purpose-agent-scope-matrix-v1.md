# Relationship Memory Access, Purpose, and Agent-Scope Matrix v1

- Status: Preparation-only; no role or runtime authorization
- Scope: REL-MEM-03 and Position 2

All future operations require immutable authenticated Tenant and Area scope;
Project and Session only narrow a bound signal. Purpose, classification, review,
freshness, retention, and deletion state must match before use.

| Actor | Permitted future operation | Explicitly forbidden |
| --- | --- | --- |
| Service owner | service-handle customer request after documented contract, purpose, and technical checks | customer self-service control, direct-store action, scope/purpose override |
| Reader | consume a purpose-matched, reviewed, fresh signal as untrusted context | cross-scope read; truth, authority, profile, or write inference |
| Candidate proposer | submit an inactive typed candidate to the Memory Transition Gate | direct write, self-review, activation, retrieval, scope widening |
| Reviewer | record an independent disposition through the owning Gate | supply scope, approve own candidate, create policy/approval/authority |
| Data-subject service intake | auditable access, correction, or deletion request intake/response | dashboard or direct-store path; bypassing correction/deletion reconciliation |
| Dreaming worker | only propose inactive Area-local hypotheses from a future authorized snapshot | cross-scope linking, tools, activation, promotion, active mutation |
| NB-1 Planner | consider a future minimized approved view as untrusted context | truth, authority, profile decision, memory mutation, tool call, effect |

An unknown actor, scope, purpose, classification, review, or policy denies the
operation. This matrix grants no runtime role.
