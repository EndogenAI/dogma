---
slug: "claude-sdk-subagents"
title: "Subagents — Claude Agent SDK Documentation"
url: "https://code.claude.com/docs/en/agent-sdk/subagents"
authors: "Anthropic (product documentation)"
year: "2025"
type: documentation
topics: [subagents, multi-agent, orchestration, context-isolation, parallelism, tool-restrictions, sdk, claude-agent-sdk]
cached: true
evidence_quality: documentation
date_synthesized: "2026-03-06"
cache_path: ".cache/sources/claude-sdk-subagents.md"
---

# Subagents — Claude Agent SDK Documentation

**URL**: https://code.claude.com/docs/en/agent-sdk/subagents
**Type**: documentation
**Cached**: `uv run python scripts/fetch_source.py https://code.claude.com/docs/en/agent-sdk/subagents --slug claude-sdk-subagents`

## Citation

Anthropic. (2025). *Subagents*. Claude Agent SDK Documentation.
https://code.claude.com/docs/en/agent-sdk/subagents
(Accessed 2026-03-06; reflects early-2026 Claude Agent SDK release.)

## Research Question Addressed

How should developers define, configure, invoke, and manage subagents programmatically using the Claude Agent SDK? This documentation page covers the full lifecycle of SDK-defined subagents: the three creation pathways, the `AgentDefinition` schema, context-inheritance rules, invocation modes (automatic and explicit), dynamic configuration patterns, session resumption, tool restriction strategies, and common troubleshooting scenarios.

## Theoretical / Conceptual Framework

The source operates within the **Task-tool mediated sub-fleet model**: a parent agent invokes child agents exclusively via the `Task` tool, passing context only through an explicit prompt string. This enforces strict context-isolation as an architectural invariant — there is no implicit context bleed from parent to child. The SDK's design applies a **declarative role separation** paradigm: each subagent's behavior is fully specified by its `AgentDefinition` (a description, a system prompt, an optional tool list, and an optional model override), and Claude's own reasoning determines when to delegate. The model is influenced by the broader **minimal-footprint** principle: subagents carry only the tools they require for their stated role.

## Methodology and Evidence

This is official Anthropic product documentation for the Claude Agent SDK, written to serve as an authoritative reference rather than an argumentative or experimental source. Evidence quality is that of a specification: all claims are normative descriptions of what the SDK does or recommends, backed by working code examples in both Python and TypeScript. The document provides: a reference table for `AgentDefinition` fields, a table of common tool combinations by use case, a troubleshooting section, and multiple complete runnable code samples. The document is explicit about one hard constraint: "Subagents cannot spawn their own subagents" — a first-class architectural limit rather than a recommendation. Where behaviour depends on SDK version or platform, the documentation notes it (e.g., Windows command-line length limits, filesystem-based agents loading only at startup).

## Key Claims

- **Three creation pathways exist, with programmatic preferred**:
  > "You can create subagents in three ways: Programmatically: use the `agents` parameter in your `query()` options; Filesystem-based: define agents as markdown files in `.claude/agents/` directories; Built-in general-purpose: Claude can invoke the built-in `general-purpose` subagent at any time via the Task tool."
  The SDK documentation explicitly recommends the programmatic approach for SDK applications, positioning filesystem-based agents as an alternative rather than the primary pattern.

- **Context isolation is the primary architectural benefit**:
  > "Each subagent runs in its own fresh conversation. Intermediate tool calls and results stay inside the subagent; only its final message returns to the parent."
  This makes subagents the correct primitive for any subtask that would pollute the parent's context window if run inline — a direct analogue to the EndogenAI Scout/Synthesizer separation.

- **Context inheritance is narrowly constrained — only the Task prompt string passes through**:
  > "The only channel from parent to subagent is the Task prompt string, so include any file paths, error messages, or decisions the subagent needs directly in that prompt."
  This is a key operational constraint: the parent cannot rely on shared memory or implicit state; all necessary context must be marshalled into the handoff prompt explicitly.

- **Subagents receive project CLAUDE.md but NOT the parent's system prompt**:
  The inheritance table specifies the subagent receives "Its own system prompt (`AgentDefinition.prompt`) and the Task prompt" and "Project CLAUDE.md (loaded via `settingSources`)" but does NOT receive "The parent's conversation history or tool results" or "The parent's system prompt." This means project-wide conventions encoded in CLAUDE.md propagate to all subagents automatically.

- **The `description` field drives automatic delegation**:
  > "Claude automatically decides when to invoke subagents based on the task and each subagent's `description` field. Write clear descriptions that explain when the subagent should be used, and Claude will automatically delegate appropriate tasks."
  The description is the primary routing signal — equivalent to the `description` field in EndogenAI's `.agent.md` front-matter that governs agent selection.

- **Explicit invocation is always available as an override**:
  > "To guarantee Claude uses a specific subagent, mention it by name in your prompt: 'Use the code-reviewer agent to check the authentication module'"
  This bypasses automatic matching, providing a deterministic control path when needed — important for scripted orchestration workflows.

- **Parallelization is a first-class pattern**:
  > "Multiple subagents can run concurrently, dramatically speeding up complex workflows. Example: during a code review, you can run `style-checker`, `security-scanner`, and `test-coverage` subagents simultaneously, reducing review time from minutes to seconds."
  This is the canonical justification for the parallel sub-fleet pattern in EndogenAI's research workflow.

- **Subagents cannot recurse — no nesting beyond one level**:
  > "Subagents cannot spawn their own subagents. Don't include `Task` in a subagent's `tools` array."
  This is a hard SDK limit, not a recommendation. Any design that assumes multi-level agent trees (e.g., a Scout spawning sub-Scouts) is architecturally invalid under the current SDK.

- **Dynamic `AgentDefinition` factory pattern is supported**:
  > "You can create agent definitions dynamically based on runtime conditions. This example creates a security reviewer with different strictness levels, using a more powerful model for strict reviews."
  Runtime parameterisation of agents (varying prompt, model, tools) enables a single script to produce a heterogeneous sub-fleet tailored to the task at hand.

- **Subagent session resumption preserves full conversation history**:
  > "Subagents can be resumed to continue where they left off. Resumed subagents retain their full conversation history, including all previous tool calls, results, and reasoning."
  Resumption requires capturing `session_id` from the parent query and `agentId` from the Task tool result content — a two-step extraction process illustrated with TypeScript code.

- **Tool restriction is implemented via the `tools` field in `AgentDefinition`**:
  > "Subagents can have restricted tool access via the `tools` field: Omit the field: agent inherits all available tools (default); Specify tools: agent can only use listed tools."
  Four canonical combinations are documented: read-only analysis (`Read`, `Grep`, `Glob`), test execution (`Bash`, `Read`, `Grep`), code modification (full read/write without shell), and full access (inherited). Tool minimality is the default recommendation.

- **The `Task` tool must be present in the parent's `allowedTools` for any subagent delegation**:
  > "The `Task` tool must be included in `allowedTools` since Claude invokes subagents through the Task tool."
  Missing this is the most common failure mode, explicitly surfaced in the troubleshooting section.

- **Subagent transcripts persist independently and survive main-conversation compaction**:
  > "Main conversation compaction: When the main conversation compacts, subagent transcripts are unaffected. They're stored in separate files."
  Transcripts persist for 30 days by default (`cleanupPeriodDays`). This has implications for context management and privacy in long-running research sessions.

## Critical Assessment

**Evidence Quality**: Documentation

This is normative product documentation authored by Anthropic for official SDK release. It is authoritative for current SDK behaviour but carries no empirical claims about effectiveness or quality of outcomes produced by subagent patterns. All guidance is prescriptive rather than evidence-based. Code samples are presented without test results or performance benchmarks — they illustrate API shape, not validated workflows.

**Gaps and Limitations**: The documentation covers the Python and TypeScript SDK surfaces but does not address the `AGENTS.md` / `.agent.md` filesystem convention used by EndogenAI (which is distinct from the `.claude/agents/` SDK convention). The constraint that subagents cannot spawn subagents is stated but no alternative is offered for multi-level hierarchies — this gap matters for tree-of-agent research designs. The document does not address how to handle subagent failures gracefully (retry strategies, error propagation to parent). Resumption flow is TypeScript-only in the example, with no Python equivalent provided. The document is snapshot documentation from early 2026 and may not reflect SDK changes after that date.

## Connection to Other Sources

- Agrees with / extends: [claude-code-agent-teams.md](./claude-code-agent-teams.md) — both describe Anthropic-native multi-agent orchestration, but `agent-teams` focuses on the Claude Code UI/CLI layer while this source covers the programmatic SDK layer; together they span the full Anthropic multi-agent surface area.
- Agrees with / extends: [anthropic-building-effective-agents.md](./anthropic-building-effective-agents.md) — the context-isolation principle here directly operationalises the "orchestrator-workers" pattern described there; the `AgentDefinition` schema is the concrete implementation of the abstract worker-agent concept.

## Relevance to EndogenAI

The SDK subagents documentation is the most directly applicable technical reference for the quasi-encapsulated sub-fleet pattern codified in [`.github/agents/`](../../.github/agents/). EndogenAI's current `.agent.md` front-matter convention (with `description`, `tools`, and `systemPrompt` fields) is structurally isomorphic to the SDK's `AgentDefinition` schema — the description-driven automatic delegation logic, the tool-restriction field, and the role-specific system prompt all map one-to-one. This alignment means EndogenAI's agent definitions can be translated into SDK-compatible `AgentDefinition` objects with minimal transformation, enabling programmatic orchestration via `scripts/` without re-authoring agent behaviour. **ADOPT**: the `AgentDefinition` pattern should be the reference model when extending `scripts/scaffold_agent.py` or any future orchestration script that spawns sub-agents programmatically.

The strict context-isolation model — "the only channel from parent to subagent is the Task prompt string" — directly validates and strengthens the handoff conventions in [`.tmp/<branch>/<date>.md`](../../AGENTS.md) scratchpads. Because subagents receive no implicit parent history, the scratchpad's role as an explicit, written context-transfer surface is not just a convenience but an architectural necessity. The prompt-enrichment chain pattern (each subagent's input is the enriched output of the preceding stage, written to scratchpad) is the correct implementation of this constraint. **ADOPT**: formalise the scratchpad handoff section format to match the marshalling requirements implied by this architecture — specifically, each delegation prompt should embed all file paths, prior findings, and constraints as explicit text, not as references to parent context.

The hard limit that subagents cannot spawn their own subagents caps the EndogenAI sub-fleet at one level of nesting. This affects the `Executive Researcher` → `Scout` → (sub-Scout) design: any plan in which a Scout agent spawns further Scouts is architecturally invalid under the SDK constraint. The practical correction is to have the Executive orchestrate all parallel subagent invocations directly rather than delegating orchestration to a Scout. This also informs [docs/guides/workflows.md](../../docs/guides/workflows.md): the self-loop phase gate should be implemented as a looping parent query, not as a recursive subagent chain. **ADAPT**: update the research workflow documentation to reflect the one-level nesting limit and redesign any multi-level sub-fleet proposals accordingly.

## Referenced By

<!-- Populated automatically by scripts/link_source_stubs.py — do not edit manually -->
- [A2A Announcement](../sources/a2a-announcement.md)
- [Agentic Research Flows](../agentic-research-flows.md)
- [Anthropic Building Effective Agents](../sources/anthropic-building-effective-agents.md)
- [Arxiv React](../sources/arxiv-react.md)
- [Claude Code Agent Teams](../sources/claude-code-agent-teams.md)
- [Code Claude Com Docs En Sub Agents](../sources/code-claude-com-docs-en-sub-agents.md)
- [Cookbook Research Lead Agent](../sources/cookbook-research-lead-agent.md)
- [Cookbook Research Subagent](../sources/cookbook-research-subagent.md)
- [Platform Claude Com Docs En Build With Claude Prompt Enginee](../sources/platform-claude-com-docs-en-build-with-claude-prompt-enginee.md)
- [Tds Claude Skills Subagents](../sources/tds-claude-skills-subagents.md)
- [Xml Agent Instruction Format](../xml-agent-instruction-format.md)
