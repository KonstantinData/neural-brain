# ADR Status

This is the canonical current-state view for Neural Brain architecture
decisions. It is the first document to read when deciding whether an ADR is
current authority, retained subsystem authority, or historical evidence.

## Current Baseline

| Layer | Governing ADRs | Status |
| --- | --- | --- |
| Product boundary | ADR-018 | Current complete protected cognitive-system target. |
| Memory Core | ADR-015, ADR-016, ADR-017 | Retained subsystem authority inside ADR-018. |
| Scope and isolation | ADR-002, ADR-016 | Current for operational objects and hierarchy catalog scope. |
| Protected ledger and evidence | ADR-003, ADR-012 | Current for PostgreSQL, audit, retention, and evidence immutability. |
| Security floor and policy | ADR-005 | Current and widened by ADR-018. |
| Runtime and inference | ADR-013, ADR-014 | Current foundation baseline; capability enablement remains stage-gated. |

## Clean Authority Model

| Authority | ADRs | Rule |
| --- | --- | --- |
| Current | ADR-001, ADR-002, ADR-003, ADR-005, ADR-012, ADR-013, ADR-014, ADR-016, ADR-017, ADR-018 | These records may authorize implementation when aligned with the current architecture directive, contracts, tests, and release gates. |
| Retained subsystem | ADR-010, ADR-015 | These records authorize only the Memory Core subset named in their headers. They do not define the full Neural Brain product boundary. |
| Historical | ADR-004, ADR-006, ADR-007, ADR-008, ADR-009, ADR-011 | These records are preserved as design history. They cannot authorize runtime implementation until revalidated by a new accepted ADR. |

## Required Reading Order

1. ADR-018 for the complete product boundary.
2. Architecture Directive v4.0 for operational architecture.
3. ADR-015, ADR-016, and ADR-017 for retained Memory Core constraints.
4. ADR-013 and ADR-014 for runtime and inference constraints.
5. Historical ADRs only when revalidating earlier Goal, Action, dispatch,
   kill-switch, or verification designs.

## Active Revalidation Queue

| Historical topic | Historical ADRs | Required before implementation |
| --- | --- | --- |
| Goal and Action gates | ADR-004, ADR-007, ADR-011 | New complete-system ADR or explicit revalidation under ADR-018. |
| Kill switch | ADR-006 | New Protected Control Plane decision and tests under ADR-018. |
| Action preparation and commit | ADR-008 | New Action Gate, budget, fence, audit, and reconciliation contract. |
| Dispatch journal and effect reconciliation | ADR-009 | New delivery-stage decision; generalized outbox remains later-stage work. |

## Maintenance Rule

Every ADR must have a uniform header containing status, date, authority, theme,
stage scope, supersession links, amendment links, and a Notion decision source.
Every ADR must also appear in `README.md` and `adr-authority.json`.

The authoritative consistency check is:

```powershell
python tools/validate_adrs.py
```
