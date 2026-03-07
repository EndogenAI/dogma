---
slug: "platform-claude-com-docs-en-agents-and-tools-agent-skills-ov"
source_url: "https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview"
cache_path: ".cache/sources/platform-claude-com-docs-en-agents-and-tools-agent-skills-ov.md"
fetched: 2026-03-06
research_issue: "Issue #12 — XML-Tagged Agent Instruction Format"
title: "Agent Skills overview — Anthropic platform documentation"
authors: "Anthropic"
year: "2025"
type: documentation
topics: [agent-skills, SKILL-md, frontmatter, claude-api, claude-code, progressive-disclosure]
cached: true
evidence_quality: documentation
date_synthesized: "2026-03-06"
---

# Synthesis: Agent Skills overview — Anthropic platform documentation

## 1. Citation

Anthropic. (2025). *Agent Skills: Overview*. Anthropic Platform Documentation. https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview. Accessed 2026-03-06.

## 2. Research Question Addressed

This documentation addresses what Agent Skills are, how they are structured as filesystem resources, what the `SKILL.md` file format requires, how content is progressively loaded into Claude's context, and where Skills work across Anthropic's product surfaces. For Issue #12, it directly answers: does the Agent Skills format use XML or Markdown in instruction bodies, and how does it compare to the Claude Code sub-agent format?

## 3. Theoretical Framework

Agent Skills embody a **progressive disclosure** architecture: rather than loading all domain context at inference start, Claude loads metadata at startup, instructions when a skill is triggered, and ancillary resources only as needed. This is framed as a filesystem-analogy: Skills are directories navigated like a developer navigates an onboarding guide — purposively, on demand.

The Skills model distinguishes itself from prompt-based instructions by being **on-demand and reusable** across conversations rather than injected once per session. No named academic framework underpins this; the philosophy is product-engineering driven, emphasising token economy and context-window efficiency.

## 4. Methodology / Source Type

Official product documentation maintained by Anthropic for the Claude API, Claude Code, Agent SDK, and claude.ai surfaces. The page is the primary overview for the Agent Skills system and the authoritative source for the `SKILL.md` format. Content is explanatory and procedural — structured in conceptual sections (why, how, where, structure, security, limitations) with code blocks illustrating canonical formats. The cached version is 426 lines; the page appears complete — no obvious truncation.

## 5. Key Claims with Evidence

- **Every Skill requires a `SKILL.md` file with YAML frontmatter; the body is Markdown prose instructions.**

  > "Every Skill requires a `SKILL.md` file with YAML frontmatter"

  The canonical structure shown:
  ```
  ---
  name: your-skill-name
  description: Brief description of what this Skill does and when to use it
  ---

  # Your Skill Name

  ## Instructions
  [Clear, step-by-step guidance for Claude to follow]

  ## Examples
  [Concrete examples of using this Skill]
  ```
  The instruction body is **plain Markdown** — no XML. Section: "Skill structure."

- **Only `name` and `description` are required fields in the frontmatter.**

  > "**Required fields**: `name` and `description`"

  This matches the Claude Code sub-agent requirement exactly: only two required fields, both the same names. Section: "Skill structure."

- **The `name` field has strict constraints: max 64 characters, lowercase letters/numbers/hyphens only, no XML tags, no reserved words.**

  > "`name`: Maximum 64 characters. Must contain only lowercase letters, numbers, and hyphens. Cannot contain XML tags. Cannot contain reserved words: 'anthropic', 'claude'."

  The explicit prohibition on XML tags in `name` values indicates Anthropic is aware of XML usage patterns and is constraining them to prevent collision with the model's XML parsing. Section: "Skill structure."

- **The `description` field has a 1024-character limit and likewise cannot contain XML tags.**

  > "`description`: Must be non-empty. Maximum 1024 characters. Cannot contain XML tags."

  The description serves dual purpose: human documentation and Claude's runtime trigger signal. The XML prohibition applies here too. Section: "Skill structure."

- **Level 1 metadata (YAML frontmatter) is always loaded at startup; the instruction body is only loaded when the skill is triggered.**

  > "Claude loads this metadata at startup and includes it in the system prompt. This lightweight approach means you can install many Skills without context penalty; Claude only knows each Skill exists and when to use it."

  At startup each skill costs ~100 tokens (metadata only). The full `SKILL.md` body loads only when triggered (under 5k tokens). Section: "Three types of Skill content, three levels of loading."

- **Claude accesses Skill content via bash filesystem reads, not prompt injection.**

  > "When a Skill is triggered, Claude uses bash to read SKILL.md from the filesystem, bringing its instructions into the context window."

  This architecture means Skills are not injected at session start — they are read from disk on demand via bash commands. This is architecturally distinct from the sub-agent `skills` frontmatter field, which injects content at sub-agent startup. Section: "The Skills architecture."

- **A Skill directory can contain additional Markdown files, scripts, and resources at Level 3, loaded only when referenced.**

  Example structure:
  ```
  pdf-skill/
  ├── SKILL.md (main instructions)
  ├── FORMS.md (form-filling guide)
  ├── REFERENCE.md (detailed API reference)
  └── scripts/
      └── fill_form.py (utility script)
  ```
  Scripts are executed via bash; their code never enters the context window — only their output does. Section: "Level 3: Resources and code."

- **The Agent Skills format is distinct from and NOT the same as the Claude Code sub-agent format.**

  > "Claude Code Skills are filesystem-based and don't require API uploads."
  > "Custom Skills do not sync across surfaces. Skills uploaded to one surface are not automatically available on others."

  Sub-agents live in `.claude/agents/` with a rich 12-field frontmatter schema. Skills live in `.claude/skills/` (or `~/.claude/skills/`) with a minimal 2-field schema. They are complementary systems: a sub-agent can load a Skill via its `skills` frontmatter field, but the two file formats are architecturally separate. Section: "Where Skills work — Claude Code."

- **Pre-built Agent Skills cover four document types: PowerPoint (pptx), Excel (xlsx), Word (docx), PDF (pdf).**

  > "The following pre-built Agent Skills are available for immediate use: PowerPoint (pptx)... Excel (xlsx)... Word (docx)... PDF (pdf)..."

  These are available on Claude API and claude.ai but not as filesystem Skills in Claude Code. Section: "Available Skills."

- **Custom Skills do not sync across surfaces; each surface (claude.ai, API, Claude Code) requires separate setup.**

  > "You'll need to manage and upload Skills separately for each surface where you want to use them."

  Surface-specific behaviour:
  - **claude.ai**: individual user scope; zip upload via Settings
  - **Claude API**: workspace-wide; uploaded via `/v1/skills` endpoints; no network access at runtime
  - **Claude Code**: filesystem-based; personal (`~/.claude/skills/`) or project (`.claude/skills/`)

  Section: "Cross-surface availability" and "Sharing scope."

- **Security policy explicitly warns against XML in Skill names and descriptions; Skills from untrusted sources are treated as potential attack vectors.**

  > "We strongly recommend using Skills only from trusted sources... a malicious Skill can direct Claude to invoke tools or execute code in ways that don't match the Skill's stated purpose."

  Risks enumerated: data exfiltration, unauthorized system access, unexpected network calls. The prohibition on XML tags in `name` and `description` fields is partly a security measure. Section: "Security considerations."

- **The description should encode both what the Skill does and when Claude should use it — this is the trigger signal.**

  > "The `description` should include both what the Skill does and when Claude should use it."

  This mirrors the sub-agent `description` field exactly: it drives automatic invocation without requiring explicit user instruction. Section: "Skill structure."

- **The Skills system is designed for composability: multiple Skills can be combined to build complex workflows.**

  > "**Compose capabilities**: Combine Skills to build complex workflows"

  No XML or special syntax is needed for composition — Claude infers which Skills to invoke based on descriptions. Section: "Why use Skills."

## 6. Critical Assessment

**Evidence Quality: Documentation**

First-party Anthropic documentation. Authoritative for the surface it describes. The cached version (426 lines) represents a complete page with no obvious truncation. No independent verification or peer review; accuracy depends on Anthropic maintaining the page.

**Gaps and Limitations:**

- The page does not specify what Python packages are pre-installed in the Skills execution environment; this is cross-linked to the code execution tool documentation.
- No examples of multi-file Skill directories are provided beyond the structural listing — no working `FORMS.md` or script examples are reproduced in full, making it harder to understand real-world complexity.
- The document does not address whether the `SKILL.md` body can contain XML tags within the instruction prose (as opposed to the prohibited uses in frontmatter fields). This is the central open question for Issue #12.
- Versioning of the Skill format is not discussed — no changelog or compatibility guarantees are stated.
- The relationship between Agent SDK Skills and Claude Code Skills is described only briefly; the shared `SKILL.md` format makes them seem interchangeable, but deployment paths differ significantly.

## 7. Cross-Source Connections

- Contrasts with [code-claude-com-docs-en-sub-agents](./code-claude-com-docs-en-sub-agents.md): the sub-agent format (`.claude/agents/`) uses a 12-field YAML frontmatter and a prose Markdown system prompt body. The Skills format (`SKILL.md`) uses a 2-field YAML frontmatter and a prose Markdown instruction body. Both use Markdown bodies; neither uses XML in canonical examples.
- Extends [anthropic-building-effective-agents](./anthropic-building-effective-agents.md): Skills are the concrete implementation of the "reusable context injection" concept described there.
- Connects to [platform-claude-com-docs-en-build-with-claude-prompt-enginee](./platform-claude-com-docs-en-build-with-claude-prompt-enginee.md): the prohibition on XML tags in `name`/`description` fields is consistent with Anthropic's broader use of XML as a special delimiter in prompts — XML is a reserved syntax at the model layer, not recommended for structural use in user-facing identifiers.

## 8. Project Relevance

**Issue #12 — XML-Tagged Agent Instruction Format**: The Agent Skills documentation provides a second independent data point from Anthropic's own format conventions. Like the sub-agent format, Skills use **plain Markdown** in the instruction body — no XML sectioning, no `<instructions>`, `<context>`, or `<guidance>` tags in canonical examples. Critically, the format *explicitly prohibits* XML tags in `name` and `description` fields as a security and parsing measure, signalling that Anthropic treats XML as a reserved layer, not a general-purpose formatting convention. **VERDICT: REJECT XML in instruction bodies; ADOPT Markdown with conventional heading structure (`##`) for `SKILL.md`-style instruction bodies.**

For EndogenAI's `.github/agents/*.agent.md` files, the Agent Skills architecture offers a more concrete model than the sub-agent model in one respect: the **two-tier description design** (what it does + when to use it, combined in a single `description` field of ≤1024 characters) is a constraint the EndogenAI `scaffold_agent.py` script could enforce. The current EndogenAI agent files in `.github/agents/` use Markdown headings for sectioning, which aligns with Anthropic's own production format and supports the conclusion that XML sectioning would be a divergence from the ecosystem norm.

The progressive disclosure architecture — metadata at startup, instructions on demand, resources by reference — is a design pattern the EndogenAI `session-management.md` guide could incorporate when advising agents on how to structure large instruction sets. Pre-loading context into a sub-agent's `skills` field (from Source A) combined with on-demand skill loading for the main agent is a hybrid approach directly applicable to the EndogenAI session workflow.

## Referenced By

<!-- Populated automatically by scripts/link_source_stubs.py — do not edit manually -->
- [Anthropic Building Effective Agents](../sources/anthropic-building-effective-agents.md)
- [Code Claude Com Docs En Sub Agents](../sources/code-claude-com-docs-en-sub-agents.md)
- [Platform Claude Com Docs En Build With Claude Prompt Enginee](../sources/platform-claude-com-docs-en-build-with-claude-prompt-enginee.md)
- [Xml Agent Instruction Format](../xml-agent-instruction-format.md)
