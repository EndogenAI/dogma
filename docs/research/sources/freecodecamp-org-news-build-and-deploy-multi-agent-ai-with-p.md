---
slug: "freecodecamp-org-news-build-and-deploy-multi-agent-ai-with-p"
title: "Build and Deploy a Multi-Agent AI System with Python and Docker"
url: "https://www.freecodecamp.org/news/build-and-deploy-multi-agent-ai-with-python-and-docker/"
authors: "Balajee Asish Brahmandam"
year: "2025"
type: blog
topics: [multi-agent-systems, docker, python, llm-pipelines, orchestration, containerisation]
cached: true
evidence_quality: documentation
date_synthesized: "2026-03-06"
---

## Citation

Brahmandam, B. A. (2025). "Build and Deploy a Multi-Agent AI System with Python and Docker." *freeCodeCamp News*. https://www.freecodecamp.org/news/build-and-deploy-multi-agent-ai-with-python-and-docker/ (Accessed 2026-03-06.)

## Research Question Addressed

This handbook-style tutorial addresses the question: how do you design, build, containerise, and schedule a reliable multi-agent AI pipeline from scratch using only Python and Docker? It is specifically targeted at developers who are comfortable with Python but have not previously used Docker or multi-agent architectures.

## Theoretical / Conceptual Framework

The article operates within the **ReAct (Reasoning + Acting)** paradigm for individual agent behaviour and applies a **separation-of-concerns** design principle at the system level. Each agent is assigned one narrow responsibility; the LLM is invoked only where language understanding or reasoning is genuinely required. This explicitly rejects the "God Model" anti-pattern (one monolithic agent doing everything), positioning specialised, composable micro-agents as the preferred architectural unit. The pipeline topology follows a classic **synchronous sequential DAG** — no back-channels or feedback loops — implemented via Docker Compose service dependency ordering.

## Methodology and Evidence

This is a practitioner handbook, not an empirical study. Evidence is demonstrated through worked code examples, annotated Dockerfiles, a `docker-compose.yml`, unit-test snippets, and an end-to-end integration test script. The article is structured to walk a reader from concept through to a running, schedulable system. Justifications are given by reasoning from first principles (e.g., why layered Dockerfile ordering improves rebuild speed) rather than by benchmark data.

The cost table comparing `gpt-4o-mini`, `gpt-4o`, and Ollama is the closest thing to empirical evidence, though the figures reference OpenAI pricing "as of early 2025" and are inherently subject to change. Code samples are complete and runnable, not pseudocode, which strengthens their reliability as practical evidence. The article demonstrates error resilience through pytest unit tests for the Prioritizer's scoring function and a shell-based integration test verifying output file existence and content. Observability is addressed through both human-readable and JSON-formatted logging patterns, and a list of five useful operational metrics is provided (files ingested, summarizer latency, token usage, error/retry count, output-file success flag).

## Key Claims

- **ReAct loop as the agent execution model**: "Agents typically follow a loop called the **ReAct pattern**, which stands for Reasoning plus Acting. At each step, the agent thinks about what to do, takes an action, observes the result, and decides whether it has reached its goal." This is the foundational design assumption underlying every agent in the pipeline.

- **God Model anti-pattern explicitly named**: "That approach is called the 'God Model' pattern, and it has real problems. When you ask a single LLM to ingest data, summarise it, prioritise it, and format it all in one prompt, you are giving it too much to think about at once." The article frames multi-agent separation as a direct remedy.

- **Minimal LLM usage as a design goal**: "Notice that only one of the four agents actually calls an LLM. The others are plain Python. This is intentional — you should only use an LLM when you need reasoning or language understanding. Everything else should be deterministic code. It is cheaper, faster, and more predictable."

- **Shared-volume pattern for inter-agent communication**: All four agents communicate via a Docker-mounted shared volume (`./data:/data`). Each agent reads from the previous agent's output file and writes its own output file. This is the simplest viable IPC pattern for a synchronous pipeline.

- **`service_completed_successfully` as the correct Compose dependency condition**: "This setting (available in Compose v2) tells Docker to wait until the previous container exits with a zero exit code before starting the next one. Without this condition, `depends_on` only waits for the container to *start*, not to *finish* — which would cause race conditions."

- **Structured consistent logging across the fleet**: Every agent uses the same `logging.basicConfig` format string (`"%(asctime)s [%(levelname)s] %(name)s: %(message)s"`). "When Docker Compose runs all four containers, it interleaves their logs with container name prefixes, giving you a unified timeline of the entire pipeline."

- **Exponential backoff retry logic for LLM calls**: The Summarizer catches `RateLimitError` specifically and waits 5, 10, then 15 seconds between retries: "This is called **exponential backoff**. Other API errors raise immediately because retrying them will not help."

- **Graceful degradation over crashing**: "If the input is empty or the API fails completely, the agent writes a fallback message instead of crashing, so the downstream agents can still run." This ensures pipeline continuity even under LLM API failure.

- **Docker layer ordering for rebuild performance**: "By putting dependency installation before the code copy, Docker only re-runs `pip install` when your requirements actually change, making rebuilds much faster — seconds instead of minutes." This is a concrete operational best practice.

- **Cost of gpt-4o-mini for a daily pipeline**: "For a daily personal digest processing a few thousand tokens of input, `gpt-4o-mini` costs less than a penny per run. That works out to roughly three dollars per year." Local Ollama is listed as a free alternative for full privacy.

- **Ollama integration for local LLM via `host.docker.internal`**: The article provides a complete code snippet using `http://host.docker.internal:11434/api/generate` to reach an Ollama server from inside a Docker container, with a Linux `extra_hosts` workaround.

- **Token budget management via hard text slice**: `text[:8000]` is used as a simple context-window guard before the API call. The article acknowledges this is a blunt instrument: "For production, you would want smarter chunking that splits on sentence or paragraph boundaries rather than a raw character count."

- **Secrets management hierarchy**: `.env` files for development; Docker Secrets (mounted at `/run/secrets/`) for production Swarm/Kubernetes deployments. Environment variables are noted as visible in process listings and inspect commands, making them less secure than mounted secrets.

- **Event-driven upgrade path**: "For more complex systems, you could replace the shared volume with a message broker like Redis or RabbitMQ, which lets agents run asynchronously and react to events." This is flagged as the natural next architectural progression beyond the synchronous pipeline.

- **Unit-test isolation without Docker**: "Because each agent's core logic is a plain Python function, you can test it in isolation without Docker." The test example imports `score_line` from `agents/prioritizer/app.py` directly via `sys.path.insert`, demonstrating the value of single-responsibility functions for testability.

- **Feedback-loop upgrade as explicit future direction**: The article closes by recommending: "Add an agent that evaluates the quality of the daily digest and adjusts the Summarizer's prompts over time. This is how production agent systems learn and improve." This describes a self-loop phase gate — the agent fleet reflecting on its own output and modifying its own prompts — which is the pattern being codified in the EndogenAI Research Workflow.

- **Agent collaboration frameworks named as next step**: "Tools like CrewAI and LangGraph let you build agents that delegate tasks to each other, negotiate priorities, and collaborate in more sophisticated ways." These are positioned as the natural progression beyond file-coupled pipeline agents, relevant to D1 gate deliverables surveying multi-agent pipeline tools.

- **Cron and Task Scheduler integration for daily automation**: The article gives full crontab instructions for Linux/macOS (`0 7 * * *`) and Task Scheduler guidance for Windows to schedule the pipeline without any additional tooling. This is a practical zero-dependency scheduling pattern applicable to the EndogenAI `fetch_all_sources.py` and similar scripts.

## Critical Assessment

**Evidence Quality**: Documentation

This is a well-structured practitioner tutorial from a credible educational platform. It does not present original research or benchmarks beyond a pricing table. All claims are backed by code examples and first-principles reasoning rather than measured experiments. The evidence for performance and reliability claims (e.g., "seconds instead of minutes" for faster rebuilds) is asserted rather than demonstrated. The OpenAI pricing figures are dated and volatile. The article is comprehensive and internally consistent, but its authority derives from practical experience and coding pedagogy rather than rigorous empirical methodology.

**Gaps and Limitations**: The article covers a synchronous sequential pipeline only; concurrent or parallel agent execution is mentioned only as a future extension. There is no treatment of agent coordination, negotiation, or shared state beyond simple file handoffs — the agents are fully decoupled and cannot communicate bidirectionally. Error recovery is limited to retry logic and fallback strings; there is no circuit-breaker, dead-letter queue, or human-in-the-loop escalation. The Prioritizer's keyword-scoring approach is explicitly a simplification with no evaluation of accuracy. The section on production deployment (Swarm, Kubernetes, Cloud) is very thin — a few paragraphs with no worked configuration. The article does not address prompt versioning, model pinning, or LLM output validation, which are important for production reliability. There is also no guidance on agent versioning or rollback when a pipeline stage is updated, which becomes a real operational concern in any environment with more than one developer. The article does not address how to integrate a persistent memory or knowledge-graph layer (such as Graphiti or Cognee) into the pipeline — agents are fully stateless between runs, which limits their ability to learn from previous executions. Finally, the shared-volume IPC pattern does not extend to distributed deployments: once agents run on separate machines, the file-handoff model breaks entirely and the message-broker upgrade path (Redis/RabbitMQ) becomes mandatory, but no migration guidance is given.

## Connection to Other Sources

- Agrees with / extends: [anthropic-building-effective-agents.md](./anthropic-building-effective-agents.md) — both advocate for minimal LLM invocation, separation of concerns, and explicit pipeline orchestration over monolithic agents.
- Agrees with / extends: [arxiv-react.md](./arxiv-react.md) — the article explicitly names and applies the ReAct loop as its agent execution model.
- Practical complement to: [cookbook-research-lead-agent.md](./cookbook-research-lead-agent.md) — both deal with orchestrating sub-agents in a pipeline; this article provides the containerisation layer that the cookbook omits.
- Partially contradicts: [arxiv-generative-agents.md](./arxiv-generative-agents.md) — this article's agents are stateless, single-pass, and file-coupled, in contrast to the persistent memory and social simulation model described in generative agents research. The tradeoff is simplicity and reproducibility vs. adaptive, stateful behaviour.
- Contextualises: [tds-claude-skills-subagents.md](./tds-claude-skills-subagents.md) — the Claude subagent model operates within a single LLM session context, whereas this article packages each agent as an independent container process; both approaches realise the separation-of-concerns principle at different architectural layers.
- Protocol upgrade path: [a2a-announcement](./a2a-announcement.md) — A2A's artefact-passing model is the network-capable formalisation of this article's file-based handoff pattern; adopting A2A would allow per-agent containers to run on separate machines without redesigning application logic.
- Memory integration gap: [github-com-getzep-graphiti](./github-com-getzep-graphiti.md) and [github-com-topoteretes-cognee](./github-com-topoteretes-cognee.md) — this article's agents are fully stateless between runs; adding a Graphiti or Cognee sidecar container to the Compose stack would close the cross-run memory gap without changing the agent logic.

## Relevance to EndogenAI

This source is directly relevant to the EndogenAI Research Workflow as a concrete implementation reference for the **quasi-encapsulated sub-fleet pattern** codified in the current workflow. The article's four-agent pipeline (Ingestor → Summarizer → Prioritizer → Formatter) maps closely onto the Scout → Synthesizer → Reviewer → Archivist phases described in [docs/research/agentic-research-flows.md](../agentic-research-flows.md). The key structural lesson — assign one narrow responsibility per agent and invoke the LLM only where reasoning is genuinely required — reinforces existing EndogenAI convention and should be **ADOPTED** as explicit guidance in [docs/guides/agents.md](../../guides/agents.md), specifically in any section describing when to delegate to a sub-agent vs. when to use deterministic code.

The `service_completed_successfully` Compose pattern and shared-volume IPC model are useful references for any future infrastructure work on the EndogenAI scripts layer (e.g., `scripts/fetch_all_sources.py`, `scripts/link_source_stubs.py`). The current scripts run sequentially in a single process; if they are ever containerised or parallelised, this article provides a production-tested template. The pattern should be **ADOPTED** conditionally: it applies if and when the scripts are containerised, but is not urgent for the current single-machine, `uv run`-based execution model.

The article's recommendation to replace shared volumes with Redis or RabbitMQ for event-driven pipelines is relevant to the D4 gate deliverable on token offloading tools. Redis is named as a lightweight message broker that enables asynchronous agent execution without a full orchestration framework. This is worth **ADOPTING** into the OPEN_RESEARCH.md follow-up list as a concrete candidate for the async inter-agent communication pattern, but should not be acted on until the synchronous pipeline is stable.

The article's treatment of the feedback-loop upgrade path — adding a quality-evaluation agent that modifies Summarizer prompts over time — directly mirrors the self-loop phase gate concept central to the current EndogenAI research question. This is the clearest external validation encountered so far for that pattern; no framework or API is required, just an additional agent stage checking its predecessor's output against a rubric. This finding should be **ADOPTED** as supporting evidence when formalising the self-loop gate in [docs/research/agentic-research-flows.md](../agentic-research-flows.md), and cited to demonstrate that the pattern appears in practitioner literature independent of EndogenAI's own derivation.

## Referenced By

<!-- Populated automatically by scripts/link_source_stubs.py — do not edit manually -->
- [A2A Announcement](../sources/a2a-announcement.md)
- [Agentic Research Flows](../agentic-research-flows.md)
- [Anthropic Building Effective Agents](../sources/anthropic-building-effective-agents.md)
- [Arxiv Generative Agents](../sources/arxiv-generative-agents.md)
- [Arxiv React](../sources/arxiv-react.md)
- [Cookbook Research Lead Agent](../sources/cookbook-research-lead-agent.md)
- [Github Com Getzep Graphiti](../sources/github-com-getzep-graphiti.md)
- [Github Com Topoteretes Cognee](../sources/github-com-topoteretes-cognee.md)
- [Kdnuggets Com Docker Ai For Agent Builders Models Tools And ](../sources/kdnuggets-com-docker-ai-for-agent-builders-models-tools-and-.md)
- [Opensourceprojects Dev Post E7415816 A348 4936 B8Bd 0C651C4A](../sources/opensourceprojects-dev-post-e7415816-a348-4936-b8bd-0c651c4a.md)
- [Tds Claude Skills Subagents](../sources/tds-claude-skills-subagents.md)
