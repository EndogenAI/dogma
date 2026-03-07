---
slug: "code-claude-com-docs-en-sub-agents"
source_url: "https://code.claude.com/docs/en/sub-agents"
cache_path: ".cache/sources/code-claude-com-docs-en-sub-agents.md"
fetched: 2026-03-06
research_issue: "Issue #12 — XML-Tagged Agent Instruction Format"
title: "Create custom subagents — Claude Code documentation"
authors: "Anthropic"
year: "2025"
type: documentation
topics: [subagents, agent-format, frontmatter, claude-code, tools, YAML]
cached: true
evidence_quality: documentation
date_synthesized: "2026-03-06"
---

# Synthesis: Create custom subagents — Claude Code documentation

## 1. Citation

Anthropic. (2025). *Create custom subagents*. Claude Code Documentation. https://code.claude.com/docs/en/sub-agents. Accessed 2026-03-06.

## 2. Research Question Addressed

This documentation addresses how to define, configure, and deploy custom sub-agent files within Claude Code, including the complete frontmatter schema, file format, tool access model, and permission system. It answers the direct question: what is the canonical file format for Claude Code `.claude/agents/` sub-agent files, and what instruction-body conventions does it use?

## 3. Theoretical Framework

The document operates within the Claude Code **sub-agent delegation model**: Claude's main conversation detects a task matching a sub-agent's `description` and routes it to an isolated context window. The framework is pragmatic rather than theoretical — the design choices (YAML frontmatter + Markdown body, tool allowlists/denylists, permission modes, scope hierarchy) reflect engineering decisions for security, cost control, and context preservation rather than any named research paradigm.

The delegation architecture follows a single-level, non-recursive pattern: sub-agents cannot spawn other sub-agents. The instruction body is treated as a **system prompt**, not a structured data schema, reinforcing its prose-and-Markdown nature.

## 4. Methodology / Source Type

Official product documentation maintained by Anthropic for Claude Code. The page is the primary authoritative reference for sub-agent file format. Content is procedural (how-to), supplemented by worked examples, tables of supported fields/values, and inline code blocks showing canonical file structures. The page is comprehensive (1,199 lines in cached form), covering built-in agents, quickstart, all configuration options, usage patterns, and example agent files.

This is first-party documentation with no peer-review process; accuracy depends on Anthropic keeping it current. The cached version reflects the page as of 2026-03-06.

## 5. Key Claims with Evidence

- **Sub-agent files are Markdown with YAML frontmatter; the body is a prose system prompt.**

  > "Subagent files use YAML frontmatter for configuration, followed by the system prompt in Markdown."

  The instruction body is unstructured natural language Markdown — **not** XML. The example file given:
  ```
  ---
  name: code-reviewer
  description: Reviews code for quality and best practices
  tools: Read, Glob, Grep
  model: sonnet
  ---

  You are a code reviewer. When invoked, analyze the code and provide
  specific, actionable feedback on quality, security, and best practices.
  ```
  Section: "Write subagent files."

- **Only `name` and `description` are required frontmatter fields.**

  > "The following fields can be used in the YAML frontmatter. Only `name` and `description` are required."

  All other fields (`tools`, `disallowedTools`, `model`, `permissionMode`, `maxTurns`, `skills`, `mcpServers`, `hooks`, `memory`, `background`, `isolation`) are optional. Section: "Supported frontmatter fields."

- **The `tools` field is an allowlist of named Claude Code internal tools.**

  > "Tools the subagent can use. Inherits all tools if omitted."

  Documented values include: `Read`, `Grep`, `Glob`, `Bash`, `Write`, `Edit`, `Agent`, `Agent(subagent-name)`. Sub-agents inherit all parent tools if `tools` is omitted. Section: "Available tools."

- **The `disallowedTools` field is a denylist applied on top of the allowlist.**

  > "Tools to deny, removed from inherited or specified list."

  Both fields can coexist: first `tools` sets the allowed set (or all by default), then `disallowedTools` removes specific entries. Section: "Supported frontmatter fields."

- **The `model` field accepts named aliases, not full model identifiers.**

  > "Use one of the available aliases: `sonnet`, `opus`, or `haiku`"

  A fourth pseudo-value `inherit` causes the sub-agent to use whatever model the main conversation is using. Omitting the field also defaults to `inherit`. Section: "Choose a model."

- **The `permissionMode` field has five named values.**

  Values and meanings:
  | Mode | Behaviour |
  |---|---|
  | `default` | Standard permission checking with prompts |
  | `acceptEdits` | Auto-accept file edits |
  | `dontAsk` | Auto-deny permission prompts (explicitly allowed tools still work) |
  | `bypassPermissions` | Skip all permission checks |
  | `plan` | Plan mode (read-only exploration) |

  Section: "Permission modes."

- **Sub-agents are stored in scoped directories; `.claude/agents/` is the project scope.**

  > "Store them in different locations depending on scope."

  Priority order (highest to lowest):
  1. `--agents` CLI flag (current session only)
  2. `.claude/agents/` (project)
  3. `~/.claude/agents/` (user / all projects)
  4. Plugin `agents/` directory

  Section: "Choose the subagent scope."

- **The `hooks` field supports `PreToolUse`, `PostToolUse`, and `Stop` lifecycle events inside the frontmatter.**

  > "Define hooks directly in the subagent's markdown file. These hooks only run while that specific subagent is active and are cleaned up when it finishes."

  Hooks use YAML block structure (not XML) and reference external shell scripts via `command`. Section: "Hooks in subagent frontmatter."

- **The `memory` field enables a persistent directory that survives across conversations.**

  > "The `memory` field gives the subagent a persistent directory that survives across conversations."

  Values: `user` (~/.claude/agent-memory/<name>/), `project` (.claude/agent-memory/<name>/), `local` (.claude/agent-memory-local/<name>/). Section: "Enable persistent memory."

- **The `skills` field injects full skill content into the sub-agent context at startup.**

  > "Use the `skills` field to inject skill content into a subagent's context at startup. This gives the subagent domain knowledge without requiring it to discover and load skills during execution."

  > "The full content of each skill is injected into the subagent's context, not just made available for invocation. Subagents don't inherit skills from the parent conversation; you must list them explicitly."

  Section: "Preload skills into subagents."

- **The `isolation` field can run the sub-agent in a git worktree.**

  > "Set to `worktree` to run the subagent in a temporary git worktree, giving it an isolated copy of the repository."

  Section: "Supported frontmatter fields."

- **CLI-defined sub-agents pass the same fields as JSON; the body system prompt is a `prompt` key.**

  > "The `--agents` flag accepts JSON with the same frontmatter fields as file-based subagents: `description`, `prompt`, `tools`, `disallowedTools`, `model`, `permissionMode`, `mcpServers`, `hooks`, `maxTurns`, `skills`, and `memory`. Use `prompt` for the system prompt, equivalent to the markdown body in file-based subagents."

  Section: "Choose the subagent scope."

- **Sub-agents receive only their own system prompt, not the parent Claude Code system prompt.**

  > "Subagents receive only this system prompt (plus basic environment details like working directory), not the full Claude Code system prompt."

  Section: "Write subagent files."

## 6. Critical Assessment

**Evidence Quality: Documentation**

This is first-party official documentation. It is authoritative for the described behaviour as of the access date but carries no independent verification or peer review. The cached version is 1,199 lines and covers the full page, so the synthesis reflects complete source text.

**Gaps and Limitations:**

- The documentation does not define the full list of valid `tools` values beyond the examples shown (`Read`, `Grep`, `Glob`, `Bash`, `Write`, `Edit`). The internal tools reference is cross-linked but not reproduced here, so the complete enumeration requires consulting `/docs/en/settings#tools-available-to-claude`.
- No information is given about character limits for `name`, `description`, or `prompt` fields (unlike the Agent Skills documentation for Skills, which specifies exact character counts).
- The documentation describes Claude Code behaviour only; the `platform.claude.com` Agent Skills format is a separate system (see Source B).
- Versioning of the frontmatter schema is implicit; changes between Claude Code releases may not be immediately reflected in the docs.
- The document does not address whether XML inside the instruction body (between Markdown) has any supported or special semantics.

## 7. Cross-Source Connections

- Contrasts with [platform-claude-com-docs-en-agents-and-tools-agent-skills-ov](./platform-claude-com-docs-en-agents-and-tools-agent-skills-ov.md): Agent Skills use a `SKILL.md` file format with only `name` and `description` in YAML frontmatter; sub-agents use a richer frontmatter schema (12+ fields). They are architecturally distinct systems that can interoperate via the `skills` frontmatter field.
- Extends [anthropic-building-effective-agents](./anthropic-building-effective-agents.md): provides the concrete implementation schema for the sub-agent patterns described there.
- Relates to [claude-sdk-subagents](./claude-sdk-subagents.md): the Agent SDK uses compatible sub-agent file conventions but with its own `allowed_tools` configuration layer.
- The `--agents` CLI JSON format matches the `code-visualstudio-com-docs-copilot-customization-custom-agen.md` VS Code agent format structurally (both use frontmatter + body) but differ in specific field names and available values.

## 8. Project Relevance

**Issue #12 — XML-Tagged Agent Instruction Format**: The Claude Code sub-agent documentation provides the clearest first-party answer on instruction body format. The instruction body is **plain Markdown prose** — there is no XML tagging in the canonical examples, no reference to XML section boundaries, and the format is explicitly described as "the system prompt in Markdown." This is direct evidence against XML being Anthropic's own preferred format for Claude Code agent files. **VERDICT: ADOPT Markdown body; REJECT XML in instruction bodies for `.claude/agents/` files.**

The EndogenAI `.github/agents/*.agent.md` format is analogous to `.claude/agents/*.md` but for VS Code Copilot. Both use YAML frontmatter + Markdown body. The Claude Code schema is more feature-rich (12+ fields vs the VS Code schema's ~5 fields), but the underlying architecture — identifier/trigger in frontmatter, prose instructions in body — is identical. EndogenAI agent files should remain consistent with this approach.

For `.github/agents/AGENTS.md` and the `scaffold_agent.py` script, the `tools` field values documented here (named aliases: `Read`, `Grep`, `Glob`, `Bash`, `Write`, `Edit`, `Agent`) are directly applicable if EndogenAI ever targets Claude Code deployment. The `skills` field pattern (preloading domain knowledge into agent context at startup, bypassing runtime discovery) is worth ADOPTING as a design principle in the EndogenAI guide authoring conventions — it mirrors the "Endogenous-First" axiom.

## Referenced By

<!-- Populated automatically by scripts/link_source_stubs.py — do not edit manually -->
- [Anthropic Building Effective Agents](../sources/anthropic-building-effective-agents.md)
- [Claude Sdk Subagents](../sources/claude-sdk-subagents.md)
- [Platform Claude Com Docs En Agents And Tools Agent Skills Ov](../sources/platform-claude-com-docs-en-agents-and-tools-agent-skills-ov.md)
- [Xml Agent Instruction Format](../xml-agent-instruction-format.md)
