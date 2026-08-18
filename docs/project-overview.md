# Neural Brain: External Project Overview

## What This Project Is

Neural Brain is an engineering foundation for a protected cognitive system. It
focuses on a difficult prerequisite for AI-enabled products: retaining and
retrieving scoped memory without allowing a caller, prompt, or shared database
connection to change the trusted Tenant context.

The repository is designed for engineers and teams who value clear system
boundaries, auditable state changes, and evidence before capability claims.

## What Works Today

The implemented Memory Core provides:

- a PostgreSQL-backed Brain-to-Session scope catalog;
- one PostgreSQL Runtime identity per Tenant, with controlled provisioning,
  credential revision, rotation, and deprovisioning primitives;
- Tenant-bound database pools that verify the requested Tenant against the
  database identity before a connection is used;
- OIDC-authenticated access to existing Memory Gate operations;
- atomic observation, Working Memory, checkpoint, and audit persistence; and
- a local demonstration and automated verification environment.

This is useful as a reference implementation and integration foundation where
strict Tenant isolation and protected memory state matter.

## What Is Deliberately Not Claimed

The repository does not provide a hosted service, a customer deployment, a
production Secret Store integration, or an externally operated OIDC/JWKS
integration. It also does not claim production autonomy or completion of the
full Neural Brain target.

Those boundaries are intentional: the code distinguishes implemented local
mechanisms from operating controls that must be designed, deployed, and
verified in the target environment.

## Integration Starting Point

A first technical integration can build on the existing Tenant provisioning,
Tenant-specific pool resolver, and OIDC consumer library. It needs four
environment-specific components:

1. a PostgreSQL environment with the protected schema and administrative
   provisioning access;
2. a managed Secret Store implementing the credential provider interfaces;
3. an approved OIDC issuer, audience, and JWKS operating model; and
4. a service Runtime that exposes the consumer library through the product's
   authenticated boundary.

## Engineering Focus

The project demonstrates practical work across Python, PostgreSQL security,
OIDC authentication, scoped authorization, connection-pool isolation, typed
domain boundaries, migration safety, automated testing, and traceable
architecture decisions.

For implementation detail, begin with the [README](../README.md), then follow
the source packages under `src/neural_brain/` and the executable migrations in
`migrations/`.
