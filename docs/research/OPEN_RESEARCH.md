---
title: Open Research Tasks
status: Final
governs: [endogenous-first]
---

# Open Research Tasks

## 1. Executive Summary

This document tracks open research questions for the endogenic development methodology.
Each section corresponds to a GitHub Issue representing a discrete search for endogenous knowledge or external best practices.

## 2. Hypothesis Validation

The research tasks listed below test the viability of scaling the agent fleet while maintaining [MANIFESTO.md §3](../../MANIFESTO.md#3-local-compute-first) constraints.

## 3. Pattern Catalog

(No patterns defined in this aggregate document)

> **Action required**: Open each section below as a GitHub Issue in this repository using the
> [Research template](../../.github/ISSUE_TEMPLATE/research.yml). Labels: `research`.

---

## 1. Running VS Code Copilot Locally with Local Models

**Priority: High** (directly reduces token cost — Priority C from AccessiTech/EndogenAI#35)

### Research Question
How do we configure VS Code GitHub Copilot to use local LLM inference (Ollama, LM Studio, llama.cpp) instead of cloud APIs?

### Why This Matters
Cloud inference is expensive in tokens, money, and environmental impact. Running inference locally enables the **local-compute-first** principle ([MANIFESTO.md §3](../../MANIFESTO.md#3-local-compute-first)) and can significantly reduce per-session costs.

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
**Deliverable**: [`docs/research/agent-fleet-design-patterns.md`](./agents/agent-fleet-design-patterns.md)

Open follow-up questions are tracked in the **Issue #10 Follow-Up Open Questions** section below.


---

## 7. Episodic and Experiential Memory for Agent Sessions

**Status**: ✅ Research resolved 2026-03-10
**Deliverable**: [`docs/research/episodic-memory-agents.md`](./agents/episodic-memory-agents.md)

Cognee adoption follow-up tracked in [#131](https://github.com/EndogenAI/dogma/issues/131) — **deferred** pending local compute baseline (OPEN_RESEARCH.md #1).

---

## 8. XML-Tagged Agent Instruction Format

**Status**: ✅ Research resolved 2026-03-06 | **Implementation**: Partially complete
**Deliverable**: [`docs/research/xml-agent-instruction-format.md`](./agents/xml-agent-instruction-format.md)
**Script**: `scripts/migrate_agent_xml.py` (exists; fleet migration not yet run)

Open implementation questions tracked in **Issue #12 Follow-Up Open Questions** below.
Remaining implementation gate deliverables: D3 (fleet migration), D4 (scaffold_agent.py XML output), D5 (guide + AGENTS.md updates).

---

## Issue #12 Follow-Up Open Questions (XML Agent Instruction Format)

Resolved: 2026-03-06. The following questions remain open after the primary research deliverable was completed.

**OQ-12-1 — Language Model API prompt pre-processing**
✅ **RESOLVED 2026-03-07** — VS Code LM API confirmed as verbatim passthrough: `LanguageModelChatMessage.User(string)` forwards content unchanged to the model endpoint. No XML normalisation, caching, or transformation at any documented VS Code layer. Secondary finding: LM API does not support system messages — `.agent.md` bodies are injected as User-role messages. Source: `.cache/sources/code-visualstudio-com-api-extension-guides-ai-language-model.md`. Resolution committed to `docs/research/xml-agent-instruction-format.md`, issue #23 D1 closed.

**OQ-12-2 — Instruction-following fidelity: XML vs. plain Markdown (empirical)**
✅ **RESOLVED 2026-03-07** — Secondary evidence surveyed: Anthropic, OpenAI, and Google all prescribe XML structuring but provide no quantitative ablation data; Anthropic notes formatting "likely becoming less important as models become more capable" (moderate effect size). Ablation test protocol designed and documented in `docs/research/xml-agent-instruction-format.md` Section 9.2 (`scripts/eval_xml_fidelity.py` spec). Provisional finding: XML provides moderate, qualitative fidelity benefit for current-generation Claude models. See Section 9.

**OQ-12-3 — Non-Claude model XML degradation**
✅ **RESOLVED 2026-03-07** — Per-family verdicts: GPT (`gpt-*`, `openai/*`) — **beneficial** (OpenAI guide explicitly recommends Markdown+XML hybrid); Gemini (`google/gemini*`) — **beneficial** (Gemini 3 guide uses same XML tag vocabulary); Local models (`ollama/*`, `lmstudio/*`) — **neutral pass-through** (no XML-specific training; Markdown delimiters preferred); MistralAI API — **neutral provisional** (docs unreachable). `migrate_agent_xml.py --model-scope` can safely extend to `all-cloud` (`claude + gpt-* + google/gemini*`). Local model exclusion confirmed correct. See `docs/research/xml-agent-instruction-format.md` Section 10.

**OQ-12-4 — `handoffs: prompt:` field and XML**
✅ **RESOLVED 2026-03-09** — XML tags in `handoffs: prompt:` YAML values are preserved verbatim through YAML parsing (angle brackets are not YAML special characters). Injection path confirmed: handoff prompts enter the model as user-role messages, not concatenated into the agent body. XML is technically safe but **not recommended** for most handoff prompts — explicit Markdown branch templates (`**If approved:**` / `**If revise:**`) are preferred for UI clarity. XML is appropriate only when a handoff prompt contains a typed content block (`<examples>`, `<context>`, verbatim document excerpt). `migrate_agent_xml.py` should not transform `handoffs: prompt:` values. See `docs/research/xml-agent-instruction-format.md` Section 11.

---

## Issue #10 Follow-Up Open Questions (Agent Fleet Design Patterns)

Resolved: 2026-03-06. The following questions were resolved 2026-03-10.

**OQ-10-1 — Compression ratio by task type**
✅ **RESOLVED 2026-03-10** — The 1,000–2,000 token Anthropic figure is calibrated for research synthesis handoffs, not all task types. Precision-critical degradation onset: for code synthesis, when any function signature or API parameter is paraphrased (typically below ~2,000 tokens); for research, when secondary citations are dropped (typically below ~800 tokens). **Recommendation**: adopt task-type-differentiated ceilings. Task-type compression table appended to `docs/research/agent-fleet-design-patterns.md`. Sources: `agent-fleet-design-patterns.md` §6; Anthropic context engineering docs; ReAct paper.

| Task Type | Recommended Token Ceiling |
|---|---|
| Code synthesis (file-level) | 2,000–3,000 |
| Research synthesis handoff | 1,500–2,000 |
| Multi-source fact lookup | 1,500–2,500 |
| Evaluation/review feedback | 800–1,500 |
| Sequential planning / workplan update | 600–1,200 |
| Session/phase memory-write | 500–1,000 |

**OQ-10-2 — Minimal viable `.tmp/` scratchpad isolation without new infrastructure**
✅ **RESOLVED 2026-03-10** — Section-scoped writes (existing AGENTS.md convention) are **sufficient for sequential runs** (the standard case). Not validated for concurrent parallel runs — `agent-fleet-design-patterns.md` §7 explicitly identifies write concurrency as unresolved. **Recommendation**: keep existing section-naming convention for sequential runs; escalate to per-agent separate files (`<agent>-<date>.md`) for parallel runs — naming convention change only, no new script required. Sources: `agent-fleet-design-patterns.md` §7; `AGENTS.md` Agent Communication; Claude Code agent-teams guidance (file-level ownership as minimum concurrent isolation).

**OQ-10-3 — Evaluator-optimizer convergence criteria for synthesis tasks**
✅ **RESOLVED 2026-03-10** — LLM-as-judge is reliable for narrow, explicitly-specified structural checks; unreliable for open-ended quality (consistent with `llm-behavioral-testing.md` H1, H4). **Three concrete stopping conditions for the Reviewer agent on synthesis documents:**
1. **Structural gate (hard)**: `validate_synthesis.py` exits 0 — required sections, `status: Final`, ≥ 100 lines
2. **Gap-acknowledgment gate (Reviewer-checked)**: `## Critical Assessment` names ≥ 1 specific limitation or open question (not a generic disclaimer)
3. **Iteration ceiling (deadlock prevention)**: After 2 feedback rounds with unresolved failures, escalate to Executive + ship with named gaps in Critical Assessment — never loop a third time
Sources: `llm-behavioral-testing.md` H1, H4; `agent-fleet-design-patterns.md` Pattern 2; `review.agent.md`; Anthropic "Building effective agents."

---

## Research Sprint — VS Code Agent Format & Toolset Best Practices

**Added**: 2026-03-07 | **Status**: ✅ D1 resolved 2026-03-07 (b26d188); D2/D3 resolved 2026-03-07 | **Priority**: Medium | **Closes**: [#23](https://github.com/EndogenAI/dogma/issues/23)

Deep dive on VS Code Copilot custom agent file format: toolset declarations (which tools map to which capabilities), `applyTo` glob patterns, the VS Code Language Model API layer, instruction-following fidelity between XML and Markdown bodies (OQ-12-2), and non-Claude model degradation (OQ-12-3). Closes remaining open questions from issue #12.

**Target deliverable**: Append findings to [`docs/research/xml-agent-instruction-format.md`](./agents/xml-agent-instruction-format.md) or create `docs/research/vscode-agent-format.md`
**GitHub issue**: [#23](https://github.com/EndogenAI/dogma/issues/23)
**Prerequisite**: Resolves OQ-12-1, OQ-12-2, OQ-12-3 from Issue #12 Follow-Up Open Questions above

---

## Research Sprint — Context Compaction Best Practices (VS Code Copilot /compact)

**Added**: 2026-03-07 | **Status**: ✅ Complete 2026-03-07 | **Priority**: High | **Closes**: [#24](https://github.com/EndogenAI/dogma/issues/24)

Research and document best practices for VS Code Copilot Chat's `/compact` slash command and "Compact Conversation" context window button.

**Deliverable**: `docs/guides/session-management.md` — [Context Compaction section](../guides/session-management.md#context-compaction)
**Encoded in**: All three `AGENTS.md` files (compaction-aware writing guardrail + `gh --body-file` guardrail)

---

## Research Sprint — Copilot PR Review Automation

**Added**: 2026-03-07 | **Status**: ✅ Complete 2026-03-07 | **Priority**: High | **Closes**: [#29](https://github.com/EndogenAI/dogma/issues/29)

Research whether requests for GitHub Copilot PR reviews can be triggered programmatically (REST API, `gh` CLI, GraphQL, GitHub Actions, CODEOWNERS). Primary finding: no public API exists for per-PR bot reviewer requests. The only supported automation path is a repository ruleset gated on GitHub Pro or a public repo. Manual re-request via UI is the correct baseline until then.

**Target deliverable**: [`docs/research/copilot-pr-review-automation.md`](./infrastructure/copilot-pr-review-automation.md)
**GitHub issue**: [#29](https://github.com/EndogenAI/dogma/issues/29)

---

## Research Sprint — GitHub as Episodic & Long-term Memory Substrate

**Added**: 2026-03-07 | **Status**: ✅ Complete 2026-03-07 | **Priority**: High | **Closes**: [#30](https://github.com/EndogenAI/dogma/issues/30)

Research whether GitHub Issues, PRs, commits, and Projects can serve as a structured episodic memory layer for the agent fleet. Finding: GitHub is a viable episodic tier — issues and commit log are queryable via `gh` CLI and GraphQL at practical rate limits. Not a semantic or working memory replacement. Four-tier memory architecture defined with GitHub occupying the episodic slot. Complements (but does not replace) the external memory research in Issue #7/#13.

**Target deliverable**: [`docs/research/github-as-memory-substrate.md`](./infrastructure/github-as-memory-substrate.md)
**GitHub issue**: [#30](https://github.com/EndogenAI/dogma/issues/30)

---

## Completed Research

_Items below are resolved. Open follow-up questions are still tracked in the main body (OQ-10, OQ-12 sections)._

| Issue | Title | Deliverable | Closed |
|---|---|---|---|
| [#2](https://github.com/EndogenAI/dogma/issues/2) | Research and document detailed agent workflows | [`agentic-research-flows.md`](./agents/agentic-research-flows.md) | 2026-03-07 |
| [#10](https://github.com/EndogenAI/dogma/issues/10) | Agent Fleet Design Patterns | [`agent-fleet-design-patterns.md`](./agents/agent-fleet-design-patterns.md) | 2026-03-06 |
| [#12](https://github.com/EndogenAI/dogma/issues/12) | XML-Tagged Agent Instruction Format _(implementation in progress)_ | [`xml-agent-instruction-format.md`](./agents/xml-agent-instruction-format.md) | 2026-03-06 |
| [#13](https://github.com/EndogenAI/dogma/issues/13) | Episodic and Experiential Memory for Agent Sessions | [`episodic-memory-agents.md`](./agents/episodic-memory-agents.md) | 2026-03-10 |
| [#14](https://github.com/EndogenAI/dogma/issues/14) | AIGNE AFS Context Governance Layer Evaluation | [`aigne-afs-evaluation.md`](./agents/aigne-afs-evaluation.md) | 2026-03-10 |
| [#16](https://github.com/EndogenAI/dogma/issues/16) | Testing Tools & Frameworks | [`testing-tools-and-frameworks.md`](./infrastructure/testing-tools-and-frameworks.md) | 2026-03-07 |
| [#17](https://github.com/EndogenAI/dogma/issues/17) | Development Workflow Automations | [`dev-workflow-automations.md`](./infrastructure/dev-workflow-automations.md) | 2026-03-07 |
| [#18](https://github.com/EndogenAI/dogma/issues/18) | OSS Documentation Best Practices | [`oss-documentation-best-practices.md`](oss-documentation-best-practices.md) | 2026-03-07 |
| [#19](https://github.com/EndogenAI/dogma/issues/19) | PM & Dev Team Structures | [`pm-and-team-structures.md`](./pm/pm-and-team-structures.md) | 2026-03-07 |
| [#20](https://github.com/EndogenAI/dogma/issues/20) | Product Research & Design _(seed)_ | [`product-research-and-design.md`](./pm/product-research-and-design.md) | 2026-03-07 |
| [#21](https://github.com/EndogenAI/dogma/issues/21) | Comms, Marketing & Bizdev _(seed)_ | [`comms-marketing-bizdev.md`](./pm/comms-marketing-bizdev.md) | 2026-03-07 |
| [#22](https://github.com/EndogenAI/dogma/issues/22) | GitHub Project Management & Automation | [`github-project-management.md`](./pm/github-project-management.md) | 2026-03-07 |
| [#24](https://github.com/EndogenAI/dogma/issues/24) | Context Compaction Best Practices | [`session-management.md#context-compaction`](../guides/session-management.md) | 2026-03-07 |
| [#72](https://github.com/EndogenAI/dogma/issues/72) | Context-sensitive axiom amplification (OQ-VE-2) | [`epigenetic-tagging.md`](./methodology/epigenetic-tagging.md) | 2026-03-10 |
| [#74](https://github.com/EndogenAI/dogma/issues/74) | LLM behavioral testing for value fidelity (OQ-VE-4) | [`llm-behavioral-testing.md`](./models/llm-behavioral-testing.md) | 2026-03-10 |
| [#76](https://github.com/EndogenAI/dogma/issues/76) | XML structuring in `handoffs.prompt` fields (OQ-12-4) | [`xml-agent-instruction-format.md`](./agents/xml-agent-instruction-format.md) §11 | 2026-03-10 |
| [#83](https://github.com/EndogenAI/dogma/issues/83) | Encoding external product/client values — layered value architecture | [`external-value-architecture.md`](./methodology/external-value-architecture.md) | 2026-03-10 |
