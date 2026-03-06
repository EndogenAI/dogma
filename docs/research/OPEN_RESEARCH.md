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
- [ ] A2A (Agent-to-Agent) protocol patterns
- [ ] https://arxiv.org/html/2512.05470v1 (referenced in AccessiTech/EndogenAI#32)
- [ ] https://towardsdatascience.com/claude-skills-and-subagents-escaping-the-prompt-engineering-hamster-wheel/

### Gate Deliverables
- [ ] D1 — Agent fleet pattern catalog in `docs/guides/agents.md`
- [ ] D2 — Recommendations for when to create new specialist agents vs. extend existing ones
- [ ] D3 — Updated `.github/agents/README.md` with pattern documentation
