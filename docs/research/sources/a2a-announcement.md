---
slug: "a2a-announcement"
title: "Announcing the Agent2Agent Protocol (A2A)"
url: "https://cloud.google.com/blog/products/ai-machine-learning/announcing-the-agent2agent-protocol-a2a"
authors: "Rao Surapaneni, Miku Jha, Michael Vakoc, Todd Segal (Google Cloud)"
year: "2025"
type: blog
topics: [agents, multi-agent, interoperability, protocols, mcp, agent-cards, orchestration, enterprise-ai]
cached: true
evidence_quality: opinion
date_synthesized: "2026-03-06"
cache_path: ".cache/sources/a2a-announcement.md"
---

# Announcing the Agent2Agent Protocol (A2A)

**URL**: https://cloud.google.com/blog/products/ai-machine-learning/announcing-the-agent2agent-protocol-a2a
**Type**: blog / announcement
**Cached**: `uv run python scripts/fetch_source.py https://cloud.google.com/blog/products/ai-machine-learning/announcing-the-agent2agent-protocol-a2a --slug a2a-announcement`

## Citation

Surapaneni, R., Jha, M., Vakoc, M., & Segal, T. (2025, April 9). *Announcing the Agent2Agent Protocol (A2A)*. Google Cloud Blog.
https://cloud.google.com/blog/products/ai-machine-learning/announcing-the-agent2agent-protocol-a2a

## Research Question Addressed

How can AI agents from different vendors, built on different frameworks, securely communicate, discover each other's capabilities, and coordinate on tasks without requiring shared memory, shared context, or shared tooling? This announcement introduces A2A as Google's answer: an open, HTTP-based protocol that standardises agent-to-agent communication at the network layer, complementing MCP's tool-access layer.

## Theoretical / Conceptual Framework

A2A operates within a **layered agent interoperability** paradigm. The underlying model is a two-role interaction: a *client agent* (orchestrator, task-issuer) and a *remote agent* (specialist, task-executor). This maps directly onto the orchestrator-worker and scout-synthesizer patterns common in multi-agent literature. The protocol explicitly decouples inter-agent communication (A2A) from tool-context provisioning (MCP), treating them as **complementary layers** rather than competing standards. The five design principles — agentic capability support, existing standards reuse, security-by-default, long-running task support, and modality agnosticism — reflect a **pragmatic enterprise engineering** ethos rather than a formal academic framework.

## Methodology and Evidence

This is a product launch announcement authored by Google Cloud engineers and product managers. The evidence base is Google's internal experience scaling multi-agent systems and input from more than 50 named technology and services partners across enterprise software (SAP, Salesforce, ServiceNow, Workday), infrastructure (MongoDB, DataStax, Elastic), and professional services (Accenture, Deloitte, McKinsey, PwC). The post provides a conceptual walkthrough of the protocol's four functional areas (capability discovery, task management, collaboration, UX negotiation) illustrated with a candidate-sourcing end-to-end scenario. No empirical benchmark data is provided; all supporting evidence is in the form of partner endorsement quotes and design-rationale narrative. The draft specification and code samples are linked externally to the `github.com/google/A2A` repository.

## Key Claims

- **Complementary to MCP, not competing**: > "A2A is an open protocol that complements Anthropic's Model Context Protocol (MCP), which provides helpful tools and context to agents." A2A addresses agent-to-agent communication; MCP addresses tool and context access. The two protocols occupy different layers of the agent stack.

- **Agent Card for capability discovery**: > "Agents can advertise their capabilities using an 'Agent Card' in JSON format, allowing the client agent to identify the best agent that can perform a task and leverage A2A to communicate with the remote agent." This is the canonical A2A discovery mechanism — a machine-readable manifest of what a given agent can do.

- **Task object as the core unit**: > "The communication between a client and remote agent is oriented towards task completion, in which agents work to fulfill end-user requests. This 'task' object is defined by the protocol and has a lifecycle." Tasks can complete immediately or remain open across hours or days, with status synchronisation throughout.

- **Artifacts as task output**: > "It can be completed immediately or, for long-running tasks, each of the agents can communicate to stay in sync with each other on the latest status of completing a task. The output of a task is known as an 'artifact.'" This named artefact concept creates a clear handoff primitive between agents.

- **Parts-based UX negotiation**: > "Each message includes 'parts,' which is a fully formed piece of content, like a generated image. Each part has a specified content type, allowing client and remote agents to negotiate the correct format needed and explicitly include negotiations of the user's UI capabilities." Format negotiation is built into the protocol, not bolted on.

- **Built on existing HTTP standards**: > "The protocol is built on top of existing, popular standards including HTTP, SSE, JSON-RPC, which means it's easier to integrate with existing IT stacks businesses already use daily." This lowers the adoption barrier significantly compared to a bespoke binary protocol.

- **No shared memory required by design**: > "A2A focuses on enabling agents to collaborate in their natural, unstructured modalities, even when they don't share memory, tools and context." This differentiates A2A from tightly coupled agent frameworks and makes it viable for cross-vendor deployments.

- **Security parity with OpenAPI**: > "A2A is designed to support enterprise-grade authentication and authorization, with parity to OpenAPI's authentication schemes at launch." Security is a first-class design constraint, not an add-on.

- **Long-running and human-in-the-loop tasks**: > "We designed A2A to be flexible and support scenarios where it excels at completing everything from quick tasks to deep research that may take hours and or even days when humans are in the loop. Throughout this process, A2A can provide real-time feedback, notifications, and state updates." The protocol is explicitly scoped to include research-class workflows, not just transactional exchanges.

- **Modality agnostic**: > "The agentic world isn't limited to just text, which is why we've designed A2A to support various modalities, including audio and video streaming." Future-proofing against multi-modal agent interactions is built into the design rather than deferred.

- **50+ partner ecosystem at launch**: > "Today, we're launching a new, open protocol called Agent2Agent (A2A), with support and contributions from more than 50 technology partners like Atlassian, Box, Cohere, Intuit, Langchain, MongoDB, PayPal, Salesforce, SAP, ServiceNow, UKG and Workday." The breadth of partners signals industry convergence, not just Google preference.

- **Standardised management across platforms**: > "Critically, businesses benefit from a standardized method for managing their agents across diverse platforms and cloud environments." The Agent Card / discovery layer implies an agent registry pattern beneficial for governance and observability.

- **Collaboration primitive (message passing)**: > "Agents can send each other messages to communicate context, replies, artifacts, or user instructions." Messages are the synchrony primitive; state is managed through the task lifecycle rather than shared mutable state.

- **LangChain endorsement frames the protocol's scope**: > "LangChain believes agents interacting with other agents is the very near future, and we are excited to be collaborating with Google Cloud to come up with a shared protocol which meets the needs of the agent builders and users." — Harrison Chase, LangChain CEO. This endorsement from the leading open-source agent orchestration library validates A2A's alignment with practitioner-facing tooling.

- **Production readiness timeline**: > "We are working with partners to launch a production-ready version of the protocol later this year." The April 2025 launch was a draft specification; production stability was planned for late 2025. This is now approximately on schedule given the current date of March 2026.

## Critical Assessment

**Evidence Quality**: Opinion / Documentation

This is a launch announcement, not a peer-reviewed paper or empirical study. All claims are design-rationale assertions backed by partner testimonials rather than measurable outcomes. The 50+ partner list is evidence of industry backing, not evidence of technical effectiveness — endorsement quotes are uniformly positive and none address failure modes, edge cases, or adoption friction. No benchmarks, throughput figures, or security audit results are provided.

**Gaps and Limitations**: The announcement provides an architectural overview but is deliberately thin on implementation detail — the full specification is deferred to `github.com/google/A2A`, which is not included in the cache. As a result, this synthesis cannot analyse the JSON-RPC wire format, authentication flow specifics, or Agent Card schema in depth. The document does not address how A2A handles partial failures or how task state is persisted across agent restarts. There is no discussion of versioning strategy, backward compatibility guarantees, or governance beyond "open source with contribution pathways." The candidate-sourcing example is illustrative but generic; no domain-specific adoption guidance is given. Finally, the announcement predates full production deployment and the competitive landscape has shifted since (e.g. whether OpenAI's agent-to-agent work has converged or diverged from A2A is unknown from this source alone).

## Connection to Other Sources

- Agrees with / extends: [anthropic-building-effective-agents](./anthropic-building-effective-agents.md) — both sources recommend layered, composable agent architectures where orchestrators delegate to specialist workers; A2A formalises the inter-agent communication layer that Anthropic's post treats as an implementation detail.
- Agrees with / extends: [arxiv-react](./arxiv-react.md) — A2A's task-lifecycle model (issue → in-progress → artefact) is compatible with and extends the ReAct observe-plan-act loop to distributed multi-agent settings.
- Agrees with / extends: [claude-sdk-subagents](./claude-sdk-subagents.md) — the client/remote agent distinction in A2A directly parallels the orchestrator/subagent pattern in Claude's SDK; A2A provides a protocol-level formalisation of that pattern.
- Practical implementation context: [freecodecamp-org-news-build-and-deploy-multi-agent-ai-with-p](./freecodecamp-org-news-build-and-deploy-multi-agent-ai-with-p.md) — that article shows a working synchronous pipeline using shared volumes; A2A's message-passing and artefact model is the natural protocol-level upgrade path when the pipeline needs to cross network boundaries or vendor stacks.
- Memory layer complement: [github-com-getzep-graphiti](./github-com-getzep-graphiti.md) — A2A handles agent-to-agent task coordination; Graphiti handles the persistent memory that agents need to retain state across those tasks. The two protocols are non-overlapping and jointly necessary for stateful multi-agent systems.
- Context engineering foundation: [arxiv-org-html-2512-05470v1](./arxiv-org-html-2512-05470v1.md) — AIGNE's Constructor/Updater/Evaluator pipeline describes context governance within a single agent; A2A describes coordination across agents — the two frameworks are complementary at different scopes.
- Multi-agent pipeline baseline: [freecodecamp-org-news-build-and-deploy-multi-agent-ai-with-p](./freecodecamp-org-news-build-and-deploy-multi-agent-ai-with-p.md) — that article's shared-volume file handoff pattern is the simplest viable multi-agent architecture; A2A's artefact model is its rigorous network-capable formalisation.

## Relevance to EndogenAI

**Agent Card ↔ `scripts/generate_agent_manifest.py` — ADOPT**: The most direct connection from this source to the EndogenAI codebase is structural: A2A's Agent Card (a JSON manifest advertising an agent's capabilities, inputs, outputs, and authentication requirements) is architecturally identical to what `scripts/generate_agent_manifest.py` generates for the `.github/agents/` fleet. The EndogenAI manifest exists to give agents and contributors an accurate, machine-readable picture of the fleet. A2A validates this pattern at industry scale, with 50+ partners agreeing it is the correct primitive for capability discovery. The recommendation is to **ADOPT** the Agent Card schema as an informing reference when evolving `generate_agent_manifest.py` — specifically, ensure the manifest captures: (1) declared capabilities, (2) modality constraints, (3) authentication/trust requirements, and (4) a lifecycle model for task handoffs. This positions the EndogenAI manifest for interoperability with external A2A-compliant agents in future sessions.

**A2A ↔ MCP complementarity — ADOPT for architecture documentation**: A2A's explicit framing that it complements rather than replaces MCP maps cleanly onto the EndogenAI stack. MCP-style tool provisioning (context, retrieval, execution) is already implied by the guides in `docs/guides/` and the scout/synthesizer patterns in `docs/research/agentic-research-flows.md`. The A2A protocol formalises the *inter-agent* layer that sits above tool access. The recommendation is to **ADOPT** this two-layer framing in `docs/guides/agents.md` and any future multi-agent architecture documentation: tool access = MCP-layer, agent coordination = A2A-layer. This clarifies a design gap in the current guides, which do not distinguish between these two concerns.

**Long-running task support — ADAPT for session management**: A2A's design explicitly targets long-running, human-in-the-loop tasks with real-time status updates — the exact profile of an EndogenAI research session. The `.tmp/<branch>/<date>.md` scratchpad already serves as a crude task-state object (accumulating findings, handoff notes, and session summaries). The recommendation is to **ADAPT** the session management conventions in `docs/guides/session-management.md` to reflect A2A's task-lifecycle primitives: issue → in-progress → artefact. Naming scratchpad sections with lifecycle-aligned labels (e.g. `## Task: Scout` → `## Artefact: Scout Output`) would make inter-agent handoffs more legible and reduce context re-discovery overhead in subsequent sessions.

**No-shared-memory constraint — REJECT as a limitation, ADOPT as a design target**: A2A's requirement that agents collaborate without shared memory, tools, or context is framed as a strength, not a constraint. For EndogenAI, this is the correct posture: sub-fleet agents should be designed so they can operate with only what is passed to them in a task brief or scratchpad excerpt — not global access to the full workflow state. The current AGENTS.md guidance on "minimal posture" (agents carry only the tools required for their stated role) directly echoes this A2A principle. The recommendation is to **ADOPT** A2A's no-shared-memory principle as an explicit design target in `docs/guides/agents.md`, reinforcing the existing minimal-posture constraint with the additional framing that context isolation is not a limitation to work around but the default operating mode for robust multi-agent systems.

## Referenced By

<!-- Populated automatically by scripts/link_source_stubs.py — do not edit manually -->
- [Agentic Research Flows](../agentic-research-flows.md)
- [Freecodecamp Org News Build And Deploy Multi Agent Ai With P](../sources/freecodecamp-org-news-build-and-deploy-multi-agent-ai-with-p.md)
- [Github Com Getzep Graphiti](../sources/github-com-getzep-graphiti.md)
- [Github Com Topoteretes Cognee](../sources/github-com-topoteretes-cognee.md)
- [Kdnuggets Com Docker Ai For Agent Builders Models Tools And ](../sources/kdnuggets-com-docker-ai-for-agent-builders-models-tools-and-.md)
- [Tds Claude Skills Subagents](../sources/tds-claude-skills-subagents.md)
