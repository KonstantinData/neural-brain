# ADR-014: Local Ollama-Only Inference

- Status: Accepted
- Date: 2026-07-15
- Decision owner: Konstantin Milonas
- Authorization: Direct repository implementation instruction dated 2026-07-15
- Notion source: https://app.notion.com/p/39e1c1ac5ec08161ad4cd737a9375e4f
- Notion page ID: `39e1c1ac-5ec0-8161-ad4c-d737a9375e4f`
- Related contract: `docs/architecture/contracts/inference-provider.json`

## Amendment by ADR-015 and ADR-017

Inference supports bounded memory processing only. The `InferencePort` is not a
cognitive-agent port, and Neural Brain does not contain planners, executors,
tools, goals, completion logic, or autonomous workflows. A model result may
only become a validated, provenance-bearing typed memory request; it cannot
write memory directly or confer consumer authority.

When inference supports Dreaming, the model receives only minimized content
from one authenticated Area snapshot. Its response remains untrusted analysis
input and cannot approve a candidate, suppress contradictory evidence, activate
memory, or change an active-version pointer.

## Context

Neural Brain requires model inference without allowing model integrations to
expand runtime authority, leak scoped data to an external provider, or create a
silent availability-driven cloud fallback. ADR-013 deliberately left provider
selection to a separate decision.

The cognitive runtime needs a provider-neutral internal boundary so that domain
components do not depend on a provider SDK. The currently authorized deployment
must nevertheless be narrower than that internal abstraction: inference is
local, uses Ollama, and fails closed when the approved local service or approved
model is unavailable.

No concrete model name, version, digest, or endpoint is authorized by this ADR.
Those values are deployment-bound approvals and must be present and verified
before inference can be enabled.

## Decision

Neural Brain exposes inference only through a provider-neutral internal
`InferencePort`. Memory components depend on that port and never import or call
a provider SDK directly.

The only approved inference adapter is the local Ollama adapter. Its trusted
deployment configuration must bind all of the following before startup can
report the inference capability as ready:

- adapter identity identifying the approved local Ollama adapter;
- an explicitly approved, non-public local Ollama endpoint;
- `model_id`;
- `model_version`;
- `model_digest`;
- a positive request timeout within the approved deployment limit;
- an approved inference budget and enforceable budget reference; and
- the applicable payload-minimized logging policy.

`model_id`, `model_version`, and `model_digest` are distinct mandatory values.
The adapter must resolve the deployed model and verify that all three match the
approved deployment record before accepting work. A tag, alias, latest-version
selector, or model name without an exact approved digest is insufficient.

The endpoint, model selection, timeout, budget, and logging policy come only
from trusted deployment configuration and authoritative runtime state. A
request, prompt, model response, tool output, persisted untrusted payload, or
operator-provided conversational input cannot select or override them.

## Prohibited Provider and Fallback Behavior

The following are denied:

- OpenAI APIs, SDKs, endpoints, models, credentials, and compatibility modes;
- any other external or cloud-hosted model provider;
- arbitrary or request-selected inference endpoints;
- automatic cloud fallback or provider switching;
- automatic selection of another model, tag, version, or digest;
- API-key-based fallback or loading cloud-provider credentials for inference;
- public network egress from the inference adapter; and
- treating model output as authenticated scope, identity, authority, policy,
  approval, kill-switch state, protected-state mutation, tool authorization, or
  verified evidence.

Provider-neutrality of `InferencePort` is an internal dependency boundary, not
permission to configure another provider. Supporting another provider requires
a separate accepted ADR, an approved adapter, updated egress policy, threat and
privacy assessment, and corresponding contract and test changes.

## Failure and Availability Contract

Inference fails closed when the local service cannot be reached, the endpoint
is not the approved local endpoint, the configured model is absent, any model
identity value is missing or mismatched, the digest cannot be verified, the
budget is unavailable or exhausted, the timeout is invalid or expires, egress
controls cannot be established, or logging controls cannot be applied.

Failure returns a typed unavailable or denied outcome through `InferencePort`.
It does not invoke another provider or model and does not weaken a transition
guard. Any bounded retry must target the same approved endpoint and the same
exact model identity and must be separately authorized by runtime policy and
budget; this ADR creates no automatic retry entitlement.

Startup and readiness checks must verify the configured endpoint, exact model
identity, digest, budget enforcement, and egress restrictions. A process being
alive or an Ollama endpoint returning HTTP success is not sufficient readiness
evidence.

## Data Minimization and Logging

Inference requests contain only data necessary for the declared, authorized
purpose and current immutable scope. The adapter must not add unrelated memory,
cross-area context, credentials, secrets, or raw audit payloads.

Prompt assembly is request-scoped. Server-side conversation reuse, prompt
caches, and batching MUST NOT combine scopes or carry context into a later
request. Raw Working Memory remains inside its authenticated area and is never
transferred through a cross-area handover.

Logs and metrics record minimized operational metadata such as trusted trace
references, model identity references, timings, token or resource usage, and a
typed outcome. Prompt and response bodies are excluded by default. Any later
content capture requires an explicit data classification, purpose, retention
rule, access control, and accepted architecture authorization. Secrets and
credentials are never logged.

Model responses remain untrusted input. They require runtime schema validation
before conversion into typed domain objects and cannot directly execute tools,
write protected state, or determine goal success.

The inference adapter MUST NOT retrieve memory or write through the Memory
Transition Gate. A validated model response may only become a typed request to
that gate with authenticated scope, provenance, and producer identity. In
Stage 1, the only permitted durable result is an inactive, non-retrievable
Memory Candidate.

## Network and Credential Boundary

The Ollama adapter may communicate only with the exact local endpoint permitted
by trusted deployment configuration and enforced egress controls. Publicly
routable destinations, redirects outside the approved local boundary, proxies
that can reach external providers, and unapproved DNS or endpoint changes are
denied.

The adapter does not require an inference API key and must not read, accept, or
transmit OpenAI or other cloud-provider credentials. The presence of a
provider-fallback credential or external-provider configuration is a
configuration error, not an alternate execution path.

## Consequences

- Provider details remain isolated behind a typed internal port.
- Stage 1 has one explicit, local inference path with no silent external data
  transfer or availability fallback.
- Deployments cannot enable inference until exact approved model and endpoint
  values exist and are verified.
- Model replacement is a reviewed deployment approval, not a prompt or runtime
  convenience decision.
- Availability is intentionally lower than a cloud-fallback design; loss of the
  approved local service produces a visible fail-closed outcome.
- Introducing another provider is an architecture change requiring an accepted
  ADR and cannot be achieved through configuration alone.

## Alternatives Considered

### Direct Ollama Dependencies in Cognitive Components

Rejected because provider-specific dependencies would spread across domain and
runtime boundaries and make policy, test, and future review controls harder to
enforce.

### Automatic Cloud Fallback

Rejected because it changes the data-processing boundary, egress behavior,
credential surface, provider trust, cost model, and availability semantics
without an explicit architecture decision.

### OpenAI-Compatible Endpoint Mode

Rejected even when pointed at a local service. Compatibility mode creates an
unnecessary SDK and configuration surface that can be redirected to an OpenAI
or other external endpoint. The approved adapter uses the local Ollama contract
only.
