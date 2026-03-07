---
source_url: "https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/use-xml-tags"
cache_path: ".cache/sources/platform-claude-com-docs-en-build-with-claude-prompt-enginee.md"
fetched: 2026-03-06
research_issue: "Issue #12 — XML-Tagged Agent Instruction Format"
slug: "platform-claude-com-docs-en-build-with-claude-prompt-enginee"
title: "Prompt Engineering Reference — Claude 4.6 (Anthropic Platform Docs)"
url: "https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/use-xml-tags"
authors: "Anthropic"
year: "2025"
type: documentation
topics: [xml-tags, prompt-engineering, structured-prompts, agentic-systems, tool-use, system-prompts, context-management]
cached: true
evidence_quality: strong
date_synthesized: "2026-03-06"
---

# Synthesis: Prompt Engineering Reference — Claude 4.6 (Anthropic Platform Docs)

## 1. Citation

Anthropic. (2025). *Prompt engineering — build with Claude: Use XML tags*. Anthropic Platform Documentation.
https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/use-xml-tags
Accessed: 2026-03-06.

This is the single canonical prompt engineering reference for Claude Opus 4.6, Claude Sonnet 4.6, and Claude Haiku 4.5, covering foundational techniques, output control, tool use, thinking, and agentic systems.

## 2. Research Question Addressed

Should structured, named XML tags be used to delimit semantic sections in prompts and system instructions delivered to Claude? This source directly addresses how XML tags help Claude disambiguate content types within complex prompts, what naming conventions Anthropic recommends, and which canonical tag names appear in official sample prompts — making it the primary authoritative reference for Issue #12.

## 3. Theoretical Framework

This source operates within a **structured prompting** paradigm: Claude's context window is treated as a typed substrate where different content categories (instructions, context, examples, inputs, behavioural guardrails) should be explicitly labelled rather than positionally implied. The framework assumes that parseable, machine-readable structure inside natural language prompts reduces ambiguity and improves model compliance — not through model architecture changes but through prompt-surface design. Anthropic's own sample snippets throughout this document demonstrate this paradigm in practice, using XML tags as semantic containers for every category of system-prompt content.

## 4. Methodology / Source Type

**Official product documentation** authored and maintained by Anthropic for practitioners integrating Claude via the API. Content is produced from internal empirical testing, product team guidance, and model capability characterisation. It is not a peer-reviewed academic study, but it carries the highest possible epistemic authority on how Claude is trained to process structured prompts, since Anthropic controls both the documentation and the model training. The page consolidates guidance across all prompt engineering domains for Claude 4.x models in a single, hierarchical reference.

Evidence quality: **Strong** — first-party vendor documentation from the model's creator. Carries direct authoritative weight on the model's trained preferences.

## 5. Key Claims with Evidence

- **XML tags are the canonical grouping mechanism for complex prompts.**
  > "XML tags help Claude parse complex prompts unambiguously, especially when your prompt mixes instructions, context, examples, and variable inputs. Wrapping each type of content in its own tag (e.g. `<instructions>`, `<context>`, `<input>`) reduces misinterpretation."
  *(Section: "Structure prompts with XML tags")*
  Assessment: **Supported** — directly stated guideline from Anthropic.

- **Consistent, descriptive tag names are a first-class best practice.**
  > "Use consistent, descriptive tag names across your prompts."
  *(Section: "Structure prompts with XML tags" — best practices bullet)*
  Assessment: **Supported** — explicit naming convention guidance. Implies semantic naming (e.g. `<instructions>` not `<a>` or `<section1>`) is preferred over structural naming.

- **Hierarchical content should use nested XML tags.**
  > "Nest tags when content has a natural hierarchy (documents inside `<documents>`, each inside `<document index="n">`)."
  *(Section: "Structure prompts with XML tags" — best practices bullet)*
  Assessment: **Supported** — documents the `<documents>/<document index="n">` nesting pattern as canonical, directly applicable to agent file corpora where sections have natural parent/child relationships.

- **Examples must be wrapped in `<example>` and `<examples>` tags.**
  > "Wrap examples in `<example>` tags (multiple examples in `<examples>` tags) so Claude can distinguish them from instructions."
  *(Section: "Use examples effectively")*
  Assessment: **Supported** — prescribes specific canonical tag names for few-shot examples.

- **Behavioural instruction blocks in system prompts use XML tag wrappers in Anthropic's own guidance.**
  Anthropic's official sample prompts throughout the document uniformly use XML-tagged blocks for named behavioural modes:
  - `<default_to_action>` — proactive action bias
  - `<do_not_act_before_instructions>` — conservative action bias
  - `<use_parallel_tool_calls>` — parallel tool calling
  - `<investigate_before_answering>` — grounded code analysis
  - `<avoid_excessive_markdown_and_bullet_points>` — formatting control
  - `<frontend_aesthetics>` — design style guidance
  *(Sections: "Tool usage", "Output and formatting", "Agentic systems", "Capability-specific tips")*
  Assessment: **Supported** — Anthropic's own prompt snippets model the pattern that behavioural instruction sections should be XML-tagged, not free-prose paragraphs.

- **XML format indicators can control output format.** 
  > "Use XML format indicators — Try: 'Write the prose sections of your response in `<smoothly_flowing_prose_paragraphs>` tags.'"
  *(Section: "Control the format of responses")*
  Assessment: **Supported** — XML is recommended not only for input structure but also for steering the format of model outputs.

- **Matching prompt style to desired output style reduces formatting drift.**
  > "The formatting style used in your prompt may influence Claude's response style. If you are still experiencing steerability issues with output formatting, try matching your prompt style to your desired output style as closely as possible."
  *(Section: "Control the format of responses")*
  Assessment: **Supported** — establishes a bidirectional relationship between prompt structure and output structure; XML-structured prompts predispose XML-structured outputs, which has implications for agent file design.

- **System prompt role-setting improves behavioural focus, even with a single sentence.**
  > "Setting a role in the system prompt focuses Claude's behavior and tone for your use case. Even a single sentence makes a difference."
  *(Section: "Give Claude a role")*
  Assessment: **Supported** — confirms the system prompt (which in EndogenAI maps to agent file content) has outsized influence on model behaviour.

- **Tag names in official samples follow lowercase, underscore-separated conventions.**
  All named sample prompt blocks use lowercase with underscores: `<default_to_action>`, `<use_parallel_tool_calls>`, `<investigate_before_answering>`, `<avoid_excessive_markdown_and_bullet_points>`, `<frontend_aesthetics>`. No sample uses PascalCase, kebab-case, or Markdown heading equivalents.
  *(Throughout all sample prompt code blocks)*
  Assessment: **Supported** — implicit but consistent convention, directly informing a proposed EndogenAI naming standard.

- **Long-form data should be placed above queries; XML metadata wraps document content.**
  > "Structure document content and metadata with XML tags: When using multiple documents, wrap each document in `<document>` tags with `<document_content>` and `<source>` (and other metadata) subtags for clarity."
  *(Section: "Long context prompting")*
  Assessment: **Supported** — establishes `<document>`, `<document_content>`, `<source>` as canonical subtag names for context injection scenarios, applicable when agent files inject corpus documents.

## 6. Critical Assessment

**Evidence Quality: Strong**
This is first-party documentation from the model's creator, updated for Claude 4.6. It carries higher evidential authority than any third-party benchmark or blog post on how Claude parses structured prompts — Anthropic designed the training signals that make these patterns effective.

**Gaps and Limitations:**
- The cached page is a broad prompt engineering reference, not a narrowly focused XML tagging specification. XML tag guidance occupies a relatively small proportion of the full document (one explicit section plus recurring usage in examples); no exhaustive tag vocabulary is enumerated.
- No empirical benchmarks are provided comparing XML-tagged vs. non-XML-tagged prompts. Claims about reduction of misinterpretation are asserted rather than demonstrated with controlled experiment data.
- The document does not address the specific question of whether `.agent.md` static instruction files (as opposed to dynamic API system prompts) benefit equally from XML tagging. Agent files are transformed at read-time into system prompts; the distinction is implicit but not stated.
- No schema or DTD is provided. Tag naming is exemplified, not formally specified. Future agents relying solely on this source cannot fully enumerate a closed vocabulary.
- The documentation is versioned to Claude 4.6 (2025). If model versions change significantly, tagging conventions may need re-evaluation.

## 7. Cross-Source Connections

- Extends [anthropic-building-effective-agents](./anthropic-building-effective-agents.md) — that source establishes agentic workflow patterns; this source specifies the prompt-surface conventions (XML tags) that implement those patterns reliably. Together they form a complete picture of Anthropic's preferred agentic prompting stack.
- Agrees with [cookbook-research-lead-agent](./cookbook-research-lead-agent.md) and [cookbook-research-subagent](./cookbook-research-subagent.md) — Anthropic cookbooks consistently employ XML-tagged sections (`<task>`, `<context>`, `<search_quality_reflection>`) for agent instruction content, corroborating this document's guidance in working code.
- Agrees with [claude-code-agent-teams](./claude-code-agent-teams.md) / [claude-sdk-subagents](./claude-sdk-subagents.md) — where agent-to-agent delegation patterns are documented, XML tags are the mechanism used to delimit payloads.
- No known contradictions in the existing corpus. All Anthropic-origin sources converge on XML tagging as the preferred prompt structuring mechanism.

## 8. Project Relevance

**Direct applicability to Issue #12 — XML-Tagged Agent Instruction Format**

This source is the single strongest authoritative basis for adopting XML tags in EndogenAI `.agent.md` files. Anthropic's own sample system prompts use XML-tagged behavioural blocks (`<default_to_action>`, `<investigate_before_answering>`, etc.) — proving that the same constructs found in `.agent.md` files (role definition, tool constraints, behavioural guardrails, scope limitations) are precisely the use cases Anthropic designed XML tagging to serve. The evidence is not theoretical; it is demonstrated in live official guidance written by the model's creators.

**ADOPT — XML tags as section boundaries in `.agent.md` files**

The current `.agent.md` format uses Markdown headings (`## Persona`, `## Instructions`, `## Tools`) as section delimiters. This source justifies replacing or augmenting those headings with XML tags:

- `<persona>` or `<role>` — replaces the `## Persona` heading; maps to the "Give Claude a role" guidance
- `<instructions>` — replaces `## Instructions`; the explicitly recommended tag name in the source
- `<tools>` — replaces `## Tools`; scopes tool availability declarations
- `<constraints>` or `<guardrails>` — maps to safety/scope limitation sections
- `<context>` — for any environmental or codebase context injected into the agent file
- `<examples>` / `<example>` — for few-shot demonstrations inside agent files

**Naming convention:** lowercase with underscores, matching all Anthropic sample prompts (`<default_to_action>`, not `<DefaultToAction>` or `<default-to-action>`).

**ADOPT — XML wrapper for each behavioural mode block**

Any named behavioural instruction inside `.agent.md` files (e.g. "always verify before modifying files", "minimise subagent spawning") should be wrapped in a descriptive XML tag rather than written as a prose paragraph or Markdown bullet list. This matches the `<investigate_before_answering>`, `<avoid_excessive_markdown_and_bullet_points>`, and `<use_parallel_tool_calls>` patterns demonstrated throughout this source.

**ADAPT — retain Markdown headings as human-readable anchors alongside XML tags**

Because `.agent.md` files are also read by humans in editors, a pragmatic hybrid is appropriate: Markdown `##` headings remain as the visible document structure for human readers, with XML tags wrapping the content payload that Claude processes. Example:

```markdown
## Instructions

<instructions>
You are the Research Synthesizer...
</instructions>
```

This preserves the documentation legibility mandated by the Documentation-First constraint in `AGENTS.md` while maximising Claude's ability to parse section boundaries unambiguously.

## Referenced By

<!-- Populated automatically by scripts/link_source_stubs.py — do not edit manually -->
- [Anthropic Building Effective Agents](../sources/anthropic-building-effective-agents.md)
- [Claude Code Agent Teams](../sources/claude-code-agent-teams.md)
- [Claude Sdk Subagents](../sources/claude-sdk-subagents.md)
- [Code Visualstudio Com Api Extension Guides Chat](../sources/code-visualstudio-com-api-extension-guides-chat.md)
- [Code Visualstudio Com Docs Copilot Customization Custom Agen](../sources/code-visualstudio-com-docs-copilot-customization-custom-agen.md)
- [Cookbook Research Lead Agent](../sources/cookbook-research-lead-agent.md)
- [Cookbook Research Subagent](../sources/cookbook-research-subagent.md)
- [Microsoft Github Io Autogen Stable User Guide Agentchat User](../sources/microsoft-github-io-autogen-stable-user-guide-agentchat-user.md)
- [Platform Claude Com Docs En Agents And Tools Agent Skills Ov](../sources/platform-claude-com-docs-en-agents-and-tools-agent-skills-ov.md)
- [Platform Openai Com Docs Guides Prompt Engineering](../sources/platform-openai-com-docs-guides-prompt-engineering.md)
- [Xml Agent Instruction Format](../xml-agent-instruction-format.md)
