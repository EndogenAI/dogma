---
title: "Claude Code CLI Productivity Patterns for Multi-Agent Research Pipelines"
status: "Final"
research_issue: 284
closes_issue: 284
date: 2026-03-17
sources:
  - https://code.claude.com/docs/en/hooks
  - https://code.claude.com/docs/en/sub-agents
  - https://code.claude.com/docs/en/cli-reference
  - https://code.claude.com/docs/en/settings
  - https://code.claude.com/docs/en/common-workflows
  - https://github.com/anthropics/claude-code
  - AGENTS.md
  - MANIFESTO.md
---

# Claude Code CLI Productivity Patterns for Multi-Agent Research Pipelines

## Executive Summary

Claude Code's non-interactive print mode (`claude -p`), structured output flags
(`--output-format json`, `--json-schema`), and hooks lifecycle each address a
distinct class of constraint that dogma currently handles through agent-level
prompt instructions. This research confirms that three of these primitives map
directly onto existing dogma scripts and represent a shift from T1 (verbal
instruction) to T3/T4 (static and runtime) enforcement — the same upward
movement the Governer A/B stack achieved for heredoc prevention. The practical
result is that phase-gate compliance, session lifecycle management, context
amplification, and compaction guards can all be encoded as deterministic hook
invocations rather than relied upon as prompt-time reminders subject to drift.

The hooks system is the highest-value adoption target. Eight Claude Code hook
types (`SessionStart`, `SessionEnd`, `Stop`, `TaskCompleted`, `PreCompact`,
`PostCompact`, `UserPromptSubmit`, `PostToolUse`) each have a direct dogma
counterpart script. Encoding these mappings converts dogma's existing T2
(text-constraint) layer into a T4 (runtime-enforcement) layer. This aligns with
the [Programmatic-First](../../MANIFESTO.md#programmatic-first-principle-cross-cutting)
principle: tasks performed twice interactively must be encoded as scripts; hooks
are the mechanism that binds those scripts to the agent lifecycle automatically.

Print mode (`claude -p`) is the lower-risk, immediately adoptable primitive.
It produces deterministic, auditable output from a single CLI invocation with no
interactive session overhead. Combined with `--output-format json` and
`--json-schema`, it satisfies the [Algorithms-Before-Tokens](../../MANIFESTO.md#2-algorithms-before-tokens)
requirement for structured, deterministic outputs over token-burning interactive
exchanges. Cost and context-window implications are non-trivial: practitioner
reports document ~50K tokens of system prompt overhead per Claude Code
subprocess, making per-query subagent invocation impractical for batch workloads.
Print mode sidesteps this by targeting single-pass synthesis tasks directly.

---

## Hypothesis Validation

### H1: Claude Code print mode (`claude -p`) can replace interactive terminal sessions in dogma automation scripts

**VERDICT: CONFIRMED**

Print mode accepts a prompt string and exits after one response with no
interactive state. The `--output-format json` flag returns a structured envelope
(`result`, `cost_usd`, `duration_ms`, `session_id`, `num_turns`). The
`--json-schema` flag (print mode only) enforces output conformance to a provided
JSON Schema object, enabling downstream scripts to consume outputs without
defensive parsing. The `--max-turns 1` flag prevents multi-turn escalation in
batch contexts. Together these three flags (`-p`, `--output-format json`,
`--json-schema`) produce a deterministic, script-consumable output primitive that
directly satisfies the [Algorithms-Before-Tokens](../../MANIFESTO.md#2-algorithms-before-tokens)
axiom: encode the task once; get a deterministic result each run.

### H2: Claude Code hooks can encode dogma's phase-gate constraints programmatically, reducing reliance on agent-level prompt reminders

**VERDICT: CONFIRMED**

The `Stop` hook (fires when Claude is about to stop) and `TaskCompleted` hook
(fires on explicit task completion signal) both support `type: "prompt"` — meaning
the hook body is evaluated by an LLM against multi-criteria conditions, with exit
code 2 sending feedback and continuing the agent rather than stopping. This is
precisely the mechanism needed to encode phase-gate-sequence criteria
(`docs/research/` section checks, commit verification, issue AC confirmation)
as runtime gates rather than prompt instructions. The Stop hook includes a
`stop_hook_active` environment variable that must be checked to prevent infinite
loops — agents must guard against a Stop hook triggering a continuation that fires
another Stop.

### H3: The Claude Code subagent architecture (`.claude/agents/*.md`) is compatible with dogma's `.github/agents/*.agent.md` fleet

**VERDICT: PARTIALLY SUPPORTED**

Claude Code subagent frontmatter — `description`, `tools`, `model`, `maxTurns`,
`hooks`, `skills`, `memory`, `isolation`, `background` — overlaps substantially
with dogma's `.agent.md` frontmatter (`name`, `description`, `tools`, `tier`,
`handoffs`). The conceptual model is congruent: named agents with scoped tool
access, role-specific instructions, and handoff topology. However, VS Code Custom
Agents (`.github/agents/*.agent.md`) are the current dogma standard and are
validated by `scripts/validate_agent_files.py`. Claude Code's `.claude/agents/`
format targets the Claude Code CLI runtime; the two runtimes are not yet
interchangeable in VS Code. Migration is forward-compatible but not automatic —
the equivalence should be documented so the path is clear when Claude Code's VS
Code integration stabilizes.

### H4: Each Claude Code subprocess (~50K tokens system overhead) makes per-query subagent invocation cost-prohibitive

**VERDICT: CONFIRMED**

Practitioner documentation confirms approximately 50K tokens of system prompt
overhead per Claude Code subprocess invocation. At current API pricing this
represents a significant per-invocation floor that makes a 24/7 wrapper pattern
(spawning a new subprocess for each query) economically impractical for high-
frequency pipelines. The recommended pattern is print mode (`claude -p`) for
single-pass queries and reserved full-agent sessions only for multi-step
automation where interactive context accumulation justifies the overhead. This
finding directly supports the [Local-Compute-First](../../MANIFESTO.md#3-local-compute-first)
principle: minimize token usage; prefer local script execution over agent
invocation wherever a deterministic script can handle the task.

---

## Pattern Catalog

### P1: Hook-Driven Phase Gate

**Intent**: Encode phase-completion criteria as Claude Code `Stop` or
`TaskCompleted` hooks rather than relying on agent-level prompt instructions,
shifting enforcement from T1 (verbal) to T4 (runtime).

**Mechanism**: A `type: "prompt"` hook body is evaluated by a lightweight LLM
call. Exit code `0` allows stop; exit code `2` sends the feedback string back to
the agent as a continuation prompt. Guards: always read `$STOP_HOOK_ACTIVE` and
exit 0 if set, to prevent infinite hook-fires-continuation loops.

**Canonical example**:

```json
{
  "hooks": {
    "Stop": [{
      "type": "prompt",
      "prompt": "Before stopping, verify: (1) all TODO markers are resolved, (2) git status is clean, (3) the issue acceptance criteria checkboxes are marked [x]. If any criterion fails, output the failing criterion and exit 2.",
      "timeout": 30
    }]
  }
}
```

This maps directly to dogma's `phase-gate-sequence` SKILL.md checklist. Instead
of the agent relying on prompt memory to run the checklist, the runtime enforces
it structurally.

**Anti-pattern**: Using `async: true` on a `Stop` hook when the gate decision is
needed — async hooks cannot block the stop event. Decision hooks must omit
`async` (they are synchronous by default). A second anti-pattern is omitting the
`stop_hook_active` guard: a Stop hook that performs agentic continuation will
fire another Stop, entering an infinite loop.

---

### P2: Print-Mode Pipeline Integration

**Intent**: Use `claude -p` with `--output-format json` and `--json-schema` to
integrate Claude Code as a deterministic, single-pass CLI primitive in
automation scripts — returning structured JSON that downstream scripts consume
without defensive parsing.

**Mechanism**: Print mode exits after one response. `--output-format json`
wraps the response in a JSON envelope. `--json-schema` enforces the output
structure against a provided schema (print mode only). `--max-turns 1` prevents
escalation. `--max-budget-usd` caps cost per invocation.

**Canonical example**:

```bash
result=$(claude -p "Summarise the failing test output and return a JSON object with keys: 'root_cause', 'affected_files', 'suggested_fix'." \
  --output-format json \
  --json-schema '{"type":"object","properties":{"root_cause":{"type":"string"},"affected_files":{"type":"array","items":{"type":"string"}},"suggested_fix":{"type":"string"}},"required":["root_cause","affected_files","suggested_fix"]}' \
  --max-turns 1 \
  --max-budget-usd 0.10)

echo "$result" | jq '.result.suggested_fix'
```

This is the correct dogma integration primitive for single-pass LLM tasks in
CI scripts (test failure analysis, synthesis quality checks, doc lint suggestions)
where the output must be machine-readable.

**Anti-pattern**: Spinning up a full interactive Claude Code session (or a named
`--name` session) for single-query tasks incurs ~50K tokens of system prompt
overhead per invocation. For a batch pipeline running 20 synthesis checks, this
is 1M tokens of overhead alone — use print mode. A second anti-pattern is
omitting `--max-turns` and `--max-budget-usd` in automated pipelines: without
these guards, a misbehaving agent can exhaust quota.

---

## Gap & Differentiation Matrix

| Dimension | Current dogma (AGENTS.md + scripts) | With Claude Code hooks | Gain |
|---|---|---|---|
| **Phase gate reliability** | T2 text constraint; prompt-dependent; drift-prone per session | T4 runtime; `Stop`/`TaskCompleted` gate; LLM-evaluated multi-criteria | Structural enforcement replaces prompt memory |
| **Token overhead** | Agent-level prompts re-state checklist each phase | Hook evaluates criteria as a lightweight side-call; not inline agent tokens | Reduced inline token burn |
| **Session persistence** | `.tmp/<branch>/<date>.md` scratchpad; per-day file; git-ignored | `memory: project` → `MEMORY.md`; persists cross-session; CLI-native | Complementary; both useful at different scopes |
| **MCP integration** | MCP servers loaded via VS Code settings; no per-invocation isolation | `--mcp-config ./mcp.json` + `--strict-mcp-config`; per-invocation isolation | Finer-grained MCP scoping for CI invocations |
| **Local compute alignment** | Pre-commit hooks + local scripts (T3); shell governor (T4) | Print mode + local hook scripts; no cloud-only enforcement | Consistent with Local-Compute-First axiom |
| **Compaction awareness** | Session-management SKILL.md; text instructions | `PreCompact`/`PostCompact` hooks fire deterministically at compaction boundary | Eliminates silent compaction risk |
| **Permission model** | `--allowedTools`/`--disallowedTools` via agent frontmatter | Same flags per invocation + `--permission-mode plan` for read-only analysis | Finer per-invocation surface control |

---

## Recommendations

### 1. ADOPT `claude -p` print mode for batch synthesis tasks

Where agent interaction isn't needed — synthesis quality checks, doc lint
evaluations, structured output generation — replace full interactive sessions
with `claude -p` + `--output-format json` + `--json-schema`. This aligns with
[Local-Compute-First](../../MANIFESTO.md#3-local-compute-first): minimize token usage;
run locally whenever possible. Always pair with `--max-turns 1` and
`--max-budget-usd` to prevent runaway invocations.

### 2. ENCODE dogma's phase-gate-sequence as Claude Code `Stop`/`TaskCompleted` hooks

The LLM-evaluated `type: "prompt"` hook enables complex multi-criteria gates
(commit verification, AC checkbox confirmation, ruff/test pass) that are not
expressible in simple pre-commit hooks. This is the
[Programmatic-First](../../MANIFESTO.md#programmatic-first-principle-cross-cutting)
principle applied at the agent lifecycle layer: encode the checklist once in a
hook; stop relying on every agent remembering to run it. Guard every `Stop` hook
with `stop_hook_active` to prevent infinite loops.

### 3. MAP dogma scripts to the SessionStart/SessionEnd hook lifecycle

The following hook bindings are direct and should be formalized in a
`CLAUDE.md`-level hook configuration when Claude Code integration is adopted:

| Dogma pattern | Claude Code hook | Alignment |
|---|---|---|
| `prune_scratchpad.py --init` | `SessionStart` + `additionalContext` | Direct |
| Phase gate quality check | `Stop` (type: prompt) or `TaskCompleted` | Direct |
| Compaction checkpoint script | `PreCompact` + `PostCompact` | Direct |
| `amplify_context.py` | `UserPromptSubmit` + `additionalContext` | Direct |
| `annotate_provenance.py` | `InstructionsLoaded` | Direct |
| Per-file lint gate | `PostToolUse` on `Edit\|Write` | Direct |
| Session summary write | `SessionEnd` | Direct |

This mapping is the migration specification. Each existing script already handles
its domain; the hooks provide the trigger layer that removes the text-instruction
dependency.

### 4. DEFER Claude Code subagent architecture as a future compatibility target

VS Code Custom Agents (`.github/agents/*.agent.md`) are the current dogma
standard, validated by `scripts/validate_agent_files.py` in CI. The Claude Code
`.claude/agents/` format is a forward-compatible evolution but not yet
interchangeable with the VS Code runtime. Document the YAML field equivalences
(`name`↔`description`, `tools`↔`tools`, `isolation: worktree`↔per-session
isolation, `memory: project`↔`/memories/repo/`) so the migration path is
unambiguous. Revisit when Claude Code's VS Code integration stabilises.

---

## Open Questions

- **#297 MCP server**: How should `mcp__<server>__<tool>` naming and
  `PostToolUse` regex matchers interact with the dogma MCP server design? Hook
  matchers using `mcp__memory__.*` patterns are already a documented pattern —
  this should inform the MCP server tool naming convention.
- **#303 MCP tool surface**: `Elicitation`/`ElicitationResult` hooks for
  sanitizing user-input requests and `PostToolUse` with `updatedMCPToolOutput`
  for replacing tool output are relevant to #303; follow-up synthesis needed.
- **#304 SQLite scratchpad**: Does `memory: project` (MEMORY.md) replace or
  complement the SQLite-based scratchpad? The use cases partially overlap.
- **Hook configuration management**: Where should hook configuration live in a
  dogma-derived project — `CLAUDE.md`, a committed `hooks.json`, or the
  `settings.local.json` layer? This warrants a short decision record.
- **`--no-session-persistence` for ephemeral CI invocations**: Whether this
  flag should be a required default for all CI-context print mode invocations
  needs an explicit policy decision.

---

## Sources

1. Anthropic. (2025). *Claude Code: CLI Reference*. https://code.claude.com/docs/en/cli-reference
2. Anthropic. (2025). *Claude Code: Hooks*. https://code.claude.com/docs/en/hooks
3. Anthropic. (2025). *Claude Code: Sub-Agents*. https://code.claude.com/docs/en/sub-agents
4. Anthropic. (2025). *Claude Code: Settings*. https://code.claude.com/docs/en/settings
5. Anthropic. (2025). *Claude Code: Common Workflows*. https://code.claude.com/docs/en/common-workflows
6. Anthropic. (2025). *anthropics/claude-code* [GitHub repository]. https://github.com/anthropics/claude-code
7. EndogenAI Workflows. (2026). *AGENTS.md — Operational Constraints*. `/Users/conor/Sites/dogma/AGENTS.md`
8. EndogenAI Workflows. (2026). *MANIFESTO.md — Foundational Axioms*. `/Users/conor/Sites/dogma/MANIFESTO.md`
