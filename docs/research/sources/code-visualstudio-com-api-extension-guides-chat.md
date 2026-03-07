---
source_url: "https://code.visualstudio.com/api/extension-guides/chat"
cache_path: ".cache/sources/code-visualstudio-com-api-extension-guides-chat.md"
fetched: "2026-03-06"
research_issue: "Issue #12 — XML-Tagged Agent Instruction Format"
slug: "code-visualstudio-com-api-extension-guides-chat"
title: "VS Code Chat Participant API"
authors: "Microsoft / VS Code Team"
year: "2026"
type: documentation
topics: [vscode, chat-participant, extension-api, copilot, typescript, language-model, tool-calling, prompt-construction]
cached: true
evidence_quality: documentation
date_synthesized: "2026-03-06"
---

# Synthesis: VS Code Chat Participant API

## 1. Citation

Microsoft / VS Code Team. (2026, March 4). "Chat Participant API." *Visual Studio Code Extension API Documentation*.
https://code.visualstudio.com/api/extension-guides/chat

Accessed: 2026-03-06. Page displays "3/4/2026" as last-updated date. This is the canonical developer-facing reference for the TypeScript Chat Participant API, which is the extension mechanism that underpins Copilot Chat participants in VS Code. This synthesis reflects the state of the page on the retrieval date.

---

## 2. Research Question Addressed

This page answers: how does a VS Code extension implement a custom Copilot Chat participant using the TypeScript extension API? Specifically, it documents participant registration, the request handler interface, prompt construction, response streaming, tool calling, slash commands, and follow-up providers.

For Issue #12 the operative sub-questions are:
1. How does the extension API pass instruction prompts to the language model — raw string, structured object, or transformed markup?
2. What is the precise relationship between file-based `.agent.md` custom agents and this extension-level API?
3. Does VS Code perform any parsing, transformation, or stripping of prompt body content (including XML tags) before forwarding it to the model?

---

## 3. Theoretical Framework

N/A — applied guide; no explicit theoretical framework.

The page is a programming guide. Its implicit model is the **handler-stream pattern**: a registered TypeScript function (`ChatRequestHandler`) receives a structured `ChatRequest` object and writes to a `ChatResponseStream`. Prompt construction is fully controlled by the extension author — VS Code acts as a conduit, not a transformer.

---

## 4. Methodology / Source Type

**Documentation** — primary normative specification maintained by the VS Code product team. This is the authoritative TypeScript API guide for the `vscode.chat` namespace. Evidence type: Documentation.

The source was retrieved as a full-page Markdown distillation (799 lines) covering: purpose of chat participants vs. language model tools, the five-step implementation walkthrough, code samples in TypeScript, supported response output types with annotated code examples, tool-calling patterns (both via `@vscode/chat-extension-utils` and manual implementation), success measurement via telemetry, guidelines and naming conventions, and publishing guidance. The cached version appears complete and untruncated.

---

## 5. Key Claims with Evidence

- **Chat participants are distinct from language model tools and from `.agent.md` file-based agents.** The page explicitly positions three orthogonal extension points:
  > "Chat participants are different from language model tools that are invoked as part of the LLM orchestrating the steps needed to resolve the user's chat prompt. Chat participants receive the user's prompt and orchestrate the tasks that are needed themselves."
  
  `.agent.md` file-based custom agents (documented at `code.visualstudio.com/docs/copilot/customization/custom-agents`) are a *higher-level, file-based abstraction* that VS Code translates into the same underlying chat participant mechanism — but without requiring the extension author to write TypeScript. The extension API is the substrate; `.agent.md` is a configuration layer on top.

- **Prompt body is an arbitrary string — no XML parsing or sanitisation mentioned.** The `sendChatParticipantRequest` call accepts a `prompt` property:
  > "`prompt`: (optional) Instructions for the chat participant prompt."
  
  The type is a plain string. There is no schema validation, no stripping of markup, and no documented transformation. The string is forwarded to the selected language model via the Language Model API.

- **Extension authors have full, low-level control over what is sent to the model.** The `ChatHandlerOptions` object exposes: `prompt` (string), `model` (optional override), `tools` (optional tool list), `requestJustification` (string), and `responseStreamOptions`. Nothing in this interface filters or parses the prompt string content.

- **Responses are streamed back as Markdown.** The `ChatResponseStream` methods (`stream.markdown()`, `stream.progress()`, `stream.button()`, etc.) accept CommonMark Markdown. Markdown rendering is applied to *outbound* responses, not to *inbound* prompts — there is no inbound Markdown-to-XML or XML-to-Markdown conversion documented.
  > "Render a fragment of Markdown text simple text or images. You can use any Markdown syntax that is part of the CommonMark specification."

- **Trusted domain filtering applies to links in responses, not to prompt bodies.** The one documented content transformation is link protection:
  > "Images and links are only available when they originate from a domain that is in the trusted domain list."
  
  This is outbound (response rendering) only and is unrelated to instruction body content.

- **The prompt construction is the extension's responsibility — not VS Code's.** The request handler pattern hands raw user input to the extension, the extension constructs whatever prompt string it wants, and that string is passed to the LLM:
  > "Often, chat extensions use the `request.model` language model instance to process the request. In this case, you might adjust the language model prompt to match the user's intent."
  
  VS Code imposes no constraints on how that prompt is structured — XML, Markdown, plain text, or JSON are all treated identically.

- **Chat history is passed as-is to the participant, unparsed.** The participant gets raw `ChatRequestTurn` and `ChatResponseTurn` objects from `context.history`. Inclusion of history in the LLM prompt is the extension's choice:
  > "History will not be automatically included in the prompt, it is up to the participant to decide if it wants to add history as additional context when passing messages to the language model."

- **Participant detection uses `description` and `examples` metadata, not body content.** The `disambiguation` property in `package.json` drives automatic routing. This is separate from the instruction prompt body and is not affected by its format.

- **`@workspace` uses multiple tools internally, demonstrating that extension-level complexity is hidden from the file-based abstraction layer.** The guide notes:
  > "Internally, `@workspace` is powered by multiple tools: GitHub's knowledge graph, combined with semantic search, local code indexes, and VS Code's language services."
  
  This confirms that extension API participants and file-based custom agents exist on separate tiers — the extension tier handles complex orchestration that file-based agents cannot directly express.

- **Command injection protection applies only to command-link URIs in Markdown responses, not to prompt bodies.** When a response contains `command:commandId` links, `isTrusted` must be explicitly set. This is response-side security, not prompt-side content filtering.

- **The `@vscode/chat-extension-utils` library wraps the extension API but likewise accepts an arbitrary `prompt` string.** No transformation of that string is indicated in the library's documented interface. XML tags in that string would be forwarded unchanged.

---

## 6. Critical Assessment

**Evidence Quality: Documentation**

This is the authoritative Microsoft-published specification for the VS Code Chat Participant API. It is not a research paper — there are no empirical claims to evaluate. As a primary specification document it is the highest-quality evidence available for questions about API behaviour. Limitations derive from scope, not quality.

**Gaps and Limitations**:

1. The page documents the TypeScript extension API specifically. It does not document the internal VS Code process that reads an `.agent.md` file and synthesises a chat participant from it — that translation layer is undocumented (the user-facing `.agent.md` docs describe the file format but not the internal compilation step).
2. The page does not address how VS Code Copilot injects its own system prompt — only the extension's contribution to the prompt is covered. It is possible that Copilot's system prompt wraps the agent body in a way not disclosed in this guide.
3. No information on whether the Language Model API performs any pre-processing of prompt strings before sending to the model endpoint — that layer is documented separately at `/api/extension-guides/ai/language-model`.
4. The cached version is from March 4, 2026; the API is evolving rapidly and any claim about absence of XML parsing should be re-verified against newer releases or repository source if the stakes are high.
5. The guide uses `@cat` as its running example, which is a trivial toy participant. Real-world implications for complex production agent prompts (including XML-structured bodies) are not illustrated.

---

## 7. Cross-Source Connections

- Extends and is the substrate beneath: [code-visualstudio-com-docs-copilot-customization-custom-agen](./code-visualstudio-com-docs-copilot-customization-custom-agen.md) — `.agent.md` custom agents are a file-based configuration layer that compiles down to the chat participant API described here. The synthesis of the custom-agents doc established that the `.agent.md` body is "free-form Markdown" with no structural constraints; this API doc confirms no XML filtering or parsing at the underlying API level either.
- Partially addressed by: [platform-claude-com-docs-en-build-with-claude-prompt-enginee](./platform-claude-com-docs-en-build-with-claude-prompt-enginee.md) — if that synthesis covers Claude's treatment of XML in system prompts, it provides the model-side complement to this VS Code host-side analysis.
- Related architecture layer: [anthropic-building-effective-agents](./anthropic-building-effective-agents.md) — Anthropic's cookbook agents use XML-tagged instruction bodies; those bodies are passed directly to the Claude API. The VS Code Chat Participant API is an intermediary that forwards prompt strings unchanged to the model, making Anthropic's XML conventions directly applicable when the underlying model is Claude.

---

## 8. Project Relevance

This source is decisive for Issue #12 at the **host layer** of the XML-tagged instruction format question. The VS Code Chat Participant API documentation establishes that VS Code acts as a conduit for prompt strings, not a transformer. Prompt bodies — whether plain text, Markdown, XML, or any mixture — are accepted as arbitrary strings and forwarded unchanged to the language model via the Language Model API. There is no documented XML parsing, stripping, or special treatment anywhere in the Chat Participant API surface. **ADOPT**: the conclusion that VS Code imposes no constraint on prompt body format is supported by this source and should be recorded in the Issue #12 synthesis as a confirmed negative finding for the host layer.

The source also clarifies the architectural relationship between `.agent.md` files and extension-based chat participants, which is directly relevant to how XML bodies in `.github/agents/*.agent.md` files will be handled at runtime. The file-based custom agent mechanism (`code.visualstudio.com/docs/copilot/customization/custom-agents`) compiles `.agent.md` files into the same underlying chat participant construct documented here. This means the "no transformation" guarantee at the extension API level propagates upward: if the extension API does not parse XML, and the file-based layer sits on top of it, then the file-based layer almost certainly forwards the body as-is too. **ADAPT**: this inference should be verified by inspecting VS Code's open-source parser for `.agent.md` files, but it is the most parsimonious reading consistent with both documents. The `.github/agents/` files, specifically any `.agent.md` file in that folder (e.g., `executive-researcher.agent.md`, `github.agent.md`, `review.agent.md`), would have their XML-tagged bodies passed directly to the configured language model without host-level transformation.

One important gap this source exposes: the Language Model API (a separate layer below the Chat Participant API) is not covered here. It is possible that the Language Model API performs prompt assembly, caching, or normalisation steps that would affect XML tags. The Issue #12 research should explicitly target the Language Model API documentation (`.../ai/language-model`) as a follow-up source before finalising the migration recommendation for `scripts/migrate_agents_to_xml.py`. Until that layer is confirmed to be equally pass-through, the XML adoption decision should be marked as contingent on verifying the Language Model API layer. **REJECT** treating this source alone as sufficient to close Issue #12 — it closes the host/extension layer question but leaves the model-API intermediary layer open.

---

## Referenced By

<!-- Populated automatically by scripts/link_source_stubs.py — do not edit manually -->
- [Anthropic Building Effective Agents](../sources/anthropic-building-effective-agents.md)
- [Code Visualstudio Com Docs Copilot Customization Custom Agen](../sources/code-visualstudio-com-docs-copilot-customization-custom-agen.md)
- [Platform Claude Com Docs En Build With Claude Prompt Enginee](../sources/platform-claude-com-docs-en-build-with-claude-prompt-enginee.md)
- [Xml Agent Instruction Format](../xml-agent-instruction-format.md)
