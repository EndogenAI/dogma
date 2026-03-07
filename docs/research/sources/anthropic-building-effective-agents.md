---
slug: "anthropic-building-effective-agents"
title: "Building effective agents"
url: "https://www.anthropic.com/engineering/building-effective-agents"
authors: "Erik Schluntz and Barry Zhang (Anthropic Engineering)"
year: "2024"
type: blog
topics: [agents, workflows, orchestration, tool-design, evaluator-optimizer, parallelization, routing, simplicity]
cached: true
evidence_quality: opinion
date_synthesized: "2026-03-06"
cache_path: ".cache/sources/anthropic-building-effective-agents.md"
---

# Building Effective Agents

**URL**: https://www.anthropic.com/engineering/building-effective-agents
**Type**: blog
**Cached**: `uv run python scripts/fetch_source.py https://www.anthropic.com/engineering/building-effective-agents --slug anthropic-building-effective-agents`

## Citation

Schluntz, E., & Zhang, B. (2024, December 19). *Building effective agents*. Anthropic Engineering.
https://www.anthropic.com/engineering/building-effective-agents

## Research Question Addressed

What architectural patterns and design principles lead to successful LLM-powered agentic systems in production? This post addresses how practitioners should choose between workflows and autonomous agents, which composable patterns best fit which task profiles, and how to engineer tools so that agents use them reliably.

## Theoretical / Conceptual Framework

The source operates within the **augmented-LLM agent loop** paradigm — a model enhanced with retrieval, tools, and memory acts as the core reasoning unit, and complexity is added through composition of a fixed pattern library rather than through monolithic frameworks. A central architectural distinction between *workflows* (LLMs orchestrated through predefined code paths) and *agents* (LLMs that dynamically direct their own processes and tool usage) anchors all prescriptive recommendations. The post implicitly applies a **complexity-proportionality principle**: every increase in architectural complexity must demonstrate a measurable improvement in outcomes before it is justified.

## Methodology and Evidence

The post is a practitioner synthesis by two Anthropic engineers drawing on "work with dozens of teams building LLM agents across industries" — it is experience-grounded opinion, not a controlled experiment. Evidence is anecdotal and pattern-based: the authors identify recurring structures across customer deployments and Anthropic's own internal agent work (including the SWE-bench coding agent and the Claude computer-use demo). The five workflow patterns (prompt chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer) are described with canonical use-case examples rather than empirical benchmarks. Two appendices extend the argument into specific domains (customer support, coding agents) and tool prompt-engineering practice, grounding the ACI concept in a concrete failure-and-fix story from the SWE-bench implementation. The source is well-structured and frankly self-aware about its limits: it recommends measuring performance and iterating, rather than prescribing fixed topologies. No quantitative data is provided.

## Key Claims

- > "Consistently, the most successful implementations weren't using complex frameworks or specialized libraries. Instead, they were building with simple, composable patterns."
  This is the central empirical claim — composite evidence from dozens of customer teams, not a controlled study.

- **Workflows vs. Agents is a hard architectural boundary**: "Workflows are systems where LLMs and tools are orchestrated through predefined code paths. Agents, on the other hand, are systems where LLMs dynamically direct their own processes and tool usage." Conflating the two leads to over-engineering simple pipelines or under-resourcing genuinely autonomous ones.

- > "We recommend finding the simplest solution possible, and only increasing complexity when needed. This might mean not building agentic systems at all."
  The null option (a single optimised LLM call with retrieval and in-context examples) is explicitly advocated; agentic systems are opt-in, not default.

- **Frameworks obscure the substrate**: "They often create extra layers of abstraction that can obscure the underlying prompts and responses, making them harder to debug. They can also make it tempting to add complexity when a simpler setup would suffice." Direct API use is recommended, with frameworks used only when understood fully.

- **Prompt chaining** "decomposes a task into a sequence of steps, where each LLM call processes the output of the previous one. You can add programmatic checks (see 'gate' in the diagram below) on any intermediate steps to ensure that the process is still on track." This is the pattern most directly analogous to the EndogenAI prompt-enrichment chain.

- **Routing** "classifies an input and directs it to a specialized followup task… Without this workflow, optimizing for one kind of input can hurt performance on other inputs." Routing is underutilised in most agentic pipelines; it is the pattern with the clearest ROI at scale.

- **Parallelization** comes in two distinct variants: *sectioning* (independent subtasks run in parallel) and *voting* (same task run N times for ensemble output). "LLMs generally perform better when each consideration is handled by a separate LLM call, allowing focused attention on each specific aspect."

- **Orchestrator-workers**: "a central LLM dynamically breaks down tasks, delegates them to worker LLMs, and synthesizes their results." The key differentiator from parallelization is "its flexibility — subtasks aren't pre-defined, but determined by the orchestrator based on the specific input." This is the EndogenAI Executive Researcher topology.

- **Evaluator-optimizer** is a generation-evaluation-feedback loop and is "particularly effective when we have clear evaluation criteria, and when iterative refinement provides measurable value." The criterion for good fit: if a human articulating feedback demonstrably improves LLM responses, an evaluator LLM can do the same thing.

- > "For the SWE-bench implementation, we actually spent more time optimizing our tools than the overall prompt."
  This is the strongest practical evidence in the post: tool definition quality dominates total agent performance at production depth.

- **Agent-Computer Interface (ACI)**: "Think about how much effort goes into human-computer interfaces (HCI), and plan to invest just as much effort in creating good agent-computer interfaces (ACI)." Good tool definitions include example usage, edge cases, input format requirements, and clear boundaries from other tools.

- **Poka-yoke your tools**: change tool arguments so that it is structurally harder for the model to make mistakes. Example given: requiring absolute file paths rather than relative ones eliminated an entire class of SWE-bench agent errors completely.

- **Stopping conditions are mandatory**: "Agents can then pause for human feedback at checkpoints or when encountering blockers… it's also common to include stopping conditions (such as a maximum number of iterations) to maintain control." Autonomy increases cost and compounds errors — explicit ceilings are not optional.

- **Ground truth at each step**: "it's crucial for the agents to gain 'ground truth' from the environment at each step (such as tool call results or code execution) to assess its progress." Agents that cannot access real environmental feedback hallucinate progress.

- **Three core principles for agents**: (1) Maintain simplicity in agent design. (2) Prioritize transparency by explicitly showing the agent's planning steps. (3) Carefully craft the ACI through thorough tool documentation and testing. These are stated as Anthropic's own operating principles, not recommendations derived from external research.

- **Coding agents succeed because feedback is verifiable**: "Code solutions are verifiable through automated tests; agents can iterate on solutions using test results as feedback." Tasks with objective, fast feedback loops are where autonomous agents show the largest gains over single-call LLMs.

- > "We suggest that developers start by using LLM APIs directly: many patterns can be implemented in a few lines of code. If you do use a framework, ensure you understand the underlying code."
  This directly supports the EndogenAI `minimal-posture` and `local-compute-first` constraints in `AGENTS.md`.

- **Model routing for token offloading**: "Routing easy/common questions to smaller, cost-efficient models like Claude Haiku 4.5 and hard/unusual questions to more capable models like Claude Sonnet 4.5 to optimize for best performance." Model routing is an explicit mechanism for reducing inference cost within the routing pattern — directly relevant to D4.

## Critical Assessment

**Evidence Quality**: Opinion

The source is practitioner opinion from product engineers at Anthropic — credible and internally consistent, but not peer-reviewed, not independently replicated, and tied to Anthropic's own ecosystem (Claude models, Anthropic API). The pattern taxonomy is derived from team experience rather than a systematic study of agentic architectures, which means coverage gaps are possible and selection bias toward patterns that fit Claude's capabilities is likely.

**Gaps and Limitations**: The post does not address multi-agent coordination protocols, state sharing across agents, or memory architectures beyond a passing mention. It says nothing about failure modes that emerge specifically from LLM non-determinism at fleet scale (e.g., cascading errors across orchestrator-worker topologies). The ACI appendix is the sharpest section but remains abstract — no templates, schema examples, or formal specification language is provided. The evaluator-optimizer section does not discuss convergence guarantees or termination conditions in the feedback loop, only asserting that iteration improves results. Publication date is December 2024; the agent SDK referenced in the framework list post-dates the article, so the framework survey is partially outdated relative to the cached version.

**Adoption risks for EndogenAI**: The source is firmly in Anthropic's ecosystem. Universal claims (e.g., "simple patterns beat complex frameworks") may not hold equally across other model providers or open-source stacks. The Poka-yoke tool advice requires knowing in advance what mistakes the model is likely to make — this is easy for Anthropic given internal eval suites, but harder for a small project without automated evaluation infrastructure.

## Connection to Other Sources

- [claude-sdk-subagents](./claude-sdk-subagents.md) — extends the orchestrator-workers pattern into the Claude SDK's native sub-agent API; the SDK post operationalises what this post describes architecturally.
- [cookbook-research-lead-agent](./cookbook-research-lead-agent.md) — a concrete implementation of the orchestrator-workers pattern, verifying this post's claims about subtask delegation in practice.
- [cookbook-research-subagent](./cookbook-research-subagent.md) — implements the worker side of the orchestrator-workers pattern; together with the lead agent cookbook, validates the pattern's real-world structure.
- [arxiv-react](./arxiv-react.md) — ReAct is the theoretical foundation for the agent loop described here ("ground truth at each step"); this post is the applied, industrial-pattern version of ReAct's academic framing.
- [arxiv-generative-agents](./arxiv-generative-agents.md) — generative agents research grounds the memory and planning assumptions underlying the autonomous agent section; this post does not cite it but operates in the same design space.
- [tds-claude-skills-subagents](./tds-claude-skills-subagents.md) — applies the same composable-patterns thesis to Claude's skills system; broadly supports the post's simplicity-first claims.

## Relevance to EndogenAI

The **evaluator-optimizer pattern** is the direct conceptual ancestor of the EndogenAI Reviewer phase gate. `.github/agents/research-reviewer.agent.md` runs exactly the generate-evaluate-feedback loop described here. The alignment is strong enough to ADOPT the post's precise evaluation criteria language ("clear evaluation criteria" + "demonstrable improvement from feedback") directly into that agent's mandate block — this would tighten the Reviewer's self-termination logic, which currently lacks an explicit convergence criterion. The post also validates the overall Executive Researcher → Scout → Synthesizer → Reviewer → Archivist delegation chain as an orchestrator-workers pattern, confirming the architecture is on established ground.

The **ACI appendix** indicts current EndogenAI tool documentation practice. Both `scripts/fetch_source.py` and `scripts/link_source_stubs.py` lack parameter-level docstrings, edge-case notes, and worked usage examples of the kind Anthropic says are mandatory for reliable agent tool use. ADOPT the Poka-yoke principle specifically: `fetch_source.py` should enforce absolute path output for `cache_path` fields, and `link_source_stubs.py` should validate slug-to-file mappings before writing, structurally preventing the most common agent tool errors in live research sessions. This recommendation feeds directly into gate deliverable D4 (token offloading through better tool design reduces retry loops).

The **stopping conditions requirement** exposes a genuine gap in `.github/agents/executive-researcher.agent.md`: there is no explicit iteration ceiling or budget gate. The post calls this mandatory for any autonomous agent ("the autonomous nature of agents means higher costs, and the potential for compounding errors"). ADAPT: add a `max_scout_rounds` parameter and an explicit escalation path (stop and report to user vs. push to next phase) to the Executive Researcher instructions. This aligns with the self-loop phase gate pattern codified in the active research question and feeds into D2 (`docs/guides/workflows.md`).

The **routing workflow** is completely absent from the EndogenAI research pipeline. The Scout currently receives all research queries through an undifferentiated entry point — there is no classification gate that strips narrow factual queries to a simpler single-call path and reserves full multi-source orchestration for genuine synthesis questions. ADAPT: add a routing step at the top of `docs/guides/workflows.md` as the recommended first architectural decision for any new research flow; model routing to cheaper local models for narrow queries is the direct mechanism for D4 (token offloading). The workflows-vs-agents distinction also has direct import for `docs/guides/agents.md`, which currently conflates the two; the precise Anthropic vocabulary should be ADOPTED verbatim into that guide.

## Referenced By

<!-- Populated automatically by scripts/link_source_stubs.py — do not edit manually -->
- [A2A Announcement](../sources/a2a-announcement.md)
- [A2Aproject Github Io A2A Latest Specification](../sources/a2aproject-github-io-A2A-latest-specification.md)
- [Agent Fleet Design Patterns](../agent-fleet-design-patterns.md)
- [Agentic Research Flows](../agentic-research-flows.md)
- [Anthropic Com Engineering Effective Context Engineering For ](../sources/anthropic-com-engineering-effective-context-engineering-for-.md)
- [Anthropic Com Engineering Multi Agent Research System](../sources/anthropic-com-engineering-multi-agent-research-system.md)
- [Arxiv Context Engineering Survey](../sources/arxiv-context-engineering-survey.md)
- [Arxiv Generative Agents](../sources/arxiv-generative-agents.md)
- [Arxiv Org Html 2512 05470V1](../sources/arxiv-org-html-2512-05470v1.md)
- [Arxiv React](../sources/arxiv-react.md)
- [Claude Code Agent Teams](../sources/claude-code-agent-teams.md)
- [Claude Sdk Subagents](../sources/claude-sdk-subagents.md)
- [Code Claude Com Docs En Sub Agents](../sources/code-claude-com-docs-en-sub-agents.md)
- [Code Visualstudio Com Api Extension Guides Chat](../sources/code-visualstudio-com-api-extension-guides-chat.md)
- [Code Visualstudio Com Docs Copilot Customization Custom Agen](../sources/code-visualstudio-com-docs-copilot-customization-custom-agen.md)
- [Cookbook Citations Agent](../sources/cookbook-citations-agent.md)
- [Cookbook Research Lead Agent](../sources/cookbook-research-lead-agent.md)
- [Cookbook Research Subagent](../sources/cookbook-research-subagent.md)
- [Freecodecamp Org News Build And Deploy Multi Agent Ai With P](../sources/freecodecamp-org-news-build-and-deploy-multi-agent-ai-with-p.md)
- [Github Com Getzep Graphiti](../sources/github-com-getzep-graphiti.md)
- [Github Com Mem0Ai Mem0](../sources/github-com-mem0ai-mem0.md)
- [Kdnuggets Com Docker Ai For Agent Builders Models Tools And ](../sources/kdnuggets-com-docker-ai-for-agent-builders-models-tools-and-.md)
- [Microsoft Github Io Autogen Stable User Guide Agentchat User](../sources/microsoft-github-io-autogen-stable-user-guide-agentchat-user.md)
- [Opensourceprojects Dev Post E7415816 A348 4936 B8Bd 0C651C4A](../sources/opensourceprojects-dev-post-e7415816-a348-4936-b8bd-0c651c4a.md)
- [Platform Claude Com Docs En Agents And Tools Agent Skills Ov](../sources/platform-claude-com-docs-en-agents-and-tools-agent-skills-ov.md)
- [Platform Claude Com Docs En Build With Claude Prompt Enginee](../sources/platform-claude-com-docs-en-build-with-claude-prompt-enginee.md)
- [Platform Openai Com Docs Api Reference Assistants](../sources/platform-openai-com-docs-api-reference-assistants.md)
- [Platform Openai Com Docs Guides Prompt Engineering](../sources/platform-openai-com-docs-guides-prompt-engineering.md)
- [Python Langchain Com Docs Concepts Agents](../sources/python-langchain-com-docs-concepts-agents.md)
- [Tds Claude Skills Subagents](../sources/tds-claude-skills-subagents.md)
- [Xda Developers Com Youre Using Local Llm Wrong If Youre Prom](../sources/xda-developers-com-youre-using-local-llm-wrong-if-youre-prom.md)
- [Xml Agent Instruction Format](../xml-agent-instruction-format.md)
