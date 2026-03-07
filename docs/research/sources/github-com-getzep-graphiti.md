---
slug: "github-com-getzep-graphiti"
title: "Graphiti: Build Real-Time Knowledge Graphs for AI Agents"
url: "https://github.com/getzep/graphiti"
authors: "Zep (getzep)"
year: "2025"
type: repo
topics: [knowledge-graph, episodic-memory, temporal-reasoning, rag, agent-memory, graph-database]
cached: true
evidence_quality: documentation
date_synthesized: "2026-03-06"
---

## Citation

Zep. (2025). *Graphiti: Build Real-Time Knowledge Graphs for AI Agents* [Software repository]. GitHub. https://github.com/getzep/graphiti. Accessed 2026-03-06. See also companion paper: Zep. (2025). "Zep: A Temporal Knowledge Graph Architecture for Agent Memory." arXiv:2501.13956.

## Research Question Addressed

This repository addresses the following problem: how should AI agents persist, update, and query memory across sessions when the underlying facts change over time? Traditional RAG approaches rely on batch processing and static summarisation, making them unsuitable for frequently changing data or long-running agent sessions. Graphiti exists to provide a production-ready, incrementally-updatable knowledge graph layer purpose-built for agents operating in dynamic environments.

## Theoretical / Conceptual Framework

Graphiti operates within the **temporally-aware knowledge graph** paradigm, specifically building on the classic triplet model (entity–relationship–entity) while adding a **bi-temporal data model**: every fact records both the time the event occurred and the time it was ingested. This is distinct from both vanilla RAG (embedding lookup) and Microsoft GraphRAG (community summaries via LLM). The framework's retrieval philosophy is **hybrid**: semantic embeddings plus BM25 keyword search plus graph traversal, surfacing information across three retrieval axes simultaneously. Contradiction handling is handled via **temporal edge invalidation** rather than LLM summarisation judgements — a structural commitment to deterministic conflict resolution.

## Methodology and Evidence

Graphiti is an open-source Python framework (Apache-2.0) with 23.4k GitHub stars, 2.3k forks, and 191 releases as of v0.28.1 (February 2026). The repository is the primary artifact; documentation, quickstart examples, and a companion arXiv paper (2501.13956) are the supporting evidence base. The framework exposes a `graphiti-core` Python package installable via `pip` or `uv`, and ships with a FastAPI REST server, an MCP server, Docker Compose configurations, and a pluggable graph driver layer supporting Neo4j, FalkorDB, Kuzu, and Amazon Neptune. Evaluation evidence referenced in the README cites a Zep blog post claiming "State of the Art in Agent Memory" benchmarks, but the methodology for that benchmark is external to this repository. The codebase is primarily Python (99.3%) and includes CI for linting, unit tests, and typechecking.

## Key Claims

- **Real-time incremental ingestion (no batch recomputation)**: "Graphiti continuously integrates user interactions, structured and unstructured enterprise data, and external information into a coherent, queryable graph… without requiring complete graph recomputation." This directly addresses the latency and staleness problem of batch RAG pipelines.

- **Bi-temporal data model**: Graphiti provides "Explicit tracking of event occurrence and ingestion times, allowing accurate point-in-time queries." Both _when something happened_ and _when it was recorded_ are first-class properties of every edge.

- **Sub-second query latency vs. GraphRAG's seconds-to-tens-of-seconds**: The README comparison table lists Graphiti query latency as "Typically sub-second latency" against GraphRAG's "Seconds to tens of seconds." This is attributed to the hybrid retrieval approach that avoids sequential LLM summarisation calls at query time.

- **Contradiction handling via edge invalidation, not LLM summarisation**: Where GraphRAG uses "LLM-driven summarization judgments" for contradictions, Graphiti uses "Temporal edge invalidation." This makes conflict resolution deterministic and auditable.

- **Hybrid retrieval across three axes**: "Combines semantic embeddings, keyword (BM25), and graph-based search methods." No single retrieval modality is relied upon exclusively, reducing the failure modes of pure vector search.

- **Custom entity definitions via Pydantic models**: "Flexible ontology creation and support for developer-defined entities through straightforward Pydantic models." Agents can teach the graph what domain entities to track without modifying the core framework.

- **Pluggable driver architecture with 11 operation ABCs**: The architecture exposes a `GraphDriver` ABC and 11 sub-interfaces (`EntityNodeOperations`, `EpisodicEdgeOperations`, `SearchOperations`, etc.) so that Neo4j, FalkorDB, Kuzu, and Neptune can be swapped without altering application logic.

- **Supports local LLMs via Ollama**: "Graphiti supports Ollama for running local LLMs and embedding models via Ollama's OpenAI-compatible API. This is ideal for privacy-focused applications or when you want to avoid API costs." The `OpenAIGenericClient` wrapper handles local endpoints with a 16K default token limit.

- **Best with structured-output-capable LLMs**: "Graphiti works best with LLM services that support Structured Output (such as OpenAI and Gemini). Using other services may result in incorrect output schemas and ingestion failures. This is particularly problematic when using smaller models." This is a hard constraint on local model choices.

- **Concurrency controlled by SEMAPHORE_LIMIT**: "Graphiti's ingestion pipelines are designed for high concurrency. By default, concurrency is set low [SEMAPHORE_LIMIT=10] to avoid LLM Provider 429 Rate Limit Errors." Increasing this cap is the primary lever to improve ingestion throughput.

- **MCP server for direct Claude/Cursor integration**: "The mcp_server directory contains a Model Context Protocol (MCP) server implementation for Graphiti. This server allows AI assistants to interact with Graphiti's knowledge graph capabilities through the MCP protocol." Key features include episode management, entity management, semantic and hybrid search, and group management.

- **Episodic data model distinct from GraphRAG's community summaries**: Graphiti's knowledge structure is described as "Episodic data, semantic entities, communities" as opposed to GraphRAG's "Entity clusters and community summaries." Episodes are the unit of ingestion — raw interactions or documents atomically added to the graph.

- **Explicit distinction between Zep (managed) and Graphiti (OSS core)**: "Choose Zep if you want a turnkey, enterprise-grade platform… Choose Graphiti if you want a flexible OSS core and you're comfortable building/operating the surrounding system." This positions Graphiti as the self-hosted, infrastructure-responsible option.

- **Apache-2.0 license; opt-out telemetry**: Telemetry can be disabled with `export GRAPHITI_TELEMETRY_ENABLED=false`. Telemetry collects only LLM provider type, DB backend, embedder type, OS and Python version — never queries, graph content, or API keys.

- **191 releases as of v0.28.1 (February 2026)**: The cadence and release count indicate active, production-grade maintenance — not an abandoned prototype.

- **Kuzu driver supports in-process operation without a server**: Among supported backends, Kuzu runs as an embedded local graph database requiring no separate server process — the path of least resistance for single-machine deployments aligned with the EndogenAI Local Compute First principle.

- **Episodes are the atomic unit of ingestion; no full re-index required**: Each ingestion call adds a bounded, reversible unit of knowledge. This contrasts with vector stores that require re-embedding the entire corpus when new content is added.

- **Driver swap is architecture-level, not application-level**: The `GraphDriver` ABC means switching backends (e.g., Neo4j to Kuzu) requires changing only the driver instantiation, not any application-level `Graphiti` API calls — a direct application of Dependency Inversion.

- **Telemetry collects only operational metadata, never query content**: Telemetry can be disabled with `export GRAPHITI_TELEMETRY_ENABLED=false` and collects only LLM provider type, DB backend, OS and Python version — never queries, graph content, or API keys.

- **Neo4j and FalkorDB recommended for production scale**: The README distinguishes embedded backends (Kuzu) for lightweight local use from server-backed stores (Neo4j, FalkorDB, Amazon Neptune) for production scale, giving a clear migration path as data volume grows.

## Critical Assessment

**Evidence Quality**: Documentation

The README is a well-structured, technically detailed repository landing page. It provides architectural specifics (the 11-operation ABC pattern, the bi-temporal model, the `SEMAPHORE_LIMIT` mechanism) that are verifiable against source code but are not independently peer-reviewed. The companion paper (arXiv:2501.13956) provides deeper academic grounding and is cited in the README; that paper is not synthesised here. The "State of the Art in Agent Memory" claim references a Zep blog post, not a neutral benchmark. All performance claims (sub-second latency) are presented without reproducible benchmark conditions in the README itself.

**Gaps and Limitations**: The cached page is the GitHub repository README, not the full documentation site (`help.getzep.com/graphiti`), the companion paper, the quickstart examples, or the MCP server README — all of which contain substantive technical content not captured here. The README is silent on: cost models for graph storage at scale, failure modes when the graph becomes inconsistent, migration strategies between graph backends, and operational guidance for long-running agent deployments. The requirement for Structured Output compatibility from the LLM is a hard constraint that significantly narrows local model choices and is underweighted in the feature summary. The arXiv companion paper (2501.13956) is cited but not synthesised here; it may address benchmark methodology, graph consistency guarantees, and evaluation criteria that are absent from the README. Additionally, the README does not discuss how Graphiti handles schema evolution — a real concern for long-lived agents whose entity ontologies grow over time — nor how it responds when two concurrent ingestion jobs create conflicting facts about the same entity.

## Connection to Other Sources

- Extends / contextualises: [arxiv-react.md](./arxiv-react.md) — Graphiti provides a persistent memory substrate that ReAct-style agents can read and write, closing the statelessness gap in the original ReAct design.
- Contrasts with: [anthropic-building-effective-agents.md](./anthropic-building-effective-agents.md) — Anthropic's guide focuses on ephemeral context windows and tool-call patterns; Graphiti is an explicit counter-architecture that externalises and indexes cross-session memory.
- Potential complement to: [arxiv-generative-agents.md](./arxiv-generative-agents.md) — generative agents rely on a memory stream with retrieval; Graphiti's temporal graph is a more structured and queryable alternative to flat memory streams.
- May be referenced by: [agentic-research-flows.md](../agentic-research-flows.md) — the issue synthesis on agentic research flows where D4 (token offloading / memory management) is a gate deliverable.
- Overlapping scope / compare and contrast: [github-com-topoteretes-cognee](./github-com-topoteretes-cognee.md) — Cognee also builds knowledge graphs for agent memory but emphasises a higher-level add→cognify→search pipeline; Graphiti offers finer-grained control over the temporal edge model and is more explicit about bi-temporal query semantics.
- Overlapping scope: [github-com-mem0ai-mem0](./github-com-mem0ai-mem0.md) — mem0 is an abstraction layer over multiple memory backends; Graphiti is a specific temporal graph backend that mem0 could in principle wrap, though direct integration is not described in either source.
- Academic grounding: [arxiv-org-html-2512-05470v1](./arxiv-org-html-2512-05470v1.md) — the AIGNE context engineering paper explicitly surveys Graphiti/Zep as prior work in its related-work section, validating Graphiti's positioning within the broader context engineering research space.
- Infrastructure deployment: [kdnuggets-com-docker-ai-for-agent-builders-models-tools-and-](./kdnuggets-com-docker-ai-for-agent-builders-models-tools-and-.md) — FalkorDB can be launched via Docker Compose alongside Docker Model Runner, enabling a fully containerised local inference-plus-memory agent stack.
- Workflow scratchpad evolution: [agentic-research-flows.md](../agentic-research-flows.md) — the `.tmp/` scratchpad is a flat precursor to what Graphiti's temporal graph offers; the two represent successive stages of memory infrastructure maturity in the research workflow.
- Protocol complement: [a2a-announcement](./a2a-announcement.md) — A2A manages inter-agent task coordination while Graphiti manages persistent cross-session memory; both are simultaneously required for a fully stateful distributed multi-agent system.
- Programmatic scripting: the Graphiti Python SDK integrates naturally with `uv run` scripts, consistent with the EndogenAI programmatic-first principle that repeated memory operations be encoded as scripts rather than performed interactively by agents.

## Relevance to EndogenAI

**D4 — Token offloading and the Research Workflow memory gap.** The EndogenAI research workflow currently accumulates context in `.tmp/<branch>/<date>.md` scratchpad files, with `scripts/prune_scratchpad.py` as the sole memory management mechanism. This is a flat, append-only model with no retrieval layer — it handles volume but not semantic access. Graphiti directly addresses this gap: its hybrid retrieval (semantic + BM25 + graph traversal) would let the Executive Researcher agent query "what did the Scout find about episodic memory?" rather than reading through hundreds of lines of scratchpad. **Recommendation: ADOPT as an architectural target for Phase 2 of the Research Workflow**. The immediate blocker is infrastructure: deploying Neo4j or FalkorDB adds operational overhead that is inconsistent with the Local Compute First principle unless a self-contained embedded backend (Kuzu, which supports in-process operation) is used. FalkorDB via Docker (`docker run falkordb/falkordb:latest`) lowers the barrier.

**Ollama compatibility and local compute alignment.** The `OpenAIGenericClient` with Ollama support positions Graphiti as viable under the "local compute first" constraint in AGENTS.md. However, the README's structured-output caveat is a material risk: local models that do not support structured output reliably will produce ingestion failures. Any adoption plan must specify a tested local model (e.g., Llama 3.1 via Ollama with structured output enabled) rather than defaulting to the smallest available model. **Recommendation: ADAPT** — adopt the Graphiti architecture but pilot against an Ollama-served model verified for structured output support before encoding it into the workflow scripts.

**MCP server integration with `.github/agents/` custom agents.** The Graphiti MCP server exposes episode management and hybrid search via the Model Context Protocol — the same protocol that Claude-based agents consume. Any EndogenAI agent equipped with MCP tools could read from and write to Graphiti's graph directly, replacing scratchpad appendage with structured memory writes. This is directly relevant to the `Executive Researcher` agent (`.github/agents/`) and the `session-management.md` guide. **Recommendation: ADOPT** the MCP server integration path as the preferred agent-memory interface rather than a custom Python SDK wrapper, since it requires no changes to agent frontmatter beyond adding the MCP endpoint.

## Referenced By

<!-- Populated automatically by scripts/link_source_stubs.py — do not edit manually -->
- [A2A Announcement](../sources/a2a-announcement.md)
- [Arxiv Org Html 2512 05470V1](../sources/arxiv-org-html-2512-05470v1.md)
- [Freecodecamp Org News Build And Deploy Multi Agent Ai With P](../sources/freecodecamp-org-news-build-and-deploy-multi-agent-ai-with-p.md)
- [Github Com Letta Ai Letta](../sources/github-com-letta-ai-letta.md)
- [Github Com Mem0Ai Mem0](../sources/github-com-mem0ai-mem0.md)
- [Github Com Topoteretes Cognee](../sources/github-com-topoteretes-cognee.md)
- [Kdnuggets Com Docker Ai For Agent Builders Models Tools And ](../sources/kdnuggets-com-docker-ai-for-agent-builders-models-tools-and-.md)
