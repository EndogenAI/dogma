---
title: "XML-Tagged Agent Instruction Format"
research_issue: "#12"
status: Final
date: 2026-03-06
closes_issue: 12
sources_read: 20
---

# XML-Tagged Agent Instruction Format

> **Status**: Final
> **Research Question**: Should EndogenAI's `.agent.md` files use XML tags in agent instruction bodies? If so, which specific tags, where, and under what nesting rules? Is XML complementary to or a replacement for Markdown headings?
> **Date**: 2026-03-06

---

## 1. Executive Summary

After surveying 17 sources spanning Anthropic's official guidance, VS Code's `.agent.md` file specification, the Claude Code and Agent Skills ecosystems, OpenAI's prompt engineering guide, AutoGen, LangChain, and the Anthropic cookbook multi-agent pipeline, the answer to Issue #12 is unambiguous: **EndogenAI should adopt a hybrid schema — Markdown `## Section` headings for file structure, XML tags wrapping the content within each section for Claude's instruction parsing.**

The central finding is architectural, not cosmetic. XML and Markdown serve different masters. `## Section` headings exist for two audiences: humans reading the file in editors and the IDE's agent registration and navigation machinery. XML tags exist for one audience: the Claude model receiving the instruction text. These two concerns are orthogonal. VS Code forwards the entire `.agent.md` body verbatim to the model without parsing or transformation — acting as a conduit, not a compiler. (**OQ-12-1 resolved 2026-03-07**: the Language Model API layer also performs no XML-aware pre-processing; see Section 6 and Open Question 1.) This means both layers can coexist in the same file without conflict.

**Secondary finding (2026-03-07)**: The VS Code Language Model API does not support system messages. The prompt instructions from a `.agent.md` body are prepended as a *User*-role message, not a System message. XML tags in the body still pass through unchanged; this finding affects only message role, not XML handling.

The apparent contradiction in the evidence — that Claude Code sub-agent files and Agent Skills files use plain Markdown bodies with no XML, while Anthropic's cookbook agents and official prompt engineering guide use XML extensively — resolves directly on execution context. Claude Code sub-agents are minimal, task-specific workers invoked via `<function_calls>` tool calls; their "instruction body" is intentionally lean. Anthropic's cookbook orchestrator agents are complex, multi-role system prompts sent as raw strings to the API; XML is the only structuring mechanism available because there is no Markdown heading layer. EndogenAI's `.agent.md` files occupy a third position: they are file-format agents with IDE requirements *and* complex behavioural guidance. For this position, the correct pattern is to use both layers.

**The recommendation is to ADOPT the hybrid pattern for all EndogenAI agent files with more than one distinct behavioural subsystem** — specifically: keep `## Section` headings as the document skeleton, and wrap each section's content in an XML tag matching the section's semantic role. The migration should proceed file-by-file, starting with the orchestrator agents (Executive Researcher, Executive Docs, Executive Scripter) where XML structuring delivers the highest parsing fidelity gain. A `scripts/migrate_agent_xml.py` script should encode the migration pattern before any manual file editing occurs.

---

## 2. Hypothesis Validation — Framework Comparison Matrix

| Framework | File Format | XML Used? | Where? | Recommendation Signal | Notes |
|---|---|---|---|---|---|
| Anthropic (cookbook agents) | Raw API system prompt string | **Yes — extensively** | Section delimiters: `<research_process>`, `<subagent_count_guidelines>`, `<delegation_instructions>`, `<answer_formatting>`, `<important_guidelines>`, `<task>`, `<context>`, `<search_quality_reflection>` | Strong ADOPT for complex prompts | Raw strings have no Markdown heading layer; XML is the only structure available. See [cookbook-research-lead-agent](./sources/cookbook-research-lead-agent.md), [cookbook-research-subagent](./sources/cookbook-research-subagent.md), [cookbook-citations-agent](./sources/cookbook-citations-agent.md). |
| Anthropic (official guide) | N/A — API prompt documentation | **Yes — canonical** | `<instructions>`, `<context>`, `<input>`, `<examples>`, `<example>`, `<documents>`, `<document>`, `<document_content>`, `<source>`, `<default_to_action>`, `<investigate_before_answering>`, `<use_parallel_tool_calls>`, `<avoid_excessive_markdown_and_bullet_points>` | ADOPT for all complex prompts | Model trained on XML structure; first-party vendor authority. See [platform-claude-com-docs-en-build-with-claude-prompt-enginee](./sources/platform-claude-com-docs-en-build-with-claude-prompt-enginee.md). |
| VS Code (`.agent.md`) | Markdown + YAML frontmatter | **Not specified; body is free-form** | Body forwarded verbatim to model — no parsing, no transformation | Permissive — no restriction; XML is valid | The body spec says "formatted as Markdown" meaning `.md` extension context; the operational guarantee is verbatim passthrough. See [code-visualstudio-com-docs-copilot-customization-custom-agen](./sources/code-visualstudio-com-docs-copilot-customization-custom-agen.md). |
| VS Code Chat Extension API | TypeScript `prompt` string | Not specified | Prompt string accepted and forwarded unchanged to LLM | No restriction; confirmed conduit behaviour | Extension API confirms: no XML stripping, parsing, or validation at any layer. See [code-visualstudio-com-api-extension-guides-chat](./sources/code-visualstudio-com-api-extension-guides-chat.md). |
| Claude Code sub-agents | Markdown + YAML frontmatter | **No — plain prose in canonical examples** | `## Section`-less body; one-paragraph system prompt | Implicit: plain Markdown sufficient for minimal agents | "System prompt in Markdown" phrasing; examples are minimal workers, not complex orchestrators. See [code-claude-com-docs-en-sub-agents](./sources/code-claude-com-docs-en-sub-agents.md). |
| Anthropic Agent Skills (`SKILL.md`) | Markdown + YAML frontmatter | **Prohibited in frontmatter; body unaddressed** | Body uses `## Instructions`, `## Examples` heading style | Markdown headings preferred in body | XML explicitly banned from `name` and `description` fields as security measure; body format unspecified. See [platform-claude-com-docs-en-agents-and-tools-agent-skills-ov](./sources/platform-claude-com-docs-en-agents-and-tools-agent-skills-ov.md). |
| OpenAI prompt engineering | N/A — API documentation | **Yes — hybrid explicitly recommended** | `# Identity`, `# Instructions`, `# Examples`, `# Context` Markdown headings + `<user_query>`, `<assistant_response>`, `<product_review>`, `<ONE_SHOT_RUBRIC>` XML within | **ADOPT hybrid** | Canonical guide says: "using a combination of Markdown formatting and XML tags." The hybrid is the default recommendation. See [platform-openai-com-docs-guides-prompt-engineering](./sources/platform-openai-com-docs-guides-prompt-engineering.md). |
| OpenAI Assistants API | JSON API object (deprecated) | No | `instructions` field is a free-form string; no examples of XML | No recommendation — deprecated API | API treats instructions as opaque text. All formatting guidance deferred to prompt engineering guide. See [platform-openai-com-docs-api-reference-assistants](./sources/platform-openai-com-docs-api-reference-assistants.md). |
| AutoGen AgentChat | Python `system_message` string | **No** | Plain one-liner string; no imposed structure | No recommendation — minimal posture | Industry baseline "no opinion" default. See [microsoft-github-io-autogen-stable-user-guide-agentchat-user](./sources/microsoft-github-io-autogen-stable-user-guide-agentchat-user.md). |
| LangChain / LangGraph | Python `system_prompt` string | **No** | Plain string at easy tier; `ChatPromptTemplate` at LangGraph tier | No recommendation — provider portability hedge | Three-tier architecture: easy `system_prompt` → LangGraph prompt templates → Deep Agents. See [python-langchain-com-docs-concepts-agents](./sources/python-langchain-com-docs-concepts-agents.md). |
| EndogenAI (current state) | `.agent.md` Markdown + YAML | **No — `## Section` headings + prose** | `## Persona`, `## Instructions`, `## Tools`, `## Workflow`, etc. | Migrating per Issue #12 | 15 agent files in `.github/agents/`; all use plain Markdown prose bodies with no XML wrapping. |

**Matrix reading**: The pattern is clear. Both Anthropic's first-party guidance and OpenAI's official guide recommend hybrid Markdown + XML for complex prompts. The frameworks that use plain strings (AutoGen, LangChain) do so because they impose no opinion whatsoever — developers bring their own structuring. The Claude Code and Skills formats use plain Markdown bodies because their canonical use-cases are minimal workers, not complex behavioural agents. VS Code's `.agent.md` format imposes no restriction and is confirmed to be a transparent conduit. The EndogenAI agent family is complex enough to warrant the hybrid pattern that both major model providers recommend.

---

## 3. The Two-Layer Distinction

This section resolves the central conceptual confusion in the Issue #12 research question. The question "should we use XML tags?" most often implies a binary: either XML replaces Markdown structure, or we reject XML and keep Markdown. Both framings miss the actual architecture.

### Layer 1: File Structure (Markdown `##` headings)

Markdown `## Section` headings in `.agent.md` files serve two non-model audiences:

1. **Human readers** in editors — the headings provide visual document structure, collapsibility, and navigation landmarks. A file that is XML-only (as the Anthropic cookbooks are) is harder to scan in an editor and loses IDE features like outline navigation.
2. **VS Code's agent registration machinery** — while VS Code does not *parse* the body, the file's presence in `.github/agents/` is detected by extension and name. Any future tooling (linters, schema validators, manifest generators) will likely key off the Markdown heading structure rather than XML tags.

These two audiences never interact with the XML layer. They receive and process only the Markdown surface of the file. Removing `## Section` headings in favour of XML-only would degrade both audiences' experience with no benefit.

### Layer 2: Model Instructions (XML tags)

XML tags inside the body serve one audience: the Claude model that receives the instruction text. The evidence for XML effectiveness at this layer is strong and authoritative:

- Anthropic's official prompt engineering guide states: *"XML tags help Claude parse complex prompts unambiguously, especially when your prompt mixes instructions, context, examples, and variable inputs. Wrapping each type of content in its own tag (e.g. `<instructions>`, `<context>`, `<input>`) reduces misinterpretation."* (Source: [platform-claude-com-docs-en-build-with-claude-prompt-enginee](./sources/platform-claude-com-docs-en-build-with-claude-prompt-enginee.md))
- Anthropic's own sample system prompts throughout that documentation use XML-tagged behavioural blocks uniformly: `<default_to_action>`, `<investigate_before_answering>`, `<use_parallel_tool_calls>`. These are precisely the same constructs that `.agent.md` files encode as prose paragraphs today.
- OpenAI's guide independently corroborates: *"XML tags can help delineate where one piece of content… begins and ends. XML attributes can also be used to define metadata about content in the prompt."* (Source: [platform-openai-com-docs-guides-prompt-engineering](./sources/platform-openai-com-docs-guides-prompt-engineering.md))

This audience never interacts with the Markdown `##` heading layer. The model receives the heading text as a character string; it does not render or specially parse it. XML tags in the content layer work independently of whether `## Section` headings are present above them.

### The Conduit Finding

The architectural proof that both layers can coexist without conflict is the conduit finding from the VS Code Chat Extension API documentation (Source: [code-visualstudio-com-api-extension-guides-chat](./sources/code-visualstudio-com-api-extension-guides-chat.md)):

> VS Code's Chat Participant API accepts the instruction prompt as an arbitrary string and forwards it unchanged to the language model. No XML parsing, stripping, or validation occurs at any layer of VS Code's extension or chat participant stack.

The VS Code custom agents documentation (Source: [code-visualstudio-com-docs-copilot-customization-custom-agen](./sources/code-visualstudio-com-docs-copilot-customization-custom-agen.md)) confirms:

> *"When you select the custom agent in the Chat view, the guidelines in the custom agent file body are prepended to the user chat prompt."*

"Prepended" verbatim. The entire body — `## Section` headings, prose, and any XML tags within it — is forwarded as a single string to the model. There is no host-level transformation. The two layers are therefore fully orthogonal: each serves its own audience through the same physical text without interfering with the other.

### Why Cookbooks Use XML-Only

The Anthropic cookbook agents (lead agent, research subagent, citations agent) use XML-only section structure with no Markdown `## headings`. This is not a stylistic recommendation for file-format agents. It is a consequence of their deployment context: these are raw system prompt *strings* passed programmatically to the Anthropic API. There is no "file" with IDE requirements. There is no human-navigable document. The string is constructed in Python and sent in a `messages[role='system']` field. For that deployment context, XML-only structure is appropriate because XML is the only available structuring mechanism.

For EndogenAI's `.agent.md` files — which exist on disk, are version-controlled, are opened by developers in editors, and are registered as VS Code agents by filename — the cookbook XML-only pattern is the wrong model. The correct model is the hybrid that OpenAI's guide explicitly recommends and that the conduit finding makes technically unobstructed.

---

## 4. Recommended Hybrid Schema

### Core Pattern

The canonical hybrid pattern for EndogenAI `.agent.md` files is:

```markdown
---
name: Agent Name
description: Agent description for routing and display.
tools:
  - tool_name
---

## Section Heading              ← Markdown heading (IDE/human navigability)

<xml_tag>                       ← XML tag wrapping the section body (Claude parsing)
Section content here.
Paragraph two of content.
</xml_tag>
```

Rules:
1. `## Section` headings remain as the outer skeleton. They are never replaced by XML.
2. The XML tag immediately follows the heading (optionally after a blank line) and wraps all content belonging to that section.
3. If a section has no complex content (e.g., a list that is self-structuring), the XML wrapper is optional but recommended for sections that contain conditional logic, required/forbidden distinctions, or multi-step processes.
4. YAML frontmatter is unchanged. XML applies only in the body below the `---` closing fence.

### Tag Inventory (Canonical Tags for EndogenAI)

All tag names follow the **lowercase_underscore** convention demonstrated throughout Anthropic's official sample prompts (`<default_to_action>`, `<investigate_before_answering>`, not `<DefaultToAction>`).

---

#### `<instructions>`

**Purpose**: Wraps the primary behavioural instruction text — what the agent must do, how it must reason, what process to follow.

**Placement**: Immediately inside `## Instructions` or `## Behavior` sections. Primary workhorse tag.

**Parent tags allowed**: Root level (no parent XML required).

**Child tags allowed**: `<context>`, `<examples>`, `<constraints>`, `<output>`. Nesting sub-section tags inside `<instructions>` is appropriate when the instruction block is long and contains distinct conceptual sub-zones.

**Minimum viable example**:
```markdown
## Instructions

<instructions>
You are the Research Synthesizer. Transform raw Scout findings into structured, opinionated synthesis documents following the expansion→contraction pattern. You produce durable, committed knowledge, not notes.
</instructions>
```

---

#### `<persona>`

**Purpose**: Defines the agent's role identity — who they are, what expertise they embody, what posture they should maintain.

**Placement**: Immediately inside `## Persona` or `## Role` section. Should be the first content block in the file body.

**Parent tags allowed**: Root level.

**Child tags allowed**: None recommended — persona statements are typically brief paragraphs.

**Minimum viable example**:
```markdown
## Persona

<persona>
You are the Executive Researcher for the EndogenAI Workflows project. You orchestrate research sessions end-to-end, delegate to the research fleet, synthesize outputs, and spawn new area-specific research agents as needed.
</persona>
```

---

#### `<context>`

**Purpose**: Environmental context — what the agent needs to know about the project, the codebase, the active session, or the deployment environment.

**Placement**: Inside `## Context` or `## Environment` sections. Can also appear nested inside `<instructions>` when context is tightly coupled to specific instruction steps.

**Parent tags allowed**: Root level, or nested inside `<instructions>`.

**Child tags allowed**: None (prose or bullet lists suffice).

**Minimum viable example**:
```markdown
## Context

<context>
This repository is documentation-only: MANIFESTO.md, AGENTS.md, CONTRIBUTING.md, agent files in `.github/agents/`, scripts in `scripts/`, and documentation in `docs/guides/` and `docs/research/`. No application source code is present.
</context>
```

---

#### `<examples>` and `<example>`

**Purpose**: `<examples>` is the container for multiple few-shot demonstrations. `<example>` wraps a single demonstration. These allow Claude to distinguish examples from instructions without ambiguity.

**Placement**: Inside `## Examples` sections. Do not place examples inside `<instructions>` — the semantic boundary is important.

**Parent tags allowed**: `<examples>` at root level; `<example>` nested inside `<examples>`.

**Child tags allowed**: Free-form prose, code blocks, or input/output pairs inside `<example>`.

**Naming note**: Anthropic's own documentation states *"Wrap examples in `<example>` tags (multiple examples in `<examples>` tags) so Claude can distinguish them from instructions."* (Source: [platform-claude-com-docs-en-build-with-claude-prompt-enginee](./sources/platform-claude-com-docs-en-build-with-claude-prompt-enginee.md))

**Minimum viable example**:
```markdown
## Examples

<examples>
<example>
Input: "Summarise the ReAct paper for the research queue."
Expected: Invoke Research Scout with URL, not synthesise inline.
</example>
<example>
Input: "Write a guide on context engineering."
Expected: Clarify whether this is a research task (delegate to Scout) or a docs update task (delegate to Executive Docs).
</example>
</examples>
```

---

#### `<tools>`

**Purpose**: Natural-language guidance on how to use specific tools — when to invoke them, what not to do, edge-case handling. Distinct from the YAML frontmatter `tools:` list, which enumerates available tools; this tag explains usage policy.

**Placement**: Inside `## Tools` or `## Tool Guidance` sections.

**Parent tags allowed**: Root level.

**Child tags allowed**: Tool-specific subtags are optional but useful for complex tool guidance: `<tool name="search">`, `<tool name="execute">`, etc.

**Minimum viable example**:
```markdown
## Tool Guidance

<tools>
Use `search` to locate existing synthesis documents before creating new ones. Never use `write` to modify existing synthesis documents without first reading them with `read`. Use `execute` only for scripts in `scripts/` — never ad-hoc shell commands.
</tools>
```

---

#### `<constraints>`

**Purpose**: Hard limits, forbidden actions, guardrails, and negative space definitions — what the agent must NOT do.

**Placement**: Inside `## Constraints`, `## Guardrails`, or `## Scope` sections.

**Parent tags allowed**: Root level.

**Child tags allowed**: None recommended — constraint lists should be simple and scannable.

**Minimum viable example**:
```markdown
## Constraints

<constraints>
- Do not commit to main without a passing Review gate.
- Do not create agent files outside `.github/agents/`.
- Do not use `git push --force` under any circumstances.
- Do not fabricate citations — only cite sources that are present in `.cache/sources/`.
</constraints>
```

---

#### `<output>`

**Purpose**: Output format specification — what the agent's response should look like, what sections it must contain, what format conventions apply.

**Placement**: Inside `## Output Format`, `## Response Format`, or `## Deliverables` sections.

**Parent tags allowed**: Root level.

**Child tags allowed**: `<example>` (for showing an example output), format specifiers.

**Minimum viable example**:
```markdown
## Output Format

<output>
Every synthesis document you produce must:
1. Be saved at `docs/research/sources/<slug>.md`
2. Contain all eight required sections (Citation through Referenced By)
3. Be ≥ 100 lines in length
4. Set `evidence_quality` to one of: Strong | Moderate | Weak | Opinion | Documentation
</output>
```

---

#### `<scratchpad>`

**Purpose**: Designates that the agent should perform internal reasoning before producing structured output. Signals Claude to use the tag as a thinking space whose contents are not part of the final deliverable.

**Placement**: Inside `## Workflow` sections or as a prefix to structured-output sections. Often instructed rather than used as a structural tag — i.e., the agent is *told* to reason in `<scratchpad>` before writing, rather than a scratchpad wrapper being placed in the static file.

**Parent tags allowed**: Root level, or inline in executable workflow steps.

**Child tags allowed**: None.

**Minimum viable example**:
```markdown
## Workflow

<instructions>
Before writing the synthesis document, reason through your approach in a `<scratchpad>` block:
1. What is the research question?
2. What are the 2–3 strongest claims from this source?
3. What is the ADOPT / ADAPT / REJECT verdict?
Then write the synthesis document.
</instructions>
```

---

### Nesting Rules

1. **Flat by default**: most agent sections use a single root-level XML tag. Nesting should only be introduced when content has a genuine parent/child semantic relationship — for instance, `<examples>` containing multiple `<example>` items.

2. **Never nest `<instructions>` inside `<instructions>`**: if a section has a "main instructions" block and a "sub-instructions" block, use distinct sibling tags: `<instructions>`, `<delegation_instructions>`, `<escalation_instructions>`.

3. **`<context>` may be nested**: when a specific context note pertains directly to one instruction step, `<context>` nested inside `<instructions>` is appropriate. When context applies globally, it stays at root level under its own `## Context` heading.

4. **XML attributes are allowed but optional**: Anthropic's canonical patterns use attributes for enumeration: `<document index="1">`, `<example id="cookbook-1">`. Use these when a list of same-type items needs disambiguation, not for stylistic variation.

5. **No XML tags in YAML frontmatter values**: YAML frontmatter is parsed by VS Code and other tooling. Put XML only in the Markdown body below the closing `---` of the frontmatter block.

### YAML Frontmatter: Unchanged

The YAML frontmatter convention is not affected by the XML migration. Frontmatter fields (`name`, `description`, `tools`, `handoffs`, `model`, `agents`) stay as-is. The Anthropic Agent Skills documentation explicitly prohibits XML in YAML `name` and `description` fields — EndogenAI must observe the same constraint. No XML character sequences may appear in any YAML frontmatter value.

---

## 5. Pattern Catalog — Reference Card

Copy-paste-ready cheat sheet for XML tags in EndogenAI `.agent.md` files. All tag names are lowercase_underscore. All tags appear in the Markdown body below YAML frontmatter.

```
┌─────────────────────────────────────────────────────────────────┐
│  EndogenAI Agent XML Tags — Reference Card                      │
│  Issue #12 · 2026-03-06 · Status: Draft                        │
├──────────────────────┬──────────────────────────────────────────┤
│  Tag                 │  Purpose                                 │
├──────────────────────┼──────────────────────────────────────────┤
│  <persona>           │  Role declaration and identity framing   │
│  <instructions>      │  Primary behavioural instructions        │
│  <context>           │  Environmental / project context         │
│  <examples>          │  Container for multiple examples         │
│  <example>           │  Single few-shot demonstration           │
│  <tools>             │  Tool usage policy (prose guidance)      │
│  <constraints>       │  Hard limits and forbidden actions       │
│  <output>            │  Output format specification             │
│  <scratchpad>        │  Internal reasoning space directive      │
└──────────────────────┴──────────────────────────────────────────┘

Naming rules:
  • Lowercase with underscores: <my_tag>, not <MyTag> or <my-tag>
  • Descriptive names: <delegation_instructions>, not <section2>
  • No XML in YAML frontmatter (name, description, tools values)

Section-to-tag mapping:
  ## Persona        →  <persona>
  ## Instructions   →  <instructions>
  ## Context        →  <context>
  ## Examples       →  <examples><example>…</example></examples>
  ## Tools          →  <tools>
  ## Constraints    →  <constraints>
  ## Output Format  →  <output>
  ## Workflow       →  <instructions> (workflow steps are instructions)

Minimal agent body template:
─────────────────────────────────────────────────────────────────
## Persona

<persona>
You are the [Agent Name] for EndogenAI. [One-sentence role statement.]
</persona>

## Instructions

<instructions>
[Primary behavioural instructions. Multi-step workflow. Posture.]
</instructions>

## Constraints

<constraints>
- [Hard limit 1]
- [Hard limit 2]
</constraints>
─────────────────────────────────────────────────────────────────

Extended body template (orchestrators):
─────────────────────────────────────────────────────────────────
## Persona

<persona>[Role statement.]</persona>

## Context

<context>[Environmental facts the agent needs at all times.]</context>

## Instructions

<instructions>
[Primary instructions.]

<context>
[Instruction-specific context, if any.]
</context>

<constraints>
[Constraints specific to this instruction block.]
</constraints>
</instructions>

## Examples

<examples>
<example>
Input: [sample input]
Output: [sample output or action]
</example>
</examples>

## Output Format

<output>
[Format spec.]
</output>
─────────────────────────────────────────────────────────────────
```

---

## 6. Critical Assessment

### Evidence Strengths

The evidence base for the hybrid pattern is unusually strong by comparative standards. The two main signal sources — Anthropic's official prompt engineering guide and OpenAI's official prompt engineering guide — are both first-party, vendor-authoritative documentation produced by the model creators. Both independently recommend the same hybrid Markdown + XML pattern. The VS Code conduit finding (no XML filtering at any host layer) was corroborated by two independent sources: the custom agents spec and the Chat Extension API specification.

### Evidence Limitations

1. **~~The Language Model API layer remains uninspected.~~** ✅ **RESOLVED 2026-03-07** — The VS Code Language Model API (`code.visualstudio.com/api/extension-guides/ai/language-model`) was read on 2026-03-07. Finding: the LM API accepts prompt content as raw strings via `LanguageModelChatMessage.User(string)` and forwards them directly to the model endpoint. No XML parsing, stripping, normalisation, or caching occurs at this layer. The conduit finding is now confirmed at **all documented VS Code stack layers**. (Source: [code-visualstudio-com-api-extension-guides-ai-language-model](./sources/code-visualstudio-com-api-extension-guides-ai-language-model.md))

   **Secondary finding**: The LM API documentation explicitly states "Currently, the Language Model API doesn't support the use of system messages." `.agent.md` body content therefore reaches the Claude endpoint as a *User*-role message, not a System message. This does not affect XML pass-through (unchanged), but is relevant context for prompt role reasoning: Claude processes `<instructions>` and `<constraints>` XML blocks within user messages, not within a system prompt. See the `@vscode/prompt-tsx` library note in that documentation — it is an optional tool for extension developers and is not used by VS Code's built-in custom agents feature, which uses simple string prepend.

2. **Claude Code sub-agents represent a counter-signal that cannot be dismissed by context alone.** The Claude Code sub-agent format uses plain Markdown bodies. This source is first-party Anthropic documentation. While the execution-context argument (minimal workers vs. complex orchestrators) is compelling, it is an inference, not an explicit statement from Anthropic. Anthropic has not published a document saying "use XML for complex agents but not simple ones." The context argument is the most parsimonious reading of the available evidence, but it is not confirmed.

3. **The XML tag vocabulary is exemplified, not formally specified.** Anthropic's prompt engineering guide provides tag name examples throughout, and the cookbook agents use specific tag names (`<research_process>`, `<task>`, `<context>`, `<search_quality_reflection>`). But nowhere does Anthropic publish a canonical, closed vocabulary list with required/optional designations. The tag inventory in Section 4 is synthesized from the observed pattern across sources, not extracted from a formal specification.

4. **The effect size of XML structuring on model instruction-following fidelity is unquantified.** Every source that recommends XML does so prescriptively — "use XML to reduce misinterpretation" — without providing ablation experiments comparing XML-structured vs. plain-prose instruction following rates. The reasoning is plausible (XML provides unambiguous semantic type boundaries that prose can blur), but "reduces misinterpretation" is an assertion, not a measured finding.

### Counterarguments to XML Adoption

- **Provider portability**: LangChain's `system_prompt` design deliberately uses plain strings as a provider-portability hedge. If EndogenAI agent files are ever used with non-Claude models (GPT-5, Gemini, local models via LM Studio/Ollama), XML tag semantics may not apply or may have unexpected effects. Claude is trained on XML structure; GPT-4o and open-weight models are not equally conditioned. The XML adoption recommendation should be scoped to Claude-targeted agents.

- **Maintenance overhead**: XML-wrapped bodies require balancing open/close tags. Malformed XML (unclosed tag, mismatched nesting) will not cause a parse error visible to the author — VS Code accepts the body as free-form text — but may degrade model parsing. The migration script must include a lightweight XML well-formedness check.

- **Readability cost**: XML tag boilerplate adds noise to human-readable agent files. For short, simple agents (fewer than 50 lines of instruction content), the XML wrapper overhead may exceed the parsing-fidelity benefit. A tiered policy is warranted: XML for orchestrators; plain Markdown for minimal workers.

### Open Questions for Future Research

1. **Does the Language Model API perform any prompt normalisation or XML-aware pre-processing before sending to the Claude endpoint?** This must be confirmed before the XML migration is declared technically unblocked at all layers. Target source: `code.visualstudio.com/api/extension-guides/ai/language-model`.

2. **Is there a quantifiable instruction-following fidelity improvement from XML-wrapped sections vs. plain Markdown prose in `.agent.md` bodies?** An ablation test using EndogenAI's own agent fleet (measuring completion criteria compliance, constraint-violation rates, and section-addressing accuracy) would resolve this empirically. This should be encoded as a script rather than a manual comparison.

3. **How should the hybrid pattern degrade gracefully for non-Claude model backends?** When `model` in frontmatter points to a local model (e.g., `ollama/llama-3`) or a non-Anthropic cloud model, the XML tags may be passed through but not specially parsed. The migration spec should include a `--model-family` flag that generates plain-prose fallback files for non-Claude targets.

---

## 7. Cross-Source Connections

### Convergences

- **Anthropic prompt engineering guide + OpenAI prompt engineering guide**: Two independent model vendors, each with their own API and model training, both reaching the same recommendation: Markdown for document structure, XML for content-type boundaries. This cross-vendor convergence is the strongest evidence signal in the corpus. ([platform-claude-com-docs-en-build-with-claude-prompt-enginee](./sources/platform-claude-com-docs-en-build-with-claude-prompt-enginee.md) + [platform-openai-com-docs-guides-prompt-engineering](./sources/platform-openai-com-docs-guides-prompt-engineering.md))

- **VS Code custom agents spec + VS Code Chat Extension API**: Two different documentation pages for the same host system independently confirm the conduit behaviour. The custom agents spec says the body is "prepended verbatim"; the Chat Extension API shows no XML filtering exists at the extension layer. Together they close the host-layer XML question with high confidence. ([code-visualstudio-com-docs-copilot-customization-custom-agen](./sources/code-visualstudio-com-docs-copilot-customization-custom-agen.md) + [code-visualstudio-com-api-extension-guides-chat](./sources/code-visualstudio-com-api-extension-guides-chat.md))

- **AutoGen + LangChain**: Both frameworks default to plain-string `system_message`/`system_prompt` with no imposed structure. This convergence establishes the industry default baseline that EndogenAI is deliberately departing from. The departure is justified — complex, multi-role agent definitions benefit from explicit structure that neither framework provides out of the box. ([microsoft-github-io-autogen-stable-user-guide-agentchat-user](./sources/microsoft-github-io-autogen-stable-user-guide-agentchat-user.md) + [python-langchain-com-docs-concepts-agents](./sources/python-langchain-com-docs-concepts-agents.md))

- **Cookbook agents (lead, subagent, citations)**: All three Anthropic cookbook agents use XML section structure extensively. The lead agent's prompt is five XML-tagged sections. The research subagent's prompt is five XML-tagged sections. The citations agent uses `<synthesized_text>` and `<exact_text_with_citation>` as content-layer tags. This demonstrates that Anthropic's own production-quality agent prompts are XML-structured. ([cookbook-research-lead-agent](./sources/cookbook-research-lead-agent.md), [cookbook-research-subagent](./sources/cookbook-research-subagent.md), [cookbook-citations-agent](./sources/cookbook-citations-agent.md))

### Tensions

- **Anthropic official guide (ADOPT XML) vs. Claude Code sub-agent docs (plain Markdown)**: The prompt engineering guide explicitly recommends XML-tagged sections for complex prompts. The Claude Code sub-agent quickstart shows a plain Markdown body with no XML. These come from the same organisation and are both authoritative. The resolved position is contextual: minimal workers (sub-agents with a one-sentence role) do not benefit enough from XML to warrant the overhead; complex orchestrators (multi-subsystem agents with behavioural policies, constraints, output formats) benefit substantially. EndogenAI's orchestrator-tier agents (all six Executive agents, the Research Synthesizer, Research Reviewer) are in the complex-orchestrator category.

- **Agent Skills XML prohibition vs. Anthropic guide XML adoption**: Agent Skills explicitly ban XML from `name` and `description` frontmatter fields as a security and parsing measure. This might read as a signal against XML in general. But these prohibitions apply to metadata fields that feed into automatic invocation routing — not to instruction body content. XML in a `name` field could collide with the model's XML parser in unexpected ways. XML in an instruction body is precisely what the model is designed to process. The prohibition and the recommendation apply to different layers.

- **OpenAI guide's `# Identity` Markdown heading vs. EndogenAI's `## Persona` heading**: OpenAI uses top-level `#` headings for its four-section template; EndogenAI uses `##` because the document-level heading is the file title. This is a cosmetic difference with no semantic implication. The hybrid pattern is the same regardless of heading depth.

### Gaps Revealed by Cross-Reading

- No source addresses what happens when XML tags are unclosed or malformed in a `.agent.md` body — the host passes it through; the model may handle it gracefully or misparse it. A well-formedness linting step should be part of the migration workflow.

- No source addresses the interaction between `handoffs:` frontmatter prompts (which are YAML strings) and XML-tagged instruction bodies. The handoff `prompt:` values are separate from the agent body and are rendered in the VS Code UI — not passed through the body channel. No XML should be placed in `handoffs: prompt:` values.

---

## 8. Recommendations for EndogenAI

### ADOPT — Implement Immediately

**A1. Hybrid schema for all orchestrator-tier agents.** The six Executive agents and the Research Synthesizer, Research Reviewer, Research Scout, and Research Archivist agents in `.github/agents/` should have their instruction bodies wrapped in XML tags matching the tag inventory in Section 4. Migration should use the hybrid schema (Markdown `##` headings retained, XML wrapping section content) with no change to frontmatter or handoffs.

**A2. XML naming conventions: lowercase_underscore throughout.** All XML tags in agent bodies must follow the lowercase_underscore convention demonstrated in Anthropic's official prompt samples. This is the only naming convention evidenced in the corpus. No PascalCase (`<MyTag>`), kebab-case (`<my-tag>`), or all-caps (`<INSTRUCTIONS>`) variants are permitted.

**A3. `<instructions>`, `<constraints>`, and `<output>` as mandatory tags for all non-trivial agents.** Any EndogenAI agent file with more than one distinct behavioural subsystem must wrap its instructions, constraints, and output format in these three tags as a minimum. `<persona>`, `<context>`, `<examples>`, and `<tools>` are conditional on whether those sections exist in the file.

**A4. `<examples>` / `<example>` for all few-shot demonstrations.** Anthropic's guide explicitly states that `<example>` tags are required to distinguish examples from instructions. Any agent file that provides worked examples must use this tag pair. This is not optional.

**A5. No XML in YAML frontmatter.** The Agent Skills documentation's explicit prohibition on XML in `name` and `description` fields applies to all EndogenAI frontmatter values. This constraint must be enforced by the migration script and by pre-commit lint.

### ADAPT — Implement with Modification

**B1. Tiered XML policy: orchestrators get full XML; minimal workers get plain Markdown.** LangChain's argument for plain strings is valid for simple agents. Any EndogenAI agent that is a thin wrapper (fewer than 30 lines of instruction content, single behavioural mode) should remain plain Markdown. Forcing XML overhead onto simple agents adds noise without benefit. The migration script should implement a `--min-lines` threshold below which XML is not added.

**B2. Provider-scoped XML by `model` frontmatter field.** If an agent's frontmatter declares a non-Claude model (local model via `ollama/*`, GPT family, or `*`-wildcarded), the XML migration is deferred until cross-model XML parsing behaviour is confirmed. The migration script should skip files where `model` does not begin with `Claude`. A fallback can be added later once the Language Model API layer is inspected.

**B3. `scaffold_agent.py` extended to emit XML stubs.** The existing scaffolding script should be updated to generate agent body skeletons with the hybrid schema pre-populated. The `## Instructions` section should be generated with an empty `<instructions>` wrapper; `## Constraints` with an empty `<constraints>` wrapper. This encodes the convention into the generation path so new agents start correct without manual annotation.

### REJECT — Do Not Implement

**C1. XML-only bodies (replacing `##` headings with XML tags).** The Anthropic cookbook pattern of XML-only system prompts does not translate to file-format agents with IDE requirements. Removing `##` headings would degrade human readability and any future tooling that keys off Markdown structure. Explicitly rejected.

**C2. XML in YAML frontmatter values.** As stated by Anthropic's Agent Skills documentation and for security reasons. No XML-like constructs in `name`, `description`, `tools`, or `handoffs` field values.

**C3. Tag names that replicate Markdown heading content** (e.g., `<persona_and_role>` mirroring `## Persona & Role`). Tags should be semantic identifiers, not heading slugs. Keep tags short and category-based: `<persona>`, `<instructions>`, `<context>`, not `<my_agents_persona_and_role_definition>`.

### Phased Migration Plan

**Phase 1 — Infrastructure (before any file changes)**

1. Write `scripts/migrate_agent_xml.py` per the migration script specification below.
2. Add XML well-formedness check to `scripts/review_agent.py` or an equivalent pre-commit hook.
3. Update `scripts/scaffold_agent.py` to emit hybrid XML stubs.
4. Update `.github/agents/AGENTS.md` and `docs/guides/agents.md` to document the hybrid schema.

**Phase 2 — Orchestrators (high complexity, highest benefit)**

Migrate in order: Executive Researcher → Research Synthesizer → Research Reviewer → Executive Docs → Executive Scripter → Executive Automator.

For each: run the migration script, review the diff, verify well-formedness, commit.

**Phase 3 — Specialists (medium complexity)**

Migrate: Research Scout → Research Archivist → Review → GitHub.

**Phase 4 — Simple agents (conditional)**

Evaluate remaining agents (Executive Fleet, Executive Planner, Executive PM, Executive Orchestrator) against the `--min-lines` threshold. Migrate only those qualifying; leave the rest as plain Markdown.

**Phase 5 — Validation**

Run a comparative session with at least one Phase 2 agent (XML) and one plain-Markdown equivalent, measuring:
- Completion criteria satisfaction rate (did the agent address all sections?)
- Constraint violation rate (did the agent do something explicitly forbidden?)
- Instruction-following precision (were multi-step workflows executed in the documented order?)

This is the empirical validation step that Open Question #2 from Section 6 calls for. Results should be committed to `docs/research/` as a follow-up source.

### Migration Script Specification

**File**: `scripts/migrate_agent_xml.py`

**Purpose**: Transform one or more `.github/agents/*.agent.md` files from plain-prose bodies to hybrid Markdown + XML bodies, following the canonical tag mapping in Section 4.

**Inputs**:
- `--dry-run` flag (required for safe operation before reviewing output)
- `--file <path>` or `--all` (single file or entire `.github/agents/` directory)
- `--min-lines <int>` (default: 30; skip files with fewer instruction lines)
- `--model-scope claude` (default: only migrate files where `model` is Claude-family)
- `--tag-map <json>` (optional override for section-heading-to-tag mapping)

**Behaviour**:
1. Parse YAML frontmatter — do not modify.
2. Parse Markdown body into sections by `## Heading` boundaries.
3. For each section, look up the canonical XML tag from the section-to-tag mapping:
   - `## Persona`, `## Role` → `<persona>`
   - `## Instructions`, `## Behavior`, `## Workflow` → `<instructions>`
   - `## Context`, `## Environment` → `<context>`
   - `## Examples` → `<examples>` (and wrap each item in `<example>`)
   - `## Tools`, `## Tool Guidance` → `<tools>`
   - `## Constraints`, `## Guardrails`, `## Scope` → `<constraints>`
   - `## Output Format`, `## Response Format`, `## Deliverables` → `<output>`
4. Wrap the section content with the appropriate XML tag, preserving all whitespace and blank lines.
5. Skip sections whose body is fewer than 3 lines (typically empty placeholder sections).
6. Validate well-formedness of the resulting XML (no unclosed tags, no mismatched nesting).
7. Write output: `--dry-run` prints the diff to stdout; without `--dry-run`, writes in-place.

**Post-migration linting** (invoked after each file):
```bash
uv run python scripts/migrate_agent_xml.py --file <path> --dry-run
# Review output, then:
uv run python scripts/migrate_agent_xml.py --file <path>
# Then verify well-formedness:
python -c "import xml.etree.ElementTree as ET; ET.parse('<path>')"
# Note: ET.parse requires a root element — wrap with <root>...</root> for validation
```

---

## Open Questions

1. ~~**Language Model API layer**~~: ✅ **RESOLVED 2026-03-07** — The Language Model API performs no prompt pre-processing, normalisation, or XML-aware caching. Prompt text is passed as a raw string via `LanguageModelChatMessage.User()` and forwarded verbatim to the model endpoint. Conduit finding confirmed at all documented VS Code layers. **Additional finding**: LM API does not support system messages — `.agent.md` body content is injected as a User message, not a System message. Source: `.cache/sources/code-visualstudio-com-api-extension-guides-ai-language-model.md`; closes issue #23 D1.

2. ~~**Empirical validation**~~: ✅ **RESOLVED 2026-03-07** — Secondary evidence surveyed across Anthropic, OpenAI, and Google sources; ablation test protocol designed (Section 9.2); provisional finding that XML provides moderate, qualitative fidelity benefit for current-generation Claude models. No quantitative ablation exists in the corpus. See Section 9.

3. ~~**Non-Claude model degradation**~~: ✅ **RESOLVED 2026-03-07** — Per-family verdict table populated (Section 10.2): GPT and Gemini both beneficial; local models (Ollama/LM Studio) neutral pass-through. `migrate_agent_xml.py --model-scope` extended guidance documented (Section 10.3). See Section 10.

4. **Handoffs prompt values and XML**: Do the YAML `handoffs: prompt:` field values benefit from (or tolerate) XML structuring when those prompts are complex multi-step instructions? These are currently plain prose strings.

5. **Tag schema versioning**: As the EndogenAI agent fleet evolves, how should tag name changes be managed? Should a `<!-- xml-schema-version: 1.0 -->` comment be added to migrated files for future tooling?

---

## Sources

All sources read as part of this synthesis. Sources 1–9 were synthesized in the original session (new D3s); sources 10–17 are existing D3s from prior sessions; source 18 added 2026-03-07 to resolve OQ-12-1.

| # | Source | Type | Key Contribution |
|---|---|---|---|
| 1 | [Anthropic — Use XML Tags (Prompt Engineering)](./sources/platform-claude-com-docs-en-build-with-claude-prompt-enginee.md) | Documentation | Canonical XML tag vocabulary; naming conventions; official recommendation |
| 2 | [VS Code — Custom Agents spec](./sources/code-visualstudio-com-docs-copilot-customization-custom-agen.md) | Documentation | `.agent.md` file format; conduit finding; full frontmatter schema |
| 3 | [Claude Code — Sub-agents](./sources/code-claude-com-docs-en-sub-agents.md) | Documentation | Plain Markdown body convention; sub-agent format |
| 4 | [Anthropic — Agent Skills overview](./sources/platform-claude-com-docs-en-agents-and-tools-agent-skills-ov.md) | Documentation | `SKILL.md` format; XML prohibition in frontmatter; plain Markdown body |
| 5 | [OpenAI — Prompt Engineering Guide](./sources/platform-openai-com-docs-guides-prompt-engineering.md) | Documentation | Hybrid Markdown + XML recommendation; `# Section` + `<xml_tag>` canonical pattern |
| 6 | [OpenAI — Assistants API Reference](./sources/platform-openai-com-docs-api-reference-assistants.md) | Documentation | `instructions` field as free-form string; API deprecated → Responses API |
| 7 | [AutoGen — AgentChat Quickstart](./sources/microsoft-github-io-autogen-stable-user-guide-agentchat-user.md) | Documentation | Industry baseline: plain-string `system_message`, no imposed structure |
| 8 | [LangChain — Agent Concepts](./sources/python-langchain-com-docs-concepts-agents.md) | Documentation | Industry baseline convergence with AutoGen; tiered architecture |
| 9 | [VS Code — Chat Extension API](./sources/code-visualstudio-com-api-extension-guides-chat.md) | Documentation | Conduit confirmation: no XML parsing at extension API layer |
| 10 | [Anthropic — Building Effective Agents](./sources/anthropic-building-effective-agents.md) | Blog | Orchestrator-workers pattern; ACI; simplicity principle |
| 11 | [Cookbook — Citations Agent](./sources/cookbook-citations-agent.md) | Cookbook | XML content-layer tags in production agent prompts |
| 12 | [Cookbook — Research Lead Agent](./sources/cookbook-research-lead-agent.md) | Cookbook | XML-structured orchestrator prompt (5 tagged sections) |
| 13 | [Cookbook — Research Subagent](./sources/cookbook-research-subagent.md) | Cookbook | XML-structured worker prompt (5 tagged sections) |
| 14 | [Claude SDK — Subagents](./sources/claude-sdk-subagents.md) | Documentation | SDK subagent architecture; context isolation |
| 15 | [Claude Code — Agent Teams](./sources/claude-code-agent-teams.md) | Documentation | Multi-agent coordination; CLAUDE.md as shared context |
| 16 | [TDS — Claude Skills and Subagents](./sources/tds-claude-skills-subagents.md) | Blog | Progressive disclosure; lazy-loading analogy; token economics |
| 17 | [Anthropic — Agent Skills overview (detailed)](./sources/platform-claude-com-docs-en-agents-and-tools-agent-skills-ov.md) | Documentation | See row 4 — same source, complete reading |
| 18 | [VS Code — Language Model API](./sources/code-visualstudio-com-api-extension-guides-ai-language-model.md) | Documentation | **OQ-12-1 resolution**: LM API passes prompts as raw strings via `LanguageModelChatMessage.User()`; no XML pre-processing at any layer; no system message support (bodies injected as User messages) |
| 19 | [Google — Gemini API Prompting Strategies](./sources/ai-google-dev-gemini-api-docs-prompting-strategies.md) | Documentation | **OQ-12-3 D3**: Gemini 3 explicitly recommends XML-style tags (`<role>`, `<constraints>`, `<context>`, `<task>`, `<instructions>`, `<output_format>`) — same vocabulary as Anthropic. XML beneficial for Gemini. |
| 20 | [Ollama Blog — How to Prompt Code Llama](./sources/ollama-com-blog-how-to-prompt-code-llama.md) | Blog | **OQ-12-3 D3**: Local model prompt format reference; no XML-specific guidance; confirms Ollama models use token-level chat format distinct from arbitrary XML body tags. |

---

## 9. OQ-12-2 Findings — Instruction-Following Fidelity

### 9.1 Secondary Evidence Survey

The central claim — "XML tags help Claude parse complex prompts unambiguously and reduce misinterpretation" — originates from Anthropic's official prompt engineering guide (Source: [platform-claude-com-docs-en-build-with-claude-prompt-enginee](./sources/platform-claude-com-docs-en-build-with-claude-prompt-enginee.md)) and is echoed by OpenAI's and Google's guides. Across all surveyed sources, the recommendation is **prescriptive, not empirically measured**. No surveyed source provides quantitative ablation experiments comparing XML-structured vs. plain-prose instruction-following rates.

The strongest secondary evidence is Anthropic's own hedging in its context engineering post (Source: [anthropic-com-engineering-effective-context-engineering-for-](./sources/anthropic-com-engineering-effective-context-engineering-for-.md)):

> "We recommend organizing prompts into distinct sections (like `<background_information>`, `<instructions>`, `## Tool guidance`, etc) and using techniques like XML tagging or Markdown headers to delineate these sections, **although the exact formatting of prompts is likely becoming less important as models become more capable.**"

This is a material qualification from the primary model provider. It implies:
1. XML structure *does* provide benefit in the current generation of models.
2. The effect size is expected to diminish as model reasoning improves.
3. Markdown headers are cited as an equivalent alternative, not a lesser one.

Google's Gemini 3 prompting guide independently corroborates XML for structured prompting: "Employ clear delimiters to separate different parts of your prompt. XML-style tags (e.g., `<context>`, `<task>`) or Markdown headings are effective" (Source: [ai-google-dev-gemini-api-docs-prompting-strategies](./sources/ai-google-dev-gemini-api-docs-prompting-strategies.md)). This cross-vendor consistency strengthens the qualitative case.

**Summary**: Secondary evidence suggests a moderate, positive qualitative effect from XML structuring on instruction-following fidelity for current-generation Claude models, with no quantified effect size in any source.

### 9.2 Ablation Test Protocol

The following protocol would quantify the fidelity improvement. It is designed to be encoded as `scripts/eval_xml_fidelity.py`.

**Experimental design:**
- **Control variant**: Current plain-Markdown `.agent.md` bodies (e.g., Research Synthesizer, Executive Researcher)
- **Treatment variant**: Same agent files with hybrid XML schema applied per Section 4

**Primary metrics:**

| Metric | Definition | Measurement method |
|---|---|---|
| Completion criteria satisfaction rate | % of explicitly stated section deliverables present in agent output | Automated: parse output against section checklist in agent file |
| Constraint violation rate | Count of explicit MUST NOT actions taken per 10 sessions | Automated: match known forbidden-action patterns against session transcript |
| Workflow sequence compliance | % of multi-step workflows executed in documented order | Automated: sequence detection on transcript |
| Section-addressing accuracy | % of named `## Section` headings in the agent file that were addressed in output | Automated: heading-name matching in output text |

**Experimental parameters:**
- 10 task instances per agent per variant (20 sessions per agent)
- Minimum 2 agents (Research Synthesizer + Executive Researcher)
- Total: ≥ 40 scored sessions
- Same task instances across control and treatment variants (controls for task difficulty variance)

**Evaluation method:**
A separate Claude instance receives: (a) agent file body, (b) session transcript, (c) scoring rubric, and returns a JSON score object. The evaluating instance must not see whether the session was control or treatment (blind scoring).

**Script specification** (`scripts/eval_xml_fidelity.py`):
- `--control-agent <path>` — path to plain-Markdown agent file
- `--treatment-agent <path>` — path to XML-hybrid agent file
- `--sessions-dir <path>` — directory of session transcript files
- `--output <path>` — JSON results file
- `--dry-run` — print rubric and session count without running evaluation
- Exit 0 if treatment significantly outperforms control on primary metric; exit 1 if no significant difference; exit 2 if control outperforms treatment

**Stopping rule:** Complete when: (a) 95% CI intervals for completion-criteria satisfaction are non-overlapping between variants, (b) 15% relative improvement threshold is exceeded on primary metric, or (c) 40 sessions scored without a significant finding (null result).

### 9.3 Provisional Finding

Based on available secondary evidence: adopting the hybrid XML schema is provisionally justified by prescriptive vendor guidance from three independent model providers (Anthropic, OpenAI, Google). The qualitative reasoning is sound — XML provides unambiguous semantic type boundaries that prose can blur — but the effect size for current-generation models is likely **moderate and diminishing** rather than transformative. Anthropic's own proviso ("likely becoming less important as models become more capable") is a meaningful hedge.

**Provisional answer to OQ-12-2**: XML structuring improves instruction-following fidelity for current-generation Claude (and Gemini) models with moderate effect size. The improvement is prescriptively supported by all major model vendors but empirically unquantified. The ablation protocol in Section 9.2 is the path to a quantified answer.

---

## 10. OQ-12-3 Findings — Non-Claude Model XML Degradation

### 10.1 Per-Model-Family Evidence

#### GPT-4o / GPT-5 / o3 (OpenAI)

OpenAI's official prompt engineering guide (Source: [platform-openai-com-docs-guides-prompt-engineering](./sources/platform-openai-com-docs-guides-prompt-engineering.md), "Message formatting with Markdown and XML" section) explicitly states:

> "you can help the model understand logical boundaries of your prompt and context data using a combination of Markdown formatting and XML tags… XML tags can help delineate where one piece of content begins and ends. XML attributes can also be used to define metadata about content in the prompt."

The guide provides a full worked example of a developer message using Markdown headers with XML-wrapped content — the same hybrid pattern as EndogenAI's schema.

**Verdict: Beneficial pass-through** — GPT models are explicitly designed by OpenAI to benefit from hybrid Markdown+XML prompts. No degradation.

#### Gemini (Google Gemini 3, Gemini 1.5 Pro)

Google's Gemini 3 prompting guide (Source: [ai-google-dev-gemini-api-docs-prompting-strategies](./sources/ai-google-dev-gemini-api-docs-prompting-strategies.md), "Structured prompting examples" section) explicitly recommends XML-style tags with a vocabulary substantially identical to Anthropic's convention:

```
<role>, <constraints>, <context>, <task>, <instructions>, <output_format>
```

The guide provides the hybrid Markdown+XML pattern as the "Example template combining best practices" for Gemini 3 system instructions.

**Verdict: Beneficial pass-through** — Gemini 3 is explicitly designed to benefit from XML structure using the same tag names as EndogenAI's schema. No degradation; tag vocabulary is directly compatible.

#### Local Models via Ollama/LM Studio (LLaMA 3, Mistral, Phi, Qwen)

The XDA developers article on local LLM prompting (Source: [xda-developers-com-youre-using-local-llm-wrong-if-youre-prom](./sources/xda-developers-com-youre-using-local-llm-wrong-if-youre-prom.md)) documents the fundamental difference: local models lack cloud-side reasoning and inference-assistance layers that make cloud models forgiving of ambiguous prompts. The article explicitly recommends `###` and `---` Markdown delimiters as structure — not XML.

Key structural facts about open-weight model chat formats:
- **LLaMA 3**: Uses special tokenizer tokens (`<|begin_of_text|>`, `<|start_header_id|>system<|end_header_id|>`) as chat delimiters. XML tags in the body prompt (e.g., `<instructions>`) are processed as literal text characters — not as semantic tokens.
- **Mistral**: Uses `[INST]` and `[/INST]` instruction format tokens. XML in the body is literal text.
- **Phi-4 (Microsoft)**: Uses `<|user|>` and `<|assistant|>` special tokens. XML in body is literal text.
- **Qwen**: Uses `<|im_start|>system` tokens. XML in body is literal text.

All open-weight models are trained on vast code and markup data (including HTML/XML), so they can parse XML syntactically. However, none are explicitly trained to treat XML tags as semantic instruction delimiters in the way Claude is. The XDA article confirms: "local models don't have the same layers of assistance that cloud models add behind the scenes."

**Verdict: Neutral pass-through** — XML tags are read as text characters; well-formed XML causes no inference errors or active interference. However, XML provides no reliable semantic benefit comparable to Claude/Gemini. For local models, prefer `###` Markdown headings and `---` section separators.

#### MistralAI (La Plateforme API)

The MistralAI documentation site (`docs.mistral.ai`) was unreachable due to HTTP 308 permanent redirects at the time of research. Evidence for Mistral's hosted API is inferred from open-weight Mistral model behaviour above. Hosted Mistral-class models with RLHF fine-tuning may have partial exposure to structured prompt patterns, but no published guidance confirms XML-specific behaviour.

**Verdict: Neutral pass-through (provisional)** — Based on open-weight model inference; confirm with direct Mistral API documentation when accessible.

### 10.2 Summary Verdict Table

| Model Family | XML Handling | Verdict | Source |
|---|---|---|---|
| Claude (`claude-*`) | Explicitly semantically trained; XML reduces misinterpretation | **Beneficial** | `platform-claude-com-docs-en-build-with-claude-prompt-enginee.md` |
| GPT (`gpt-*`, `openai/*`) | OpenAI guide explicitly recommends hybrid Markdown+XML | **Beneficial** | `platform-openai-com-docs-guides-prompt-engineering.md` |
| Gemini (`google/gemini*`) | Google Gemini 3 guide recommends same XML tag vocabulary | **Beneficial** | `ai-google-dev-gemini-api-docs-prompting-strategies.md` |
| Local (`ollama/*`, `lmstudio/*`) | No XML-specific training; tags read as literal text; Markdown delimiters preferred | **Neutral pass-through** | `xda-developers-com-youre-using-local-llm-wrong-if-youre-prom.md` |
| MistralAI API | Documentation unreachable; inference from open-weight behaviour | **Neutral (provisional)** | Inference |

### 10.3 Impact on ADAPT Item B2

Section 5's ADAPT item B2 states: "if an agent's frontmatter declares a non-Claude model (local model via `ollama/*`, GPT family, or `*`-wildcarded), the XML migration is deferred until cross-model XML parsing behaviour is confirmed."

This research resolves the deferral:

1. **`--model-scope` extended**: `google/gemini*` and `gpt-*` / `openai/*` prefixes are confirmed as XML-beneficial. The migration script's scope can include these families without concern for degradation.

2. **`--model-scope` exclusion confirmed**: `ollama/*` and `lmstudio/*` (local models) remain excluded. XML is a no-op benefit for these models; Markdown-only structure is preferred.

3. **Wildcard-model agents** (no `model:` field, or `model: *`) default to XML migration since the primary deployment is Claude. This remains the correct conservative default.

**Updated `--model-scope` flag guidance for `migrate_agent_xml.py`:**

```
--model-scope claude        # Claude family only (existing default)
--model-scope all-cloud     # claude + gpt-* + google/gemini* (extended, safe)
--model-scope all           # all models including local (not recommended)
```
