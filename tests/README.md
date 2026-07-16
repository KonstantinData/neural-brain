# Tests

This directory contains automated acceptance, isolation, privacy, safety,
recovery, cognitive-capability, and regression evidence for Neural Brain.

Test organization should mirror the implemented contracts and delivery stages.
Tests must distinguish implemented behavior from target contracts and the
Cognitive Plane from the Protected Control Plane. Product-specific fixtures do
not belong in the platform suite. Every cognitive claim additionally requires
baselines, ablations, held-out transfer, robustness, and calibration evidence.

The first NB-1 vertical slice requires deterministic tests for its fixed-version
recurrent neural workspace, bounded trainable feature gating, authenticated
session isolation, checkpoint replay and stale-version rejection, and typed
internal goal, plan, and metacognitive proposals. Tests must prove that no
external effect can be requested or executed through this slice.

NB-1.2 tests verify deterministic train-only selection, complete candidate
disclosure, immutable parameter/training/model digests, tamper rejection, and
the absence of a runtime training export. Hidden-evaluator tests validate only
the external interface and no-claim boundary; their synthetic contract fixture
is not hidden evidence. NB-1.3 live PostgreSQL tests verify exact replay,
changed-payload and stale-version denial, scoped restart recovery, corrupt-state
denial, and rollback when cognitive audit insertion fails. Those tests require
the guarded disposable PostgreSQL 18 fixture via `MIGRATION_ADMIN_DSN`.

`EVAL-01.NB-1.safe-serial-cognition.v3` supersedes rejected v2 and freezes the
external hidden-split contract, six baselines, three ablations, resource budget,
confidence method, and hard safety thresholds before execution. Architecture
tests prove only that the specification and digest are well-formed; development
evaluation tests prove only harness behavior. Neither proves a gate passed or that NB-1 is
complete.
