---
title: "PR #2 - FND-02 Executable Architecture Baseline"
created_at: 2026-07-17T11:05:00+02:00
area: Neural Brain
repository: D:\Git-GitHub\Repositories\condata\neural-brain
task: "Learn PR #2: feat: complete executable FND-02 architecture baseline"
task_type: per-pr-learning-artifact
domain: Architecture contracts, protected state, threat modeling
difficulty: advanced
estimated_learning_time: 90 minutes
concepts:
  - ADR sequence
  - machine-readable contracts
  - protected state machines
  - release stops
  - threat model
  - property-based tests
prerequisites:
  - JSON Schema basics
  - state machine modeling
  - test-driven architecture review
  - security threat modeling basics
related_files:
  - docs/architecture/architecture-directive-v1.1.md
  - docs/architecture/threat-model.md
  - docs/architecture/contracts/envelopes.json
  - docs/architecture/contracts/ledger-invariants.json
  - docs/architecture/contracts/release-stops.json
  - docs/architecture/contracts/stage-capabilities.json
  - tests/architecture/test_contract_json_schema.py
  - tests/architecture/test_machine_readable_contracts.py
related_components:
  - FND-02 architecture baseline
  - architecture contracts
  - release stops
related_repositories:
  - neural-brain
related_topics:
  - PR #2
  - ADR-001 through ADR-014
  - protected state
  - local-only inference boundary
learning_status: new
tags:
  - Projektbasiert
  - Fortgeschritten
notion_tracker_url: https://app.notion.com/p/3a01c1ac5ec081189f12ce0778537d72
---

# PR #2 - FND-02 Executable Architecture Baseline

## 1. Task Summary

PR #2 converted Neural Brain's early architecture into versioned decisions, machine-readable contracts, and tests. It defined protected state ownership, state machines, ledger invariants, release stops, local-only inference boundaries, and a threat model.

The learning goal is to understand how architecture can become executable evidence instead of static documentation.

Source PR: https://github.com/KonstantinData/neural-brain/pull/2

## 2. Context

FND-01 made the repository reproducible. FND-02 made the architecture reviewable and testable. The project needed exact rules for authority, state transitions, quiescence, ledger behavior, and release blockers before any protected runtime could be safely implemented.

## 3. Approach

The PR added ADRs, architecture directive text, JSON contracts, and tests that verify contract structure and invariants. It also added negative and property-based tests so invalid state transitions and unsafe release assumptions fail.

The key method is "docs plus tests": normative architecture is written in Markdown, but important boundaries are also encoded in machine-readable files and tested.

## 4. Key Decisions

One decision was that protected state must have explicit transition gates. General application code should not become a writer just because it can reach the database.

Another decision was that unknown scope, actor, policy, state, or external-effect outcome fails closed. This prevents the system from silently accepting ambiguous authority.

ADR-014 also established local Ollama-only inference as the approved future boundary, with no automatic cloud fallback.

## 5. Concepts and Methods

Machine-readable contracts make architecture enforceable. A JSON file can express allowed states, required fields, stage capabilities, or release stops, and tests can detect drift.

Release stops are non-negotiable conditions that block release when evidence or safety is missing.

Property-based testing checks broad classes of behavior rather than only hand-picked examples.

## 6. Knowledge Prerequisites and Gaps

You should understand JSON Schema, finite state machines, and how tests can enforce documentation. You should also study the difference between an architectural invariant and an implementation detail.

The gap to focus on is translating prose requirements into contracts without losing meaning.

## 7. Learning Path

```text
Executable architecture
|-- ADR rationale
|-- Architecture directive
|-- JSON contracts
|-- Positive and negative tests
`-- Release-stop enforcement
```

## 8. Practical Examples

Compare `docs/architecture/contracts/release-stops.json` with `tests/architecture/test_release_stop_contract.py`. The contract records release blockers; the test ensures they remain structured and present.

Review `tests/architecture/test_machine_readable_contracts.py` to see how contract shape becomes a quality gate.

## 9. Exercises

### Beginner

- Objective: Pick one contract and summarize its purpose.
- Expected result: Five bullet points.
- Hints: Start with `release-stops.json`.
- Validation criteria: You can explain what would break if it disappeared.

### Intermediate

- Objective: Map one ADR to one contract and one test.
- Expected result: A traceability chain.
- Hints: Use ADR-014 or ledger invariants.
- Validation criteria: The chain includes rationale, artifact, and verification.

### Advanced

- Objective: Write a contract idea for a future NB-2 perception gate.
- Expected result: Required fields plus one positive and one negative test idea.
- Hints: Preserve fail-closed unknown state.
- Validation criteria: Missing evidence blocks release.

## 10. Reflection Questions

1. What makes architecture "executable"?
2. Why are release stops non-compensatory?
3. What should remain prose-only?
4. Where can JSON contracts become too rigid?
5. Why was inference kept local-only at the architecture boundary?

## 11. Common Mistakes and Risks

The main mistake is believing architecture is enforced because it is documented. In this PR, enforcement starts when contracts and tests make drift visible.

Another risk is encoding too much too early. Contracts should cover durable invariants, not incidental implementation details.

## 12. Key Takeaways

1. Architecture decisions need testable surfaces.
2. Unknown authority must fail closed.
3. Release blockers should be explicit artifacts.
4. Local-only inference prevents accidental cloud fallback.
5. FND-02 prepares implementation by narrowing ambiguity.

## 13. Area and Repository Context

This PR belongs to Neural Brain's foundation baseline. Some Goal and Action concepts were later superseded, but the method of executable architecture remains important.

Related Notion tracker entry: https://app.notion.com/p/3a01c1ac5ec081189f12ce0778537d72

## 14. Related Themes

### ADR Governance

- Relationship: ADRs provide decision authority.
- Type: Architecture documentation.
- Learning value: Teaches durable decision tracking.

### Contract Testing

- Relationship: Contracts are verified by tests.
- Type: Quality engineering.
- Learning value: Converts architecture drift into failures.

### Safety Boundaries

- Relationship: Release stops prevent unsafe delivery.
- Type: Risk management.
- Learning value: Keeps capability claims evidence-bound.

## 15. Further Learning Resources

- `docs/architecture/architecture-directive-v1.1.md`
- `docs/architecture/contracts/`
- `tests/architecture/`

