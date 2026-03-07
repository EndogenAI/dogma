---
slug: "tds-claude-skills-subagents"
title: "Claude Skills and Subagents: Escaping the Prompt Engineering Hamster Wheel"
url: "https://towardsdatascience.com/claude-skills-and-subagents-escaping-the-prompt-engineering-hamster-wheel/"
authors: "Ruben Broekx"
year: "2026"
type: blog
topics: [agents, subagents, skills, context-management, token-economics, mcp, multi-agent, orchestration, lazy-loading, prompt-engineering]
cached: true
evidence_quality: opinion
date_synthesized: "2026-03-06"
cache_path: ".cache/sources/tds-claude-skills-subagents.md"
---

# Claude Skills and Subagents: Escaping the Prompt Engineering Hamster Wheel

**URL**: https://towardsdatascience.com/claude-skills-and-subagents-escaping-the-prompt-engineering-hamster-wheel/
**Type**: blog
**Cached**: `uv run python scripts/fetch_source.py https://towardsdatascience.com/claude-skills-and-subagents-escaping-the-prompt-engineering-hamster-wheel/ --slug tds-claude-skills-subagents`

## Citation

Broekx, R. (2026, February 28). *Claude Skills and Subagents: Escaping the Prompt Engineering Hamster Wheel*. Towards Data Science.
https://towardsdatascience.com/claude-skills-and-subagents-escaping-the-prompt-engineering-hamster-wheel/

## Research Question Addressed

How can AI-assisted development workflows escape the "prompt engineering hamster wheel" — the repeated, manual re-application of the same prompting patterns — through reusable, automatically invoked instruction artifacts? The article addresses the architecture of Claude Skills and Subagents as a systematic answer to context bloat, token cost, and the gap between raw model capability and domain-specific expertise.

## Theoretical / Conceptual Framework

The article operates within the **agentic infrastructure** paradigm: the claim that the marginal value of AI development has shifted from model capability to the scaffolding and architecture built around models. It draws on standard software-engineering abstractions — lazy loading, progressive disclosure, function encapsulation, and call-stack observability — and maps them onto LLM agent design. The conceptual centrepiece is the **skills-MCP-subagents triad**: skills provide expertise (the "how"), MCP provides capability (the "what"), and subagents provide context isolation (the "where"). The framing of subagents as "the new functions" is the article's most explicit theoretical move, grounding agent composition in first-principles software architecture.

## Methodology and Evidence

The article is a practitioner's blog post published in Towards Data Science (February 2026), authored by a working AI developer. Evidence is primarily experiential and anecdotal, supported by two forms of quantitative illustration: back-of-the-envelope token cost calculations (enumerating specific MCP server token overhead with concrete dollar figures) and a real worked example (the "feature branch wrap-up" / PR subagent workflow with a reproduced `change-report` skill). The author explicitly acknowledges the post reflects the state of Claude Skills as of February 2026 and that details may be outdated. There is no empirical study, controlled experiment, or peer review. The writing is editorial and opinionated, framed around a central thesis. The token cost arithmetic is independently reproducible and constitutes the closest thing to primary evidence in the piece.

## Key Claims

- **Prompt engineering hamster wheel**: Crafting a great prompt, then re-prompting from scratch each time the same behaviour is needed, is characterised as a "fundamentally broken workflow."
  > "This is what I call the *prompt engineering hamster wheel*. And it's a fundamentally broken workflow."

- **Skills as lazy-loaded context**: Skills are markdown files placed in `.claude/skills/` with a name, description, and body. At startup only name and description (~100 tokens) are loaded; the full body (~5,000 tokens) is loaded only when the agent determines relevance; referenced files are loaded on further demand.
  > "In essence, skills are lazy-loaded context. The agent doesn't consume the full instruction set upfront. It progressively discloses information to itself, pulling in only what's needed for the current step."

- **Three-level progressive disclosure**: Skills operate across metadata (startup), body (invocation), and referenced files (demand). Each level has its own context budget and is triggered only when needed.
  > "This progressive disclosure operates across three levels, each with its own context budget: 1. Metadata (loaded at startup)… 2. Skill body (loaded on invocation)… 3. Referenced files (loaded on demand)."

- **MCP token overhead is substantial**: A typical professional MCP setup (AWS ×3, Context7, Figma, GitHub, Linear, Serena, Sentry) costs ~32,000 tokens of metadata loaded into *every message* regardless of use.
  > "That's a total of roughly **~32,000 tokens** of tool metadata, loaded into *every single message*, whether you're interacting with the tool or not."

- **Idle MCP metadata has a real dollar cost**: At Claude Opus 4.6 pricing (~$5/M input tokens), 32K idle tokens adds $0.16 per message. At 50 messages/day over a 20-day month, that is ~$160/month in pure overhead before accounting for latency or quality effects.
  > "Let's say on average you send 50 messages a day over a 20-day work month, that's $8/day, **~$160/month** in *pure overhead*, just for tool descriptions sitting in context."

- **MCP is eager, skills are lazy — they are complementary, not competing**: MCP gives an agent capabilities; skills give it expertise. They serve different functions and work together.
  > "MCP gives an agent capabilities (the 'what'). Skills give it expertise (the 'how') and thus they're complementary."

- **Subagents provide isolated context and isolated tools**: A subagent starts with a clean context window, its own system prompt, and only its assigned tools. Its intermediate reasoning, dead ends, and API responses are discarded after completion — only the result returns to the main agent.
  > "Once a subagent finishes its task, its entire context is discarded. The tool metadata, the intermediate reasoning, the API responses: all gone. Only the result flows back to the main agent."

- **Subagents are lazy-loaded workers**: Just as skills are lazy-loaded context, subagents are lazy-loaded workers. The main agent knows what specialists it can call on and spins one up only when a task demands it.
  > "Similar to skills being lazy-loaded *context*, subagents are lazy-loaded *workers*: the main agent knows what specialists it can call on, and only spins one up when a task demands it."

- **Skills, MCP, and subagents operate in harmony**: The PR workflow example demonstrates the triad: skill provides the PR-structuring playbook, GitHub MCP provides create-PR capability, and the subagent provides a context boundary that keeps the main agent clean.
  > "The skill provides expertise and instruction, MCP provides the capability, the subagent provides the context boundary (keeping the main agent's context clean)."

- **Infrastructure value exceeds model value**: The author argues the centre of gravity in AI development has shifted from better models to better infrastructure.
  > "MCP and Claude Code were genuinely revolutionary. Upgrading Claude Sonnet from 3.5 to 3.7 honestly was not. The incremental model improvements we're getting today matter far less than the infrastructure we build around them."

- **Heterogeneous model routing for cost efficiency**: Multi-agent parallelism enables an expensive frontier model to orchestrate while cheaper models handle execution, matching Anthropic's own multi-agent research system design.
  > "This naturally leads to heterogeneous model routing, where an expensive frontier model orchestrates and plans, while smaller, cheaper models handle execution."

- **Subagents as functions — the abstraction argument**: A subagent maps to a function: input (task description), internal state (context window), tools (MCP servers), instructions (skills), and output. Benefits include isolation (blast-radius limitation), specialisation, composability, and observability.
  > "A subagent is a self-contained unit of work… That's a function. The main agent becomes the execution thread: orchestrating, branching, delegating, and synthesizing results from specialized workers."

- **Write concurrency is an open problem**: Parallelism works well for read tasks but produces inconsistency for write tasks that touch shared state, since subagents working from different snapshots can produce conflicting outputs.
  > "This is a classic concurrency problem, coming from the AI workflows of the near-future, which to date remains an open problem."

- **Skill composition and layered inheritance anticipated**: The author forecasts layered skills that reference other skills, creating an inheritance hierarchy of expertise (base skill → language-specific → team-specific).
  > "I expect skill composition to become more sophisticated. Today, skills are relatively flat… But the architecture naturally supports layered skills that reference other skills, creating something like an inheritance hierarchy of expertise."

- **A2A (Agent-to-Agent Protocol) as a peer-to-peer coordination layer**: Google's A2A could standardise agent-to-agent communication complementing MCP's agent-to-tool coverage, though adoption is slow and the author characterises it as "one to watch, not one to bet on yet."

## Critical Assessment

**Evidence Quality**: Opinion

The article is a practitioner's editorial, not a peer-reviewed study. Its token-cost arithmetic is internally consistent and reproducible, but the broader claims about quality degradation at long context lengths are stated rather than evidenced with citations. The "agents as functions" analogy is intellectually productive but is offered as framing, not empirical finding. The worked example (PR subagent) is illustrative and grounded in real practice, lending moderate credibility to its design claims.

**Gaps and Limitations**: The article is specific to Claude's Skills implementation and Claude Code's subagent model; it does not address whether equivalent lazy-loading patterns exist in other agent frameworks (LangGraph, AutoGen, CrewAI). The concurrency problem for write tasks is named as open but not explored at any depth. The forecast of skill inheritance hierarchies and widespread A2A adoption remains speculative. Cost figures use Claude Opus 4.6 pricing as of February 2026 and will not remain accurate over time. The article does not engage with the security or trust implications of subagent delegation (prompt injection, scope creep), which is a significant gap for production systems.

## Connection to Other Sources

- Agrees with / extends: [anthropic-building-effective-agents](./anthropic-building-effective-agents.md) — both sources advocate for composable, single-responsibility agent units; Broekx's "subagent as function" argument is a concrete instantiation of Anthropic's orchestrator/subagent pattern.
- Agrees with / extends: [claude-sdk-subagents](./claude-sdk-subagents.md) — directly covers the same subagent mechanics from a more API/SDK-centric angle; the two sources are complementary on the same topic.
- Agrees with / extends: [claude-code-agent-teams](./claude-code-agent-teams.md) — agent teams feature referenced in the "where it's heading" section is covered in depth there.
- Tangentially related: [a2a-announcement](./a2a-announcement.md) — the A2A protocol is mentioned as a peer-to-peer coordination layer; the announcement doc provides primary source detail.

## Relevance to EndogenAI

**ADOPT — Progressive disclosure as a first-class design principle for agent knowledge.** The EndogenAI agent fleet currently stores agent instructions in `.github/agents/*.agent.md` files, which are loaded wholesale into context. The skills pattern — metadata at startup, body on invocation, referenced files on demand — is directly applicable to the EndogenAI agent authoring convention. The `docs/guides/workflows.md` guide should be updated to codify progressive disclosure as a structural principle: agent frontmatter as the "metadata tier," the agent body as the "invocation tier," and linked external files as the "demand tier." This maps cleanly onto the three-level skills architecture without requiring any new infrastructure.

**ADOPT — Subagents as quasi-encapsulated context boundaries.** The article's central architectural argument — that subagents prevent intermediate reasoning from compounding into the main agent's context — directly validates and refines the "quasi-encapsulated sub-fleet" pattern that has been codified in this research session. The key insight to carry forward is that the isolation benefit is as much about *discarding intermediate tokens* as it is about *scoping tools*. The EndogenAI Research Workflow should explicitly state that sub-fleet agents (Scout, Synthesizer, Archivist) are to be treated as subagents: their dead-end searches, retried queries, and intermediate notes do not belong in the Executive's context. This aligns with the scratchpad convention in `AGENTS.md` (`.tmp/<branch>/<date>.md`) and strengthens the rationale for the phase-gate handoff model.

**ADAPT — Skills as a prompt library pattern for the Prompt Library deliverable (D3).** The article's `change-report` skill example is a direct demonstration of what a Prompt Library entry should look like: a named, versioned instruction set with a description, a body codifying procedure, and linked reference files (templates, schemas). The EndogenAI project should adapt this format when building out `docs/research/` prompt patterns — not as Claude-specific `.claude/skills/` files, but as analogous markdown artifacts callable by any agent in the fleet. The `scripts/scaffold_agent.py` script could be extended to scaffold skill-style prompt artifacts alongside agent files, encoding the progressive disclosure structure into the generator itself.

## Referenced By

<!-- Populated automatically by scripts/link_source_stubs.py — do not edit manually -->
- [A2A Announcement](../sources/a2a-announcement.md)
- [Agent Fleet Design Patterns](../agent-fleet-design-patterns.md)
- [Agentic Research Flows](../agentic-research-flows.md)
- [Anthropic Building Effective Agents](../sources/anthropic-building-effective-agents.md)
- [Claude Code Agent Teams](../sources/claude-code-agent-teams.md)
- [Claude Sdk Subagents](../sources/claude-sdk-subagents.md)
- [Freecodecamp Org News Build And Deploy Multi Agent Ai With P](../sources/freecodecamp-org-news-build-and-deploy-multi-agent-ai-with-p.md)
- [Github Com Letta Ai Letta](../sources/github-com-letta-ai-letta.md)
- [Xml Agent Instruction Format](../xml-agent-instruction-format.md)
