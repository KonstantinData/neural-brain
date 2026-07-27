# Model and Inference Inventory v1

- Status: Normative Foundation-governance contract; not a deployment or activation inventory.
- Contract: [`../architecture/contracts/model-inference-inventory-v1.json`](../architecture/contracts/model-inference-inventory-v1.json)
- Governing decisions: ADR-018, Architecture Directive v4.0, and the Neural Brain Recognition Standard.

## Purpose and current boundary

This contract defines the immutable, fail-closed evidence record required for a model, model candidate, adapter, or inference boundary. It applies to the complete product- and domain-neutral Neural Brain system. The Memory Core is a protected internal subsystem; it neither narrows that boundary nor grants model, inference, deployment, or promotion authority.

The repository has no approved productive model deployment or inference adapter. The current NB-1 fixed-version development bundle is not a production model. ADR-014 describes a future local Ollama boundary only: no Ollama activation, adapter, fallback, endpoint, credential, egress path, or runtime inference is created by this contract.

## Required immutable record

Each record binds one exact asset to an immutable digest and requires model ID and version; artifact digest, source and provenance; supplier or producer identity; licence/usage-terms and model-card evidence; exact quantisation/precision and context-window/input bound; inference-boundary and deployment status; authenticated scope and intended-use reference; training-data/adapter provenance; evaluation status/evidence; safety, privacy, security, release-stop and reassessment evidence.

Unknown, absent, stale, contradictory, mutable, or scope-mismatched information makes the record incomplete. An incomplete or unknown entry is denied for model or inference use and cannot support a capability, deployment, promotion, or recognition claim.

## Authority boundary

An inventory record is evidence only. It is not a legal or licence conclusion, security/privacy assessment, policy decision, approval, deployment approval, Model Promotion Gate decision, runtime activation, or release decision. Only the applicable Protected Control Plane gate and separately required evidence may decide those matters. No productive model may modify itself or the control, evaluation, promotion, or inventory rules.
