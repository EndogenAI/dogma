---
title: "Agent Fleet Design Patterns"
research_issue: "#10"
status: Final
date: 2026-03-06
closes_issue: 10
sources:
  - docs/research/sources/anthropic-com-engineering-effective-context-engineering-for-.md
  - docs/research/sources/anthropic-com-engineering-multi-agent-research-system.md
  - docs/research/sources/a2aproject-github-io-A2A-latest-specification.md
  - docs/research/sources/a2a-announcement.md
  - docs/research/sources/arxiv-context-engineering-survey.md
  - docs/research/sources/arxiv-generative-agents.md
  - docs/research/sources/arxiv-org-html-2512-05470v1.md
  - docs/research/sources/arxiv-react.md
  - docs/research/sources/claude-code-agent-teams.md
  - docs/research/sources/tds-claude-skills-subagents.md
  - docs/research/sources/anthropic-building-effective-agents.md
  - docs/research/sources/cookbook-research-lead-agent.md
  - docs/research/sources/cookbook-research-subagent.md
  - docs/research/sources/cookbook-citations-agent.md
---

# Agent Fleet Design Patterns

> **Status**: Final
> **Research Question**: What are the best design patterns for hierarchical agent fleets? How should executives, sub-agents, and specialist agents be structured?
> **Date**: 2026-03-06

---

## 1. Executive Summary

Across fourteen sources spanning production engineering retrospectives, peer-reviewed research, normative specifications, and practitioner cookbooks, a coherent and mutually reinforcing picture of agent fleet design has emerged. Three design hypotheses were submitted for validation; all three required refinement, but two are confirmed directionally and one required a significant reframe.

The most important single finding is the **Compression-on-Ascent / Focus-on-Descent** reframe of the original Prompt Enrichment Chain hypothesis. Context does not enrich as it cascades through a delegation hierarchy — it contracts. Lead agents dispatch precise, narrow task briefs downward; subagents explore extensively and then compress findings into dense 1,000–2,000 token handoffs on ascent. Anthropic's production multi-agent research system produced a 90.2% improvement over single-agent baselines not by enriching prompts through the chain, but by multiplying total token budget across parallel isolated context windows. This reframe has direct implications for every agent file in `.github/agents/`: outbound handoff briefs should be minimal and focused; inbound results should be aggressively compressed.

The second key finding is the confirmation and specification of phase-gated self-loops. Every high-performing agent architecture in the corpus — from ReAct's Thought/Action/Observation cycle, to AIGNE's Constructor/Updater/Evaluator pipeline, to Claude Code's plan-approval gate and hook-based completion enforcement, to Anthropic's three-layer review gate (subagent interleaved thinking → lead re-evaluation → CitationAgent post-processing) — implements explicit evaluation checkpoints before output is accepted and before context advances. The EndogenAI handoff model currently lacks these gates in executable form; they exist as instructions but not as enforced scripts.

The third finding validates the endogenic principle directly: agent coherence in high-performing fleets emerges from absorbed context (agent files, task briefs, shared memory stores) rather than from shared runtime state or external constraint. Isolation is the mechanism of coherence, not coupling. The one structural gap this exposes in the EndogenAI architecture is the shared `.tmp/` scratchpad: when multiple agents read and write it freely, cross-agent context bleed partially undermines the isolation that makes parallel execution reliable and non-duplicative.

For EndogenAI, the priority recommendation is a three-part ADOPT: (1) rename and reverse the H2 framing in all agent files to Focus-on-Descent / Compression-on-Ascent, (2) encode explicit checkpoint scripts in `scripts/` that act as gate enforcement for synthesis document quality, and (3) scope `.tmp/` scratchpad access so agents write to named sections and read only their own prior output.

---

## 2. Hypothesis Validation

### H1 — Self-Loop Handoffs as Phase Gates

**Verdict**: CONFIRMED — with richer specification than the original statement

**Evidence**:

The hypothesis proposed that executive agents should use "self-referential handoff buttons as procedural checkpoints." Across the corpus, this pattern is not merely confirmed; it is instantiated at multiple layers within individual systems.

[anthropic-com-engineering-multi-agent-research-system](sources/anthropic-com-engineering-multi-agent-research-system.md) describes a **three-layer gate** in Anthropic's production Research feature:
1. **Subagent self-evaluation**: Each subagent uses interleaved thinking after every tool result — evaluating quality, identifying gaps, and refining its next query before returning results to the lead.
2. **Lead re-evaluation loop**: The lead agent synthesises subagent results and explicitly decides whether more research is needed before proceeding or exiting the loop.
3. **CitationAgent post-gate**: A dedicated post-processing agent validates all lead output before delivery to the user.

[claude-code-agent-teams](sources/claude-code-agent-teams.md) formalises this at the product level with two concrete mechanisms:
- The **plan-approval gate**: teammates work in read-only plan mode until the lead explicitly approves their approach.
- **Hook-based enforcement**: `TeammateIdle` and `TaskCompleted` hooks return exit code 2 to keep an agent working or block task completion until programmatic quality checks pass.

[arxiv-org-html-2512-05470v1](sources/arxiv-org-html-2512-05470v1.md) names this architecturally: AIGNE's **Evaluator** component closes the pipeline loop, validating outputs and writing verified knowledge back to persistent storage before any downstream agent receives it.

[arxiv-react](sources/arxiv-react.md) provides the academic foundation: the Thought→Action→Observation loop is the canonical instantiation of this pattern, and ablation results confirm that removing the reasoning trace (the evaluation step) degrades performance — the loop is not optional.

[arxiv-generative-agents](sources/arxiv-generative-agents.md) demonstrates that the reflection component — a second-order evaluation of accumulated memory — is individually necessary: removing it degrades believability even when observation and planning are intact.

**Refined Statement**: Phase gates are not simply handoff routing decisions; they are mandatory evaluation operations at every boundary in the agent tree. Effective gates operate at three levels: (a) intra-agent after each tool call (subagent self-evaluation via interleaved thinking), (b) inter-agent after subagent return (lead agent re-evaluation before synthesis), and (c) post-pipeline as a dedicated review agent before delivery. The EndogenAI handoff model should encode all three levels, not just the inter-agent layer.

**EndogenAI Action**: **ADOPT** — introduce explicit checkpoint semantics at all three gate levels. At minimum: (1) add a post-completion evaluation step in Synthesizer instructions before the Archivist commits, and (2) build a `scripts/validate_synthesis.py` script that enforces the ≥ 100 line, all-sections-present quality gate programmatically, equivalent to Claude Code's `TaskCompleted` hook.

---

### H2 — Prompt Enrichment Chain as Value Propagation

**Verdict**: REQUIRES REFINEMENT — the direction of enrichment is backwards

**Evidence**:

The original hypothesis predicted that each delegation level *enriches* context by adding denser project knowledge as prompts flow down the hierarchy. The evidence across the corpus uniformly contradicts the enrichment-on-descent model and supports the inverse: **Focus-on-Descent, Compression-on-Ascent**.

[anthropic-com-engineering-multi-agent-research-system](sources/anthropic-com-engineering-multi-agent-research-system.md) is the most direct refutation. The lead agent receives the raw user query, then *decomposes* it — the subtask brief dispatched to each subagent is narrower, not richer, than the original query. Subagents then explore extensively and return condensed summaries. The 90.2% improvement over single-agent baselines was analysed against the BrowseComp benchmark; **token usage alone explains 80% of performance variance**. The mechanism is parallel budget multiplication, not enrichment propagation.

[anthropic-com-engineering-effective-context-engineering-for-](sources/anthropic-com-engineering-effective-context-engineering-for-.md) provides the most explicit compression ratio: subagents "explore extensively, using tens of thousands of tokens or more, but return only a condensed, distilled summary of their work (often 1,000–2,000 tokens)." This is the only quantified handoff boundary figure across all sources, and it describes compression-on-ascent, not enrichment.

[cookbook-research-lead-agent](sources/cookbook-research-lead-agent.md) encodes this in operational instruction: the lead's "primary role is to coordinate, guide, and synthesize — NOT to conduct primary research yourself." Just-in-time synthesis briefings are explicitly contrasted with pre-loaded enriched context. The subagent task descriptions in that cookbook are narrow, scoped to a specific sub-question, not enriched with accumulated prior knowledge.

[tds-claude-skills-subagents](sources/tds-claude-skills-subagents.md) explains the architecture at the token economics level: subagents provide context isolation precisely by discarding their internal reasoning after completion — "the intermediate reasoning, the dead ends, and the API responses: all gone. Only the result flows back to the main agent." Enrichment propagation would require the opposite: accumulating and forwarding intermediate reasoning, which this source identifies as a cost and coherence failure mode.

[anthropic-building-effective-agents](sources/anthropic-building-effective-agents.md) validates the contraction direction through the parallelisation pattern: "LLMs generally perform better when each consideration is handled by a separate LLM call, allowing focused attention on each specific aspect." Focused attention per call is the mechanism — not accumulated enrichment.

**What the hypothesis got partially right**: Value *does* propagate through the hierarchy, and context management *is* a primary driver of fleet performance. The mistake was the direction: value flows from the compression of extensive exploration into dense handoffs, not from the injection of accumulated knowledge into downstream agents.

**Refined Statement** (replacing "Prompt Enrichment Chain"):
> **Focus-on-Descent / Compression-on-Ascent**: At each delegation boundary, the outbound brief contracts the problem space to the narrowest useful scope for that subagent. On ascent, the subagent compresses extensive exploration into a dense 1,000–2,000 token result. The fleet's performance advantage comes from parallel context window multiplication (total token budget scales with fleet size), not from cross-agent context enrichment.

**EndogenAI Action**: **ADAPT** — rename this hypothesis in all agent file handoff documentation. Audit `handoffs: prompt:` fields in all `.github/agents/*.agent.md` files. Outbound delegation prompts should be precise and narrow; inbound result summaries should be aggressively compressed (target: ≤ 2,000 tokens). The current Executive Researcher delegation prompts should be reviewed against this criterion.

---

### H3 — Quasi-Encapsulated Sub-Fleets

**Verdict**: CONFIRMED — isolation mechanism specified; one EndogenAI gap identified

**Evidence**:

The hypothesis proposed that agent coherence comes from absorbed context (endogenic substrate), not shared state or external constraint. This is confirmed and the isolation mechanism is now specified.

[anthropic-com-engineering-multi-agent-research-system](sources/anthropic-com-engineering-multi-agent-research-system.md) identifies three isolation mechanisms:
1. **Separate context windows**: each subagent operates in an independent context with no shared memory of other subagents' searches.
2. **Distinct task briefs**: the lead crafts each subagent's research objective, output format, and tool guidance individually; briefs are designed to prevent duplication — vague briefs produced duplicated searches in early development.
3. **External filesystem outputs**: subagents write large artifacts to external storage and return lightweight references, preventing any one subagent's output from bloating the lead's context.

[tds-claude-skills-subagents](sources/tds-claude-skills-subagents.md) confirms that context isolation is as much about *discarding* intermediate tokens as it is about *scoping* tools: "the entire context is discarded" after subagent completion, preventing compounding error chains. The "subagents as functions" framing makes the isolation explicit: function scope boundaries are the coherence mechanism.

[claude-code-agent-teams](sources/claude-code-agent-teams.md) enforces this architecturally: "each teammate has its own context window... the lead's conversation history does not carry over." File-level ownership boundaries ("two teammates editing the same file leads to overwrites") are the minimum coordination discipline when isolation is not enforced. Scope tasks for independent ownership.

[a2aproject-github-io-A2A-latest-specification](sources/a2aproject-github-io-A2A-latest-specification.md) formalises this as a protocol requirement: A2A agents collaborate through declared capabilities and exchanged data, never through shared internal state. The "opaque execution" principle maps directly onto the quasi-encapsulation hypothesis.

[arxiv-org-html-2512-05470v1](sources/arxiv-org-html-2512-05470v1.md) provides the formal architectural model: AIGNE's AFS namespace isolation (`/context/memory/agentID`) allows each agent to operate with a distinct context slice, with the Executive as the only agent that holds full session context at any given time.

**Gap identified**: The EndogenAI `.tmp/` scratchpad is a shared mutable resource. The current AGENTS.md convention allows all agents to read and append to the same session scratchpad. When multiple agents (Scout, Synthesizer, Reviewer) access a shared `.tmp/<branch>/<date>.md` file, they introduce exactly the lateral-communication failure mode that isolated fleet architectures are designed to avoid. Agents reading another agent's section may carry forward another agent's framing, duplicating or conflating search trajectories.

**Refined Statement**: Quasi-encapsulated sub-fleet coherence is achieved through three jointly necessary mechanisms: (1) separate context windows per subagent, (2) distinct task briefs that encode each subagent's scope, and (3) artifact-based return (not inline response passing) for large outputs. The lead agent is the sole integration point; subagents do not communicate laterally. Context absorption into agent instructions (the endogenic substrate) is the mechanism by which agents know how to behave — not runtime shared state.

**EndogenAI Action**: **ADAPT** — scope `.tmp/` scratchpad access. Each agent should append to a named section (`## Scout Output`, `## Synthesizer Output`) and read only its own prior section, not the full scratchpad. The Executive reads the full scratchpad as the sole integration point. This restores the isolation property without requiring new infrastructure.

---

## 3. Pattern Catalog

### Pattern 1 — Orchestrator-Workers

**Context**: A complex task that can be decomposed into parallel or sequentially dependent subtasks, where individual subtasks require diverse research, analysis, or execution capabilities and the final output requires integration of all results.

**Forces**: (a) A single-agent solution would exhaust one context window and serialize all work; (b) subtask results require cross-referencing that only a synthesising agent can perform; (c) the decomposition of the task is not known in advance and must be determined dynamically.

**Solution**: A single lead (orchestrator) agent receives the full problem, decomposes it into subtasks, dispatches each to a worker agent with a narrow task brief, and synthesises worker results into a final output. The lead does not conduct primary research; workers do not synthesise cross-task findings. The lead's conversation history does not carry over to workers.

**Consequences**: + Parallel execution reduces wall-clock time; + each worker's context is focused on one subtask, improving quality; + intermediate worker reasoning is discarded, keeping lead context clean. − Token cost scales with fleet size (15× chat for multi-agent systems); − lead agent becomes a bottleneck if workers fail silently; − synchronous execution of worker batches creates wait phases.

**Evidence**: [anthropic-building-effective-agents](sources/anthropic-building-effective-agents.md), [anthropic-com-engineering-multi-agent-research-system](sources/anthropic-com-engineering-multi-agent-research-system.md), [cookbook-research-lead-agent](sources/cookbook-research-lead-agent.md), [claude-code-agent-teams](sources/claude-code-agent-teams.md)

---

### Pattern 2 — Evaluator-Optimizer Loop

**Context**: A generation task where a single pass is unlikely to meet quality criteria, where iterative refinement demonstrably improves outputs, and where clear evaluation criteria can be stated in advance.

**Forces**: (a) Generation quality is bounded by what one pass can reason about; (b) the generator and the evaluator require different objective functions and may interfere if collapsed into one; (c) iteration must terminate or costs compound unboundedly.

**Solution**: Separate the generation and evaluation roles into two distinct agents or passes. The generator produces an output; the evaluator scores it against explicit criteria and returns structured feedback. The generator revises accordingly. The loop exits when the evaluator's criteria are met or a maximum iteration count is reached. The Thought→Action→Observation loop (ReAct) is the canonical single-agent expression; the generator-evaluator split is the multi-agent expression.

**Consequences**: + Quality improves with each iteration; + generator and evaluator can be tuned independently; + loop is inspectable and auditable at each step. − Convergence is not guaranteed; explicit stopping conditions are mandatory; − token cost per task is unbounded without an iteration ceiling; − generator and evaluator may deadlock if criteria are underspecified.

**Evidence**: [anthropic-building-effective-agents](sources/anthropic-building-effective-agents.md), [arxiv-react](sources/arxiv-react.md), [arxiv-org-html-2512-05470v1](sources/arxiv-org-html-2512-05470v1.md), [arxiv-generative-agents](sources/arxiv-generative-agents.md), [claude-code-agent-teams](sources/claude-code-agent-teams.md) (plan-approval gate; hook enforcement)

---

### Pattern 3 — Parallel Research Fleet

**Context**: A breadth-first research question that can be decomposed into N distinct, independent sub-questions, each resolvable by a standalone search-and-summarise agent, where parallel exploration materially outperforms sequential exploration.

**Forces**: (a) Sequential exploration serialises the available token budget; (b) diverse search trajectories surface different evidence, reducing single-path bias; (c) the lead needs to integrate N summaries, not N raw search histories.

**Solution**: The lead classifies the query as breadth-first, enumerates all sub-questions (sometimes via a preliminary single subagent), and spawns N subagents in parallel with distinct search briefs. Subagents explore independently, use internal tools before external search, and return condensed 1,000–2,000 token summaries. The lead's context receives only summaries, not raw search outputs. Token budget scales with N; Anthropic's production system uses 3–5 subagents for standard queries, up to 10+ for complex ones, with a hard ceiling of 20.

**Consequences**: + Wall-clock time is bounded by the slowest subagent, not by N × single-agent time; + parallel trajectories reduce anchoring bias; + lead context remains bounded regardless of total exploration depth. − Token cost scales linearly with N (15× chat baseline); − work requires genuinely independent sub-questions; − vague sub-question briefs produce duplicated or circular searches.

**Evidence**: [anthropic-com-engineering-multi-agent-research-system](sources/anthropic-com-engineering-multi-agent-research-system.md) (90.2% improvement; parallel tool calls cut research time by up to 90%), [cookbook-research-lead-agent](sources/cookbook-research-lead-agent.md) (breadth-first topology; subagent count heuristics), [cookbook-research-subagent](sources/cookbook-research-subagent.md) (OODA inner loop; tool budget tiers)

---

### Pattern 4 — Focus-Dispatch / Compression-Return

**Context**: Any delegation boundary in a multi-agent system where context must cross from one agent's window to another, in either direction.

**Forces**: (a) Passing raw exploration history from a subagent to the lead bloats lead context; (b) passing a vague or over-specified brief from the lead to a subagent wastes the subagent's bounded budget on disambiguation; (c) the value created in a subagent's extensive exploration must be preserved without the exploration overhead.

**Solution**: Outbound (lead→subagent): compress the full problem context into a narrow, scoped task brief that is the minimum necessary for the subagent to complete its task — no more. Inbound (subagent→lead): require the subagent to compress its full exploration into a dense result summary, targeting 1,000–2,000 tokens regardless of how many tokens were consumed in exploration. Design the result format explicitly (key findings, source references, confidence flags) so the lead can integrate without re-reading the underlying sources.

**Consequences**: + Lead context grows with number of subagent completions, not with depth of each; + each subagent's focused attention on the task brief improves output quality; + total fleet token usage scales with breadth (fleet size), not with depth (per-subagent exploration). − Aggressive compression risks losing nuanced findings; compression prompt tuning is required (maximise recall first, iterate for precision); − the lead loses access to the subagent's reasoning chain after completion.

**Evidence**: [anthropic-com-engineering-effective-context-engineering-for-](sources/anthropic-com-engineering-effective-context-engineering-for-.md) (1K–2K token handoff figure; compression-on-ascent), [anthropic-com-engineering-multi-agent-research-system](sources/anthropic-com-engineering-multi-agent-research-system.md) (80% of BrowseComp variance from token budget; lead dispatches narrow briefs), [cookbook-research-subagent](sources/cookbook-research-subagent.md) (internal verbose / external concise duality; `complete_task` exit)

---

### Pattern 5 — Context-Isolated Sub-Fleet

**Context**: A multi-agent fleet where more than one subagent executes simultaneously on distinct tasks, and where correctness requires that subagents do not interfere with each other's state, outputs, or context.

**Forces**: (a) Subagents operating from a shared mutable state may overwrite each other's work or conflate their search contexts; (b) passing a full shared context to every subagent bloats each subagent's window with irrelevant information; (c) coherence across isolated agents must still be achieved.

**Solution**: Each subagent operates in its own context window, receives only a task-specific brief (not the lead's full conversation history), and returns results via a structured artifact or a `complete_task`-equivalent tool call. Large artifacts (research results, generated files) are written to external storage; lightweight references (file paths, IDs) are returned to the lead. Subagents do not communicate laterally. The lead is the sole integration point. The `CLAUDE.md` equivalent (agent instructions) is loaded by each subagent from its working directory, providing shared behavioural substrate without shared runtime state.

**Consequences**: + Subagent outputs are non-interfering by construction; + each subagent's context is focused and bounded; + the lead's integration context grows only with aggregated references, not raw outputs. − Coordination requires the lead to sequence or batch subagent tasks deliberately; − write concurrency across subagents on shared files is an open problem and must be resolved through file ownership boundaries; − no lateral communication means subagents cannot coordinate; the lead must re-dispatch if one subagent's result changes another's task scope.

**Evidence**: [anthropic-com-engineering-multi-agent-research-system](sources/anthropic-com-engineering-multi-agent-research-system.md) (subagents write to external systems; pass lightweight references), [tds-claude-skills-subagents](sources/tds-claude-skills-subagents.md) (context discarded after subagent completion), [claude-code-agent-teams](sources/claude-code-agent-teams.md) (context isolation enforced; file-level ownership), [a2aproject-github-io-A2A-latest-specification](sources/a2aproject-github-io-A2A-latest-specification.md) (opaque execution; no shared internals)

---

### Pattern 6 — Agent Card Discovery

**Context**: A multi-agent fleet that grows over time, requires new specialist agents to be composed dynamically, and must allow an orchestrator to identify which available agent is best suited to a given task without a central hardcoded registry.

**Forces**: (a) Hardcoded capability lists in the orchestrator become stale as the fleet evolves; (b) agents from different providers or repos need to be discoverable without bespoke integration code; (c) capability advertisement must be verifiable, not just self-reported.

**Solution**: Each agent publishes a structured capability manifest (an Agent Card, served at `/.well-known/agent-card.json` for network-addressable agents, or held in the frontmatter of an `.agent.md` file for local fleets). The manifest declares the agent's skills (with IDs, descriptions, tags, input/output modes), supported interfaces, and authentication requirements. An orchestrator bootstraps discovery by resolving the well-known URI or reading the agent manifest, matching skill tags and media types to the current task, and routing accordingly. For local EndogenAI fleets, the `scripts/generate_agent_manifest.py` script generates the equivalent in-repo manifest.

**Consequences**: + Fleet can grow without modifying the orchestrator; + capability mismatch errors are surfaced at the protocol layer before execution; + two-tier card model (public + authenticated extended card) enables progressive capability disclosure. − Discovery is static; no real-time availability or load signals are carried in the Agent Card; − skill-level versioning is absent from A2A v1.0; backward compatibility management is left to implementers.

**Evidence**: [a2aproject-github-io-A2A-latest-specification](sources/a2aproject-github-io-A2A-latest-specification.md) (full AgentCard schema; `.well-known/agent-card.json`; two-tier capability model), [a2a-announcement](sources/a2a-announcement.md) (50+ partner ecosystem; capability advertisement as the core discovery primitive), [anthropic-building-effective-agents](sources/anthropic-building-effective-agents.md) (routing workflow as the orchestration pattern that Agent Card discovery enables)

---

### Pattern 7 — Memory-Write-Before-Truncation

**Context**: A long-horizon agent task where the agent's context window may be exhausted before the task is complete, and where plan state, key decisions, or partial results must survive context resets.

**Forces**: (a) Context truncation silently discards plan state; (b) reconstructing lost plan state from scratch wastes tokens and introduces errors; (c) not all context is equally valuable — plan state and key decisions have higher carry-through value than raw API responses.

**Solution**: Before the context window reaches its limit, the agent explicitly writes its current plan, key decisions, architectural choices, and unresolved open questions to an external memory store (file, notes document, structured memory API). After truncation or reset, the agent reads back this written state as the first action in the new context window — restoring plan coherence without rerunning prior work. The write trigger should be configurable: at 200K tokens (Anthropic's production threshold), at phase boundaries, or before any risky action.

**Consequences**: + Plan coherence survives context resets; + memory writes create a durable audit trail of agent reasoning; + partial results can be resumed rather than restarted. − Memory-write discipline requires explicit encoding in agent instructions; − compaction quality varies; over-conservative compression loses subtle context, over-aggressive compression loses critical nuance; − memory stores can accumulate stale state if not pruned.

**Evidence**: [anthropic-com-engineering-multi-agent-research-system](sources/anthropic-com-engineering-multi-agent-research-system.md) (lead saves plan at 200K token threshold before truncation), [anthropic-com-engineering-effective-context-engineering-for-](sources/anthropic-com-engineering-effective-context-engineering-for-.md) (compaction strategies; structured note-taking; Claude plays Pokémon), [arxiv-generative-agents](sources/arxiv-generative-agents.md) (memory stream as persistent append-only record; importance scoring), [arxiv-org-html-2512-05470v1](sources/arxiv-org-html-2512-05470v1.md) (AIGNE's Evaluator write-back; context manifest for traceability)

---

### Pattern 8 — Specialist-by-Separation (Citation Gate)

**Context**: A pipeline whose output must meet both content quality criteria (accurate prose) and attribution quality criteria (correctly sourced claims), where optimising for both simultaneously in one agent degrades performance on both.

**Forces**: (a) Synthesis and citation attribution require different objective functions; (b) a synthesising agent that also cites may hallucinate citations because it cannot verify source text while constructing prose; (c) the output of one specialised pass is the input of the next.

**Solution**: Separate the synthesis and citation concerns into sequential, single-responsibility agents. The synthesis agent produces uncited prose, explicitly instructed not to include citations. A downstream citations agent receives the synthesised text and source documents and adds citations at semantic-unit boundaries, with hard constraints against text modification, sentence fragmentation, and redundant same-source citations within a sentence. The citations agent validates its own output against the source texts.

**Consequences**: + Synthesis quality improves because the generator is not distracted by attribution; + citation quality improves because the attribution agent can focus on source-text matching without prose generation; + the separation enables automated diff-based validation (prose must be identical pre/post citation pass). − Adds one agent invocation to the pipeline; − the citations agent requires access to all source documents, which may be a context or access challenge.

**Evidence**: [cookbook-citations-agent](sources/cookbook-citations-agent.md) (text fidelity as hard constraint; semantic-unit citation scope; automated validation design), [cookbook-research-lead-agent](sources/cookbook-research-lead-agent.md) ("NEVER create a subagent to generate the final report"; citation agent explicitly separated), [anthropic-building-effective-agents](sources/anthropic-building-effective-agents.md) (simple, composable patterns; single-responsibility agents)

---

## 4. Fleet Topology Comparison

| Topology | Use Case | Context Handoff Mechanism | Isolation Level | Token Cost | Source Evidence |
|---|---|---|---|---|---|
| **Flat peer-to-peer** | Simple queries requiring one pass; single-responsibility tasks | Direct return; no handoff | Single window; no isolation | 1× chat baseline | [anthropic-building-effective-agents](sources/anthropic-building-effective-agents.md) (simplest solution; augmented LLM baseline) |
| **Hierarchical (orchestrator-workers)** | Complex research; parallel sub-question execution; tasks requiring synthesis across diverse results | Focus-on-Descent brief; Compression-on-Return summary (1K–2K tokens); artifact references for large outputs | Per-worker isolated windows; lead is sole integration point | ~15× chat ([anthropic-com-engineering-multi-agent-research-system](sources/anthropic-com-engineering-multi-agent-research-system.md)) | [anthropic-com-engineering-multi-agent-research-system](sources/anthropic-com-engineering-multi-agent-research-system.md), [cookbook-research-lead-agent](sources/cookbook-research-lead-agent.md), [claude-code-agent-teams](sources/claude-code-agent-teams.md) |
| **Evaluator-optimizer loop** | Iterative refinement; code generation with test feedback; synthesis validation against criteria | Generator output → evaluator feedback → generator revision; evaluation criteria are shared context | Same or split windows; evaluation objective must be decoupled from generation | 2–4× per iteration | [anthropic-building-effective-agents](sources/anthropic-building-effective-agents.md), [arxiv-react](sources/arxiv-react.md), [arxiv-org-html-2512-05470v1](sources/arxiv-org-html-2512-05470v1.md) (AIGNE Evaluator) |
| **Parallel research fleet** | Breadth-first research; independent sub-questions; competing-hypothesis investigation | Enumerated sub-questions dispatched simultaneously; condensed summaries returned in parallel; lead integrates | Full per-agent isolation; no lateral communication | N × single-agent (3–20 agents typical) | [anthropic-com-engineering-multi-agent-research-system](sources/anthropic-com-engineering-multi-agent-research-system.md), [cookbook-research-lead-agent](sources/cookbook-research-lead-agent.md), [claude-code-agent-teams](sources/claude-code-agent-teams.md) (competing-hypothesis use case) |
| **Hybrid (orchestrator + specialist sub-fleet)** | Production research pipelines requiring synthesis + attribution + review; long-horizon tasks exceeding single context; multi-phase work requiring different specialist capabilities | Phase-gated artifact handoffs; each specialist receives only its required context slice; memory-write-before-truncation for plan continuity | Per-specialist isolation; shared external memory for plan state; lead integrates across all specialists | Highest; justified by output quality requirements and avoidance of end-to-end reruns | [anthropic-com-engineering-multi-agent-research-system](sources/anthropic-com-engineering-multi-agent-research-system.md), [cookbook-citations-agent](sources/cookbook-citations-agent.md), [arxiv-org-html-2512-05470v1](sources/arxiv-org-html-2512-05470v1.md) (Constructor/Updater/Evaluator pipeline) |

---

## 5. Specialist-vs-Extend Decision Heuristics

The primary OPEN_RESEARCH.md gate deliverable: *Recommendations for when to create new specialist agents vs. extend existing ones.*

| Criterion | Signal | Decision |
|---|---|---|
| **Objective function conflict** | The new behaviour requires a different primary goal from the existing agent (e.g., an agent currently optimises for breadth; the new task requires precision over a narrow domain) | **CREATE** a specialist agent with its own objective-first instructions |
| **Context budget conflict** | The new capability requires loading additional tools, skills, or reference documents that would consume >20% of the existing agent's context budget, degrading its primary behaviour | **CREATE** with scoped tool set; keep existing agent clean |
| **Single-responsibility preservation** | The existing agent already handles one cohesive task type; the new capability is adjacent but not equivalent (e.g., research synthesis vs. citation attribution) | **CREATE** a downstream specialist; preserve pipeline separation |
| **Reuse of core task logic** | The new behaviour shares >70% of operational steps with an existing agent and requires only minor output format or scope changes | **EXTEND** via conditional fork in existing agent instructions; avoid fleet proliferation |
| **Frequency of co-invocation** | The new capability is always used together with an existing agent in fixed sequence, with no case where the capability alone is useful | **EXTEND** if coupling is tight and the combined agent stays within context budget; **CREATE** if the sequence varies or the combined agent would exceed budget |
| **Error blast-radius** | A failure in the new capability should not contaminate the existing agent's output or require a full re-run | **CREATE**; isolation is the primary mechanism for blast-radius limitation |
| **Tool set overlap** | The new capability requires tools that the existing agent must never use (e.g., a read-only research agent must not have write-capable tools from a new editing function) | **CREATE**; the endogenic minimal-posture constraint mandates agents carry only the tools required for their stated role |
| **Cross-fleet reusability** | The new capability is useful independently of any existing agent context (another agent in the fleet may need it too) | **CREATE** a composable specialist; encode as a callable unit, not a capability bolted onto one agent |
| **Cognitive load of combined instructions** | Adding the new capability to an existing agent's instructions would require the agent to disambiguate between two competing modes at decision time | **CREATE**; ambiguous decision points are a primary cause of tool-selection failures ([anthropic-building-effective-agents](sources/anthropic-building-effective-agents.md): "bloated tool sets lead to ambiguous decision points") |

**Decision tree summary**: if any of the following are true, CREATE: (1) different objective function, (2) context budget pressure, (3) error isolation needed, (4) tool set incompatibility. If all of the following are true, EXTEND: (1) same objective function, (2) >70% shared task logic, (3) always invoked together, (4) combined agent stays within context budget.

---

## 6. Context Window Management at Handoff Boundaries

This section synthesises the specific strategies from context engineering and multi-agent system sources and maps each to EndogenAI practice.

### Strategy 1 — Compaction (Summarise + Reinitiate)

**Source specification**: When an agent's context approaches its window limit, the agent summarises its accumulated history — preserving architectural decisions, unresolved bugs, and key findings while discarding redundant tool outputs — and reinitiates a new context window with the compressed summary plus the most recently accessed files. ([anthropic-com-engineering-effective-context-engineering-for-](sources/anthropic-com-engineering-effective-context-engineering-for-.md))

**Compaction tuning principle**: Maximise recall first (compress nothing important), then iterate for precision (eliminate redundancy). Tool result clearing is the "safest, lightest touch" form.

**EndogenAI mapping**: `scripts/prune_scratchpad.py` is the EndogenAI instantiation of compaction — triggered at the 2,000-line size threshold or at session end via `--force`. The current script applies a line-count threshold without distinguishing high-value from low-value content. **Gap**: prune_scratchpad.py should be extended with a model-assisted compaction pass that applies recall-first, precision-second tuning, consistent with Anthropic's guidance.

### Strategy 2 — Structured Note-Taking (External Memory Persisted Outside Window)

**Source specification**: Agents maintain an external notes document (a `NOTES.md` file, a to-do list, or a structured memory store) that survives context resets. After each reset, the agent reads its notes as the first action, restoring coherence. The lead agent in Anthropic's research system saves its plan to Memory before the context window is truncated at 200K tokens. ([anthropic-com-engineering-multi-agent-research-system](sources/anthropic-com-engineering-multi-agent-research-system.md), [anthropic-com-engineering-effective-context-engineering-for-](sources/anthropic-com-engineering-effective-context-engineering-for-.md))

**EndogenAI mapping**: The `.tmp/<branch>/<date>.md` scratchpad and the `## Session Summary` convention in AGENTS.md are direct instantiations of this pattern. The `_index.md` file of closed session stubs maps to the long-term note store. **Gap**: the write trigger is ad-hoc (user reminder or agent best practice) rather than mechanically enforced at phase transitions. The scratchpad should be written before any risky or large operation, not only at session end.

### Strategy 3 — Sub-Agent Context Isolation (Each Subagent Returns Condensed 1,000–2,000 Token Summary)

**Source specification**: "Each subagent might explore extensively, using tens of thousands of tokens or more, but returns only a condensed, distilled summary of its work (often 1,000–2,000 tokens)." The ratio is not accidental; it is an explicitly engineered compression ratio that keeps the lead's integration context bounded regardless of per-subagent exploration depth. ([anthropic-com-engineering-effective-context-engineering-for-](sources/anthropic-com-engineering-effective-context-engineering-for-.md))

The subagent research prompt formalises this as a behavioural norm: "Be detailed in your internal process, but more concise and information-dense in reporting the results." ([cookbook-research-subagent](sources/cookbook-research-subagent.md))

**EndogenAI mapping**: Synthesizer agent invocations currently return full synthesis documents (typically 100–200+ lines) directly into the Executive's scratchpad. This is not a compressed handoff; it is the full artifact. The distinction matters: the synthesis *document* should be committed to `docs/research/sources/`, while the handoff *summary* returned to the Executive should be a 1–2 paragraph digest of the synthesis's key findings and any gaps identified. **Gap**: the handoff boundary between Synthesizer and Executive is not compression-gated today.

### Strategy 4 — Memory-Write-Before-Truncation Pattern

**Source specification**: Before a context window reaches its limit, the agent proactively writes its reasoning state to persistent external memory. Triggers: reaching a token threshold (200K tokens), completing a phase, or encountering a risky action. ([anthropic-com-engineering-multi-agent-research-system](sources/anthropic-com-engineering-multi-agent-research-system.md), [arxiv-generative-agents](sources/arxiv-generative-agents.md))

**Quantitative basis**: The importance-scored retrieval model from [arxiv-generative-agents](sources/arxiv-generative-agents.md) provides design guidance for what to write: recent events (high recency weight), significant decisions (high importance weight), and context-relevant findings (high relevance weight) deserve the highest priority in any memory write operation. Trivial recent events should not crowd out significant older ones.

**EndogenAI mapping**: The `prune_scratchpad.py --force` command at session end is a memory-write operation. It is currently triggered only at session boundaries. **Adaptation**: add a `--pre-action` mode to prune_scratchpad.py that triggers a targeted write of current plan state and open decisions before any large-scope operation (e.g., before a Synthesizer invocation, before a git commit). This mirrors the 200K threshold trigger in production systems.

---

## 7. Critical Assessment

### Limitations of This Synthesis

**Source concentration**: Eight of the fourteen D3 sources are from Anthropic (engineering blog, documentation, or cookbooks). The evidence base is authoritative for Anthropic's production systems but may exhibit provider bias — patterns that work well with Claude-family models may not translate directly to other model providers. The quasi-encapsulated isolation mechanisms, for example, depend on Claude's context-window boundary enforcement; other providers may implement these boundaries differently.

**Lack of controlled experiments for most patterns**: With the exception of ReAct (ICLR 2023 peer-reviewed, ablation study), and the BrowseComp regression from the Anthropic multi-agent system (moderate evidence quality), most claims are practitioner assertions from production deployments without published datasets or rubrics. The 90.2% improvement figure is compelling but is from an undisclosed internal benchmark that cannot be independently reproduced. Pattern efficacy under controlled conditions remains an open question for most of the catalog.

**Concurrency gap**: Multiple sources flag write concurrency in parallel sub-fleets as an open problem. [tds-claude-skills-subagents](sources/tds-claude-skills-subagents.md) names it explicitly: "This is a classic concurrency problem, coming from the AI workflows of the near-future, which to date remains an open problem." No source in the corpus provides a solution beyond file-level ownership boundaries (Claude Code's recommendation). This is a production gap for any EndogenAI workflow that has multiple agents writing to shared resources.

**A2A adoption lag**: The Agent Card Discovery pattern is architecturally sound and backed by a normative specification (A2A v1.0 RC), but adoption is early-stage. The A2A specification is a Release Candidate with documented gaps (missing proto message stubs, absent skill versioning). [tds-claude-skills-subagents](sources/tds-claude-skills-subagents.md) rates A2A as "one to watch, not one to bet on yet." Dynamic fleet composition via A2A discovery is a forward-looking pattern, not a near-term implementation target for EndogenAI.

### Open Questions for OPEN_RESEARCH.md

1. **Optimal compression ratio for handoff boundaries**: The 1,000–2,000 token figure is Anthropic's engineering guideline, stated without benchmarking against task type or exploration depth. At what point does aggressive compression lose precision-critical context that only becomes important later? What task-type-specific compression ratios should be used for code synthesis (where precise syntax matters) vs. research synthesis (where conceptual coverage matters)?

2. **Scratchpad isolation without tooling overhead**: The H3 gap identified — shared `.tmp/` scratchpad partially breaking context isolation — requires a design solution that preserves cross-agent handoff visibility for the Executive while preventing lateral context bleed between peers. Section-scoped writes are the proposed solution, but the mechanism for enforcement (agent instructions alone vs. a script-enforced write gate) has not been validated. What is the minimal viable isolation mechanism that does not require new infrastructure?

3. **Evaluator-optimizer convergence in synthesis tasks**: The evaluator-optimizer loop is confirmed as a high-value pattern, but convergence criteria for synthesis tasks (as opposed to coding tasks with verifiable test outputs) are not defined across the corpus. For research synthesis documents, what constitutes a satisfactory evaluation outcome? How should the Reviewer agent in the EndogenAI fleet define its stopping condition, and how does the comprehension-generation gap (identified in [arxiv-context-engineering-survey](sources/arxiv-context-engineering-survey.md)) affect the reliability of LLM-as-judge evaluation in this context?

---

## 8. Recommendations for EndogenAI

> **README extraction targets**: The following D4 sections furnish `.github/agents/README.md` content: §4 Fleet Topology Comparison table, §5 Specialist-vs-Extend decision-tree summary, and the pattern name list from §3.

### Priority 1 — ADOPT: Rename and Reverse the Handoff Direction in All Agent Files

**Target files**: All `.github/agents/*.agent.md` files with `handoffs:` frontmatter sections, and `docs/guides/session-management.md`.

**Action**: Replace all references to "Prompt Enrichment Chain" and "context enrichment on delegation" with the Focus-on-Descent / Compression-on-Ascent model. Specifically: outbound delegation prompts should be explicitly scoped to the minimum task brief; inbound result summaries should target ≤ 2,000 tokens. Add explicit compression instructions to the `handoffs: prompt:` YAML fields.

**Basis**: H2 refutation; [anthropic-com-engineering-effective-context-engineering-for-](sources/anthropic-com-engineering-effective-context-engineering-for-.md) (1K–2K handoff target); [anthropic-com-engineering-multi-agent-research-system](sources/anthropic-com-engineering-multi-agent-research-system.md) (focus-on-descent evidenced).

---

### Priority 2 — ADOPT: Build `scripts/validate_synthesis.py` as a Phase Gate Enforcement Script

**Target**: New script in `scripts/`, invocable by the Archivist before any commit of a synthesis document.

**Action**: Implement the quality gate that Claude Code's `TaskCompleted` hook represents: verify ≥ 100 lines, all eight required sections present, evidence quality label in `## Critical Assessment`, ≥ 1 named agent file in `## Relevance to EndogenAI`. Exit with code 1 and structured error feedback if any criterion is not met. This converts a soft convention into an enforced gate.

**Basis**: [claude-code-agent-teams](sources/claude-code-agent-teams.md) (hook-based quality enforcement); [arxiv-org-html-2512-05470v1](sources/arxiv-org-html-2512-05470v1.md) (AIGNE Evaluator write-back with provenance); [anthropic-building-effective-agents](sources/anthropic-building-effective-agents.md) (stopping conditions are mandatory).

---

### Priority 3 — ADAPT: Scope `.tmp/` Scratchpad Sections by Agent

**Target**: `AGENTS.md` Agent Communication section; `docs/guides/session-management.md`; `.github/agents/executive-researcher.agent.md`.

**Action**: Codify the convention that each delegated agent appends results to a named, agent-specific section (`## Scout Output`, `## Synthesizer Output: <slug>`, etc.) and reads only its own prior section for continuation context. The Executive, as the sole integration point, reads the full scratchpad. Enforce through instruction conventions, not new infrastructure.

**Basis**: H3 gap (shared scratchpad partially breaks isolation); [anthropic-com-engineering-multi-agent-research-system](sources/anthropic-com-engineering-multi-agent-research-system.md) (subagents do not communicate laterally); [claude-code-agent-teams](sources/claude-code-agent-teams.md) (file-level ownership prevents overwrites).

---

### Priority 4 — ADOPT: Encode Query-Type Classification as the First Gate in the Research Workflow

**Target**: `docs/guides/workflows.md`; `.github/agents/executive-researcher.agent.md`.

**Action**: Add a mandatory classification step before any Scout invocation: classify the incoming request as (a) depth-first (multiple perspectives on one question → 2–5 Scouts with diverse angles), (b) breadth-first (independent sub-questions → parallel Scouts with distinct scopes), or (c) straightforward (narrow factual query → single Scout with tight scope). This routing step prevents over-investment in simple queries and under-investment in complex ones. Include the subagent count heuristics from the cookbook (1 for simple; 2–3 for standard; 3–5 for medium; 5–10 for complex).

**Basis**: [cookbook-research-lead-agent](sources/cookbook-research-lead-agent.md) (query-type taxonomy); [anthropic-building-effective-agents](sources/anthropic-building-effective-agents.md) (routing workflow; simplest solution first).

---

### Priority 5 — ADOPT: Encode Explicit Phase-Gate Checkpoints at All Three Levels

**Target**: `.github/agents/executive-researcher.agent.md`; Synthesizer and Reviewer mode instructions.

**Action**: Add three explicit gate types to the research workflow: (1) subagent self-evaluation — Scout and Synthesizer agents include a structured self-check before calling `complete_task` (did I address all gate deliverables? did I hit the minimum quality criteria?); (2) lead review gate — Executive explicitly evaluates each returned result before proceeding to the next phase; (3) post-pipeline gate — Reviewer runs before Archivist, with explicit completion criteria from `OPEN_RESEARCH.md`. Add a maximum iteration count to prevent compounding cost in the evaluator-optimizer loop.

**Basis**: [anthropic-com-engineering-multi-agent-research-system](sources/anthropic-com-engineering-multi-agent-research-system.md) (three-layer gate); [arxiv-react](sources/arxiv-react.md) (evaluation as mandatory, not optional); [anthropic-building-effective-agents](sources/anthropic-building-effective-agents.md) (stopping conditions; max iterations); [claude-code-agent-teams](sources/claude-code-agent-teams.md) (plan-approval gate).

---

### Priority 6 — ADAPT: Extend `prune_scratchpad.py` with Recall-First Compaction Logic

**Target**: `scripts/prune_scratchpad.py`.

**Action**: Extend the script with a model-assisted compaction pass option (`--compact`) that applies the Anthropic recall-first, precision-second tuning: first pass maximises recall (nothing important discarded), second pass eliminates redundancy. Add a `--pre-action` trigger mode that allows agents to write current plan state and open decisions before large-scope operations, not only at session end. This mirrors the 200K-token threshold trigger in Anthropic's production system.

**Basis**: [anthropic-com-engineering-effective-context-engineering-for-](sources/anthropic-com-engineering-effective-context-engineering-for-.md) (compaction tuning principle); [anthropic-com-engineering-multi-agent-research-system](sources/anthropic-com-engineering-multi-agent-research-system.md) (200K threshold; memory-write-before-truncation).

---

### Priority 7 — ADOPT: Audit Agent Frontmatter Against A2A AgentCard Schema

**Target**: `scripts/generate_agent_manifest.py`; all `.github/agents/*.agent.md` frontmatter.

**Action**: Review the skills declaration convention in EndogenAI agent frontmatter against the A2A `AgentSkill` schema (`id`, `name`, `description`, `tags`, `inputModes`, `outputModes`). Adopt the tags-and-modes vocabulary as the standard for skill-level capability declaration in all agent files, even without implementing full A2A wire communication. Update `generate_agent_manifest.py` to output a manifest that is structurally compatible with the A2A AgentCard format, positioning the fleet for future A2A interoperability.

**Basis**: [a2aproject-github-io-A2A-latest-specification](sources/a2aproject-github-io-A2A-latest-specification.md) (AgentSkill schema; `.well-known/agent-card.json`); [a2a-announcement](sources/a2a-announcement.md) (50+ partner backing; ADOPT recommendation); endogenic-first principle (scaffold from external best practices).

---

### Priority 8 — ADAPT: Introduce Citation-Gate Separation in the Synthesizer Pipeline

**Target**: Synthesizer mode instructions; `.github/agents/` (if a `research-citations.agent.md` specialist is warranted).

**Action**: Modify Synthesizer instructions so that the synthesis pass produces prose without inline citations, using source slugs as reference markers only. A subsequent citation pass (either a separate agent invocation or a second Synthesizer pass with the citations-agent prompt) adds properly anchored citations with the constraints from the cookbook: cite at sentence boundaries, no fragmentation, no same-sentence redundancy, cite only where source directly supports claim. This resolves the recurring fabricated-citation failure mode.

**Basis**: [cookbook-citations-agent](sources/cookbook-citations-agent.md) (text-fidelity hard constraint; separation of synthesis and attribution); [cookbook-research-lead-agent](sources/cookbook-research-lead-agent.md) (synthesis and citation agent are separate); Priority 2 validation script above (automated diff-check of pre/post citation prose).

---

## Sources

1. [Effective context engineering for AI agents](sources/anthropic-com-engineering-effective-context-engineering-for-.md) — Rajasekaran et al., Anthropic Engineering, 2025
2. [How we built our multi-agent research system](sources/anthropic-com-engineering-multi-agent-research-system.md) — Hadfield et al., Anthropic Engineering, 2025
3. [Agent2Agent (A2A) Protocol Specification — RC v1.0](sources/a2aproject-github-io-A2A-latest-specification.md) — A2A Project (Google), 2025
4. [Announcing the Agent2Agent Protocol (A2A)](sources/a2a-announcement.md) — Surapaneni et al., Google Cloud Blog, 2025
5. [A Survey of Context Engineering for Large Language Models](sources/arxiv-context-engineering-survey.md) — Mei et al., arXiv:2507.13334, 2025
6. [Generative Agents: Interactive Simulacra of Human Behavior](sources/arxiv-generative-agents.md) — Park et al., ACM UIST 2023
7. [Everything is Context: Agentic File System Abstraction for Context Engineering](sources/arxiv-org-html-2512-05470v1.md) — Xu et al., arXiv:2512.05470, 2025
8. [ReAct: Synergizing Reasoning and Acting in Language Models](sources/arxiv-react.md) — Yao et al., ICLR 2023
9. [Run agent teams — Claude Code Documentation](sources/claude-code-agent-teams.md) — Anthropic, 2025
10. [Claude Skills and Subagents: Escaping the Prompt Engineering Hamster Wheel](sources/tds-claude-skills-subagents.md) — Broekx, Towards Data Science, 2026
11. [Building effective agents](sources/anthropic-building-effective-agents.md) — Schluntz & Zhang, Anthropic Engineering, 2024
12. [Research Lead Agent System Prompt (Anthropic Cookbook)](sources/cookbook-research-lead-agent.md) — Anthropic Cookbook, 2025
13. [Research Subagent System Prompt (Anthropic Cookbook)](sources/cookbook-research-subagent.md) — Anthropic Cookbook, 2025
14. [Citations Agent System Prompt (Anthropic Cookbook)](sources/cookbook-citations-agent.md) — Anthropic Cookbook, 2024
