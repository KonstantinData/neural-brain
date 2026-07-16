# Source

This directory contains the product-neutral Neural Brain implementation. The
current packages implement early Memory Core and identity/scope prerequisites
plus the first effect-free NB-1 serial cognition slice. That slice is limited
to a fixed-version recurrent neural workspace, bounded trainable feature
gating, authenticated session scope, Memory-Gate checkpoints, and typed
internal goal, plan, and metacognitive proposals over recorded or synthetic
observations. It has no external-effect surface and does not complete NB-1.

The cognition package also contains a bounded deterministic offline training
implementation that produces a self-verifying, non-promoted parameter and
provenance bundle. It is intentionally not exported as a runtime training
surface. The PostgreSQL package provides a dedicated cognitive checkpoint
adapter whose `SECURITY DEFINER` functions remain inside the existing Memory
Transition Gate and atomically bind checkpoint, transition, training/model
evidence, receipt, and audit.

The slice is governed by the frozen
`EVAL-01.NB-1.safe-serial-cognition.v3` requires an external hidden dataset,
six baselines, three ablations, digests, and confidence bounds. The implemented
training bundle and development harness pass no evaluation or recognition gate.
The hidden-evaluation interface accepts only an externally supplied artifact and
an explicit independent-evaluator identity; the repository stores no hidden
dataset. Version 1 is
retained with v2 as rejected historical evidence. Later cognitive modules belong
here only after their ADRs, contracts, stage dependencies, and evidence gates
are accepted.

Runtime packages belong here only when their delivery-stage dependencies,
contracts, and cognitive and control-plane safety boundaries have been accepted and tested.
Product-specific integrations and prematurely enabled later-stage capabilities
do not belong here.
