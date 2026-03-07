---
slug: "github-com-letta-ai-letta"
title: "Letta (formerly MemGPT) — Stateful Agent Infrastructure"
url: "https://github.com/letta-ai/letta"
authors: "Letta AI (cpacker, sarahwooders, mattzh72 and 155 contributors)"
year: "2026"
type: repo
topics: [memory, stateful-agents, context-management, episodic-memory, agent-infrastructure, subagents]
cached: true
evidence_quality: documentation
date_synthesized: "2026-03-06"
---

## Citation

Letta AI. (2026). *Letta (formerly MemGPT)*. GitHub repository. https://github.com/letta-ai/letta
(Accessed 2026-03-06. Latest release: v0.16.6, March 4, 2026. Apache-2.0 license.)

*Original MemGPT paper*: Packer, C., Fang, V., Patil, S., Kim, H., Wooders, S., & Gonzalez, J. E. (2023). MemGPT: Towards LLMs as Operating Systems. arXiv:2310.08560.

## Research Question Addressed

This repository addresses how to build AI agents that maintain persistent, structured memory across sessions — solving the fundamental statelessness problem of LLM-based agents. The core problem it solves is context window overflow and session amnesia: how can an agent remember user-specific information, evolve a durable persona, and accumulate learned heuristics without being constrained by a fixed context window?

## Theoretical / Conceptual Framework

Letta operates within the **memory hierarchy** paradigm originally proposed in the MemGPT paper (Packer et al., 2023), which analogises LLM context windows to CPU registers and proposes tiered storage (core memory, archival memory, recall memory) inspired by operating-system virtual memory management. The underlying thesis is that intelligent, long-horizon agents require a memory substrate that is both structured and queryable — not simply a longer context window. This framework extends naturally into the **self-improving agent** paradigm: if an agent can write to and read from its own persistent memory, it can accumulate task-specific heuristics over time and approach continuous learning without retraining.

## Methodology and Evidence

The repository is the canonical open-source codebase for the Letta platform. Evidence is primarily in the form of a working production system: 175 releases, 21.4k GitHub stars, 158 contributors, and active maintenance (latest release v0.16.6 on March 4, 2026). The README provides Hello World examples for both Python and TypeScript SDKs demonstrating the `memory_blocks` API, agent creation, and message exchange. The repository structure reveals a production-grade backend: Alembic for SQL database migrations, multiple Docker Compose configurations, Nginx, OpenTelemetry (`otel/`), Fern API generation (`fern/`), and a `.skills` directory confirming the skills subsystem. The cached distillation is the GitHub web interface page (README + file tree), not the full documentation site — deeper architectural documentation lives at `docs.letta.com`, which is not available in this cache.

## Key Claims

- **Stateful agents are the core offering**: "Letta is the platform for building stateful agents: AI with advanced memory that can learn and self-improve over time." This positions Letta not as an orchestration framework (like LangGraph or CrewAI) but as infrastructure for *persistent* agents.

- **Two distinct deployment modes**: Letta Code is a CLI tool (`npm install -g @letta-ai/letta-code`) for local terminal use; the Letta API serves application-embedded stateful agents. The split acknowledges both developer-local and production-embedded use cases.

- **Memory is structured as typed blocks**: Agent creation accepts `memory_blocks` — a list of label/value pairs. The README example shows two canonical blocks:
  > `{"label": "human", "value": "Name: Timber. Status: dog..."}` and `{"label": "persona", "value": "I am a self-improving superintelligence..."}`
  This is the "core memory" layer: always in context, mutable by the agent, durable across sessions.

- **Skills and subagents as first-class features**: "Letta Code supports skills and subagents, and bundles pre-built skills/subagents for advanced memory and continual learning." Skills are composable capabilities; subagents enable agent-spawned delegation — both are pre-packaged, not user-defined only.

- **Model-agnostic by design**: "Letta is fully model-agnostic, though we recommend Opus 4.5 and GPT-5.2 for best performance." The existence of a [model leaderboard](https://leaderboard.letta.com/) implies ongoing benchmarking across providers, which benefits adopters choosing between frontier and local models.

- **Agent state is persistent and identifiable**: `agent_state = client.agents.create(...)` returns a persistent state object with a stable `agent_state.id`. Subsequent `client.agents.messages.create(agent_id=..., input=...)` calls continue the session. The agent accumulates memory across every call — this is not a stateless REST call pattern.

- **Tools are bound at agent creation**: The hello world example registers `tools=["web_search", "fetch_webpage"]` at `create()` time. This implies tools are part of the agent's identity/definition, not injected per-message — a meaningful architectural choice for long-lived agents with stable capabilities.

- **SQL-backed persistence via Alembic**: The `alembic/` directory and `init.sql` confirm that agent state (including memory blocks) is stored in a relational database with schema migrations. This makes Letta's memory model durable and portable — not in-process or filesystem-only.

- **Webhook support is built-in**: `WEBHOOK_SETUP.md` in the repo root indicates Letta supports event-driven integrations, enabling agents to receive external triggers without polling — relevant for research workflow automation.

- **Apache-2.0 licensed**: Fully permissive licence — can be integrated into commercial and proprietary toolchains, self-hosted, and modified without copyleft obligations. This is significant for an EndogenAI local-compute deployment.

- **Active community at scale**: 21.4k stars and 158 contributors put Letta among the most widely adopted open-source agent infrastructure projects. 175 releases over the project's lifetime (latest v0.16.6 on 2026-03-04) confirms continuous, non-abandoned development.

- **Multi-language SDK surface**: Both `letta-client` (Python, `pip install letta-client`) and `@letta-ai/letta-client` (TypeScript/Node.js, `npm install`) are offered, indicating the API layer is language-agnostic and the framework does not impose a Python-only constraint.

- **Docker-native deployment stack**: Multiple Compose files (`compose.yaml`, `dev-compose.yaml`, `docker-compose-vllm.yaml`, `development.compose.yml`) alongside Nginx and TLS certificates (`certs/`) suggest Letta is designed for self-hosted, containerised deployment — directly compatible with EndogenAI's local-compute-first principle.

- **Continual/self-improvement framing**: The README mission statement references "self-improve over time" and "advanced memory and continual learning" as explicit goals. Letta positions memory not merely as a UX convenience but as the mechanism enabling agent adaptation — closer to lifelong learning than session history.

- **Letta Code CLI bundles pre-built agent tooling**: "bundles pre-built skills/subagents for advanced memory and continual learning" — meaning the CLI product ships with working reference implementations of memory-aware agents, providing concrete patterns that can be studied and ported.

## Critical Assessment

**Evidence Quality**: Documentation

The cached source is the GitHub repository landing page (README + file tree rendered as HTML, then distilled to Markdown). It is not the full documentation site, not a research paper, and not an architectural deep-dive. The README is intentionally a quick-start document. Claims about the memory architecture, the MemGPT-derived tiered memory model, and the internal implementation are therefore inferred from repository structure and the original MemGPT paper lineage rather than directly quoted from this cached page. The Hello World examples are verbatim quotes from the README and are reliable.

**Gaps and Limitations**: The cache does not include the Letta documentation site (`docs.letta.com`), which would contain the full memory architecture specification, the archival/recall memory APIs, the skills authoring guide, and the subagent delegation protocol. The critical question for EndogenAI — how does Letta index and query episodic memory beyond the in-context core memory blocks? — cannot be answered from this cache alone. The repository structure hints at SQLite or PostgreSQL backends (Alembic migrations, `init.sql`), but the query API for archival memory is absent from the README. Additionally, the self-hosted resource requirements (database, container stack) are not documented in this cached page, making it difficult to assess the cost-to-run for a local deployment. For the OPEN_RESEARCH.md #7 episodic memory comparison, Letta cannot be fully evaluated against mem0, Graphiti, or Cognee without fetching the documentation site.

## Connection to Other Sources

- Agrees with / extends: [github-com-getzep-graphiti](./github-com-getzep-graphiti.md) — both address persistent structured memory for agents; Letta uses relational/block memory while Graphiti uses a temporal knowledge graph; they solve adjacent problems and can coexist.
- Agrees with / extends: [arxiv-generative-agents](./arxiv-generative-agents.md) — Letta's memory block architecture maps onto the generative agents framework's memory stream concept; Letta is a production implementation of that paradigm.
- Agrees with / extends: [arxiv-context-engineering-survey](./arxiv-context-engineering-survey.md) — Letta is a concrete deployment of tiered context/memory management strategies surveyed in context engineering literature.
- Agrees with / extends: [tds-claude-skills-subagents](./tds-claude-skills-subagents.md) — Letta Code's skills and subagents architecture parallels Claude's skills/subagents model; both treat skills as composable tool packages and subagents as delegated executors.

## Relevance to EndogenAI

**ADOPT (memory block pattern) / ADAPT (deployment) / REJECT (full platform dependency)**

Letta is directly relevant to OPEN_RESEARCH.md #7 (episodic and experiential memory) and bears on D4 of the agentic research flows gate (recommended tools for token offloading via memory management). The `memory_blocks` architecture — typed, labelled, always-in-context blobs that an agent can read and overwrite — is immediately applicable to the EndogenAI session management problem. The equivalent in the current EndogenAI substrate is `.tmp/<branch>/<date>.md` session scratchpads: ephemeral, not queryable, manually managed. Letta's `human` and `persona` block pattern could be ADOPTED as a conceptual model for `docs/guides/session-management.md`: define what belongs in "always-in-context core memory" (project context, active task state) versus "archival memory" (past session outcomes). This is a documentation and methodology adoption, not necessarily a runtime one.

For runtime use, Letta's self-hosted Docker stack could be ADAPTED as a local-compute memory server for long-running research sessions — satisfying the local-compute-first principle from `MANIFESTO.md` and `docs/guides/local-compute.md`. However, this depends on resolving OPEN_RESEARCH.md #1 (local compute setup) first, since Letta's memory queries plausibly require an embedding model for archival retrieval. The full platform dependency (database, container orchestration, API key) is a significant overhead for a documentation-only repo; a lighter approach would be to extract the architectural patterns into the EndogenAI methodology without running Letta in production. The **Executive Researcher** should flag [docs/research/agentic-research-flows.md](../agentic-research-flows.md) for a Letta-informed update to its Memory Architecture section, specifically the gap between scratchpad accumulation and a queryable episodic layer. The gate deliverable D3 for OPEN_RESEARCH.md #7 (script candidate specification) maps naturally to a `scripts/query_session_memory.py` that could replicate Letta's recall memory pattern against the existing `.tmp/<branch>/` scratchpad corpus using local embeddings.

The skills and subagents capability in Letta Code is relevant to `.github/agents/` fleet design (OPEN_RESEARCH.md #6). Letta bundles pre-built subagent patterns; the EndogenAI equivalent is the agent `README.md` and individual `.agent.md` files. Studying Letta's `.skills` directory contents (not available in this cache) could inform a more formal capability-registration pattern for EndogenAI agents — currently capability advertisement is narrative-only in agent frontmatter.

A secondary, near-term actionable finding is Letta's tool-binding-at-creation pattern. EndogenAI's current agent definitions in `.github/agents/*.agent.md` list tools in frontmatter but the semantics are advisory, not enforced. Letta's pattern — where tools are declared at agent instantiation and become part of the agent's persistent identity — suggests a stricter convention worth encoding in the [`docs/guides/agents.md`](../guides/agents.md) guide: tools should be declared and stable, not ad-hoc per invocation. This is an ADAPT recommendation: adopt the conceptual discipline without requiring the Letta runtime.

Finally, this source should be revisited alongside the `docs.letta.com` documentation (not cached) once OPEN_RESEARCH.md #1 (local compute) is resolved, to evaluate Letta's archival memory retrieval API as a candidate `scripts/` implementation for the session history query gap identified in [agentic-research-flows.md](../agentic-research-flows.md).

In summary: ADOPT the `memory_blocks` labeled-memory pattern as a conceptual model for EndogenAI session context design; ADAPT the self-hosted deployment if local compute prerequisites are met and the episodic memory bottleneck is confirmed; REJECT a hard runtime dependency on the full Letta platform until that prerequisite is satisfied.

## Referenced By

<!-- Populated automatically by scripts/link_source_stubs.py — do not edit manually -->
- [Github Com Mem0Ai Mem0](../sources/github-com-mem0ai-mem0.md)
- [Github Com Topoteretes Cognee](../sources/github-com-topoteretes-cognee.md)
- [Kdnuggets Com Docker Ai For Agent Builders Models Tools And ](../sources/kdnuggets-com-docker-ai-for-agent-builders-models-tools-and-.md)
