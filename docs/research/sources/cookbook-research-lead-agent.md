---
slug: "cookbook-research-lead-agent"
title: "Research Lead Agent System Prompt (Cookbook)"
url: "https://github.com/anthropics/anthropic-cookbook"
authors: "Anthropic (cookbook contributors)"
year: "2025"
type: cookbook
topics: [agents, orchestration, multi-agent, subagents, research-workflows, query-classification, delegation, parallel-tool-use, synthesis]
cached: true
evidence_quality: documentation
date_synthesized: "2026-03-06"
---

## Citation

Anthropic. (2025). *Research Lead Agent — system prompt* [Cookbook entry]. Anthropic Cookbook.
https://github.com/anthropics/anthropic-cookbook  
(Accessed via distilled cache: `.cache/sources/cookbook-research-lead-agent.md`)

## Research Question Addressed

How should a lead orchestrator agent structure its internal workflow to decompose arbitrary research queries, delegate to parallel sub-agents, manage synthesis, and produce a final report? The prompt encodes an opinionated, prescriptive answer: a five-stage process (assessment → query-type classification → plan development → plan execution → answer formatting) with explicit subagent-count heuristics, delegation instructions, and guardrails against over-research.

## Theoretical / Conceptual Framework

The source operates within the **orchestrator-workers** pattern as described in Anthropic's *Building Effective Agents* blog post, applied to the specific domain of research. The three-way query typology — **depth-first** (multiple perspectives on one question), **breadth-first** (parallel independent sub-questions), and **straightforward** (single-agent fact-finding) — is the central conceptual innovation that determines the entire plan-development branch. This taxonomy is not derived from academic agent theory; it is an applied engineering heuristic encoding when parallelisation pays and when it wastes tokens. The prompt also embeds a **Bayesian update posture** for handling incoming subagent results: "use Bayesian reasoning to update your priors, and then think carefully about what to do next." The intellectual heritage is the ReAct loop (reason → act → observe → reason), extended with explicit fleet management and a hard early-termination rule.

## Methodology and Evidence

This is a **prescriptive system prompt** produced by Anthropic's cookbook team — a practitioner artifact, not a research paper. It encodes accumulated operational experience into a durable instruction set for a deployed orchestrator agent. Evidence for its design choices is implicit: the specificity of subagent-count ranges (1 for simple, 2–3 for standard, 3–5 for medium, 5–20 max for high complexity) and the precision of the delegation instruction template imply iteration against real query sets. The source is structured as a single long-form XML-delimited prompt with five tagged sections: `<research_process>`, `<subagent_count_guidelines>`, `<delegation_instructions>`, `<answer_formatting>`, and `<important_guidelines>`. Each section contains numbered rules and worked examples. The worked examples (semiconductor supply chains, Fortune 500 CEOs, EU tax systems, cloud providers, healthcare AI) are illustrative but not evaluated against benchmarks. No ablation studies, failure-mode analyses, or output quality metrics are included.

## Key Claims

- **Five-stage research process as executable loop**: The prompt mandates "Assessment and breakdown → Query type determination → Detailed research plan development → Methodical plan execution → Answer formatting" in strict order before any subagent is invoked. Skipping assessment is treated as a process violation, not an efficiency gain.

- **Query-type classification gates parallelisation strategy**:
  > "Depth-first query: When the problem requires multiple perspectives on the same issue… Breadth-first query: When the problem can be broken into distinct, independent sub-questions… Straightforward query: When the problem is focused, well-defined, and can be effectively answered by a single focused investigation."
  The classification is the highest-leverage decision in the prompt; all subagent-count and delegation choices flow deterministically from it.

- **Minimum subagent floor of 1**: "Always create at least 1 subagent, even for simple tasks." This is non-negotiable — even a straightforward query requires at least one delegated research step to enforce source-gathering discipline and distribute work. The lead agent should not self-research the entire question.

- **Hard subagent ceiling of 20**:
  > "IMPORTANT: Never create more than 20 subagents unless strictly necessary. If a task seems to require more than 20 subagents, it typically means you should restructure your approach to consolidate similar sub-tasks."
  The ceiling is both resource and quality control: more subagents above a threshold produce diminishing returns through coordination overhead.

- **Subagent task descriptions must be exhaustive**: The example task description for semiconductor supply chains is ~150 words containing specific databases (SEC EDGAR), specific agencies (SEMI, Gartner, IDC), specific URLs (commerce.gov, ec.europa.eu), output format expectations, and scope constraints. The standard is explicitly: "IF all the subagents followed their instructions very well, the results in aggregate would allow you to give an EXCELLENT answer."

- **Lead agent role is coordination and synthesis, not primary research**:
  > "As the lead research agent, your primary role is to coordinate, guide, and synthesize - NOT to conduct primary research yourself. You only conduct direct research if a critical question remains unaddressed by subagents."
  This enforces a clean orchestrator/worker separation and prevents the lead from filling token context with raw browsing.

- **Parallel subagent deployment is mandatory for non-trivial queries**:
  > "You MUST use parallel tool calls for creating multiple subagents (typically running 3 subagents at the same time) at the start of the research."
  Parallel invocation is not a performance optimisation — it is the default posture. Sequential delegation is the exception, reserved for tasks with genuine serial dependencies.

- **Early termination is a first-class obligation**:
  > "When you have reached the point where further research has diminishing returns and you can give a good enough answer to the user, STOP FURTHER RESEARCH and do not create any new subagents."
  This is stated as a hard rule rather than a suggestion. The prompt frames over-research as a wasteful error symmetrical to under-research.

- **Dependency ordering governs subagent sequencing**:
  > "Consider priority and dependency when ordering subagent tasks — deploy the most important subagents first. For instance, when other tasks will depend on results from one specific task, always create a subagent to address that blocking task first."
  This is the standard topological-sort principle from distributed task scheduling, applied to LLM fleet management.

- **Internal tools must be used when available**:
  > "Never neglect using any additional available tools, as if they are present, the user definitely wants them to be used."
  The prompt enforces a `minimal-posture-violation` rule in the opposite direction for integrations: if Slack/Asana/Drive tools exist, one read-only call must be made even for queries that don't obviously require them. This is the integration surface awareness heuristic.

- **Breadth-first queries follow a two-phase pattern**: First, enumerate all sub-questions (often via one preliminary subagent); second, deploy parallel subagents against the complete enumeration. The Fortune 500 CEO example explicitly sequences: enumerate CEOs first, then split across 10 subagents of 50 each — preventing over-splitting before the full scope is known.

- **Lead agent should time-slice during blocking subagent calls**:
  > "While waiting for a subagent to complete, use your time efficiently by analyzing previous results, updating your research plan, or reasoning about the user's query."
  This is a cost-reduction heuristic: the lead should not idle. In practice it means the lead's reasoning trace during waiting improves synthesis quality.

- **Synthesis is always the lead agent's task; never delegated**:
  > "NEVER create a subagent to generate the final report — YOU write and craft this final research report yourself."
  This is stated in all-caps, indicating it is a hard constraint that was observed to be violated in practice (and presumably produced degraded outputs when it was). The final integration step requires the full cross-subagent context that only the lead holds.

- **Subagent harm scope limitation**: "Avoid creating subagents to research topics that could cause harm… If a query is sensitive, specify clear constraints for the subagent to avoid causing harm." Harm constraints propagate down through delegation; the lead bears responsibility for what subagents search.

- **Bayesian updating posture for subagent results**: "Critically think about the results provided by subagents and reason about them carefully to verify information and ensure you provide a high-quality, accurate report." Results are not accepted at face value — they are integrated into an evolving model of what is known.

- **Answer formatting defers citations to a separate agent**: "Do not include ANY Markdown citations, a separate agent will be responsible for citations. Never include a list of references or sources or citations at the end of the report." This is a clean separation of concerns: synthesis and citation attribution are decoupled into separate agents.

## Critical Assessment

**Evidence Quality**: Documentation

This is a first-party Anthropic cookbook artifact — authoritative for how Anthropic intends its orchestrator pattern to be used, but not independently reviewed or benchmarked. It encodes practical engineering decisions rather than empirically derived findings. The prompt's heuristics (subagent count ranges, parallel-by-default posture, hard ceiling of 20) are stated without justification beyond implicit operational experience. There is no evaluation framework, no ablation showing why these exact thresholds were chosen, and no failure-mode taxonomy.

**Gaps and Limitations**: The prompt does not address state management across subagent calls — how to handle partial failures, retry semantics, or inconsistent findings from parallel subagents. It provides no guidance on token budget management (the hard ceiling of 20 helps but does not address per-subagent context depth). The query-type taxonomy is binary in practice (depth vs. breadth), and many real-world research questions are hybrid — the prompt acknowledges this implicitly via the "update your plan" instruction but provides no structured hybrid resolution path. The prompt assumes subagents have reliable web search tools; it does not address degraded-tool scenarios. The citation-separation design (a separate agent handles citations) is mentioned but unexplained — that companion agent's prompt is not in scope here. Finally, the cookbook is designed around Claude-family models; subagent coordination via `run_blocking_subagent` is a Claude-specific tool call.

## Connection to Other Sources

- Agrees with / extends: [anthropic-building-effective-agents](./anthropic-building-effective-agents.md) — this prompt is a direct production instantiation of the orchestrator-workers pattern described there; all five abstract patterns from that post appear in this prompt's structure.
- Agrees with / extends: [claude-sdk-subagents](./claude-sdk-subagents.md) — the `run_blocking_subagent` tool this prompt relies on is the SDK-level primitive described in that source; the two sources occupy adjacent layers of the same stack.
- Contextualises: [arxiv-context-engineering-survey](./arxiv-context-engineering-survey.md) — the five-stage plan prior to subagent deployment is an instance of structured context engineering; this prompt operationalises what the survey describes theoretically.

## Relevance to EndogenAI

The **query-type classification step** (depth-first / breadth-first / straightforward) speaks directly to a gap in `docs/guides/workflows.md`. The EndogenAI research workflow currently routes all incoming research requests through the same full Scout → Synthesizer → Reviewer → Archivist pipeline regardless of question type. This prompt provides a tested decision heuristic to add a **pre-Scout routing gate**: narrow factual queries should be deflected to a single-call path or a lightweight single-subagent Scout, while genuine synthesis questions invoke the full fleet. ADOPT this classification scheme verbatim into `docs/guides/workflows.md` as the first decision node in any research session. It also provides the vocabulary missing from `.github/agents/executive-researcher.agent.md`, which currently lacks explicit guidance on when to use parallel vs. sequential Scout invocations — the depth-first/breadth-first framing resolves this directly.

The **early-termination obligation** ("STOP FURTHER RESEARCH… do not create any new subagents") maps directly onto the self-loop phase gate pattern in the active research question. The EndogenAI Executive Researcher agent has no explicit termination criterion — the implicit assumption is that the Reviewer phase gate handles this, but the Reviewer fires only after all Scouts complete, not during. ADOPT the early-termination heuristic as an intra-Scout gate: once the Executive Researcher can answer the gate deliverables from `OPEN_RESEARCH.md` without additional sources, new Scout invocations must stop. This closes the compounding-cost failure mode identified in `anthropic-building-effective-agents.md` and aligns with the `local-compute-first` constraint in `AGENTS.md`.

The **citation-separation design** (synthesis agent produces the body; a separate agent handles references) is directly relevant to the Archivist's current scope. `.github/agents/` currently has no dedicated citation-attribution agent; the Archivist bundles commit preparation with reference formatting. ADAPT the citation-separation pattern by either splitting the Archivist into archivist + citation-formatter roles, or by standardising that the Synthesizer's output always ends with a `## Sources` stub that the Archivist populates — never the Synthesizer itself. This would eliminate the recurring inconsistency in `## Referenced By` sections where source stubs are partially populated before `scripts/link_source_stubs.py` runs.

The **subagent instruction quality standard** ("IF all the subagents followed their instructions very well, the results in aggregate would allow you to give an EXCELLENT answer") is an actionable quality criterion for Scout delegation prompts in `.github/agents/executive-researcher.agent.md`. Current Scout invocation prompts in the EndogenAI workflow are sparse. ADOPT this standard as an evaluation heuristic: before invoking a Scout, the Executive should be able to answer "if this Scout returns exactly what I've asked for, is that sufficient for the gate deliverables?" If not, the Scout prompt is under-specified. This is a concrete quality gate that can be encoded as a checklist in the Executive Researcher agent's instructions.

## Referenced By

<!-- Populated automatically by scripts/link_source_stubs.py — do not edit manually -->
- [Agent Fleet Design Patterns](../agent-fleet-design-patterns.md)
- [Agentic Research Flows](../agentic-research-flows.md)
- [Anthropic Building Effective Agents](../sources/anthropic-building-effective-agents.md)
- [Anthropic Com Engineering Multi Agent Research System](../sources/anthropic-com-engineering-multi-agent-research-system.md)
- [Arxiv Context Engineering Survey](../sources/arxiv-context-engineering-survey.md)
- [Arxiv React](../sources/arxiv-react.md)
- [Claude Sdk Subagents](../sources/claude-sdk-subagents.md)
- [Code Visualstudio Com Docs Copilot Customization Custom Agen](../sources/code-visualstudio-com-docs-copilot-customization-custom-agen.md)
- [Cookbook Citations Agent](../sources/cookbook-citations-agent.md)
- [Cookbook Research Subagent](../sources/cookbook-research-subagent.md)
- [Freecodecamp Org News Build And Deploy Multi Agent Ai With P](../sources/freecodecamp-org-news-build-and-deploy-multi-agent-ai-with-p.md)
- [Platform Claude Com Docs En Build With Claude Prompt Enginee](../sources/platform-claude-com-docs-en-build-with-claude-prompt-enginee.md)
- [Xml Agent Instruction Format](../xml-agent-instruction-format.md)
