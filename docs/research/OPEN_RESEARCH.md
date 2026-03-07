# Open Research Tasks

This document tracks open research questions for the endogenic development methodology.
Each section corresponds to a GitHub Issue that should be opened using the **Research** issue template.

> **Action required**: Open each section below as a GitHub Issue in this repository using the
> [Research template](../.github/ISSUE_TEMPLATE/research.md). Labels: `research`.

---

## 1. Running VS Code Copilot Locally with Local Models

**Priority: High** (directly reduces token cost — Priority C from AccessiTech/EndogenAI#35)

### Research Question
How do we configure VS Code GitHub Copilot to use local LLM inference (Ollama, LM Studio, llama.cpp) instead of cloud APIs?

### Why This Matters
Cloud inference is expensive in tokens, money, and environmental impact. Running inference locally enables the **local-compute-first** principle from `MANIFESTO.md` and can significantly reduce per-session costs.

### Resources to Survey
- [ ] https://ollama.ai — local model serving, OpenAI-compatible API
- [ ] https://lmstudio.ai — GUI-based local model management
- [ ] https://www.xda-developers.com/youre-using-local-llm-wrong-if-youre-prompting-it-like-cloud-llm/
- [ ] How I built a Claude Code workflow with LM Studio for offline-first development (see AccessiTech/EndogenAI#32)
- [ ] VS Code Copilot extension GitHub docs for custom model endpoint configuration
- [ ] https://towardsdatascience.com/claude-skills-and-subagents-escaping-the-prompt-engineering-hamster-wheel/

### Gate Deliverables
- [ ] D1 — Verified step-by-step setup guide in `docs/guides/local-compute.md`
- [ ] D2 — Model selection recommendations by task type
- [ ] D3 — Benchmark: token savings vs. quality for common agent tasks

---

## 2. Locally Distributed MCP Frameworks

**Priority: High** (directly enables local compute and agent fleet scaling)

### Research Question
How do we distribute MCP (Model Context Protocol) server infrastructure across a local network? What are best practices for multi-machine agent coordination without cloud dependency?

### Why This Matters
The endogenic vision includes running agent fleets locally. MCP distribution enables multiple machines (e.g., a powerful GPU machine + a dev workstation) to share inference capacity and context.

### Resources to Survey
- [ ] https://opensourceprojects.dev/post/e7415816-a348-4936-b8bd-0c651c4ab2d8
- [ ] https://www.freecodecamp.org/news/build-and-deploy-multi-agent-ai-with-python-and-docker/
- [ ] https://www.kdnuggets.com/docker-ai-for-agent-builders-models-tools-and-cloud-offload
- [ ] AccessiTech/EndogenAI architecture docs and `docs/architecture.md`
- [ ] Docker Compose patterns for local MCP server clusters

### Gate Deliverables
- [ ] D1 — Survey of MCP distribution patterns and tools
- [ ] D2 — Recommended architecture for local multi-machine MCP deployment
- [ ] D3 — Guide in `docs/guides/` for setting up a local MCP cluster

---

## 3. Async Process Handling in Agent Workflows

**Priority: Medium** (improves agent reliability for long-running tasks)

### Research Question
How should agents and sub-agents handle async/long-running terminal processes (e.g., model downloads, Docker container startup) without hanging or silently failing?

### Why This Matters
Async processes are common in AI development workflows (pulling models, starting containers, running tests). Poor handling leads to silent failures and wasted tokens re-trying failed operations. Inspired by AccessiTech/EndogenAI#33.

### Suggested Patterns to Research
- [ ] Synchronous wait-with-timeout pattern
- [ ] Interval-based status check pattern
- [ ] Observable status APIs (Docker, Ollama, etc.) — document their check endpoints
- [ ] VS Code task `problemMatcher` for background process detection

### Gate Deliverables
- [ ] D1 — Documented patterns for common async operations (Docker, Ollama, npm install, pytest)
- [ ] D2 — Agent guidelines for async handling in `AGENTS.md`
- [ ] D3 — (optional) Script or VS Code task wrapper for common long-running operations

---

## 4. Free and Low-Cost LLM Tier Strategy

**Priority: Medium** (reduces cost, extends runway)

### Research Question
What is the optimal strategy for mixing free/low-cost LLM tiers with higher-tier models, maximizing quality while minimizing token cost?

### Why This Matters
From AccessiTech/EndogenAI#35: "Prepare for free tiered models (we have been using Claude Sonnet exclusively)" and "Utilize the Auto model in VS Code Copilot chat to get ~10% off token usage."

### Areas to Research
- [ ] VS Code Copilot Auto model selection behavior — when does it use smaller models?
- [ ] Free tier quotas and rate limits for major providers (Anthropic, OpenAI, GitHub Copilot)
- [ ] Task categorization for model selection: which tasks need Sonnet vs. a local 7B model?
- [ ] GitHub Copilot free tier capabilities

### Gate Deliverables
- [ ] D1 — Model selection decision table by task type
- [ ] D2 — Monthly token budget strategy document
- [ ] D3 — Update `docs/guides/local-compute.md` with tier strategy

---

## 5. Endogenic Methodology — Literature Review and Prior Art

**Priority: Low** (foundational, informs long-term methodology)

### Research Question
What existing methodologies, frameworks, and research most closely resemble or inform the endogenic approach? What can we learn from them?

### Why This Matters
Endogenic development is inspired by biological endogenesis but should stand on the shoulders of giants — absorbing best practices from software engineering, cognitive science, and AI research rather than reinventing them.

### Areas to Survey
- [ ] Morphogenetic computing and self-organizing systems
- [ ] Generative programming and model-driven development
- [ ] Living documentation methodologies (Architecture Decision Records, etc.)
- [ ] Agent-oriented software engineering literature
- [ ] Related GitHub projects: https://github.com/originalankur/GenerateAgents.md
- [ ] AI in science fiction — visionary concepts yet to be realized (AccessiTech/EndogenAI#36)

### Gate Deliverables
- [ ] D1 — Literature review in `docs/research/methodology-review.md`
- [ ] D2 — What to adopt vs. what is genuinely novel about the endogenic approach
- [ ] D3 — Update `MANIFESTO.md` with synthesized insights

---

## 6. Agent Fleet Design Patterns

**Priority: Low** (improves long-term agent architecture)

### Research Question
What are the best design patterns for hierarchical agent fleets? How should executives, sub-agents, and specialist agents be structured for different project types?

### Why This Matters
The current agent fleet emerged organically from the EndogenAI project. As this repo becomes the authoritative source, we should synthesize and formalize the patterns.

### Areas to Research
- [ ] Hierarchical multi-agent patterns (executive → sub-agent → specialist)
- [ ] Context window management strategies for long agent sessions
- [ ] A2A (Agent-to-Agent) protocol patterns — message envelope, task lifecycle, routing
- [ ] A2A Agent Card schema — capability advertisement and discovery mechanism (gap flagged by Scout C, 2026-03-06)
- [ ] ReAct trajectory paper — interleaved reasoning and acting as the foundation for action-oriented agents (Yao et al.; not yet fetched)
- [ ] https://arxiv.org/html/2512.05470v1 (referenced in AccessiTech/EndogenAI#32)
- [ ] https://towardsdatascience.com/claude-skills-and-subagents-escaping-the-prompt-engineering-hamster-wheel/

### Gate Deliverables
- [ ] D1 — Agent fleet pattern catalog in `docs/guides/agents.md`
- [ ] D2 — Recommendations for when to create new specialist agents vs. extend existing ones
- [ ] D3 — Updated `.github/agents/README.md` with pattern documentation


---

## 7. Episodic and Experiential Memory for Agent Sessions

**Priority: Low** (deferred until scratchpad accumulation is confirmed as a bottleneck)

### Research Question
How should agents store and query *episodic* memory (past session events) and *experiential* memory (heuristics derived from outcomes) without cloud dependency?

### Why This Matters
Identified as a gap in `docs/research/agentic-research-flows.md` (Memory Architecture section). The project currently accumulates episodic records in scratchpad session files and git history, but there is no queryable layer — no "what did we learn about X in prior sessions?" lookup. Experiential memory is served only by the Copilot memory tool, which is external, ephemeral, and non-portable. This gap becomes acute once session history grows beyond what manual `_index.md` scanning can handle.

**Prerequisite:** Resolve OPEN_RESEARCH.md #1 (local compute) before evaluating embedding-based options.

### Resources to Survey
- [ ] mem0 — embedding-based long-term memory; https://github.com/mem0ai/mem0
- [ ] Letta (formerly MemGPT) — memory hierarchy for long-horizon agents; https://github.com/letta-ai/letta
- [ ] Zep/Graphiti — knowledge-graph temporal memory; https://github.com/getzep/graphiti
- [ ] Cognee — lighter knowledge-graph option; https://github.com/topoteretes/cognee
- [ ] AIGNE AFS memory modules (AFSHistory, FSMemory) — SQLite-backed, local-first; https://arxiv.org/abs/2512.05470
- [ ] `mei2025surveycontextengineeringlarge` — broader context engineering survey (not yet fetched)

### Gate Deliverables
- [ ] D1 — Comparison of local-capable episodic/experiential memory options
- [ ] D2 — Recommended approach given current session volume and local-compute constraints
- [ ] D3 — Script candidate specification (e.g., scratchpad deduplication or semantic search wrapper)

---

## 8. XML-Tagged Agent Instruction Format

**Priority: Very High** (affects every agent file; do before next major fleet expansion)

### Research Question
Should EndogenAI `.agent.md` files use XML-tagged section boundaries (`<section_name>...</section_name>`) instead of Markdown headings (`## Section Name`) for structuring agent instructions? What is the correct XML schema for agent instruction files, and what tools, scripts, or validators support it?

### Why This Matters
The Anthropic cookbook production agents use XML-tagged sections (`<research_process>`, `<delegation_instructions>`, `<subagent_count_guidelines>`) as section delimiters — not Markdown headings. XML tags are machine-unambiguous: they cannot be confused with prose, they parse without regex fallbacks, and they are the format the model has seen most in training for structured instruction following. Our current Markdown-heading format (`## Workflow`, `## Guardrails`) is less parsing-stable and may degrade instruction fidelity for long agent bodies.

Migrating all 15+ agent files is a significant engineering change. It should be fully researched and a migration script written before any file is touched. This cannot be done piecemeal — inconsistency between XML and Markdown formats within the fleet would be worse than either uniform format.

Flagged: 2026-03-06, from `docs/research/agentic-research-flows.md` addendum (Prompt Template and Handoff Format Findings section).

### Resources to Survey
- [ ] Anthropic cookbook agent source — `research_lead_prompt.py`, `research_subagent_prompt.py` — examine exact XML schema used; https://github.com/anthropics/anthropic-cookbook
- [ ] Claude prompt engineering docs — XML section format and recommended schema
- [ ] `.chatagent` format spec — does VS Code Copilot's `.chatagent` format support or prefer XML instruction bodies?
- [ ] Existing EndogenAI agent files — inventory current Markdown-heading section names to determine XML tag candidates
- [ ] Prior art: any XML-to-agent-md migration tooling in the wild

### What to Produce (Programmatic-First)
This research should produce, at minimum:
- [ ] A documented XML schema for EndogenAI agent instruction files (section tags, nesting rules, required vs. optional sections)
- [ ] A migration script: `scripts/migrate_agents_to_xml.py --dry-run` — converts Markdown headings to XML tags across all `.agent.md` files
- [ ] A validation script: `scripts/validate_agent_format.py` — checks each file for required sections, correct tag nesting, no mixed formats
- [ ] An updated `scaffold_agent.py` that emits XML-format stubs instead of Markdown-heading stubs

### Gate Deliverables
- [ ] D1 — Documented XML schema for agent instruction files with rationale
- [ ] D2 — `scripts/migrate_agents_to_xml.py` and `scripts/validate_agent_format.py` written and tested
- [ ] D3 — All 15+ agent files migrated (via script) and validated
- [ ] D4 — `scaffold_agent.py` updated to emit XML format
- [ ] D5 — `docs/guides/agents.md` and `.github/agents/AGENTS.md` updated with XML format documentation

---

## Issue #12 Follow-Up Open Questions (XML Agent Instruction Format)

Resolved: 2026-03-06. The following questions remain open after the primary research deliverable was completed.

**OQ-12-1 — Language Model API prompt pre-processing**
Does the VS Code Language Model API (the layer below the Chat Participant API) perform any prompt normalisation, caching, or XML-aware pre-processing before forwarding to the Claude endpoint? Target source: `code.visualstudio.com/api/extension-guides/ai/language-model`. Until confirmed, the conduit finding for XML pass-through is conditional on this layer.

**OQ-12-2 — Instruction-following fidelity: XML vs. plain Markdown (empirical)**
Design and run an ablation test using the Research Synthesizer agent in XML-hybrid form vs. its current plain-Markdown form. Measure: completion criteria satisfaction rate, constraint-violation rate, and section-addressing accuracy. Encode the comparison as a script. Results to be committed to `docs/research/`.

**OQ-12-3 — Non-Claude model XML degradation**
How do XML-tagged instruction bodies behave when routed to Ollama-hosted local models or GPT-family cloud models? Is there graceful degradation, neutral pass-through, or active interference with instruction parsing? Must be resolved before the `--model-scope` gate in ADAPT item B2 can be relaxed.

**OQ-12-4 — `handoffs: prompt:` field and XML**
Do YAML `handoffs: prompt:` field values benefit from or tolerate XML structuring when those prompts are complex multi-step instructions? Currently plain prose strings. May be relevant once orchestrator-tier agents are migrated and handoff prompts grow in complexity.

---

## Recommended Issue Execution Pairings

Recorded 2026-03-06. Group remaining open issues for efficiency — each pairing shares domain, sources, and guide deliverables.

| Session | Issues | Rationale |
|---|---|---|
| Infrastructure | #5 + #6 | Local compute (Ollama/LM Studio) + locally distributed MCP share source domains and feed `docs/guides/local-compute.md` |
| Cost/Reliability | #7 + #8 | Async process handling + LLM tier strategy are both reliability/cost concerns; small source sets benefit from batching |
| Memory (deferred) | #9 + #13 + #14 | Methodology lit review, episodic memory, and AIGNE AFS all have prerequisite on #5 (local compute resolved first) |

Issue #10 (agent fleet design patterns) is executed standalone — sources are mostly already cached and the deliverables include guide + README updates.
