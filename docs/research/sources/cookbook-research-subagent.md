---
slug: "cookbook-research-subagent"
title: "Research Subagent System Prompt (Anthropic Cookbook)"
url: "https://github.com/anthropics/anthropic-cookbook/tree/main/multiagent"
authors: "Anthropic"
year: "2025"
type: cookbook
topics: [subagents, multi-agent, research-pipeline, OODA, tool-use, orchestration, prompt-engineering, epistemic-practice]
cached: true
evidence_quality: documentation
date_synthesized: "2026-03-06"
---

## Citation

Anthropic. (2025). *Research subagent system prompt* [Cookbook recipe]. Anthropic Cookbook — Multi-Agent Research.
https://github.com/anthropics/anthropic-cookbook/tree/main/multiagent
(Accessed 2026-03-06 via cached distillation at `.cache/sources/cookbook-research-subagent.md`)

## Research Question Addressed

How should a research subagent be instructed to behave when delegated a bounded task by a lead orchestrator in a multi-agent pipeline? This system prompt answers the question of sub-agent-level research discipline: how to plan work, budget tool calls, select the right tools, reason about source quality, and return a condensed report without over-running context or exceeding resource limits.

## Theoretical / Conceptual Framework

The prompt operates within a **multi-agent orchestration** paradigm in which a *lead agent* decomposes a research problem and delegates bounded sub-tasks to specialist *research subagents*. Each subagent executes a closed OODA loop (Observe → Orient → Decide → Act) and returns results to the orchestrator via a `complete_task` tool call. The framing is purely pragmatic — no named framework is cited internally — but the observable intellectual lineage includes:

- **OODA loop** (Boyd, military decision cycle): named explicitly as the inner research loop.
- **ReAct-style self-monitoring**: the subagent is instructed to review what has been gathered, what remains, and which tool to invoke next after each result.
- **Satisficing under resource constraint**: a finite "research budget" caps tool calls per task, prioritising efficiency over exhaustiveness.

## Methodology and Evidence

This document is a prescriptive **system prompt** — a full instruction set issued to a Claude instance at the start of a research subagent session. It is not a paper or study; evidence for its efficacy is Anthropic's deployment experience rather than a published evaluation. The prompt is structured as five tagged sections (`<research_process>`, `<research_guidelines>`, `<think_about_source_quality>`, `<use_parallel_tool_calls>`, `<maximum_tool_call_limit>`), each governing a distinct behavioural domain. The `<research_process>` section is the most detailed, specifying a three-stage workflow: *Planning → Tool selection → Research loop*. Tool categories are enumerated with example mappings (web_search for snippets, web_fetch for full pages, GDrive/Gmail for internal data). The epistemics section is notable for its specificity: it enumerates 12+ surface markers of low-quality sources that the agent should recognise and flag rather than report uncritically.

## Key Claims

- **Complexity-tiered research budget**: task complexity is explicitly binned and linked to tool-call quotas. Simple tasks (e.g. "when is the tax deadline") → under 5 calls; medium → ~5 calls; hard → ~10 calls; very difficult / multi-part → up to 15 calls.
  > "Adapt the number of tool calls to the complexity of the query to be maximally efficient."

- **OODA as inner loop**: the named inner cycle is Observe-Orient-Decide-Act, executed repeatedly until the task is resolved. Each iteration must reassess both what has been learned and which tool to invoke next.
  > "Execute an excellent OODA (observe, orient, decide, act) loop by (a) observing what information has been gathered so far..."

- **Internal tools take strict priority**: when internal data sources (GDrive, Gmail, GCal, Slack, project management tools) are present, the subagent is *required* to use them ahead of web search.
  > "Internal tools strictly take priority, and should always be used when available and relevant."

- **web_search → web_fetch as the canonical fetch pattern**: search results are treated as snippet indices; full-page retrieval is mandatory in three cases: (1) when more detail would help, (2) when following up on search results, (3) when a URL is provided directly.
  > "ALWAYS use `web_fetch` to get the complete contents of websites, in all of the following cases..."

- **Minimum five distinct tool calls**: the subagent is assigned a floor, not just a ceiling, on research effort — preventing premature resolution.
  > "Execute a MINIMUM of five distinct tool calls, up to ten for complex queries."

- **Hard ceiling of 20 tool calls / 100 sources**: an absolute limit prevents context overrun. At ~15 calls or 100 sources, the agent must stop gathering and compose its report.
  > "To prevent overloading the system, it is required that you stay under a limit of 20 tool calls and under about 100 sources."

- **Parallel tool invocation as a first-class efficiency norm**: multiple independent operations must be issued simultaneously rather than sequentially, specifically to minimise wall-clock latency and token overhead.
  > "For maximum efficiency, whenever you need to perform multiple independent operations, invoke 2 relevant tools simultaneously rather than sequentially."

- **Decreasing-returns exit criterion**: the agent is explicitly instructed to stop when results are no longer novel, rather than exhausting its budget.
  > "Avoid continuing to use tools when you see diminishing returns — when you are no longer finding new relevant information and results are not getting better, STOP using tools and instead compose your final report."

- **Moderate query breadth**: hyper-specific queries are flagged as error-prone. Shorter, moderately broad queries are prescribed with the instruction to narrow only when results are abundant.
  > "Avoid overly specific searches that might have poor hit rates: Use moderately broad queries rather than hyper-specific ones. Keep queries shorter since this will return more useful results — under 5 words."

- **Internal/concise duality in reporting**: the agent is instructed to be verbose internally (within its reasoning/scratchpad) but deliver information-dense, concise final reports to the lead agent.
  > "Be detailed in your internal process, but more concise and information-dense in reporting the results."

- **Epistemic surface-marker enumeration**: the quality-check section enumerates specific linguistic and structural signals of poor sources: future-tense speculation, passive voice with unnamed sources, marketing language, unconfirmed reports, cherry-picked data, and false authority — and requires explicit flagging rather than silent omission.
  > "Pay attention to the indicators of potentially problematic sources, like news aggregators rather than original sources... spin language, speculation, or misleading and cherry-picked data."

- **Conflict resolution protocol**: when sources contradict each other, the agent should prioritise based on recency, consistency, and source quality — and if it cannot resolve the conflict, it must surface both readings to the lead researcher explicitly.
  > "When encountering conflicting information, prioritize based on recency, consistency with other facts... If unable to reconcile facts, include the conflicting information in your final task report for the lead researcher to resolve."

- **complete_task as the required exit mechanism**: the subagent session terminates only via the `complete_task` tool call, which delivers the final condensed report upstream. There is no implicit exit.
  > "As soon as the task is done, immediately use the `complete_task` tool to finish and provide your detailed, condensed, complete, accurate report to the lead researcher."

## Critical Assessment

**Evidence Quality**: Documentation

This is an internal system prompt, not a peer-reviewed study or externally validated methodology. It represents Anthropic's engineering opinion on how their cookbook-style multi-agent research pipeline should operate. No ablation studies, latency benchmarks, or quality comparisons are provided. The implicit evidence base is Anthropic's internal deployment experience with Claude-based multi-agent systems.

**Gaps and Limitations**: The prompt is written for a specific toolset (web_search, web_fetch, Google Workspace, repl) and assumes a live-internet-capable agent. It does not address offline or air-gapped research contexts, nor the case where no internal tools exist. The tool-call budget tiers are asserted without empirical backing — the specific numbers (5/10/15) appear to be heuristic rather than derived from experiments. The prompt contains no guidance on how the subagent should handle task ambiguity before beginning (it is assumed the `<task>` block is well-specified by the lead agent). There is also no explicit mechanism for the subagent to *request clarification* from the orchestrator mid-task — bidirectional communication is absent. Finally, the cached version is the complete system prompt (not an abstract), so this is a full-fidelity synthesis.

## Connection to Other Sources

- Agrees with / extends: [anthropic-building-effective-agents.md](./anthropic-building-effective-agents.md) — the parallelisation, tool-selection, and satisficing principles here mirror the "parallelization" and "orchestrator-subagent" patterns described there.
- Agrees with / extends: [cookbook-research-lead-agent.md](./cookbook-research-lead-agent.md) — this subagent prompt is the complementary counterpart to the lead-agent prompt; together they define the two roles in the Anthropic cookbook multi-agent research pipeline.
- Agrees with / extends: [claude-sdk-subagents.md](./claude-sdk-subagents.md) — the OODA inner loop and `complete_task` exit mechanism align with SDK-level subagent lifecycle patterns documented there.

## Relevance to EndogenAI

**ADOPT — OODA budget structure into the Research Workflow**. The complexity-tiered research budget (simple / medium / hard / very-hard → <5 / 5 / 10 / 15 tool calls) is directly transferable to the EndogenAI research workflow. The Scout agent defined in `.github/agents/` currently has no formal budget discipline — sessions can over-run or return prematurely depending on the complexity of the query. Encoding this tier table into the Scout agent's frontmatter instructions (or as a note in `docs/guides/workflows.md`) would impose consistent effort-scaling without requiring orchestrator-level enforcement per task. The decreasing-returns exit criterion is an equally important companion: the Scout should stop when results plateau, not when the budget is exhausted.

**ADOPT — Parallel tool invocation as default posture for the Research Subagent role**. The mandate to invoke independent operations simultaneously rather than sequentially maps directly onto the `AGENTS.md` constraint that agents should batch discovery. This is already a guiding principle in this repo's AGENTS.md; the cookbook prompt validates the approach and provides specific language ("2 relevant tools simultaneously") that can be quoted or paraphrased in the Scout agent's instructions to make the norm explicit.

**ADAPT — Epistemic surface-marker checklist for the Synthesizer pass**. The detailed enumeration of source-quality warning signals (passive voice with unnamed sources, future-tense speculation, marketing language, cherry-picked data) is a strong candidate for D3 (Prompt Library). The current Research Synthesizer mode instructions reference source quality in general terms. Adding the specific surface markers as a structured checklist — either inline in the Synthesizer system prompt or as a reference card in `docs/guides/workflows.md` — would make the `## Critical Assessment` section of source synthesis documents more consistent and auditable. The conflict-resolution protocol (surface both readings when irreconcilable) should also be adopted into the Synthesizer's `## Critical Assessment` section guidance.

## Referenced By

<!-- Populated automatically by scripts/link_source_stubs.py — do not edit manually -->
- [Agent Fleet Design Patterns](../agent-fleet-design-patterns.md)
- [Agentic Research Flows](../agentic-research-flows.md)
- [Anthropic Building Effective Agents](../sources/anthropic-building-effective-agents.md)
- [Anthropic Com Engineering Multi Agent Research System](../sources/anthropic-com-engineering-multi-agent-research-system.md)
- [Claude Sdk Subagents](../sources/claude-sdk-subagents.md)
- [Code Visualstudio Com Docs Copilot Customization Custom Agen](../sources/code-visualstudio-com-docs-copilot-customization-custom-agen.md)
- [Cookbook Citations Agent](../sources/cookbook-citations-agent.md)
- [Cookbook Research Lead Agent](../sources/cookbook-research-lead-agent.md)
- [Platform Claude Com Docs En Build With Claude Prompt Enginee](../sources/platform-claude-com-docs-en-build-with-claude-prompt-enginee.md)
- [Xml Agent Instruction Format](../xml-agent-instruction-format.md)
