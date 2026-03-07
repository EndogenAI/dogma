---
slug: "claude-code-agent-teams"
title: "Run agent teams — Claude Code Documentation"
url: "https://docs.anthropic.com/docs/en/agent-teams"
authors: "Anthropic (product documentation)"
year: "2025"
type: documentation
topics: [agents, multi-agent, orchestration, parallelism, task-coordination, quality-gates, hooks, subagents, claude-code]
cached: true
evidence_quality: documentation
date_synthesized: "2026-03-06"
cache_path: ".cache/sources/claude-code-agent-teams.md"
---

# Run agent teams — Claude Code Documentation

**URL**: https://docs.anthropic.com/docs/en/agent-teams
**Type**: documentation
**Cached**: `uv run python scripts/fetch_source.py https://docs.anthropic.com/docs/en/agent-teams --slug claude-code-agent-teams`

## Citation

Anthropic. (2025). *Run agent teams*. Claude Code Documentation.
https://docs.anthropic.com/docs/en/agent-teams
(Accessed 2026-03-06; version active as of early-2026 Claude Code release; marked experimental.)

## Research Question Addressed

How should practitioners configure, coordinate, and constrain multiple Claude Code instances working together on a single complex task? This documentation page addresses the architecture, launch patterns, communication model, quality-gate enforcement, best practices, and known limitations of Claude Code's experimental "agent teams" feature — providing the authoritative reference for multi-agent orchestration within the Claude Code toolchain.

## Theoretical / Conceptual Framework

The source operates within a **lead-worker fleet topology**: a single distinguished session (the "team lead") decomposes work, spawns peers, maintains a shared task list, and synthesises results. This is a direct instantiation of the **orchestrator-workers** pattern described in Anthropic's "Building effective agents" post — but concretised as a product feature rather than an abstract architectural recommendation.

A secondary conceptual thread is the **context isolation principle**: each teammate runs in its own context window and does not inherit the lead's conversation history. This is a deliberate engineering constraint, not a limitation to work around; it prevents context bleed-through between parallel workers and forces precise spawn prompts.

The documentation implicitly frames agent teams as higher on a **delegation cost curve** than subagents: greater parallelism, peer messaging, and autonomy come at higher token cost and coordination overhead, and the document is consistent in advising against this tier unless peer communication genuinely adds value.

## Methodology and Evidence

This is first-party product documentation maintained by Anthropic. It describes Claude Code's agent teams feature as it was shipped, complete with configuration syntax, architectural tables, use-case walkthroughs, troubleshooting steps, and a limitations section. Evidence is structural and prescriptive — the document demonstrates working command outputs and explains system behaviours, but does not provide empirical benchmarks.

The documentation is candid about its experimental status: "Agent teams are experimental and disabled by default." The limitations section names seven specific known gaps (no session resumption, task-status lag, one team per session, no nested teams, etc.), which is an unusual level of transparency for product documentation and increases its practical usefulness. The worked examples (parallel code review, competing-hypothesis investigation) are illustrative rather than empirically evaluated.

## Key Claims

- **Agent teams require explicit opt-in**: > "Agent teams are experimental and disabled by default. Enable them by adding `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` to your settings.json or environment." This signals that the feature is not production-ready and requires deliberate adoption.

- **Core topology is lead + teammates + task list + mailbox**: > "An agent team consists of: Team lead — The main Claude Code session that creates the team, spawns teammates, and coordinates work; Teammates — Separate Claude Code instances that each work on assigned tasks; Task list — Shared list of work items that teammates claim and complete; Mailbox — Messaging system for communication between agents." This four-component model maps cleanly onto the endogenic Executive + sub-fleet concept.

- **Agent teams vs. subagents is a deliberate upgrade path, not a binary choice**: > "Both agent teams and subagents let you parallelize work, but they operate differently. Choose based on whether your workers need to communicate with each other." Subagents report results back to the main agent only; teammates message each other directly. Teams are chosen only when inter-worker discussion adds value.

- **Context isolation is strict and by design**: > "Each teammate has its own context window. When spawned, a teammate loads the same project context as a regular session: CLAUDE.md, MCP servers, and skills. It also receives the spawn prompt from the lead. The lead's conversation history does not carry over." Precise spawn prompts are therefore critical to correct teammate behaviour.

- **`CLAUDE.md` is the canonical mechanism for shared project context**: > "`CLAUDE.md` works normally: teammates read `CLAUDE.md` files from their working directory. Use this to provide project-specific guidance to all teammates." This makes `CLAUDE.md` the multi-agent equivalent of a shared briefing document.

- **Plan-approval gate is a first-class feature**: > "For complex or risky tasks, you can require teammates to plan before implementing. The teammate works in read-only plan mode until the lead approves their approach." The lead reviews and either approves or rejects with feedback; the teammate stays in plan mode until approved. This is a direct product-level implementation of a phase gate.

- **Hook-based quality gates enforce completion criteria**: > "Use hooks to enforce rules when teammates finish work or tasks complete: `TeammateIdle` — runs when a teammate is about to go idle. Exit with code 2 to send feedback and keep the teammate working. `TaskCompleted` — runs when a task is being marked complete. Exit with code 2 to prevent completion and send feedback." Programmatic quality enforcement without human intervention.

- **Task claiming uses file locking to prevent race conditions**: > "Task claiming uses file locking to prevent race conditions when multiple teammates try to claim the same task simultaneously." This is a concrete engineering mechanism addressing a known failure mode of parallel agent systems.

- **Token cost scales linearly and limits practical team size**: > "Token costs scale linearly: each teammate has its own context window and consumes tokens independently." And: > "Start with 3–5 teammates for most workflows. This balances parallel work with manageable coordination." 5–6 tasks per teammate is the recommended loading ratio.

- **Competing-hypotheses investigation is the signature high-value use case**: > "With multiple independent investigators actively trying to disprove each other, the theory that survives is much more likely to be the actual root cause." Sequential investigation suffers from anchoring bias; adversarial parallel investigation counters it. This is the most analytically distinctive use-case the documentation surfaces.

- **Monitor and steer is a required practice, not an optional polish step**: > "Check in on teammates' progress, redirect approaches that aren't working, and synthesize findings as they come in. Letting a team run unattended for too long increases the risk of wasted effort." Agent teams are not fire-and-forget; human-in-the-loop oversight is expected.

- **Lead cannot be promoted or transferred**: > "Lead is fixed: the session that creates the team is the lead for its lifetime. You can't promote a teammate to lead or transfer leadership." This makes the initial orchestrator assignment consequential and permanent within a session.

- **No nested teams — teammates cannot spawn sub-fleets**: > "No nested teams: teammates cannot spawn their own teams or teammates. Only the lead can manage the team." This is a hard architectural boundary preventing unbounded recursion in the agent tree.

- **Task-status lag is a known production hazard**: > "Teammates sometimes fail to mark tasks as completed, which blocks dependent tasks. If a task appears stuck, check whether the work is actually done and update the task status manually or tell the lead to nudge the teammate." This implies that task-state reconciliation requires periodic human or automated verification.

- **Scope tasks for independent ownership to avoid file conflicts**: > "Two teammates editing the same file leads to overwrites. Break the work so each teammate owns a different set of files." File-level ownership boundaries are the minimum required coordination discipline.

## Critical Assessment

**Evidence Quality**: Documentation

This is Anthropic's own product documentation; it accurately describes system behaviour as shipped. It is authoritative for understanding the Claude Code agent teams feature but is not a substitute for empirical benchmarks, independent reproduction, or comparative evaluation against other multi-agent frameworks. The document's value is prescriptive and architectural, not experimental.

**Gaps and Limitations**: The documentation covers Claude Code specifically — a terminal-based interactive agent environment. Its patterns (tmux split panes, Shift+Down navigation, `.claude/teams/` config files) are not abstractly portable; they describe a product surface, not a general methodology. Quantitative guidance on optimal team sizes and task granularity is heuristic ("3–5 teammates," "5–6 tasks per teammate") without empirical backing. The limitations section is candid but worrying for production use: session resumption does not work with in-process teammates, task status can lag and block dependent work, and the feature is disabled by default — it is experimental by Anthropic's own labelling. The document does not address failure recovery, partial team completion semantics, or how to handle teammate hallucinations or off-course investigations beyond "monitor and steer."

## Connection to Other Sources

- Agrees with / extends: [anthropic-building-effective-agents](./anthropic-building-effective-agents.md) — this document concretises the orchestrator-workers pattern from that post as a product feature in Claude Code, adding plan-approval gates, hook-based quality enforcement, and task-list management that the blog post only described abstractly.
- Agrees with / extends: [arxiv-context-engineering-survey](./arxiv-context-engineering-survey.md) — the context isolation principle (no lead conversation history in teammates; spawn prompt as the sole briefing mechanism) aligns with context engineering theory on managing window boundaries in multi-agent systems.

## Relevance to EndogenAI

The agent teams architecture described here is the closest external analogue to the EndogenAI research sub-fleet pattern. The EndogenAI agent fleet (`.github/agents/`) already implements the lead-worker topology informally: the Executive Researcher orchestrates Scout, Synthesizer, Reviewer, and Archivist agents, coordinating via the `.tmp/<branch>/` scratchpad. This documentation makes explicit what EndogenAI should formalise: the distinction between a shared context medium (Claude Code's task list and mailbox; EndogenAI's `.tmp/` scratchpad) and per-agent context isolation (Claude Code's own context window per teammate; EndogenAI's per-invocation scope constraint). **ADOPT** the task-list + context-isolation model as an explicit design constraint in `docs/guides/session-management.md` and the Executive Researcher agent definition — spawn prompts should be treated as the canonical briefing mechanism, not conversation state.

The plan-approval gate (teammate works in read-only plan mode until lead approves) is a direct parallel to the EndogenAI phase-gate concept codified in `docs/research/agentic-research-flows.md`. The Claude Code implementation offers a concrete model: a Sub-agent proposes a plan, the Executive reviews against stated criteria (e.g. "reject plans that modify the database schema"), and approval is a gated prerequisite for action. **ADOPT** this as a pattern for the Synthesizer and Scout agents when scope is ambiguous: require a plan stub before proceeding with large read or write operations. This would harden the self-loop phase gate in the research workflow.

The `TeammateIdle` and `TaskCompleted` hooks — programmatic gates that can return exit code 2 to keep a teammate working or block task completion — are the external equivalent of EndogenAI's quality gate concept. Currently, EndogenAI quality gates operate through agent instructions (completion criteria in mode instructions), not through executable scripts. **ADAPT** this pattern: the `scripts/` directory is the natural home for hook-equivalent validation logic. A script that verifies a synthesis document meets the ≥ 100 line and all-sections-present criteria before an Archivist commit runs would close the gap between aspirational and enforced quality gates, directly supporting D2 from `docs/research/OPEN_RESEARCH.md`.

## Referenced By

<!-- Populated automatically by scripts/link_source_stubs.py — do not edit manually -->
- [Agent Fleet Design Patterns](../agent-fleet-design-patterns.md)
- [Agentic Research Flows](../agentic-research-flows.md)
- [Anthropic Building Effective Agents](../sources/anthropic-building-effective-agents.md)
- [Arxiv Context Engineering Survey](../sources/arxiv-context-engineering-survey.md)
- [Claude Sdk Subagents](../sources/claude-sdk-subagents.md)
- [Platform Claude Com Docs En Build With Claude Prompt Enginee](../sources/platform-claude-com-docs-en-build-with-claude-prompt-enginee.md)
- [Tds Claude Skills Subagents](../sources/tds-claude-skills-subagents.md)
- [Xml Agent Instruction Format](../xml-agent-instruction-format.md)
