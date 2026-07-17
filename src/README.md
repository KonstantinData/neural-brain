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

The immutable EVAL-01 v3 specification and training bundle remain historical
evidence, but v3 was rejected before hidden attachment because its public
generator exposes only six distinct patterns. The cognition package now exposes
only label-free candidate predictions plus strict freeze and signed-evidence
contracts. Hidden labels, scoring, detailed correctness, evaluator code, and
signing keys remain outside the repository. Versions 1 through 3 are retained
as rejected history; a replacement specification and candidate must be frozen
before an independent hidden run.

Runtime packages belong here only when their delivery-stage dependencies,
contracts, and cognitive and control-plane safety boundaries have been accepted and tested.
Product-specific integrations and prematurely enabled later-stage capabilities
do not belong here.
