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

**Status**: ✅ Resolved 2026-03-06
**Deliverable**: [`docs/research/agent-fleet-design-patterns.md`](agent-fleet-design-patterns.md)

Open follow-up questions are tracked in the **Issue #10 Follow-Up Open Questions** section below.


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

**Status**: ✅ Research resolved 2026-03-06 | **Implementation**: Partially complete
**Deliverable**: [`docs/research/xml-agent-instruction-format.md`](xml-agent-instruction-format.md)
**Script**: `scripts/migrate_agent_xml.py` (exists; fleet migration not yet run)

Open implementation questions tracked in **Issue #12 Follow-Up Open Questions** below.
Remaining implementation gate deliverables: D3 (fleet migration), D4 (scaffold_agent.py XML output), D5 (guide + AGENTS.md updates).

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

## Issue #10 Follow-Up Open Questions (Agent Fleet Design Patterns)

Resolved: 2026-03-06. The following questions remain open after the primary research deliverable was completed.

**OQ-10-1 — Compression ratio by task type**
What task-type-specific compression ratios should be used at handoff boundaries? The 1,000–2,000 token figure is Anthropic's guideline stated without benchmark. At what compression level does precision-critical context (exact syntax in code synthesis) begin to degrade downstream output quality?

**OQ-10-2 — Minimal viable `.tmp/` scratchpad isolation without new infrastructure**
Section-scoped writes are proposed as the isolation mechanism, enforced through instruction conventions only. What is the minimum viable enforcement mechanism that prevents lateral context bleed without requiring new script infrastructure? Has agent-instruction-only enforcement been validated against multi-agent parallel runs?

**OQ-10-3 — Evaluator-optimizer convergence criteria for synthesis tasks**
The evaluator-optimizer loop specifies mandatory stopping conditions but does not define them for synthesis (as opposed to code). How reliable is LLM-as-judge evaluation for research synthesis documents, and what constitutes a well-formed stopping condition for the Reviewer agent?

---

## Research Sprint — Testing Tools & Frameworks

**Added**: 2026-03-07 | **Status**: ✅ Complete 2026-03-07 | **Closes**: #16

**Deliverable**: [`docs/research/testing-tools-and-frameworks.md`](testing-tools-and-frameworks.md)

---

## Research Sprint — Development Workflow Automations

**Added**: 2026-03-07 | **Status**: ✅ Complete 2026-03-07 | **Closes**: #17

**Deliverable**: [`docs/research/dev-workflow-automations.md`](dev-workflow-automations.md)

---

## Research Sprint — Open-Source Documentation Best Practices

**Added**: 2026-03-07 | **Status**: ✅ Complete 2026-03-07 | **Closes**: #18

**Deliverable**: [`docs/research/oss-documentation-best-practices.md`](oss-documentation-best-practices.md)

---

## Research Sprint — Project Management & Dev Team Structures

**Added**: 2026-03-07 | **Status**: ✅ Complete 2026-03-07 | **Closes**: #19

**Deliverable**: [`docs/research/pm-and-team-structures.md`](pm-and-team-structures.md)

---

## Research Seed — Product Research & Design Methodologies

**Added**: 2026-03-07 | **Status**: ✅ Complete (seed) 2026-03-07 | **Closes**: #20

**Deliverable**: [`docs/research/product-research-and-design.md`](product-research-and-design.md)
**Note**: Seed pass only. Full sprint open — see Open Questions in deliverable doc.

---

## Research Seed — Comms, Marketing & Business Development

**Added**: 2026-03-07 | **Status**: ✅ Complete (seed) 2026-03-07 | **Closes**: #21

**Deliverable**: [`docs/research/comms-marketing-bizdev.md`](comms-marketing-bizdev.md)
**Note**: Seed pass only. Full sprint open — see Open Questions in deliverable doc.

---

## Research Sprint — GitHub Project Management & Automation

**Added**: 2026-03-07 | **Status**: Complete | **Priority**: High

GitHub as the primary coordination interface for humans, Copilot agents, and automation. Focus: GitHub Projects v2 (board setup, field types, automation rules), `gh` CLI patterns for issue/PR management, structured label taxonomy, issue template schema (YAML frontmatter), Discussions API, GitHub Actions for PM automation (auto-label, auto-assign, stale bot), Milestones API, and how Copilot reads issue/PR context in agent sessions.

This research should be **fetched and cached locally** — the GitHub docs are a primary query source for agents and automation scripts.

**Target deliverable**: `docs/research/github-project-management.md`
**GitHub issue**: TBD

### Resources to fetch and cache
- https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/about-projects
- https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/using-the-api-to-manage-projects
- https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/managing-labels
- https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms
- https://docs.github.com/en/discussions
- https://cli.github.com/manual/gh_project
- https://cli.github.com/manual/gh_issue
- https://docs.github.com/en/actions/writing-workflows/choosing-when-your-workflow-runs/events-that-trigger-workflows

### Gate Deliverables
- [x] D1 — All 8 sources fetched and cached in `.cache/sources/`
- [x] D2 — `docs/research/github-project-management.md` (Status: Final)
- [x] D3 — Actionable setup checklist for this repo (Projects board, label taxonomy, issue templates, Discussions)
- [x] D4 — `gh` CLI quick-reference embedded in the synthesis doc

---

## Research Sprint — VS Code Agent Format & Toolset Best Practices

**Added**: 2026-03-07 | **Status**: Open | **Priority**: Medium

Deep dive on VS Code Copilot custom agent file format: toolset declarations (which tools map to which capabilities), `applyTo` glob patterns, the VS Code Language Model API layer, instruction-following fidelity between XML and Markdown bodies (OQ-12-2), and non-Claude model degradation (OQ-12-3). Closes remaining open questions from issue #12.

**Target deliverable**: Append findings to [`docs/research/xml-agent-instruction-format.md`](xml-agent-instruction-format.md) or create `docs/research/vscode-agent-format.md`
**GitHub issue**: TBD
**Prerequisite**: Resolves OQ-12-1, OQ-12-2, OQ-12-3 from Issue #12 Follow-Up Open Questions above
