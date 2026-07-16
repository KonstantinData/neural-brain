# Runbooks

This directory contains operational, recovery, incident, backup, restore, and
release procedures for implemented Neural Brain capabilities.

Runbooks must be executable by their intended operators, avoid secrets, and
identify safety gates that may not be bypassed.

Runbooks must preserve the boundary between the Cognitive Plane and the
independent Protected Control Plane. Planning and action selection never confer
authority; tool execution, effect recovery, shutdown, and promotion require
their accepted gates and may not be documented as model-controlled shortcuts.

- [`release-artifacts.md`](release-artifacts.md) defines deterministic release
  evidence, SBOM generation, and GitHub OIDC artifact attestation.
