---
source_url: "https://www.anthropic.com/engineering/multi-agent-research-system"
cache_path: ".cache/sources/anthropic-com-engineering-multi-agent-research-system.md"
fetched: 2026-03-06
research_issue: "Issue #10 — Agent Fleet Design Patterns"
slug: "anthropic-com-engineering-multi-agent-research-system"
title: "How we built our multi-agent research system"
authors: "Jeremy Hadfield, Barry Zhang, Kenneth Lien, Florian Scholz, Jeremy Fox, Daniel Ford (Anthropic)"
year: "2025"
type: blog
topics: [multi-agent, orchestration, sub-agents, evaluation, prompt-engineering, production-reliability, research-tasks, context-management, parallelisation, tool-design]
cached: true
evidence_quality: moderate
date_synthesized: "2026-03-06"
---

# Synthesis: How We Built Our Multi-Agent Research System

## 1. Citation

Hadfield, J., Zhang, B., Lien, K., Scholz, F., Fox, J., & Ford, D. (2025, June 13). *How we built our multi-agent research system*. Anthropic Engineering. https://www.anthropic.com/engineering/multi-agent-research-system

Published on the Anthropic Engineering blog. Not peer-reviewed. Primary source: the engineering team that built and deployed Anthropic's live Research feature inside Claude.ai. Quantitative claims are drawn from internal evaluations; methodology partly described but not independently reproducible.

---

## 2. Research Question Addressed

How should a production multi-agent research system be architected, prompted, evaluated, and operated reliably at scale? The post documents the engineering decisions behind Anthropic's Research feature — from prototype architecture to production deployment — covering agent coordination, prompt design, evaluation strategy, and failure modes unique to stateful multi-agent systems.

Secondary question: *what makes multi-agent systems outperform single-agent baselines on complex, open-ended research tasks, and at what cost?*

---

## 3. Theoretical Framework

The system is grounded in the **orchestrator-worker pattern** (also called lead agent / subagent or planner-executor). This is one of the canonical agentic composable patterns described in the companion post *Building effective agents*, here instantiated at production scale. Key intellectual inputs:

- **Collective intelligence scaling**: the post explicitly draws an analogy between individual vs. societal intelligence in humans—
  > "Even generally-intelligent agents face limits when operating as individuals; groups of agents can accomplish far more."
  This frames multi-agent systems not as a workaround but as a first-class scaling mechanism.
- **Token-as-compute framing**: the central performance finding is that token usage (not model capability alone) explains 80% of BrowseComp evaluation variance. This positions multi-agent architectures primarily as a mechanism for scaling token budget across parallel context windows.
- **Context compression / separation of concerns**: subagents are explicitly described as "intelligent filters" that compress large exploration spaces into small handoff payloads — directly linking to the context-as-resource paradigm from the companion context engineering post.

No formal academic framework is cited. The intellectual heritage is observational systems engineering with reference to BrowseComp as an external benchmark.

---

## 4. Methodology / Source Type

Production engineering retrospective. Evidence types:

- **Internal evaluation**: multi-agent Claude Opus 4 + Claude Sonnet 4 vs. single-agent Claude Opus 4 on an undisclosed internal research eval. Result: 90.2% improvement. Methodology is described at a high level (the eval involves breadth-first multi-direction queries) but the eval rubric, dataset, and scoring method are not published.
- **BrowseComp analysis**: three-factor regression explaining 95% of performance variance (token usage: 80%; tool calls; model choice). This is the most quantitatively precise claim in the source.
- **Qualitative failure mode analysis**: agents spawning 50 subagents for simple queries, circular searches, source selection biases — observed during internal testing and user feedback.
- **Operational observability data**: 4× token usage vs. chat; 15× token usage vs. chat for multi-agent systems. Source: internal usage data.
- **Anecdotal user impact**: case stories (healthcare navigation, business opportunities, days of work saved). Not measured.

The post is honest about its methodological limits: eval datasets and rubrics are not shared; the 90.2% figure is from an internal benchmark that cannot be independently reproduced.

---

## 5. Key Claims with Evidence

1. **Multi-agent systems outperform single-agent baselines by 90.2% on complex research tasks.**
   > "a multi-agent system with Claude Opus 4 as the lead agent and Claude Sonnet 4 subagents outperformed single-agent Claude Opus 4 by 90.2% on our internal research eval"
   The eval is breadth-first queries requiring parallel information gathering. The figure does not generalise to coding tasks or tasks with many inter-agent dependencies.

2. **Token usage explains 80% of BrowseComp performance variance; model choice is a secondary factor.**
   > "token usage by itself explains 80% of the variance, with the number of tool calls and the model choice as the two other explanatory factors"
   This is the most empirically grounded claim in the source. It reframes performance optimisation: scaling token budget matters more than model selection alone.

3. **Multi-agent systems consume approximately 15× more tokens than chat interactions; agents alone consume 4×.**
   > "agents typically use about 4× more tokens than chat interactions, and multi-agent systems use about 15× more tokens than chats"
   Economic viability therefore requires tasks where the value created justifies the token cost. This is an explicit constraint on when multi-agent architectures are appropriate.

4. **Subagents are intelligent compression filters, not merely workers.**
   > "Subagents facilitate compression by operating in parallel with their own context windows, exploring different aspects of the question simultaneously before condensing the most important tokens for the lead research agent."
   Each subagent explores independently and returns a condensed summary — isolating detailed search context from the lead agent's planning context.

5. **The lead agent saves its plan to external memory before context limits are reached.**
   > "The LeadResearcher begins by thinking through the approach and saving its plan to Memory to persist the context, since if the context window exceeds 200,000 tokens it will be truncated and it is important to retain the plan."
   At 200K token threshold, the plan is externalised rather than lost. This is explicit memory-before-truncation discipline.

6. **Subagents use interleaved thinking after each tool result to evaluate quality, identify gaps, and refine next queries.**
   > "Subagents also plan, then use interleaved thinking after tool results to evaluate quality, identify gaps, and refine their next query."
   This is a self-loop within each subagent — the subagent evaluates its own progress before proceeding, without waiting for the lead agent to review.

7. **Parallel tool calling within subagents cut research time by up to 90% for complex queries.**
   > "These changes cut research time by up to 90% for complex queries, allowing Research to do more work in minutes instead of hours while covering more information than other systems."
   Two levels of parallelism: lead agent spawns 3–5 subagents in parallel; each subagent uses 3+ tools in parallel.

8. **Effort scaling rules are embedded in prompts, not left to agent discretion.**
   > "Simple fact-finding requires just 1 agent with 3-10 tool calls, direct comparisons might need 2-4 subagents with 10-15 calls each, and complex research might use more than 10 subagents with clearly divided responsibilities."
   Explicit effort budget guidelines in prompts prevent over-investment in simple queries — one of the most common early failure modes.

9. **Sub-agent output to a filesystem bypasses the orchestrator for large artifacts, preventing game-of-telephone information loss.**
   > "Subagents call tools to store their work in external systems, then pass lightweight references back to the coordinator. This prevents information loss during multi-stage processing and reduces token overhead from copying large outputs through conversation history."
   Lightweight references (file paths, IDs) replace full output copying — an explicit technique for containing context bloat.

10. **Rainbow deployments are used to avoid disrupting in-progress long-running agents during code updates.**
    > "We use rainbow deployments to avoid disrupting running agents, by gradually shifting traffic from old to new versions while keeping both running simultaneously."
    Stateful, long-running agents require deployment strategies that treat agent sessions as durable processes, not stateless requests.

11. **Self-improvement loops: Claude 4 models can diagnose prompt failures and rewrite tool descriptions.**
    > "We even created a tool-testing agent—when given a flawed MCP tool, it attempts to use the tool and then rewrites the tool description to avoid failures... This process for improving tool ergonomics resulted in a 40% decrease in task completion time."
    Quantified: 40% task completion time reduction from model-assisted tool description rewriting across dozens of test runs.

12. **LLM-as-judge evaluation with a single prompt and 0.0–1.0 output scores was more consistent and more aligned with human judgement than multi-judge ensembles.**
    > "a single LLM call with a single prompt outputting scores from 0.0-1.0 and a pass-fail grade was the most consistent and aligned with human judgements"
    Simplicity wins in evaluation design: fewer moving parts, faster iteration.

13. **Synchronous lead-agent execution creates bottlenecks; asynchronous execution is the identified next step but remains unimplemented.**
    > "Currently, our lead agents execute subagents synchronously, waiting for each set of subagents to complete before proceeding. This simplifies coordination, but creates bottlenecks."
    Asynchronous execution is flagged as the next architectural evolution, blocked by result coordination and error propagation complexity.

---

## 6. Critical Assessment

**Evidence Quality**: Moderate

Stronger than a typical practitioner blog post: the BrowseComp three-factor regression is a named external benchmark with a described analytical method, and the 4× / 15× token consumption figures are internal usage data with a concrete basis. The 90.2% improvement figure is from an internal eval, which limits external reproducibility, but the eval criteria (breadth-first research tasks, lead + subagent configuration) are described clearly enough to be approximately replicated. The 40% task completion improvement from model-assisted tool description rewriting is specific and plausible. The post is honest about failure modes and limitations (synchronous bottleneck, token cost, domains where multi-agent is a poor fit).

**Gaps and Limitations**:
- The internal research eval dataset and rubric are not published; the 90.2% figure cannot be independently reproduced.
- The BrowseComp regression does not distinguish causation from correlation — higher token usage may be a proxy for harder tasks allocated more agent resources, not a direct cause of performance.
- No breakdown of how the 90.2% improvement distributes across query types; breadth-first queries are the best case for this architecture, and the figure likely overstates gains for other query types.
- The subagent isolation claim (each subagent has its own context window) is architectural but the post does not describe how shared state (e.g., the plan in external memory) is accessed without collision when multiple subagents are running in parallel.
- The post does not describe the context handoff format from lead to subagent: what structure does the lead agent's subtask brief take, and how is it validated for completeness before dispatch?

---

## 7. Cross-Source Connections

- **Directly extends**: [anthropic-building-effective-agents](./anthropic-building-effective-agents.md) — this post instantiates the parallelisation and orchestrator-worker patterns from that source at production scale, with quantitative outcomes.
- **Referenced by**: [anthropic-com-engineering-effective-context-engineering-for-](./anthropic-com-engineering-effective-context-engineering-for-.md) — the context engineering post cites this source for the 90.2% improvement figure and credits this system as the production example of sub-agent context management.
- **Extends**: [cookbook-research-lead-agent](./cookbook-research-lead-agent.md) and [cookbook-research-subagent](./cookbook-research-subagent.md) — those sources contain the prompt templates this system actually uses; this post provides the architectural and evaluation context for understanding why those prompts are structured as they are.
- **Partially contradicts**: sources suggesting that single large-context-window models are sufficient for research tasks — this post provides concrete evidence that task decomposition across parallel context windows outperforms a single large window by 90.2% on the relevant task class.

---

## 8. Project Relevance

**H1 — Self-Loop Handoffs: gates and review checkpoints between lead and subagents**

The source **confirms and specifies** H1. The lead agent does not operate as a simple dispatcher; it enters an iterative research loop that includes explicit checkpoints:
- The lead agent synthesises subagent results and **decides whether more research is needed** before proceeding or exiting the loop.
- Subagents themselves implement a self-loop via interleaved thinking after each tool call — evaluating quality and gap-filling before returning results.
- A dedicated `CitationAgent` acts as a post-processing gate: all lead agent outputs pass through it before reaching the user.

This three-layer gate structure (subagent self-evaluation → lead agent approval loop → citation gate) is a richer and more specific instantiation of H1 than the hypothesis as originally stated. EndogenAI agent handoffs currently have no explicit review or approval checkpoint between delegation levels. The `handoffs:` YAML field in agent frontmatter defines where to route next but not what to check before routing. **ADOPT** — introduce explicit checkpoint semantics into the handoff model: at minimum, a post-completion evaluation step before the lead agent accepts subagent output.

**H2 — Prompt Enrichment Chain: context enrichment from human query to lead agent to subagents**

The source **complicates and partially refutes** H2. Context does not enrichen as it flows downward:
- The lead agent receives the raw user query, then *decomposes* it — the subtask brief dispatched to each subagent is narrower, not richer, than the original query.
- Subagents return condensed summaries (1K–2K tokens from potentially tens of thousands of tokens of exploration) — compression-on-ascent.
- The 90.2% performance improvement depends on **parallel token budget expansion** (multiple context windows running simultaneously), not on context enrichment at each delegation level.

What the 90.2% figure actually depends on, from the BrowseComp analysis: 80% of variance is explained by total token usage. The multi-agent architecture effectively multiplies total available token budget by the number of subagents. Model choice and tool call count explain the remaining 20%. The H2 label "Prompt Enrichment Chain" is potentially misleading: the chain compresses downward (focused task briefs) and aggregates upward (condensed summaries). A more accurate label for this project would be **Compression-on-Ascent / Focus-on-Descent**. **ADAPT** — revise H2 naming and description in the Issue #10 issue synthesis and in any design pattern documentation.

**H3 — Quasi-Encapsulated Sub-Fleets: subagent isolation and coherence mechanism**

The source **validates and specifies** H3 with important nuance. Subagent isolation is achieved through:
1. **Separate context windows**: each subagent operates in an independent context with no shared memory of other subagents' searches.
2. **Distinct task briefs**: the lead agent provides each subagent with a specific research objective, output format, and tool guidance; task briefs are designed to prevent duplication (a documented failure mode when briefs were too vague).
3. **External filesystem outputs**: subagents write large artifacts to external storage and return lightweight references — preventing any single subagent's output from bloating the lead agent's context.

Coherence is maintained through the **lead agent as sole integration point** — not through shared state between subagents. Subagents are explicitly isolated from each other. The "quasi-encapsulated" framing in H3 is accurate: subagents share the lead agent's memory store (for the plan) but do not communicate laterally.

For EndogenAI: the current multi-agent pattern in `.github/agents/` allows agents to read the shared `.tmp/` scratchpad, which partially breaks this isolation model. Agents reading a scratchpad written by another agent introduces the lateral-communication failure mode this system was designed to avoid. **ADAPT** — consider whether `.tmp/` scratchpad access should be scoped per-agent (write own section, read only own section) to preserve the isolation property that makes parallel execution safe and non-duplicative.

## Referenced By

<!-- Populated automatically by scripts/link_source_stubs.py — do not edit manually -->
- [A2Aproject Github Io A2A Latest Specification](../sources/a2aproject-github-io-A2A-latest-specification.md)
- [Agent Fleet Design Patterns](../agent-fleet-design-patterns.md)
- [Anthropic Building Effective Agents](../sources/anthropic-building-effective-agents.md)
- [Anthropic Com Engineering Effective Context Engineering For ](../sources/anthropic-com-engineering-effective-context-engineering-for-.md)
- [Cookbook Research Lead Agent](../sources/cookbook-research-lead-agent.md)
- [Cookbook Research Subagent](../sources/cookbook-research-subagent.md)
