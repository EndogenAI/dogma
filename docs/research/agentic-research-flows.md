---
title: Agentic Research Flows
status: "Final (addendum 2026-03-06)"
date: 2026-03-06
date_updated: 2026-03-06
sources:
  - https://www.anthropic.com/engineering/building-effective-agents
  - https://www.anthropic.com/engineering/claude-research-system
  - https://towardsdatascience.com/claude-skills-and-subagents
  - https://arxiv.org/abs/2512.05470
  - https://arxiv.org/abs/2304.03442
  - https://arxiv.org/abs/2210.03629
source_syntheses:
  - sources/anthropic-building-effective-agents.md
  - sources/arxiv-context-engineering-survey.md
  - sources/arxiv-org-html-2512-05470v1.md
  - sources/claude-code-agent-teams.md
  - sources/claude-sdk-subagents.md
  - sources/cookbook-research-lead-agent.md
  - sources/cookbook-research-subagent.md
  - sources/arxiv-react.md
  - sources/a2a-announcement.md
  - sources/tds-claude-skills-subagents.md
  - sources/arxiv-generative-agents.md
  - sources/cookbook-citations-agent.md
  - sources/freecodecamp-org-news-build-and-deploy-multi-agent-ai-with-p.md
  - sources/github-com-getzep-graphiti.md
  - sources/github-com-letta-ai-letta.md
  - sources/github-com-mem0ai-mem0.md
  - sources/github-com-topoteretes-cognee.md
  - sources/kdnuggets-com-docker-ai-for-agent-builders-models-tools-and-.md
  - sources/lmstudio-ai.md
  - sources/ollama-ai.md
  - sources/opensourceprojects-dev-post-e7415816-a348-4936-b8bd-0c651c4a.md
  - sources/xda-developers-com-youre-using-local-llm-wrong-if-youre-prom.md
  - sources/session-synthesis-2026-03-06-a.md
---

# Agentic Research Flows

> **Status**: Final (addendum 2026-03-06)
> **Research Question**: How do multi-agent systems architect context, orchestration, memory, and tool use for effective research — and what patterns can be directly applied to this project?
> **Date**: 2026-03-06

---

## Executive Summary

The literature converges on a small set of durable patterns — orchestrator-workers, evaluator-optimizer loops, tiered memory, and lazy context loading — that are well-validated at production scale. Our current fleet design is broadly correct: the self-loop phase gate maps directly to the evaluator-optimizer pattern, our scratchpad satisfies the ephemeral working memory role, and git history covers the immutable audit trail. The primary gaps are (1) no semantic retrieval layer over episodic/experiential memory, (2) agent prompt files that lack explicit completion criteria and example outputs, and (3) a context loading strategy that pays full cost at session start rather than on demand. The most actionable near-term intervention is a skills-manifest script that enables lazy loading of agent metadata — estimated at a significant token reduction with no new dependencies. The longer-term architectural opportunity is an Agentic File System (AFS) layer, but that should be deferred until the local-compute-first baseline is stable.

---

## Orchestration Patterns

The Anthropic multi-agent research system and the broader five-pattern taxonomy from *Building Effective Agents* draw a consistent picture of how capable systems are structured.

The five patterns — **prompt chaining, routing, parallelization, orchestrator-workers, and evaluator-optimizer** — are not alternatives but a composable vocabulary. Our fleet uses all five, though not always by design. The executive→sub-agent→specialist hierarchy is an orchestrator-workers instance. The review-before-commit phase is an evaluator-optimizer loop. Recognising these as established patterns matters because it means the design is validated, not novel, and we should lean into their documented properties rather than re-derive them.

The **evaluator-optimizer loop** deserves explicit naming: in the literature this is the pattern our self-loop phase gate implements. We should call it that in documentation — it signals intent to future contributors and anchors the design to a body of prior art.

The **15× token multiplier** for multi-agent research (approximately 180K tokens per research query versus 12K for single-agent chat) is not a flaw — it is the cost structure of the architecture. Decisions about when to spawn parallel workers must account for this. Token usage explains approximately 80% of output quality variance in the Anthropic system; throwing more tokens at parallelism is the primary quality lever, which means our local-compute-first principle directly constrains how ambitiously we can parallelize.

The **lightweight context handoff** strategy from the Anthropic system — summarise completed phases, store in external memory, spawn fresh subagents with references rather than full content — is the direct theoretical basis for our scratchpad and `.tmp/` branch folders. Our design is correct. The scratchpad's `## Session Summary` convention implements this handoff; the `_index.md` stub file implements the reference layer. This should be documented explicitly in `docs/guides/session-management.md` so future contributors understand why the convention exists.

ReAct's interleaved Thought→Act→Observation trace confirms the value of explicit reasoning steps before and after each action. Our agents do not currently require or enforce this trace. It is worth encoding as a prompt principle in agent files for research-phase tasks where hallucination risk is elevated.

**Empirical validation — per-invocation context isolation (2026-03-06 session)**: running a Synthesizer across all 22 sources in a single invocation was found to produce context rot — fidelity to early sources degraded by the time the model reached later ones. Isolating each invocation to one source eliminated that degradation. This is the same principle as test isolation applied to synthesis, and it independently confirms the quasi-encapsulated sub-fleet posture: any design that allows implicit context inheritance across agent boundaries should be treated as a regression, not an optimisation. See [session-synthesis-2026-03-06-a](sources/session-synthesis-2026-03-06-a.md) for the first-person account.

---

## Memory Architecture

The seven-type memory hierarchy from arXiv 2512.05470v1 provides a useful audit lens for our current substrate. The mapping is closer than expected:

| Memory Type | Our Substrate | Assessment |
|---|---|---|
| **Scratchpad** | `.tmp/<branch>/<date>.md` | ✅ Satisfied |
| **Procedural** | `.github/agents/*.agent.md` + `docs/guides/` | ✅ Satisfied |
| **Fact** | `docs/` content, `AGENTS.md`, `MANIFESTO.md` | ✅ Partially satisfied — no structured retrieval |
| **Historical Record** | `git log` | ✅ Satisfied — immutable, auditable |
| **User** | Not applicable (single-operator repo) | — Not required |
| **Episodic** | Scratchpad session files | ⚠️ Present but not queryable |
| **Experiential** | `repository_memories` (Copilot memory tool) | ⚠️ External, non-portable, shallow |

The two meaningful gaps are **episodic** and **experiential** memory. We accumulate episodic records in scratchpad session files and git history, but there is no mechanism to query across them semantically — no "what did we learn about X in prior sessions?" lookup. Experiential memory (heuristics derived from past outcomes) is partially served by the Copilot memory tool, but this is external, ephemeral, and not portable across agents or sessions.

These gaps are real but not urgent. The current session-by-session scratchpad discipline, combined with the `_index.md` stub archive, is a functional episodic retrieval mechanism for most practical purposes. The gap becomes acute only when sessions accumulate enough history that manual index scanning becomes a bottleneck — likely beyond the current scale of the project.

**Write discipline is the deeper problem.** The queryability gap is secondary. Live session experience (see [session-synthesis-2026-03-06-a](sources/session-synthesis-2026-03-06-a.md)) confirmed that when agents skip writing to `.tmp/`, the next agent starts blind — scout outputs existed only in the conversation summary and had to be reconstructed at cost. The scratchpad is the only durable cross-agent memory that survives a context window boundary. Process compliance requires mechanical enforcement, not just documentation; the write-back requirement was subsequently encoded into `executive-researcher.agent.md`.

A semantic retrieval layer (e.g., mem0 or an embedded vector store over scratchpad files) would close both gaps. This should be treated as a D3 investigation item, not an immediate action.

---

## Prompt Engineering Principles

Anthropic's eight prompt engineering principles for agents (from *Building Effective Agents*) provide a direct audit framework for our `.agent.md` format. Current state:

| Principle | Our Agent Files | Status |
|---|---|---|
| 1. Clear, narrow role definition | `## Role` section in frontmatter | ✅ Present |
| 2. Explicit tool list | `tools:` frontmatter key | ✅ Present |
| 3. Explicit completion criteria (when to stop) | Not present | ❌ Missing |
| 4. Minimal context; strip irrelevant history | Partially — session scope not enforced | ⚠️ Partial |
| 5. Decompose before delegating | Documented in `AGENTS.md` | ⚠️ Principle only, not enforced in agent files |
| 6. Structured output for agent-to-agent comms | Scratchpad headings provide loose structure | ⚠️ Informal |
| 7. Examples of good vs. bad outputs | Absent from all agent files | ❌ Missing |
| 8. Explicit instructions over implicit role defaults | Variable; some agents rely on role name conventions | ⚠️ Inconsistent |

The two sharpest gaps are **completion criteria** (principle 3) and **output examples** (principle 7). These are low-cost additions to existing agent files that would meaningfully reduce ambiguous agent behaviour. Each agent file should gain a `## Completion Criteria` section and at least one annotated output example. This is a task for the Executive Docs agent, not this synthesis.

The Claude Skills progressive disclosure pattern (TDS) also implies that the current agent prompt structure — loading full `.agent.md` bodies at session start — is unnecessarily expensive. See Token Offloading below.

---

## Token Offloading

The most applicable near-term token reduction technique requires no new dependencies: the **Claude Skills lazy-loading pattern** from TDS.

Currently, any session that needs to reference agent capabilities must either load full `.agent.md` bodies (expensive) or rely on an agent knowing the fleet from training (unreliable). The Skills pattern solves this with a three-level disclosure model: (1) ~100-token metadata stub always available, (2) full instructions loaded on invocation, (3) referenced files loaded only when instructions require them.

We can implement level 1 today with a script (D5 candidate #3 — agent skills manifest generator) that enumerates `.github/agents/` and emits a JSON manifest of name, description, and capability tags for each agent. This manifest (~100 tokens per agent) becomes the default context payload for the orchestrator; full agent bodies are referenced by path and loaded only when that agent is invoked. No new infrastructure required.

**AIGNE AFS** (Agentic File System with SQLite + vector backend + MCP integration) is the longer-term architectural option most aligned with local-compute-first. It provides the context governance layer — write, select, compress, isolate — that our scratchpad implements manually today. It should be evaluated after the local-compute baseline (OPEN_RESEARCH.md #1) is stable; adopting it before that would add complexity against an uncertain inference backend.

**mem0 and Letta** are heavier dependencies that address the episodic/experiential memory gap identified in Memory Architecture. Table for a dedicated D4 evaluation once the scratchpad accumulation problem is confirmed at scale.

**Zep/Graphiti and Cognee** were surveyed as additional candidates. Zep/Graphiti provides temporal knowledge-graph-based memory — useful for relational memory over time but a heavier dependency than our current needs warrant. Cognee is a lighter knowledge-graph option with similar tradeoffs. Both are deferred alongside mem0/Letta pending confirmation of the episodic memory bottleneck; neither offers a clear advantage over the simpler scratchpad approach at current session volume.

**Token cost scales with re-discovery.** Each time an agent re-fetches a URL, re-reads a source, or re-frames a research question that was previously answered, tokens are wasted proportionally. The fetch-before-act posture, scratchpad pre-warming, per-source synthesis isolation, and the agent manifest generator all reduce re-discovery cost — they are not independent conveniences but expressions of a single underlying principle. The programmatic-first constraint in `AGENTS.md` is ultimately a token economics principle: encoding repeated tasks as scripts is the mechanism by which re-discovery cost is driven toward zero. See [session-synthesis-2026-03-06-a](sources/session-synthesis-2026-03-06-a.md) for the first-person validation of this pattern across a full session.

---

## Script Candidates

Six scripts were identified from the Scout findings. Priority order, with rationale:

1. **Agent skills manifest generator** — Enumerate `docs/` and `.github/agents/` files; emit a JSON manifest (name, description, tags, ~100 tokens per agent). Enables lazy-loading pattern immediately. Highest ROI, no dependencies, purely additive. *(Source: TDS Skills pattern)*

2. **Session checkpoint serializer** — Pre-serialize research plan + session state to a structured JSON checkpoint before context window overflow risk. Enables resume-from-checkpoint for long-running research sessions. Critical for sessions that approach the context limit without natural breakpoints. *(Source: Anthropic multi-agent context management)*

3. **Context manifest builder** — Assemble context from scratchpad + docs + prior session stubs into a JSON manifest at session start. Implements the LangChain four-stage context engineering loop (write → select → compress → isolate) as a pre-computation step. *(Source: arXiv 2512.05470v1, which cites this pattern; see also `mei2025surveycontextengineeringlarge` — not yet fetched — for fuller treatment and likely primary attribution)*

4–6 require additional evaluation before committing:

4. **Tool metadata token counter** — Compute total tool metadata token cost for any agent configuration. Useful for optimization but requires understanding our actual MCP tool inventory first. *(Source: TDS ~32K token observation)*

5. **Scratchpad deduplication script** — Cluster scratchpad entries by semantic similarity, prune near-duplicates. Depends on having a local embedding model available; premature without OPEN_RESEARCH.md #1 resolved. *(Source: arXiv 2512.05470v1 memory deduplication)*

6. **Evaluation rubric pre-builder** — Pre-build evaluation rubric files per research topic as cached artifacts. Useful for formalising the evaluator-optimizer loop, but the evaluator pattern needs to be more consistently used before rubric pre-building adds value. *(Source: Anthropic multi-agent LLM-as-judge pattern)*

Scripts 1–3 are ready to specify as issues. Scripts 4–6 should be revisited after their prerequisite gaps are closed.

---

## Gaps and Follow-Up Leads

- **Anthropic cookbook agent examples** — basic workflow patterns not yet fetched; likely contains directly applicable prompt templates. (https://platform.claude.com/cookbook/patterns-agents-basic-workflows)
- **ReAct project code** — the paper describes the pattern; the reference implementation may contain prompt templates directly usable in agent files. (https://react-lm.github.io/)
- **AIGNE AFS evaluation** — the AFS module is the strongest candidate for a context governance layer; needs a focused evaluation against our MCP setup. (https://github.com/AIGNE-Project/aigne-framework)
- **Anthropic Agent Teams for Opus 4** — impacts quasi-encapsulation design; if Agent Teams formalises multi-agent coordination at the API level, it may change how we think about executive→subagent delegation.
- **Google A2A Protocol readiness** — not assessed; relevant if we evaluate cross-provider agent coordination.
- **`mei2025surveycontextengineeringlarge`** — broader context engineering survey not fetched; likely covers the LangChain four-stage pattern and alternatives in more depth.
- **arXiv 2304.03442 identity confirmation** — confirmed as Generative Agents (Park et al.), not ReAct. ReAct is 2210.03629. Update any internal references that conflate these.
- **Episodic/experiential memory gap** — the memory architecture section identifies this as real but non-urgent; it should be added to OPEN_RESEARCH.md as a new topic once the local-compute baseline is resolved.

---

## Applicability to This Project

Immediate actions — warranted now, low risk, no new dependencies:

1. **Add `## Completion Criteria` to all agent files.** This is the highest-leverage prompt engineering improvement available. An agent that does not know when it is done will either under-deliver or over-run. Assign to Executive Docs.

2. **Script the agent skills manifest generator (D5 #1).** One script, one JSON output, immediate reduction in context loading cost. Assign to Executive Scripter.

3. **Rename the self-loop phase gate to "evaluator-optimizer loop" in documentation.** Purely a documentation change; establishes shared vocabulary with the broader literature and signals design intent. Assign to Executive Docs.

Defer with a tracking note in OPEN_RESEARCH.md:

4. **AIGNE AFS evaluation** — deferred until OPEN_RESEARCH.md #1 (local compute) is closed. Adding a context governance layer before the inference backend is stable is premature.

5. **Semantic memory layer (mem0/Letta)** — deferred until scratchpad accumulation is confirmed as a bottleneck. The current manual approach is adequate at current scale.

6. **Output examples in agent files** — desirable but lower priority than completion criteria. Can be added incrementally as agents are edited for other reasons.

The architecture does not require structural changes — the existing hierarchy, scratchpad conventions, and procedural memory in agent files are all well-grounded in the literature. What is warranted is a discipline pass on existing agent files and a small number of targeted scripts. This is evolutionary improvement, not redesign.

---

## Sources

1. Anthropic Engineering — Building Effective Agents. https://www.anthropic.com/engineering/building-effective-agents
2. Anthropic Engineering — Claude Multi-Agent Research System. https://www.anthropic.com/engineering/claude-research-system
3. Towards Data Science — Claude Skills and Subagents. https://towardsdatascience.com/claude-skills-and-subagents
4. arXiv 2512.05470v1 — Everything is Context: Agentic File System (AIGNE). https://arxiv.org/abs/2512.05470
5. arXiv 2304.03442 — Generative Agents: Interactive Simulacra of Human Behavior (Park et al.). https://arxiv.org/abs/2304.03442
6. arXiv 2210.03629 — ReAct: Synergizing Reasoning and Acting in Language Models (Yao et al.). https://arxiv.org/abs/2210.03629

---

## Addendum — Follow-Up Scout Findings

_Added 2026-03-06 following round-2 scout re-runs (Scout A: prompt templates and handoff formats, Scout B: AIGNE AFS and Agent Teams, Scout C: A2A and Mei et al. context engineering survey)._

---

### Attribution Correction — AIGNE Context Engineering Pattern

**The original synthesis contained an error that must be corrected.**

**OLD (incorrect):**
> "AIGNE introduces the write/select/compress/isolate four-stage pattern"

**CORRECT:**
The write/select/compress/isolate four-stage pattern is **LangChain's industrial practice**, cited in the AIGNE paper as `[LangChainContextEngineering2024]`. This is confirmed by both the AIGNE paper itself and the Mei et al. context engineering survey ([arxiv-context-engineering-survey](sources/arxiv-context-engineering-survey.md)).

**AIGNE's actual contribution** is the **Context Engineering Pipeline**:
- **Context Constructor**: selects and compresses context from the AFS repository; produces a JSON manifest with selected files, compressed representations, and relevance scores.
- **Context Updater** (three modes): Static Snapshot (full recompute), Incremental Streaming (delta updates), Adaptive Refresh (confidence-triggered refresh).
- **Context Evaluator**: validates outputs before committing to AFS; writes back with lineage metadata (`createdAt`, `sourceId`, `confidence`, `revisionId`); triggers human review when confidence falls below a configurable threshold.

**Also**: the correct AIGNE GitHub repository URL is `https://github.com/AIGNE-io/aigne-framework` — not the `AIGNE-Project` organisation referenced earlier.

---

### AIGNE Memory Taxonomy

The AIGNE paper (see [arxiv-org-html-2512-05470v1](sources/arxiv-org-html-2512-05470v1.md)) enumerates seven memory types with distinct persistence scopes:

| Memory Type | Persistence Scope |
|---|---|
| **Scratchpad** | Ephemeral — single reasoning step |
| **Episodic** | Session-scoped — task or conversation |
| **Fact** | Long-term — explicit factual claims |
| **Experiential** | Long-term — heuristics from outcomes |
| **Procedural** | Long-term — how-to knowledge |
| **User** | Long-term — user-specific preferences |
| **Historical Record** | Immutable — append-only audit trail |

The mapping of this taxonomy to the EndogenAI substrate (original synthesis, Memory Architecture section) remains valid. OPEN gap: Episodic and Experiential types are partially satisfied but not queryable.

---

### Comprehension-Generation Gap (Mei et al.)

The Mei et al. survey (arXiv:2507.13334, see [arxiv-context-engineering-survey](sources/arxiv-context-engineering-survey.md)) identifies a critical finding not captured in the original synthesis:

> "our survey not only establishes a technical roadmap for the field but also reveals a critical research gap: a fundamental asymmetry exists between model capabilities. While current models, augmented by advanced context engineering, demonstrate remarkable proficiency in understanding complex contexts, they exhibit pronounced limitations in generating equally sophisticated, long-form outputs. Addressing this gap is a defining priority for future research."

**Implication for EndogenAI**: the evaluator-optimizer loop is not merely a quality gate — it is the correct architectural response to the comprehension-generation gap. Structuring output generation as iterative evaluation (generate → evaluate → refine) compensates for models' relative weakness at long-form generation. This retroactively strengthens the case for the self-loop phase gate design and argues for making the loop more explicit rather than optional.

---

### A2A Protocol Findings

See [a2a-announcement](sources/a2a-announcement.md) for the full stub. Key additions to the original synthesis:

- **Agent Cards** are JSON documents advertising agent capabilities — the formal mechanism for capability discovery in a multi-agent network. `generate_agent_manifest.py` produces a structurally analogous artefact, but with a different purpose: it is a static CI context-loading artifact, not a live service-discovery document. A future A2A-compatible extension to the manifest would need to add endpoint URLs, authentication schemes, and task lifecycle fields.
- **Protocol stack**: HTTP + SSE + JSON-RPC — explicitly designed for enterprise IT stacks and air-gapped/local deployment.
- **MCP relationship confirmed**: "A2A complements Anthropic's Model Context Protocol (MCP), which provides helpful tools and context to agents." MCP governs agent↔tool interactions; A2A governs agent↔agent coordination. These are complementary layers, not competing standards.
- A2A has production commitment from 50+ technology and services partners including Salesforce, ServiceNow, Anthropic, and major consulting firms.
- Full A2A spec (endpoint paths, Agent Card JSON schema) requires fetching the `google/A2A` GitHub repository — not yet cached.

---

### Prompt Template and Handoff Format Findings

From Scout A analysis of Anthropic cookbook agents (see [cookbook-research-lead-agent](sources/cookbook-research-lead-agent.md) and [cookbook-research-subagent](sources/cookbook-research-subagent.md)):

- **XML over Markdown**: Anthropic cookbook agents use XML-tagged sections (`<research_process>`, `<delegation_instructions>`, `<subagent_count_guidelines>`) as section boundaries — machine-unambiguous, not Markdown headings. The EndogenAI agent files use Markdown headings (`## Role`, `## Completion Criteria`), which is less parsing-stable.
- **No structured handoff schema found in any external source**: "The only channel from parent to subagent is the Task prompt string" — all external sources surveyed (cookbook, SDK docs, Agent Teams docs) use unstructured natural language in the Task/prompt field. No JSON schema or typed handoff format was found.
- **OODA loop confirmed**: the Anthropic cookbook subagent prompt explicitly names the OODA loop (Observe/Orient/Decide/Act) as the production research loop — the precise equivalent of ReAct's Thought/Action/Observation trace.
- **7-element delegation checklist** (from cookbook lead agent): objective, output format, background context, key questions, sources/quality criteria, specific tools, scope boundaries.
- **Quantitative subagent budget**: simple → 1 subagent; standard → 2–3; medium → 3–5; hard → 5–10. Default: 3 for most queries.
- **EndogenAI's `.tmp/` scratchpad append-under-heading convention is novel** — no external analogue found in any source surveyed. The convention is an EndogenAI-specific invention not derived from any external framework.

---

### Open Gaps

The following gaps remain unresolved after round-2 scout re-runs:

| Gap | Status | Next Action |
|-----|--------|-------------|
| A2A Agent Card JSON schema fields | OPEN | Fetch `github.com/google/A2A` spec |
| A2A specific HTTP endpoint paths | OPEN | Fetch `github.com/google/A2A` spec |
| Mei formal context decomposition (c_x notation) | OPEN | Fetch full paper PDF body |
| Write/select/compress/isolate primary attribution (LangChain cite) | OPEN | Fetch LangChain blog post |
| AIGNE SQLite schema DDL | OPEN | Fetch AIGNE repo source |
| ReAct Thought/Action/Observation prompt format | OPEN | Fetch react-lm.github.io code |

---

### Per-Source References

Sources added in round-2 scout runs that are directly relevant to this synthesis:

- [arxiv-org-html-2512-05470v1](sources/arxiv-org-html-2512-05470v1.md) — AIGNE paper; source of AIGNE Context Engineering Pipeline and 7-type memory taxonomy
- [arxiv-context-engineering-survey](sources/arxiv-context-engineering-survey.md) — Mei et al. survey; source of comprehension-generation gap finding and LangChain attribution
- [a2a-announcement](sources/a2a-announcement.md) — Google A2A announcement; source of Agent Card format and MCP/A2A relationship
- [anthropic-building-effective-agents](sources/anthropic-building-effective-agents.md) — Anthropic BEA; primary source of five-pattern taxonomy and eight prompt engineering principles
- [cookbook-research-lead-agent](sources/cookbook-research-lead-agent.md) — Anthropic cookbook lead agent prompt; source of 7-element delegation checklist and subagent budget guidelines
- [cookbook-research-subagent](sources/cookbook-research-subagent.md) — Anthropic cookbook subagent prompt; source of OODA loop confirmation and research budget (5–15 tool calls)
- [claude-sdk-subagents](sources/claude-sdk-subagents.md) — Claude SDK subagents reference; confirms filesystem-based agent definition as `.claude/agents/` markdown files
- [tds-claude-skills-subagents](sources/tds-claude-skills-subagents.md) — TDS skills article; source of three-level progressive disclosure model for agent manifest generator

---

## Cross-Source Conclusions

_Added 2026-03-06 following completion of Pass 1 deep synthesis for all 22 source files and Pass 2 link graph. These conclusions emerge from reading the full source synthesis corpus together — none is derivable from any single source._

---

### 1. Tool-call isolation is a design law, not a heuristic

Five independent orchestration traditions — Anthropic *Building Effective Agents* ([anthropic-building-effective-agents](sources/anthropic-building-effective-agents.md)), ReAct ([arxiv-react](sources/arxiv-react.md)), AIGNE ([arxiv-org-html-2512-05470v1](sources/arxiv-org-html-2512-05470v1.md)), the Claude Agent SDK ([claude-sdk-subagents](sources/claude-sdk-subagents.md)), and Claude Code Agent Teams ([claude-code-agent-teams](sources/claude-code-agent-teams.md)) — all independently enforce strict scope isolation per reasoning step or agent invocation. The SDK states the invariant most precisely: *"the only channel from parent to subagent is the Task prompt string."* AIGNE formalises it as namespace isolation per agent context (`/context/memory/agentID`). Agent Teams enforces it mechanically: no lead conversation history enters a teammate's context window. ReAct's T/A/O loop scopes each Observation to the step that generated it.

The convergence is independent: these teams did not coordinate their specifications. For EndogenAI this means the quasi-encapsulated sub-fleet posture documented in `AGENTS.md` is not a stylistic preference — it is structurally required for reliable multi-agent behaviour. Any design that allows implicit context inheritance across agent boundaries should be treated as a regression, not an optimisation.

---

### 2. A2A Agent Card and `generate_agent_manifest.py` are structurally convergent

Google's A2A Agent Card ([a2a-announcement](sources/a2a-announcement.md)) — a JSON document advertising an agent's capabilities, modality constraints, and task lifecycle for capability discovery — is structurally identical in purpose to what `scripts/generate_agent_manifest.py` produces for the EndogenAI fleet. Both answer the same question: *how does an orchestrator know what a specialist agent can do without loading its full instruction set?* The three-level progressive disclosure model from TDS ([tds-claude-skills-subagents](sources/tds-claude-skills-subagents.md)) implements the same principle at the skill level. The A2A protocol's validation by 50+ enterprise partners confirms the manifest-as-capability-discovery-primitive pattern at industry scale.

The gap to full A2A compatibility is precisely specified: add endpoint URLs, authentication schemes, and task lifecycle state fields (`issue → in-progress → artefact`) to the manifest schema. This is an evolution path, not a redesign. It positions `generate_agent_manifest.py` as a forward-compatible foundation rather than an internal-only artifact.

---

### 3. The comprehension-generation gap independently validates iterative generation architecture across three traditions

Mei et al. ([arxiv-context-engineering-survey](sources/arxiv-context-engineering-survey.md)) document a fundamental empirical asymmetry across 1400+ surveyed papers: LLMs comprehend complex context far better than they generate equally sophisticated long-form outputs. This gap is structural, not model-family-specific.

This single finding retroactively validates the same architectural choice made independently by three separate traditions over three years:

- **Anthropic's evaluator-optimizer loop** ([anthropic-building-effective-agents](sources/anthropic-building-effective-agents.md)): generate → evaluate → refine, iterated until the evaluator judges the output satisfactory.
- **ReAct's T/A/O interleaving** ([arxiv-react](sources/arxiv-react.md)): ground each generation step in an external observation before the next thought, preventing error propagation across long output chains.
- **Park et al.'s reflection mechanism** ([arxiv-generative-agents](sources/arxiv-generative-agents.md)): compress episodic experience into distilled second-order insights before generating behaviour from them — avoiding direct generation from raw unprocessed memory.

All three architectures compensate for the same intrinsic limitation by decomposing long-form generation into multiple short-form steps, each grounded by an intermediate evaluation or observation. For EndogenAI, this convergence argues that the self-loop phase gate is the correct architectural response to the model's intrinsic constraint, not optional scaffolding. Collapsing the gate to a single-pass generation trades quality for latency against a well-characterised and well-documented failure mode.

---

### 4. The `.tmp/` scratchpad append-under-heading convention has no external analogue — it is an EndogenAI original

Across all 22 sources surveyed, no external framework documents a structured, append-under-heading scratchpad where each delegated agent contributes under its own named heading without overwriting peer contributions, and where the resulting document serves simultaneously as a cross-agent handoff surface and a session audit trail.

The Claude SDK ([claude-sdk-subagents](sources/claude-sdk-subagents.md)) uses unstructured natural-language task strings as the sole handoff mechanism. Agent Teams ([claude-code-agent-teams](sources/claude-code-agent-teams.md)) uses a task-list + mailbox model with no shared session document. The Anthropic cookbook lead agent ([cookbook-research-lead-agent](sources/cookbook-research-lead-agent.md)) uses free-form prompt composition. A2A ([a2a-announcement](sources/a2a-announcement.md)) uses named `Artifact` objects per task, not a shared session document. The Generative Agents memory stream ([arxiv-generative-agents](sources/arxiv-generative-agents.md)) is append-only but flat — no heading structure, no multi-agent contribution model.

The `.tmp/<branch>/<date>.md` append-under-heading convention is an EndogenAI-specific invention. It is not derived from any external source, and no source contradicts or improves upon it. The correct posture is to document it explicitly in `docs/guides/session-management.md` as a contribution, not an informal convention pending eventual replacement by an external framework.

---

### 5. Memory tool fragmentation confirms the episodic/experiential gap is architectural and unresolved

Four independent memory libraries — Graphiti/Zep ([github-com-getzep-graphiti](sources/github-com-getzep-graphiti.md)), Letta/MemGPT ([github-com-letta-ai-letta](sources/github-com-letta-ai-letta.md)), Mem0 ([github-com-mem0ai-mem0.md](sources/github-com-mem0ai-mem0.md)), and Cognee ([github-com-topoteretes-cognee](sources/github-com-topoteretes-cognee.md)) — each address the same episodic/experiential memory gap from a different angle: temporal knowledge graph with bi-temporal versioning (Graphiti), virtual context paging with explicit memory tiers (Letta), lightweight cross-session persistence with semantic search (Mem0), and neurosymbolic knowledge graph with entity-relation extraction (Cognee). The convergence of four independent implementations on the same problem space confirms that the gap identified in the Memory Architecture section is real, and that simple in-context workarounds are insufficient at multi-session scale.

The lack of a single dominant solution after three years of active development confirms the gap is genuinely open. No external solution can be adopted wholesale without accepting significant tradeoffs. The deferred recommendation (treat semantic memory as D3 investigation) remains correct. The new information from the synthesis corpus is the precise tradeoff space when the investigation opens: Graphiti for temporal/relational queries, Letta for large-model context management, Mem0 for lightweight persistence, Cognee for structured knowledge extraction. See also [arxiv-generative-agents](sources/arxiv-generative-agents.md) for the three-factor retrieval scoring (recency × importance × relevance) that represents current best-practice design for any semantic retrieval layer over scratchpad session files.

---

## Source Analysis

_All 22 source synthesis documents from Pass 1. Relative links point to the full synthesis file; annotations state the primary contribution to this research question._

### Orchestration and Workflows

- [anthropic-building-effective-agents](sources/anthropic-building-effective-agents.md) — Five-pattern taxonomy (prompt chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer); eight ACI design principles; Poka-yoke tool design; stopping conditions as mandatory architectural constraint.
- [claude-code-agent-teams](sources/claude-code-agent-teams.md) — Lead-worker fleet topology in a shipped product; plan-approval phase gates; `TeammateIdle` / `TaskCompleted` hook-based quality enforcement; file-level ownership to prevent write conflicts; known limitations (no nesting, task-status lag).
- [claude-sdk-subagents](sources/claude-sdk-subagents.md) — `AgentDefinition` schema and description-driven automatic delegation; context isolation invariant; one-level nesting hard limit; subagent transcript persistence independent of main session.
- [cookbook-research-lead-agent](sources/cookbook-research-lead-agent.md) — Depth/breadth/straightforward query classification gate; subagent budget heuristics (1–20, hard ceiling); early-termination obligation; synthesis never delegated; Bayesian updating posture for subagent results.
- [cookbook-research-subagent](sources/cookbook-research-subagent.md) — Worker-side OODA loop; research tool-call budget (5–15); explicit reporting format; scope boundary constraints.
- [cookbook-citations-agent](sources/cookbook-citations-agent.md) — Citation-separation pattern; dedicated agent for reference attribution decoupled from synthesis generation.
- [a2a-announcement](sources/a2a-announcement.md) — Agent Card JSON for capability discovery; A2A/MCP complementarity (inter-agent vs. tool-context layers); task/artifact lifecycle primitives; 50+ enterprise partner ecosystem validation.
- [freecodecamp-org-news-build-and-deploy-multi-agent-ai-with-p](sources/freecodecamp-org-news-build-and-deploy-multi-agent-ai-with-p.md) — Synchronous multi-agent pipeline implementation; shared-volume file handoff as simplest viable inter-agent state mechanism; A2A as the protocol-level upgrade path.

### Reasoning and Prompt Patterns

- [arxiv-react](sources/arxiv-react.md) — Thought→Action→Observation interleaved loop; grounded reasoning prevents hallucination propagation; 34% margin over RL baselines with 1–2 in-context examples; ICLR 2023 peer-reviewed.
- [arxiv-generative-agents](sources/arxiv-generative-agents.md) — Memory stream + reflection + planning architecture; three-factor retrieval scoring (recency × importance × relevance); ablation confirms all three components individually necessary; ACM UIST 2023.
- [arxiv-context-engineering-survey](sources/arxiv-context-engineering-survey.md) — Mei et al. 166-page survey of 1400+ papers; comprehension-generation gap as the field's defining open problem; tripartite foundational component model (retrieval/generation, processing, management); LangChain attribution for write/select/compress/isolate.
- [arxiv-org-html-2512-05470v1](sources/arxiv-org-html-2512-05470v1.md) — AIGNE Constructor/Updater/Evaluator pipeline; 7-type memory taxonomy with precision definitions; LLM-as-OS / Unix filesystem abstraction; human annotation as first-class context element; MCP as a first-class AFS module.
- [tds-claude-skills-subagents](sources/tds-claude-skills-subagents.md) — Three-level progressive disclosure (metadata / body / referenced files); MCP idle token overhead calculation (~32K tokens / ~$160/month); subagents as lazy-loaded context-isolated workers; write concurrency as an open problem.
- [opensourceprojects-dev-post-e7415816-a348-4936-b8bd-0c651c4a](sources/opensourceprojects-dev-post-e7415816-a348-4936-b8bd-0c651c4a.md) — Open-source multi-agent project survey; community-maintained tooling landscape adjacent to the orchestration and memory pattern spaces.

### Memory Architecture

- [github-com-getzep-graphiti](sources/github-com-getzep-graphiti.md) — Temporal knowledge-graph memory with bi-temporal versioning; relation and entity extraction from conversation history; Zep's production memory layer.
- [github-com-letta-ai-letta](sources/github-com-letta-ai-letta.md) — MemGPT-style virtual context paging across in-context, archival, and external storage tiers; stateful agent deployment with persistent identity across sessions.
- [github-com-mem0ai-mem0.md](sources/github-com-mem0ai-mem0.md) — Lightweight cross-session memory persistence with semantic search; user/agent/session scoping; lowest adoption friction of the four memory tools surveyed.
- [github-com-topoteretes-cognee](sources/github-com-topoteretes-cognee.md) — Neurosymbolic knowledge graph with ECL (Extract–Cognify–Link) pipeline; entity-relation-hyperedge model for structured memory extraction from unstructured sources.
- [xda-developers-com-youre-using-local-llm-wrong-if-youre-prom](sources/xda-developers-com-youre-using-local-llm-wrong-if-youre-prom.md) — Local LLM usage patterns; prompt structure differences between cloud and offline models; implications for agent prompt portability across inference backends.

### Local Compute and Infrastructure

- [lmstudio-ai](sources/lmstudio-ai.md) — LM Studio desktop inference server; model management UI; local OpenAI-compatible API endpoint; relevant to OPEN_RESEARCH.md #1 (local compute baseline).
- [ollama-ai](sources/ollama-ai.md) — Ollama CLI-first local model runner; API-compatible with OpenAI conventions; primary local inference tool for the EndogenAI local-compute-first posture.
- [kdnuggets-com-docker-ai-for-agent-builders-models-tools-and-](sources/kdnuggets-com-docker-ai-for-agent-builders-models-tools-and-.md) — Docker as containerisation and reproducibility layer for AI agent deployments; model service dependency management for local inference.
