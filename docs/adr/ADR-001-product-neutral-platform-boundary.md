# ADR-001: Product-Neutral Platform Boundary

- Status: Accepted
- Date: 2026-07-15
- Notion source: https://app.notion.com/p/39d1c1ac5ec081828924ca258ee85602
- Notion page ID: `39d1c1ac-5ec0-8182-8924-ca258ee85602`
- Authority: current
- Theme: product_boundary
- Applies to stages: NB-0, NB-1, NB-2, NB-3, NB-4, NB-5, NB-6, NB-7, NB-8
- Supersedes: none
- Superseded by: none
- Amends: none
- Amended by: ADR-015, ADR-018

## Amendment by ADR-018

Neural Brain is a product- and domain-neutral complete cognitive system. Its
Memory Core is governed as a protected subsystem. Product integrations are
external consumers and effect adapters; they do not define Neural Brain's
domain model, policies, defaults, goals, or architecture.

## Amendment by ADR-015

Neural Brain is a product- and domain-neutral **memory system**. Product
integrations, agents, and applications are external memory consumers; they do
not make Neural Brain an agent runtime or assign it goals, actions, or tools.

## Context

Neural Brain must serve many independent topics and projects rather than one
product.

## Decision

Neural Brain has a dedicated repository and Notion area. Product integrations
are consumers of Neural Brain, not owners of its domain model, policies,
defaults, or architecture.

## Consequences

The platform contains no product-specific assumptions. Product adapters and
policies require explicit, scoped configuration.

## Invariants and Constraints

- Neural Brain remains product- and domain-neutral.
- A consuming product does not define platform behavior implicitly.
- Product adapters and policies are introduced only through explicit, scoped
  configuration.

## Relationship to the Architecture Directive

This decision establishes the product-neutral platform boundary required by the
architecture directive. The directive applies within that boundary and may not
be reinterpreted through the assumptions of a consuming product.
