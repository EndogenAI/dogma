---
slug: "code-visualstudio-com-docs-copilot-customization-custom-agen"
source_url: "https://code.visualstudio.com/docs/copilot/customization/custom-agents"
cache_path: ".cache/sources/code-visualstudio-com-docs-copilot-customization-custom-agen.md"
fetched: "2026-03-06"
title: "Custom agents in VS Code"
authors: "Microsoft / VS Code Team"
year: "2026"
type: documentation
topics: [agent-format, vscode, copilot, custom-agents, handoffs, yaml-frontmatter, instruction-body]
cached: true
evidence_quality: documentation
date_synthesized: "2026-03-06"
research_issue: "Issue #12 — XML-Tagged Agent Instruction Format"
---

# Synthesis: Custom agents in VS Code

## 1. Citation

Microsoft / VS Code Team. (2026, March 4). "Custom agents in VS Code." *Visual Studio Code Documentation*. https://code.visualstudio.com/docs/copilot/customization/custom-agents

Accessed: 2026-03-06. Page displays "3/4/2026" as last-updated date. The VS Code documentation is continuously updated; this synthesis reflects the state on the retrieval date.

---

## 2. Research Question Addressed

This page answers three overlapping questions:
1. What is the canonical file format for `.agent.md` custom agent files in VS Code Copilot?
2. What YAML frontmatter fields are available, which are required, and what are their schemas?
3. How do handoffs, subagents, and orchestration work across custom agents?

For Issue #12 the operative question is narrower: does VS Code impose any constraint — structural, syntactic, or semantic — on the **body** of an `.agent.md` file that would prevent, restrict, or affect the use of XML-tagged section boundaries in place of Markdown headings?

---

## 3. Theoretical Framework

N/A — applied guide; no explicit theoretical framework.

The page is entirely prescriptive documentation. Its implicit model is that a custom agent is a **configuration object** (YAML frontmatter) paired with a **free-form natural-language instruction** (Markdown body). The separation between structured metadata (frontmatter) and unstructured instructions (body) is the only structural framework operative here.

---

## 4. Methodology / Source Type

This is primary normative documentation maintained by the VS Code product team — the authoritative specification for `.agent.md` file structure. Evidence type: **Documentation**. The page is versioned alongside VS Code releases; the table of frontmatter fields represents the schema as of VS Code 1.106+.

The source was retrieved as a full-page Markdown distillation that covers: the prose introduction, all frontmatter field descriptions (via tables), a handoffs schema breakdown, worked examples for planning agents, orchestration agents, and Claude-format agents, plus an FAQ. The cached version appears complete — no signs of truncation. Page length in the cache: 492 lines.

---

## 5. Key Claims with Evidence

- **`.agent.md` is Markdown by definition, body is free-form.** The spec states:
  > "The custom agent file body contains the custom agent implementation, formatted as Markdown. This is where you provide specific prompts, guidelines, or any other relevant information that you want the AI to follow when in this custom agent."

  "Formatted as Markdown" is descriptive, not restrictive — it means the file extension is `.md`, not that the body must contain only Markdown constructs. XML is valid inside Markdown and would not violate this constraint.

- **Body content is prepended to the user chat prompt verbatim.** The spec states:
  > "When you select the custom agent in the Chat view, the guidelines in the custom agent file body are prepended to the user chat prompt."

  This means the body is forwarded **as-is** to the model. XML tags in the body are transmitted unchanged. VS Code performs no parsing, validation, or transformation of the body text. Whatever format the author uses — Markdown headings, prose, XML tags, or mixed — the model receives exactly that text.

- **File references are supported using Markdown links.** The spec notes:
  > "You can reference other files by using Markdown links, for example to reuse instructions files."

  This is an opt-in Markdown feature in the body but is the only body-level syntax VS Code actively interprets. All other body content is opaque to VS Code.

- **The `#tool:<tool-name>` syntax enables tool references in the body.** The spec describes:
  > "To reference agent tools in the body text, use the `#tool:<tool-name>` syntax."

  This is the only other body-level syntax VS Code parses. It is unambiguous from XML tags; there is no conflict.

- **No minimum frontmatter is required; all frontmatter fields are optional.** The spec labels the header section "optional":
  > "The header is formatted as YAML frontmatter with the following fields"

  and introduces the table under the heading "Header (optional)". No field in the table is marked as required. An `.agent.md` file with only a body and no frontmatter is valid. An `.agent.md` file with full frontmatter and an XML-only body is equally valid.

- **Full frontmatter field inventory (all optional, per the spec):**

  | Field | Schema / Type | Notes |
  |---|---|---|
  | `description` | string | Shown as placeholder text in chat input |
  | `name` | string | Defaults to file name if absent |
  | `argument-hint` | string | Hint text in chat input field |
  | `tools` | array of strings | Tool/toolset/MCP tool names; `<server>/*` for full MCP server |
  | `agents` | array of strings (or `*` or `[]`) | Subagent allowlist |
  | `model` | string or array of strings | Single model or prioritized list tried in order |
  | `user-invocable` | boolean (default: `true`) | Controls visibility in agents dropdown |
  | `disable-model-invocation` | boolean (default: `false`) | Prevents subagent invocation by other agents |
  | `infer` | boolean | **Deprecated** — replaced by `user-invocable` + `disable-model-invocation` |
  | `target` | string (`vscode` or `github-copilot`) | Target environment |
  | `mcp-servers` | array of MCP server config objects | For GitHub Copilot target only |
  | `handoffs` | array of handoff objects | See handoff schema below |

- **`handoffs` field schema (nested object array):**

  Each handoff object supports:

  | Sub-field | Type | Required? | Description |
  |---|---|---|---|
  | `label` | string | yes | Display text on handoff button |
  | `agent` | string | yes | Target agent identifier |
  | `prompt` | string | no | Pre-filled prompt text for target agent |
  | `send` | boolean | no, default `false` | Auto-submits the prompt if `true` |
  | `model` | string | no | Qualified model name, e.g. `GPT-5 (copilot)` |

  Example from the spec:

  > ```yaml
  > handoffs:
  >   - label: Start Implementation
  >     agent: implementation
  >     prompt: Now implement the plan outlined above.
  >     send: false
  >     model: GPT-5.2 (copilot)
  > ```

- **Claude `.md` format is a separate but supported variant.** The spec documents an alternative format for `.claude/agents/` folder (plain `.md`, comma-separated `tools` string) and notes:
  > "VS Code maps Claude-specific tool names to the corresponding VS Code tools. Both the VS Code `.agent.md` format (with YAML arrays for tools) and the Claude format (with comma-separated strings) are supported."

  This is relevant because Claude agent bodies use XML-tagged sections natively. VS Code's explicit support for Claude format confirms the system is designed to ingest XML-tagged instruction bodies without modification.

- **Custom agent files detected in `.github/agents/` folder automatically.** The spec states:
  > "VS Code detects any `.md` files in the `.github/agents` folder of your workspace as custom agents."

  This is the exact folder used by EndogenAI. The detection mechanism is file extension and folder name — not body format.

- **The `agents` field controls subagent access and requires `agent` in `tools`.** The spec notes:
  > "If you specify `agents`, ensure the `agent` tool is included in the `tools` property."

  This is an important cross-field dependency constraint: the `agents` frontmatter field is only meaningful when the `agent` tool is also listed. Violating this silently degrades functionality.

- **Prioritized model lists supported natively.** The spec shows:
  > ```yaml
  > model: ['Claude Opus 4.5', 'GPT-5.2']  # Tries models in order
  > ```

  This means a single `.agent.md` file can express model fallback preferences declaratively — relevant for EndogenAI agents that need to specify local-first and cloud-fallback chains.

- **`infer` field is deprecated.** The spec explicitly deprecates `infer: true/false` in favour of the more granular `user-invocable` and `disable-model-invocation` flags. Any EndogenAI agent files using `infer` should be migrated.

---

## 6. Critical Assessment

**Evidence Quality**: Documentation

This is the official VS Code product documentation, maintained by Microsoft employees with direct knowledge of the implementation. It is the ground truth for file format semantics. As documentation (not a research paper), it is not peer-reviewed in the academic sense, but it is authoritative by definition — it describes the system as built. The page was last updated 2026-03-06, reflecting VS Code 1.106+.

**Gaps and Limitations**:

The documentation describes what VS Code supports but does not prescribe or opine on instruction-body formatting strategies. It does not compare XML tags to Markdown headings as instruction structuring approaches, because that is a prompt-engineering concern outside VS Code's scope. The spec also does not document how VS Code handles encoding edge cases in XML (e.g., unescaped `<` in prose), though because the body is forwarded verbatim to the model this is the model's parsing problem, not VS Code's.

The Claude format section is present but thin — it lists the frontmatter fields but does not document whether VS Code supports Claude-style XML body sections in the `.github/agents/` folder variant (vs. `.claude/agents/`). This is a genuine gap: EndogenAI stores agents in `.github/agents/`, so whether Claude-format XML semantics apply there vs. only in `.claude/agents/` is unconfirmed by this source.

The `mcp-servers` field is mentioned but not fully documented here — it defers to GitHub Copilot documentation. Not a gap for Issue #12.

---

## 7. Cross-Source Connections

- Extends: [anthropic-building-effective-agents](./anthropic-building-effective-agents.md) — Anthropic's guidance recommends XML-tagged instructions; this VS Code spec confirms the body format is free-form and would transmit those tags unchanged to the model.
- Extends: [cookbook-research-lead-agent](./cookbook-research-lead-agent.md), [cookbook-research-subagent](./cookbook-research-subagent.md) — the Anthropic cookbook agents use XML sections in their system prompts. The VS Code body-prepend mechanism means these XML sections would be forwarded as-is to the backing model, confirming the formats are compatible at the transport layer.
- Extends: [platform-claude-com-docs-en-build-with-claude-prompt-enginee](./platform-claude-com-docs-en-build-with-claude-prompt-enginee.md) — Claude prompt engineering docs likely document the recommended XML schema; this VS Code spec confirms the `.agent.md` file is a transparent wrapper that will preserve whatever that schema produces.
- No direct contradiction found with any existing source in the corpus.

---

## 8. Project Relevance — Direct Applicability to EndogenAI `.agent.md` Files

**Does the VS Code `.agent.md` spec explicitly support or restrict XML in the instruction body?**

The spec does **not restrict** XML. The body is defined only as "formatted as Markdown" — meaning `.md` file extension context — with the operational guarantee that its content is "prepended to the user chat prompt" verbatim. No parsing, linting, validation, or transformation of body content occurs. XML tags placed in the body will be forwarded unchanged to the model. VS Code's explicit support for the Claude agent format (which uses XML-tagged sections natively) further confirms this is by design.

**Verdict: ADOPT** XML-tagged section boundaries in EndogenAI agent bodies. The VS Code spec presents no technical barrier.

**What YAML frontmatter fields are defined (required vs. optional)?**

All frontmatter fields are **optional**. The header block itself is labelled "Header (optional)". The fields EndogenAI currently uses are `description`, `tools`, `model`, and `name` — all present and documented. Fields EndogenAI does not yet use but should evaluate:

- `agents` + `agent` tool: required pairing for any agent that orchestrates subagents. If `.github/agents/*.agent.md` files invoke subagents, this field should be explicit to prevent uncontrolled subagent escalation.
- `user-invocable: false`: useful for agents that are only valid as subagents (e.g., specialist agents invoked by an executive). Currently this control is absent from the EndogenAI fleet.
- `disable-model-invocation: true`: prevents an agent from being invoked as a subagent by other agents. Appropriate for the Review agent and GitHub agent to prevent them from being hijacked in unwanted chains.
- `model` as an array: allows declaring local-model-first priorities. Directly supports the local-compute-first principle from `MANIFESTO.md`.
- `infer` field: **deprecated** — if any EndogenAI agent files contain `infer`, they should be updated to `user-invocable` + `disable-model-invocation` equivalents.

**Are there any constraints on instruction body format that would affect an XML migration?**

Two body-level syntaxes are actively parsed by VS Code: Markdown link syntax (for file references) and the `#tool:<name>` syntax. Both are unambiguous from XML tags. Neither presents a migration blocker.

The only practical constraint is that if the body contains XML tags that happen to contain unescaped Markdown link syntax or `#tool:` strings, VS Code may try to resolve them — but this would only matter if XML-wrapped content intentionally embedded Markdown file links. Normal XML-tagged instruction sections (`<workflow>`, `<guardrails>`, `<completion_criteria>`) contain no such constructs.

**Verdict: No body-format constraints affect the XML migration.** ADOPT.

**What is the `handoffs` field schema?**

Fully documented above in §5. Summary for EndogenAI:

- `handoffs` is a YAML array under the frontmatter key.
- Each entry requires `label` (display text) and `agent` (target agent identifier).
- Optional: `prompt` (pre-filled text), `send` (boolean, default `false`), `model` (qualified model name).
- `send: false` is correct default — it shows a button but does not auto-submit, preserving human review before transition.
- The `agent` field value is the **identifier** of the target agent. In VS Code this is the file name stem (e.g., `implementation` for `implementation.agent.md`).

EndogenAI's multi-agent handoff pattern (Executive → Scout → Synthesizer → Archivist) can be encoded natively in frontmatter `handoffs`. This would make inter-agent transitions explicit and discoverable from the agent file itself — an ADOPT recommendation for the next agent fleet revision.

**Scripts and guides bearing on this synthesis:**

- [scripts/scaffold_agent.py](../../scripts/scaffold_agent.py) — should be updated to emit XML-tagged body stubs and to include complete frontmatter field coverage (especially `agents`, `user-invocable`, `disable-model-invocation`).
- [docs/guides/agents.md](../../docs/guides/agents.md) — should document the complete frontmatter schema drawn from this spec, replacing or extending any partial field tables currently present.
- [.github/agents/AGENTS.md](../../.github/agents/AGENTS.md) — should document the `handoffs` schema and the `agents` + `agent` tool pairing constraint.
- Issue #12 migration script (`scripts/migrate_agents_to_xml.py`) — technically unblocked by this spec; the body is opaque to VS Code and any XML schema can be applied.

---

## Referenced By

<!-- Populated automatically by scripts/link_source_stubs.py — do not edit manually -->
- [Anthropic Building Effective Agents](../sources/anthropic-building-effective-agents.md)
- [Code Visualstudio Com Api Extension Guides Chat](../sources/code-visualstudio-com-api-extension-guides-chat.md)
- [Cookbook Research Lead Agent](../sources/cookbook-research-lead-agent.md)
- [Cookbook Research Subagent](../sources/cookbook-research-subagent.md)
- [Microsoft Github Io Autogen Stable User Guide Agentchat User](../sources/microsoft-github-io-autogen-stable-user-guide-agentchat-user.md)
- [Platform Claude Com Docs En Build With Claude Prompt Enginee](../sources/platform-claude-com-docs-en-build-with-claude-prompt-enginee.md)
- [Platform Openai Com Docs Api Reference Assistants](../sources/platform-openai-com-docs-api-reference-assistants.md)
- [Python Langchain Com Docs Concepts Agents](../sources/python-langchain-com-docs-concepts-agents.md)
- [Xml Agent Instruction Format](../xml-agent-instruction-format.md)
