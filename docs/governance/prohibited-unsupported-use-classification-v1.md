# Prohibited and Unsupported Use Classification v1

- Status: Normative foundation-governance contract
- Contract: [`../architecture/contracts/prohibited-unsupported-use-v1.json`](../architecture/contracts/prohibited-unsupported-use-v1.json)
- Governing decisions: ADR-001, ADR-005, and ADR-018
- Current maturity: early Memory Core foundation

## Purpose

This contract provides a deterministic, fail-closed classification input for
proposed uses of the complete, product- and domain-neutral Neural Brain target.
It retains the Memory Core as a protected internal subsystem and does not
redefine the product boundary as a memory service.

The only outcomes are `prohibited` and `unsupported`. There is deliberately no
`allow`, activation, release, or deployment outcome. The ordered rules first
deny a non-overridable Security Floor conflict, then deny incomplete or unknown
evidence, then keep sensitive, high-impact, high-risk, deployment-specific,
domain-specific, and unimplemented uses unsupported. A use outside the explicit
catalog is also unsupported; absence is never permission.

## Non-overridable boundary

Security Floor prohibitions are immutable. No policy configuration, approval,
assessment, model output, prompt, memory content, tool output, request payload,
or self-report may widen authority, change trusted scope, mutate protected
state outside its Gate, cause an insufficiently controlled external effect,
permit productive self-mutation, or compensate for failed recognition evidence.

Classification and human approval can be necessary future controls, but neither
can turn a prohibited use into authorization. An unsupported outcome remains
disabled until a separately accepted future process supplies every applicable
classification, qualified lawful-operation evidence where required,
authenticated authority, scoped safeguards, complete evidence gates, and
required independent human approval.

## Deliberate limits

This contract does not make legal, regulatory, or lawfulness determinations;
classify real people, domains, or deployments; establish a lawful basis; grant
authority; approve policy; enable runtime behavior; or authorize release. Any
future deployment-specific assessment and release process remains separately
governed and must preserve all Protected Control Plane and delivery-stage gates.
