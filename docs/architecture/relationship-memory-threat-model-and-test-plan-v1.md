# Relationship Memory Threat Model and Test Plan v1

- Status: Preparation-only threat analysis; no runtime-security claim
- Scope: REL-MEM-07 and Position 3

| Threat | Required future negative evidence |
| --- | --- |
| Cross-Company, Area, or Project leakage | vary every authenticated scope and cache/index key; deny before exposure |
| Purpose bypass | missing, broader, or payload-defined purpose denies and audits |
| Profile inference | trait, score, segment, vulnerability, or eligibility output denies/quarantines |
| Direct write | data store, worker, Planner, or proposer bypass leaves no protected mutation |
| Dreaming bypass | cross-Area input, tools, activation, or promotion denies |
| Deletion remnants | derivatives, indexes, caches, replicas, and restore path unavailable until reconciliation |
| Correction conflict | no use until independently reviewed disposition |
| Planner authority escalation | signal cannot produce authority, profile, memory mutation, tool call, or effect |

Position 3 requires separate acceptance and independent verification of schema
and Memory Gate design, audit/deletion propagation, and negative Scope/Purpose
tests. Planned tests are not execution evidence.
