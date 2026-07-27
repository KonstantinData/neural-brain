# REL-MEM-01 through REL-MEM-08: Relationship Memory Preparation

- Controller: `Relationship Memory governance and preparation controller`
- Notion controller: https://app.notion.com/3aa1c1ac5ec08178b06cc7694fe00fcf
- Migrations and runtime implementation: none

| Package | Repository evidence | Boundary |
| --- | --- | --- |
| REL-MEM-01 | ADR-018 revalidation proposal | downstream, non-authorizing context only |
| REL-MEM-02 | signal schema and focused tests | contract only; no signal instance/runtime |
| REL-MEM-03/04 | scope/purpose and privacy matrices | roles/privacy facts remain future qualified work |
| REL-MEM-05 | NB-1 Planner revalidation references | future untrusted view only; no Planner runtime |
| REL-MEM-06/07 | Dreaming boundary and threat/test plan | no Dreaming execution or security claim |
| REL-MEM-08 | service-managed governance runbook | no operational procedure executed |
| REL-MEM-16 | Position 3 future enforcement package | separate acceptance and independent verification required |

Position 3 derives from Position 2 and must separately authorize schema and
Memory Gate design, audit/deletion propagation, and negative Scope/Purpose
tests. It remains runtime-disabled; retrieval, Planner, and Dreaming runtimes
remain separately contracted.
