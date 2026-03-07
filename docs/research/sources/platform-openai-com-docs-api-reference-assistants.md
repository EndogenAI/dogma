---
source_url: https://platform.openai.com/docs/api-reference/assistants
cache_path: .cache/sources/platform-openai-com-docs-api-reference-assistants.md
fetched: 2026-03-06
research_issue: "Issue #12 — XML-Tagged Agent Instruction Format"
slug: "platform-openai-com-docs-api-reference-assistants"
title: "OpenAI Assistants API Reference"
url: "https://platform.openai.com/docs/api-reference/assistants"
authors: "OpenAI"
year: "2025"
type: documentation
topics: [assistants-api, instructions-field, agent-schema, api-reference, deprecated]
cached: true
evidence_quality: documentation
date_synthesized: "2026-03-06"
---

# Synthesis: OpenAI Assistants API Reference

## 1. Citation

OpenAI. (2025). *API Reference: Assistants (Beta)*. OpenAI Platform API Reference.
https://platform.openai.com/docs/api-reference/assistants
Accessed 2026-03-06.

## 2. Research Question Addressed

This reference document specifies the complete schema of the OpenAI Assistants object —
including the `instructions` field — and all associated API methods (create, retrieve,
modify, delete, list). For Issue #12, the central question is: what format constraints,
if any, does the OpenAI Assistants API place on the `instructions` field, and does the
API reference show or endorse XML-tagged instruction content? The document also implies
cross-framework portability conclusions, since the `instructions` field is the direct
analogue of Anthropic's `system` prompt and the agent instruction files in EndogenAI.

## 3. Theoretical Framework

N/A — applied API reference documentation; no explicit theoretical framework. The
document describes a data contract: field names, types, constraints, and relationships
between objects. It is machine-readable specification prose rather than conceptual
writing. The underlying design follows a stateful agent model (Assistants hold
persistent `instructions`, `tools`, and `tool_resources` across `Threads` and `Runs`),
but this architecture is not theorised — it is described.

## 4. Methodology / Source Type

This is a machine-generated or hand-authored API reference page for OpenAI's Assistants
API (Beta), covering the object schema and CRUD methods. The document is structured as
field-by-field specification prose, not prose guidance. It lists data types, constraints
(`maxLength`), optional/required status, and accepted enum values. No examples of
formatted `instructions` content appear anywhere in the cached document. Crucially, every
Assistants API method and model is marked **"Deprecated"** in the document, with OpenAI
directing users toward the newer Responses API. The cached document is 798 lines and
covers all assistant-related stream event types in addition to the core assistant object.

## 5. Key Claims with Evidence (minimum 5)

- **The `instructions` field is a free-form string with a maximum length of 256,000
  characters and no format constraints.** The schema states: "`instructions: string` —
  The system instructions that the assistant uses. The maximum length is 256,000
  characters." No XML, Markdown, JSON, or other structural requirement is stated. The
  field is treated as opaque text by the API layer.

- **The Assistants API is deprecated as of the 2025 documentation.** Every endpoint and
  model object in the document is marked "Deprecated." This is the most operationally
  significant finding: any format guidance derived from the Assistants API docs applies
  to a sunset architecture. OpenAI's strategic direction is the Responses API (see
  [platform-openai-com-docs-guides-prompt-engineering.md](./platform-openai-com-docs-guides-prompt-engineering.md)),
  which uses `instructions` as an API parameter rather than a persistent assistant object
  field.

- **No XML-tagged instruction examples appear anywhere in the Assistants API reference.**
  The document contains zero examples of `instructions` field content. The reference
  describes the contract (field type, length limit) but defers entirely to supplementary
  documentation for how to write `instructions` content. This is in contrast to
  Anthropic's API documentation, which typically includes prompt examples inline.

- **The `instructions` field corresponds directly to the `system` role in the Chat
  Completions / Responses API.** The field description — "The system instructions that
  the assistant uses" — confirms this semantic equivalence. This means all formatting
  guidance in the prompt engineering guide (hybrid Markdown/XML) applies equally to the
  `instructions` field when using the Assistants API.

- **The assistant object has a `description` field (max 512 chars) separate from
  `instructions` (max 256,000 chars).** Schema: "`description: string — The description
  of the assistant. The maximum length is 512 characters.`" This is a metadata field, not
  a prompt field. EndogenAI agent files conflate description and instruction in a single
  Markdown document — the OpenAI object model separates them. This separation is
  architecturally meaningful for any future API-backed agent registry.

- **The assistant object supports up to 128 tools, with tool types `code_interpreter`,
  `file_search`, and `function`.** Schema: "A list of tool enabled on the assistant.
  There can be a maximum of 128 tools per assistant." For XML-tagged instruction design,
  this means the `instructions` field may need to reference tool capabilities by name
  — and XML tags such as `<tools>` or `<tool_guidance>` sections within instructions
  would be human-authored, not machine-interpreted by the API itself.

- **The `metadata` field allows 16 key-value pairs (key max 64 chars, value max 512 chars)
  for structured metadata.** Schema: "Set of 16 key-value pairs that can be attached to
  an object... useful for storing additional information about the object in a structured
  format, and querying for objects via API or the dashboard." This is the machine-readable
  structured channel; `instructions` is the human-readable free-text channel. This design
  confirms that structural metadata (agent type, version, scope) should live in
  `metadata`, not embedded as XML in `instructions`.

- **The Assistants API uses a thread/run execution model separate from the Responses API's
  stateless generation model.** Stream events include `thread.created`, `thread.run.created`,
  `thread.message.completed`, and 22+ additional event types. This stateful architecture
  means `instructions` are set once at assistant creation and persist — unlike the
  Responses API where `instructions` is passed per-request. XML-tagged section updates
  (e.g., swapping a `<context>` block) require modifying the assistant object, not just
  the request payload.

- **The Assistants API's `response_format` field supports `json_schema`, `json_object`,
  and auto.** Schema: "Setting to `{ 'type': 'json_schema', 'json_schema': {...} }` enables
  Structured Outputs which ensures the model will match your supplied JSON schema." This
  is the API-level mechanism for constraining output structure — distinct from using XML
  tags in `instructions` to guide output format prose. These two mechanisms can be used
  together or separately.

- **The `tool_resources` field binds files and vector stores to the assistant's tools.**
  `code_interpreter` accepts up to 20 file IDs; `file_search` accepts 1 vector store ID.
  The `instructions` field is the only field available for communicating tool usage
  guidance in natural language. This reinforces that any instruction about how to use
  tools, what tool invocation patterns to follow, or what data to retrieve must live in
  the free-form `instructions` string — and therefore benefits from structured formatting
  (XML + Markdown) to be clearly parseable by the model.

## 6. Critical Assessment

**Evidence Quality**: Documentation

This is official first-party API reference documentation. Its evidence quality for schema
facts (field types, constraints, enums) is high — these are ground-truth specifications.
However, its evidence quality for _how to write instructions_ is essentially zero: no
guidance, no examples. The document defines the container but not the contents.

**Gaps and Limitations**: The reference contains no examples of `instructions` field
content — not even a "hello world" agent. This silence is analytically significant: it
confirms the API treats instruction content as entirely developer-defined. The deprecation
notice means this document's relevance has a time horizon — any EndogenAI work building
atop the Assistants API object model should plan migration to the Responses API. The
document does not address how the model tokenises or processes the `instructions` field
relative to the conversation thread, making it impossible to derive context-window
management guidance from this source alone. The 256,000 character limit is generous
(roughly 60,000–80,000 tokens depending on content) but is not directly comparable to
Anthropic's token-based limits without conversion. The document does not address whether
XML-tagged sections in `instructions` are specially recognised at the tokeniser level or
treated identically to plain text.

## 7. Cross-Source Connections

- Agrees with / extends: [platform-openai-com-docs-guides-prompt-engineering.md](./platform-openai-com-docs-guides-prompt-engineering.md) —
  the prompt engineering guide is the companion resource that fills the content-of-instructions
  gap this reference leaves open. The two documents together constitute the complete
  OpenAI specification for agent instructions.
- Relevant to: [anthropic-building-effective-agents.md](./anthropic-building-effective-agents.md) — the Assistants
  `instructions` field is the OpenAI equivalent of Anthropic's `system` prompt. Comparing
  the two schemas reveals portability constraints: OpenAI uses a character limit (256k
  chars), Anthropic uses token limits; both accept free-form text with no enforced
  structure.
- Relevant to: [code-visualstudio-com-docs-copilot-customization-custom-agen.md](./code-visualstudio-com-docs-copilot-customization-custom-agen.md) — VS Code
  custom agents also use a free-form instruction / system-prompt field; the OpenAI
  Assistants schema provides an industry baseline for comparison.
- Creates tension with: the deprecation of the Assistants API challenges the relevance of
  any Assistants-specific instruction formatting research. Findings must be validated
  against the Responses API model before being applied in production EndogenAI tooling.

## 8. Project Relevance

**ADAPT — the `instructions` field schema confirms cross-framework portability of
XML-tagged agent instructions, but the deprecation context requires a framing caveat.**

The primary finding for Issue #12 is confirmatory: the OpenAI Assistants API imposes no
structural constraints on the `instructions` field. It is a free-form string. This means
that XML-tagged agent instructions authored in the EndogenAI `.github/agents/` format —
which use Markdown headings (adopted from the prompt engineering guide's recommendations)
and XML tags for content boundaries — will be accepted without modification by the
OpenAI Assistants API. Cross-framework portability is not blocked at the API layer.
Whether the model interprets the XML structure _correctly_ is a separate question not
answered by this reference document.

The `description` / `instructions` field separation in the Assistants object model is
worth ADAPTING into EndogenAI agent file conventions. Currently, agent `.md` files
combine a YAML frontmatter description with a full instruction body in a single document.
The OpenAI schema validates splitting these concerns: a short description (metadata,
≤512 chars) vs. the full instruction body (≤256k chars). The `docs/plans/` workplan
template and the `scaffold_agent.py` script in `scripts/` could reflect this separation
in the agent file frontmatter.

The deprecation status of the Assistants API is itself informative: it signals that
OpenAI's canonical instruction delivery mechanism is now the `instructions` parameter in
the Responses API (per-request, not persisted on an object). This has implications for
how session state and identity sections should be structured in EndogenAI agent files —
they should be self-contained per invocation, not assumed to be retained from a prior
session. The XML-tagged instruction format should be designed for stateless, per-request
delivery, not for a stateful Assistants object.

## Referenced By

<!-- Populated automatically by scripts/link_source_stubs.py — do not edit manually -->
- [Anthropic Building Effective Agents](../sources/anthropic-building-effective-agents.md)
- [Code Visualstudio Com Docs Copilot Customization Custom Agen](../sources/code-visualstudio-com-docs-copilot-customization-custom-agen.md)
- [Platform Openai Com Docs Guides Prompt Engineering](../sources/platform-openai-com-docs-guides-prompt-engineering.md)
- [Xml Agent Instruction Format](../xml-agent-instruction-format.md)
