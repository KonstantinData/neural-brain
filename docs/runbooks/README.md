# Runbooks

This directory contains operational, recovery, incident, backup, restore, and
release procedures for implemented Neural Brain memory capabilities.

Runbooks must be executable by their intended operators, avoid secrets, and
identify safety gates that may not be bypassed.

Runbooks must preserve the boundary between the Brain and its consumers.
External-agent planning, goal handling, tool execution, and effect recovery are
consumer concerns unless an explicit integration runbook needs to describe the
boundary; they are not Neural Brain runtime capabilities.

- [`release-artifacts.md`](release-artifacts.md) defines deterministic release
  evidence, SBOM generation, and GitHub OIDC artifact attestation.
