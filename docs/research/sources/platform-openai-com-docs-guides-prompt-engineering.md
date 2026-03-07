---
source_url: https://platform.openai.com/docs/guides/prompt-engineering
cache_path: .cache/sources/platform-openai-com-docs-guides-prompt-engineering.md
fetched: 2026-03-06
research_issue: "Issue #12 — XML-Tagged Agent Instruction Format"
slug: "platform-openai-com-docs-guides-prompt-engineering"
title: "OpenAI Prompt Engineering Guide"
url: "https://platform.openai.com/docs/guides/prompt-engineering"
authors: "OpenAI"
year: "2025"
type: documentation
topics: [prompt-engineering, xml-tags, markdown, agent-instructions, message-roles]
cached: true
evidence_quality: documentation
date_synthesized: "2026-03-06"
---

# Synthesis: OpenAI Prompt Engineering Guide

## 1. Citation

OpenAI. (2025). *Prompt engineering*. OpenAI Platform Documentation.
https://platform.openai.com/docs/guides/prompt-engineering
Accessed 2026-03-06.

## 2. Research Question Addressed

This guide addresses how developers should structure prompts — including system/developer
messages — to generate reliable, high-quality responses from OpenAI models. It covers
message roles, formatting conventions, few-shot examples, context injection, and
model-specific prompting differences between GPT and reasoning models. For Issue #12, the
directly relevant section is "Message formatting with Markdown and XML."

## 3. Theoretical Framework

The guide operates within an **instruction-following** paradigm: models respond to
explicit, hierarchically organised developer instructions rather than inferring intent
from minimal cues. A **chain-of-command** model governs message priority: `developer`
messages outrank `user` messages, which outrank nothing. This framing treats the prompt
window as a programmable contract between developer and model — closer to a function
definition than a conversational exchange. No single named academic framework is cited,
but the structure aligns with prompt programming approaches documented in the broader LLM
literature.

## 4. Methodology / Source Type

This is official product documentation authored by OpenAI for its platform APIs (Responses
API and Chat Completions API). It is prescriptive rather than empirical — it describes
recommended practice, not experimental findings. Evidence is in the form of annotated code
samples and explanatory prose sections. The guide is continuously updated and was current
as of the March 2026 cache date. The core guidance relevant to Issue #12 appears in a
dedicated section titled "Message formatting with Markdown and XML."

## 5. Key Claims with Evidence (minimum 5)

- **OpenAI explicitly recommends using both Markdown and XML tags together for structuring
  developer messages.** The guide states: "When writing `developer` and `user` messages,
  you can help the model understand logical boundaries of your prompt and context data
  using a combination of [Markdown] formatting and [XML tags]." This is the most
  unambiguous cross-format recommendation in OpenAI's official documentation.

- **Markdown headings serve a structural/hierarchical role; XML tags serve a
  content-boundary and metadata role.** The guide distinguishes the two: "Markdown headers
  and lists can be helpful to mark distinct sections of a prompt, and to communicate
  hierarchy to the model... XML tags can help delineate where one piece of content (like a
  supporting document used for reference) begins and ends. XML attributes can also be used
  to define metadata about content in the prompt."

- **The canonical four-section developer message structure uses Markdown `#` headings.**
  OpenAI's recommended structure is `# Identity`, `# Instructions`, `# Examples`,
  `# Context` — rendered as top-level Markdown headings in the prompt text, not XML tags.
  The full example shows:
  ```
  # Identity
  You are coding assistant that helps enforce the use of snake case
  variables in JavaScript code...

  # Instructions
  * When defining variables, use snake case names (e.g. my_variable)...

  # Examples
  <user_query>
  How do I declare a string variable for a first name?
  </user_query>
  ```
  This hybrid pattern is the reference implementation.

- **XML tag names shown in official examples include `<user_query>`, `<assistant_response>`,
  `<product_review>`, and `<ONE_SHOT_RUBRIC>`.** These appear in two different worked
  examples. `<product_review id="example-1">` demonstrates that **XML attributes are also
  used** to add metadata (e.g., example numbering) to content blocks. The tag names are
  semantic — they describe what the enclosed content is, not presentation.

- **The `developer` role replaces `system` in the Responses API.** The guide uses
  `developer` throughout: "Note that the `instructions` parameter only applies to the
  current response generation request." The older Chat Completions API uses `system` but
  OpenAI is actively migrating usage to the Responses API with `developer` + `user` +
  `assistant` roles, following their model spec's chain-of-command hierarchy.

- **GPT-5 coding prompts explicitly recommend Markdown formatting standards for output.**
  Under "Coding" best practices: "Guide the model to generate clean, semantically correct
  markdown using inline code, code fences, lists, and tables where appropriate—and to
  format file paths, functions, and classes with backticks." This reinforces that OpenAI
  treats Markdown as a first-class output language, not just an input structuring device.

- **Agentic GPT-5 prompts embed XML-delimited sections within the prompt body.** The
  zero-to-one web app example contains `<ONE_SHOT_RUBRIC>` as an XML-tagged internal
  reasoning block. This demonstrates that XML tagging of _internal_ model artefacts is
  also in use, not just for external data injection.

- **The guide explicitly recommends keeping reused prompt content at the beginning of
  prompts for prompt-caching efficiency.** "You should try and keep content that you expect
  to use over and over in your API requests at the beginning of your prompt." This has
  structural implications for XML-formatted agent instructions: stable identity and
  instruction blocks should precede variable context blocks.

- **OpenAI does not recommend XML-only or Markdown-only formatting.** There is no section
  that advocates for one format in isolation. The guide presents the hybrid as the default,
  with no caveats about model sensitivity to format choice.

- **Reasoning models require less structural scaffolding than GPT models.** "Generally
  speaking, reasoning models will provide better results on tasks with only high-level
  guidance. This differs from GPT models, which benefit from very precise instructions."
  This implies XML/Markdown structural scaffolding matters more for GPT models than for
  reasoning models like o1/o3.

## 6. Critical Assessment

**Evidence Quality**: Documentation

This is authoritative first-party documentation from the model provider. It represents
OpenAI's prescribed best practice as of 2025–2026 but is not peer-reviewed empirical
research. Recommendations reflect OpenAI's internal experience and model training choices
rather than controlled experiments comparing formatting approaches. It should be treated as
ground truth for how OpenAI-hosted models are designed to behave, not as universal
evidence about model behaviour in general.

**Gaps and Limitations**: The guide does not provide ablation data showing _why_ the
hybrid Markdown/XML approach works better than alternatives (pure JSON, pure Markdown,
pure XML, or natural language). The specific XML tag names shown in examples are
illustrative, not prescriptive — the guide does not enumerate a canonical tag vocabulary.
The guide conflates two use cases of XML: (1) wrapping example data in few-shot prompts,
and (2) wrapping context documents injected via RAG — and does not address the separate
question of whether XML tags in _agent definition_ frontmatter (role, tools, constraints)
carry the same benefit. The "developer" role is Responses API-specific; Chat Completions
users still use "system", creating a terminology inconsistency that can mislead readers
applying this guide to legacy integrations.

## 7. Cross-Source Connections

- Agrees with / extends: [anthropic-building-effective-agents.md](./anthropic-building-effective-agents.md) — both
  Anthropic and OpenAI recommend XML tags for content boundary marking; Anthropic is more
  prescriptive about tag names while OpenAI leaves them as illustrative examples.
- Relevant to: [platform-claude-com-docs-en-build-with-claude-prompt-enginee.md](./platform-claude-com-docs-en-build-with-claude-prompt-enginee.md) — Anthropic's
  parallel guide for comparison of philosophy and recommended tag usage.
- Relevant to: [platform-openai-com-docs-api-reference-assistants.md](./platform-openai-com-docs-api-reference-assistants.md) — the Assistants API
  `instructions` field is the concrete delivery mechanism for the formatting patterns
  described here.
- Relevant to: [arxiv-context-engineering-survey.md](./arxiv-context-engineering-survey.md) — survey literature on
  context structuring strategies; this guide represents the practitioner consensus end of
  that research space.

## 8. Project Relevance

**ADOPT — the hybrid Markdown-heading / XML-tag pattern is directly applicable to
EndogenAI agent instruction files.**

The `.github/agents/*.agent.md` files in this repository are currently structured with
Markdown headings (`## Role`, `## Tools`, `## Constraints`, etc.) but without XML tags.
OpenAI's explicit guidance — that Markdown headings communicate hierarchy while XML tags
delimit content blocks and carry metadata — validates the current heading structure and
suggests XML tagging should be added at the _content injection_ layer, not the top-level
structural layer. Concretely: `## Examples` subsections in agent files would benefit from
`<example>` / `<user_query>` / `<assistant_response>` wrappers; injected context (e.g.,
a scratchpad excerpt pasted into a prompt) would benefit from `<context>` / `</context>`
boundary tags. The top-level `## Identity` / `## Instructions` Markdown structure should
be retained as-is — it matches OpenAI's own reference implementation.

The prompt-caching ordering recommendation (stable content first) has a concrete
implication for how agent files are assembled at runtime: identity and constraint sections,
which are reused across all invocations, should precede the session-specific context
injection. This should be encoded in any `scripts/` file that assembles prompt payloads
from agent definition files.

Cross-provider portability is confirmed: OpenAI explicitly teaches the same XML-for-data,
Markdown-for-structure pattern that Anthropic recommends. Agent files written to this
hybrid convention should behave well across both providers without format-specific
variants.

## Referenced By

<!-- Populated automatically by scripts/link_source_stubs.py — do not edit manually -->
- [Anthropic Building Effective Agents](../sources/anthropic-building-effective-agents.md)
- [Arxiv Context Engineering Survey](../sources/arxiv-context-engineering-survey.md)
- [Platform Claude Com Docs En Build With Claude Prompt Enginee](../sources/platform-claude-com-docs-en-build-with-claude-prompt-enginee.md)
- [Platform Openai Com Docs Api Reference Assistants](../sources/platform-openai-com-docs-api-reference-assistants.md)
- [Xml Agent Instruction Format](../xml-agent-instruction-format.md)
