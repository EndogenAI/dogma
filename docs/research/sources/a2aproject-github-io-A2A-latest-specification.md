---
slug: "a2aproject-github-io-A2A-latest-specification"
source_url: "https://a2aproject.github.io/A2A/latest/specification/"
cache_path: ".cache/sources/a2aproject-github-io-A2A-latest-specification.md"
fetched: 2026-03-06
research_issue: "Issue #10 — Agent Fleet Design Patterns"
title: "Agent2Agent (A2A) Protocol Specification — Release Candidate v1.0"
authors: "A2A Project (Google and community contributors)"
year: "2025"
type: documentation
topics: [agents, multi-agent, interoperability, protocols, agent-cards, discovery, fleet-design, enterprise-ai]
cached: true
evidence_quality: documentation
date_synthesized: "2026-03-06"
---

# Synthesis: Agent2Agent (A2A) Protocol Specification — Release Candidate v1.0

## 1. Citation

A2A Project. (2025). *Agent2Agent (A2A) Protocol Specification, Release Candidate v1.0*.
a2aproject.github.io. https://a2aproject.github.io/A2A/latest/specification/
Accessed: 2026-03-06. Canonical authority: `spec/a2a.proto` (protobuf source); this document is the normative human-readable specification sitting above it.

---

## 2. Research Question Addressed

The specification answers the question: how should independent, opaque AI agents from different vendors and frameworks discover one another's capabilities, negotiate interaction modalities, manage shared task state, and exchange results securely — without sharing internal memory, tools, or implementation details? The spec formalises this as a three-layer protocol (Data Model → Abstract Operations → Protocol Bindings) over HTTP/JSON-RPC/gRPC, anchored by a discoverable JSON manifest (the Agent Card) served at a well-known URI.

---

## 3. Theoretical Framework

A2A operates within a **peer agent interoperability** paradigm. The specification explicitly frames agents as peers that "partner or delegate work" rather than imposing a fixed hierarchy. The architectural vocabulary is layered:

- **Layer 1** — Canonical Data Model: `AgentCard`, `Task`, `Message`, `Part`, `Artifact`, `Extension` (protobuf-normalised).
- **Layer 2** — Abstract Operations: `SendMessage`, `StreamMessage`, `GetTask`, `ListTasks`, `CancelTask`, `SubscribeToTask`, `CreatePushNotificationConfig`, `GetExtendedAgentCard`.
- **Layer 3** — Protocol Bindings: JSON-RPC 2.0, gRPC, HTTP+REST.

The framework intentionally borrows from OpenAPI 3.2 security scheme vocabulary, RFC 7515 (JWS), RFC 8785 (JSON Canonicalisation), and RFC 8414 (OAuth 2.0 metadata). The principal theoretical commitment is **opaque execution**: agents collaborate through declared capabilities and exchanged data, never through shared state or exposed internals.

---

## 4. Methodology / Source Type

This is a normative technical specification (Release Candidate v1.0, latest as of March 2026, previous stable tag `0.3.0`). It is structured as a formal multi-section RFC-style document with prose requirements (MUST/SHOULD/MAY per RFC 2119), schema tables, annotated JSON examples, and mermaid architecture diagrams. Normative authority is delegated to `spec/a2a.proto`; all JSON schema artefacts are generated from the proto at build time and are non-normative. The spec covers 14 major sections including data model (§4), scenarios (§6), authentication (§7), agent discovery (§8), three concrete bindings (§9–§11), security guidance (§13), and IANA registration templates (§14).

---

## 5. Key Claims with Evidence

### 5.1. AgentCard — Required Fields

> "A self-describing manifest for an agent. It provides essential metadata including the agent's identity, capabilities, skills, supported communication methods, and security requirements." — §4.4.1

The full schema, with field types and cardinality:

| Field | Type | Required |
|---|---|---|
| `name` | `string` | **Yes** |
| `description` | `string` | **Yes** |
| `supportedInterfaces` | array of `AgentInterface` | **Yes** — ordered; first entry is preferred |
| `version` | `string` | **Yes** |
| `capabilities` | `AgentCapabilities` | **Yes** |
| `defaultInputModes` | array of `string` (MIME types) | **Yes** |
| `defaultOutputModes` | array of `string` (MIME types) | **Yes** |
| `skills` | array of `AgentSkill` | **Yes** |
| `provider` | `AgentProvider` | No |
| `documentationUrl` | `string` | No |
| `securitySchemes` | map of `string → SecurityScheme` | No |
| `securityRequirements` | array of `SecurityRequirement` | No |
| `signatures` | array of `AgentCardSignature` | No |
| `iconUrl` | `string` | No |

### 5.2. AgentCapabilities — The Capability Gating Mechanism

> "Agents declare optional capabilities in their `AgentCard`. When clients attempt to use operations or features that require capabilities not declared as supported in the Agent Card, the agent MUST return an appropriate error response." — §3.3.4

`AgentCapabilities` fields (all optional):
- `streaming` (`boolean`) — gates `SendStreamingMessage` and `SubscribeToTask`; absent/false causes `UnsupportedOperationError`
- `pushNotifications` (`boolean`) — gates all push notification config operations; absent/false causes `PushNotificationNotSupportedError`
- `extensions` (array of `AgentExtension`) — lists protocol extensions; each has `uri`, `description`, `required` (boolean), `params` (object)
- `extendedAgentCard` (`boolean`) — gates the `GetExtendedAgentCard` endpoint

This means capability advertisement is **directly tied to error contract enforcement** — misclaiming a capability has protocol-level consequences, not just documentation consequences.

### 5.3. AgentSkill — Per-Skill Capability Scoping

> "Skills represent the abilities of an agent. It is largely a descriptive concept but represents a more focused set of behaviors that the agent is likely to succeed at." — §4.4.1 (skills field description)

`AgentSkill` fields:
- `id` (string, Required) — unique identifier, referenced by clients when invoking skills
- `name` (string, Required)
- `description` (string, Required)
- `tags` (array of string, Required) — machine-usable keyword matching
- `examples` (array of string, Optional) — sample prompts
- `inputModes` (array of string, Optional) — **overrides** `AgentCard.defaultInputModes` for this skill
- `outputModes` (array of string, Optional) — **overrides** `AgentCard.defaultOutputModes` for this skill
- `securityRequirements` (array of `SecurityRequirement`, Optional) — skill-level auth requirements that override agent-level schemes

The per-skill `inputModes`/`outputModes` override mechanism enables **fine-grained capability declaration**: an agent can offer text-in/JSON-out for one skill and text-in/image-out for another, expressed in a single Agent Card.

### 5.4. AgentInterface and Multi-Protocol Exposure

> "This allows agents to expose the same functionality over multiple protocol binding mechanisms." — §4.4.6

`AgentInterface` fields:
- `url` (string, Required) — absolute HTTPS URL
- `protocolBinding` (string, Required) — open-form string; canonical values `JSONRPC`, `GRPC`, `HTTP+JSON`
- `tenant` (string, Optional) — multi-tenancy path parameter
- `protocolVersion` (string, Required)

A single agent can appear in `supportedInterfaces` three times (once per binding) at different URLs. Client MUST select the first supported binding in the ordered list. This means protocol negotiation is resolved by Agent Card inspection, not runtime handshake.

### 5.5. `.well-known/agent-card.json` — Registry-Free Discovery

> "Well-Known URI: Accessing `https://{server_domain}/.well-known/agent-card.json`" — §8.2

> "The `.well-known/agent-card.json` URI provides a standardized location for discovering an A2A agent's capabilities, supported protocols, authentication requirements, and available skills. The resource at this URI MUST return an AgentCard object as defined in Section 4.4.1." — §14.3

The well-known URI is being submitted to IANA for standardisation (§14.3 IANA registration template). This means any domain hosting an A2A agent is, by convention, self-discovering: a client needs only the domain name to bootstrap — no central registry is required. Alternative discovery mechanisms listed in §8.2: Registries/Catalogs, Direct Configuration.

### 5.6. Extended Agent Card — Two-Tier Capability Advertisement

> "This endpoint is available only if `AgentCard.capabilities.extendedAgentCard` is true … The operation MAY return different details based on client authentication level, including additional skills, capabilities, or configuration not available in the public Agent Card." — §3.1.11

The `GET /extendedAgentCard` endpoint (protected by auth declared in the public card's `securitySchemes`) enables an agent to expose a **richer skill set to authenticated peers**. Clients retrieving the extended card SHOULD replace their cached public card with the extended version for the session duration. This creates a deliberate two-tier capability surface: public (anonymous discovery) and authenticated (full capability exposure).

### 5.7. SecurityScheme — OpenAPI-Parity Auth

> "This is a discriminated union type based on the OpenAPI 3.2 Security Scheme Object." — §4.5.1

Five auth schemes supported, exactly one per `SecurityScheme`:
- `apiKeySecurityScheme` — location (`query`/`header`/`cookie`) + name
- `httpAuthSecurityScheme` — RFC7235 scheme name (e.g. `Bearer`) + optional `bearerFormat`
- `oauth2SecurityScheme` — OAuthFlows (authorizationCode, clientCredentials, deviceCode; implicit/password are `Deprecated`)
- `openIdConnectSecurityScheme` — OIDC Discovery URL
- `mtlsSecurityScheme` — mTLS

Auth is entirely declared in the Agent Card. Credential acquisition is **out-of-band** (§7.3); the protocol layer transmits credentials but does not negotiate them.

### 5.8. Peer Topology — Not Inherently Hierarchical

> "A2A focuses on standardizing how independent, often opaque, AI agents communicate and collaborate with each other **as peers**." — §15 (Relationship to MCP section)

The protocol is symmetric: any A2A client can be simultaneously an A2A server. The `SendMessageRequest.configuration.blocking` field and `Task` lifecycle model support both synchronous orchestrator→worker delegation (blocking mode, immediate artifact return) and long-running async peer collaboration (non-blocking, push notifications). Hierarchical fleet topologies are achievable but not prescribed — the spec provides no "orchestrator" or "worker" role concepts at the protocol level.

### 5.9. Task Lifecycle and Stateful Continuity

> "Tasks are stateful and progress through a defined lifecycle." — §2.2

Task states include: `working`, `input-required`, `auth-required`, `completed`, `failed`, `canceled`, `rejected`. The `contextId` field enables multi-task conversation continuity:

> "A `contextId` logically groups multiple `Task` objects and `Message` objects that are part of the same conversational context." — §3.4.1

This means a fleet orchestrator can maintain a shared `contextId` across multiple sub-agent delegations, providing session continuity without shared memory.

### 5.10. Agent Card JWS Signing — Integrity Without PKI Dependency

> "Agent Cards MAY be digitally signed using JSON Web Signature (JWS) as defined in RFC 7515 to ensure authenticity and integrity." — §8.4

Signing process: canonicalise with RFC 8785 (JCS) → exclude `signatures` field → sign with ES256/RS256 → embed `AgentCardSignature` in the `signatures` array. The `jku` header parameter in the protected header points to a JWKS URL for public key retrieval. This enables **decentralised trust verification**: a client can verify an Agent Card without contacting a central authority, using only the JWKS URL embedded in the card's own signature header.

---

## 6. Critical Assessment

**Evidence Quality**: Documentation — Strong for its type.

This is the normative specification backed by a public GitHub repository (`a2aproject/A2A`), IANA registration submissions, and a reference protobuf (`spec/a2a.proto`). It is not peer-reviewed research, but as a technical specification it meets a high documentary standard: RFC 2119 language throughout, concrete JSON schema tables with all fields, a full sample Agent Card (§8.5), multiple annotated scenario walkthroughs (§6), and IANA registration templates (§14). This is the authoritative implementation contract, not a design sketch.

**Gaps and Limitations**:
- The spec is a Release Candidate; some sections have proto message stubs marked `Error: Message not found` (e.g. `CreateTaskPushNotificationConfigRequest` in §3.1.7), suggesting the proto and prose are not fully synchronised at this version.
- The spec does not define agent registry or catalog standards — §8.2 mentions "Registries/Catalogs" as a discovery mechanism but provides no schema or protocol for them.
- Authorization logic is explicitly implementation-specific (§7.6): the spec defines *how* to declare auth requirements but not *what* permissions mean, making portable skill-level access control difficult across vendors.
- There is no specified mechanism for an agent to query another agent's current load, latency, or availability — capability advertisement is static (card at rest), not dynamic (real-time status).
- The `skills` array has no versioning field; skill-level backward compatibility guidance is absent.
- The cached file is 5,659 lines and represents the complete specification — no truncation or abstract-only limitation.

---

## 7. Cross-Source Connections

- Extends / closes gap in: [a2a-announcement](./a2a-announcement.md) — the announcement (synthesised 2026-03-06) flagged the Agent Card JSON schema as a gap; this source fills it completely with field-level types, cardinality, and the full sample card from §8.5.
- Agrees with / extends: [anthropic-building-effective-agents](./anthropic-building-effective-agents.md) — Anthropic's effective agents guide recommends minimal, composable orchestration with clear interfaces; A2A formalises those interfaces as a network-addressable protocol with enforced capability contracts.
- Agrees with: [anthropic-com-engineering-multi-agent-research-system](./anthropic-com-engineering-multi-agent-research-system.md) — the `contextId`-grouped multi-task model maps directly to the subagent-per-subtask pattern described in Anthropic's multi-agent research system article.

---

## 8. Project Relevance

### Hypothesis 3 (Quasi-Encapsulated Sub-Fleets) — ADOPT with caveats

The Agent Card's `.well-known/agent-card.json` discovery endpoint, skill-level `inputModes`/`outputModes` overrides, and two-tier extended card mechanism together provide the technical substrate for **dynamic fleet composition without central registries** — directly addressing Hypothesis 3. An EndogenAI orchestrator agent could bootstrap discovery of any A2A-compliant specialist agent by resolving its domain's well-known URI, reading its `skills` array, matching tags and media types to task requirements, and routing accordingly. No registry service, no hardcoded capability lists.

The key caveat: the spec provides no dynamic load or availability advertising. Capability discovery is static. A fleet orchestrator in `.github/agents/` choosing between competing A2A-compliant specialist agents must rely on external health checks or heartbeat extensions, not the protocol itself.

**Recommendation for `.github/agents/`**: Agent card-like frontmatter headers in `.agent.md` files (see existing convention) should be audited against the A2A AgentCard schema. Specifically, the `skills` array pattern (with `id`, `tags`, `inputModes`, `outputModes`) is a battle-tested capability declaration vocabulary worth adopting in EndogenAI agent files, even if they never speak A2A over the wire. This aligns with the Endogenous-First principle — scaffold from external best practices.

### Fleet Topology — Both Hierarchical and Peer Models Supported — ADOPT

The spec's symmetric client/server model (§15: "collaborate as peers") combined with `blocking` mode delegation and `contextId`-based session continuity means A2A supports both the hierarchical orchestrator→worker topology (top-down, `blocking: true` calls) and the peer collaboration topology (async, `contextId`-grouped, push notifications) within the same protocol. The current EndogenAI fleet (`Executive → specialist agents` via `runSubagent`) is already hierarchical; A2A is architecturally compatible with externalising those inter-agent calls over HTTP if remote sub-fleets (local GPU machine, cloud worker) are ever introduced. The `scripts/` directory does not currently have any inter-agent communication tooling — if remote sub-fleets become a priority, A2A is the recommended protocol substrate.

### Security and Capability Gating — ADAPT

The `securitySchemes` + per-skill `securityRequirements` pattern is more granular than anything currently in EndogenAI agent files. The ADAPT recommendation: introduce a lightweight capability declaration convention in `.github/agents/` frontmatter (what the agent can and cannot do, what tool access it requires) that mirrors the A2A pattern without requiring HTTP infrastructure. This would make agent capability boundaries legible to the Executive agents without requiring a full A2A deployment.

## Referenced By

<!-- Populated automatically by scripts/link_source_stubs.py — do not edit manually -->
