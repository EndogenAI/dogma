---
slug: "microsoft-github-io-autogen-stable-user-guide-agentchat-user"
title: "AutoGen AgentChat Quickstart"
url: "https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/quickstart.html"
authors: "Microsoft AutoGen Team"
year: "2025"
type: documentation
topics: [agents, multi-agent, agent-instructions, system-message, tool-use, python]
cached: true
evidence_quality: documentation
date_synthesized: "2026-03-06"
source_url: "https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/quickstart.html"
cache_path: "/Users/conor/Sites/Workflows/.cache/sources/microsoft-github-io-autogen-stable-user-guide-agentchat-user.md"
fetched: "2026-03-06"
research_issue: "Issue #12 — XML-Tagged Agent Instruction Format"
---

# Synthesis: AutoGen AgentChat Quickstart

## 1. Citation

Microsoft AutoGen Team. (2025). *AutoGen AgentChat Quickstart*. Microsoft AutoGen Documentation (stable). https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/quickstart.html

## 2. Research Question Addressed

This quickstart guide addresses: how do you construct and run a single tool-using agent in AutoGen's AgentChat API? It demonstrates the minimum viable configuration for an `AssistantAgent`, showing which constructor arguments control identity, behaviour, tools, and — critically for Issue #12 — agent-level instructions. The implicit question it answers for this research is: **what format does AutoGen use for agent instruction strings?**

## 3. Theoretical Framework

AutoGen's `AgentChat` layer operates within a **preset-agent** model: framework-provided agent classes (`AssistantAgent`) encapsulate an LLM client, a tool registry, and a behavioural policy, and the user configures them through constructor kwargs. This is a **composition-over-inheritance** pattern — agents are assembled from interchangeable parts rather than subclassed. The framework presupposes the OpenAI Chat Completions API message format (`system` / `user` / `assistant` roles), so instruction injection maps directly to the `system` message slot. No explicit theoretical citation is present in the quickstart; the design is implicitly grounded in the ReAct-style tool-use loop (LLM → tool call → observation → final response) as evidenced by `reflect_on_tool_use=True`.

## 4. Methodology / Source Type

- **Type**: Official framework documentation — quickstart / getting-started guide.
- **Structure**: Linear narrative with inline runnable code blocks and representative terminal output.
- **Evidence basis**: Demonstrated via a concrete, self-contained weather-tool example. The output block shows actual message flow, confirming the execution model.
- **Coverage**: Covers single-agent setup only; multi-agent patterns are deferred to the tutorial series linked at the end.
- **Reproducibility**: Fully reproducible — `pip install` instructions provided, no hidden credentials beyond a standard OpenAI API key.

## 5. Key Claims with Evidence

1. **Agent instructions are plain-string `system_message` constructor arguments.**
   The `AssistantAgent` constructor accepts a `system_message` keyword argument:
   > `system_message="You are a helpful assistant."`
   This is an unformatted natural-language string. No XML, Markdown structure, or schema-validated format is imposed or recommended. The quickstart uses the minimal one-liner without comment.

2. **The `system_message` field maps directly to the LLM's `system` role slot.**
   The naming (`system_message`) is an explicit reference to the underlying Chat Completions `system` role. AutoGen treats the instruction string as a direct pass-through to the model, meaning all formatting conventions (or their absence) are inherited from whatever the model accepts — not enforced by the framework.

3. **Agent identity is declared via the `name` parameter, separate from instructions.**
   > `name="weather_agent"`
   Identity (name) and behaviour (system_message) are separate constructor arguments. This mirrors the Anthropic pattern where metadata and instruction content are distinct, but neither AutoGen argument imposes structure on the content itself.

4. **Tools are registered as Python callables in a `tools` list.**
   > `tools=[get_weather]`
   Tool schemas are derived from function signatures and docstrings (PEP 484 / Google-style), not from XML or structured instruction blocks. The agent's instruction string does not enumerate available tools — AutoGen injects tool descriptions into the context automatically.

5. **`reflect_on_tool_use=True` enables a two-step reasoning loop.**
   After a tool call returns, the agent re-invokes the LLM to produce a final natural-language response. This is an architectural toggle, not an instruction-level directive — the user need not encode this behaviour in the `system_message`.

6. **Streaming is a constructor-level flag, not a runtime parameter.**
   > `model_client_stream=True`
   The streaming configuration is declared at agent construction alongside the instruction string, reinforcing that AutoGen bundles all agent-level policy in the constructor rather than in the instruction content.

7. **The async execution model runs agents via `agent.run_stream(task=...)`, passing the user prompt at runtime.**
   > `await Console(agent.run_stream(task="What is the weather in New York?"))`
   The user task is separate from the system instruction, following the standard system/user split of Chat Completions. AutoGen adds no wrapper markup to either.

8. **Installation targets two packages: `autogen-agentchat` and `autogen-ext[openai,azure]`.**
   > `pip install -U "autogen-agentchat" "autogen-ext[openai,azure]"`
   The modular packaging signals a provider-agnostic design: the core agent logic (`agentchat`) is decoupled from model backends (`ext`). Instruction format is therefore model-agnostic at the framework level.

9. **The sample output confirms tool call → execution → final answer flow.**
   ```
   [FunctionCall(id='...', arguments='{"city":"New York"}', name='get_weather')]
   [FunctionExecutionResult(content='...', ...)]
   The current weather in New York is 73 degrees and sunny.
   ```
   This is AutoGen's internal message trace format, not the instruction format. It shows the framework wraps tool I/O in typed result objects, but leaves the instruction string untouched.

10. **Guidance for non-OpenAI models defers to external tutorials.**
    > "Simply update the `model_client` with the desired model or model client class."
    No instruction-format differences are noted for alternative model providers, implying the plain-string `system_message` is treated as universal across backends.

## 6. Critical Assessment

**Evidence Quality**: Documentation

This is first-party official documentation from the framework maintainer (Microsoft), current as of the stable release channel. It is authoritative for describing AutoGen's intended usage patterns. However, it is a quickstart, not a reference spec — it illustrates the minimal path, not the full parameter surface.

**Gaps and Limitations**:
- The quickstart covers only `AssistantAgent` and only the `system_message` constructor argument. It does not document whether AutoGen accepts or recommends structured instruction formats (XML, YAML front matter, Markdown sections) for more complex agents.
- Multi-agent patterns (teams, orchestrators, termination conditions) are explicitly out of scope and deferred to tutorial/index.html.
- No discussion of instruction length limits, templating, or dynamic instruction injection. If AutoGen supports runtime modification of the system message, this quickstart does not show it.
- The cached page is a rendered notebook export; code examples are complete but narrative explanation is minimal — the document is approximately 276 lines including navigation chrome.
- No comparative analysis with other frameworks is offered; this source speaks only to AutoGen's own conventions.

## 7. Cross-Source Connections

- **Agrees with / extends**: [anthropic-building-effective-agents](./anthropic-building-effective-agents.md) — both frameworks treat the system instruction as a plain string passed to the LLM's `system` role; neither imposes XML or schema structure at the single-agent quickstart level.
- **Agrees with / extends**: [platform-claude-com-docs-en-build-with-claude-prompt-enginee](./platform-claude-com-docs-en-build-with-claude-prompt-enginee.md) — if that source covers Anthropic prompt engineering, both converge on unstructured natural-language strings as the baseline format.
- **Contrast with**: [code-visualstudio-com-docs-copilot-customization-custom-agen](./code-visualstudio-com-docs-copilot-customization-custom-agen.md) — VS Code Copilot agent instructions are Markdown-heavy `.agent.md` files with YAML front matter and rich section structure, a significantly more opinionated format than AutoGen's plain string.
- **Contrast with**: [python-langchain-com-docs-concepts-agents](./python-langchain-com-docs-concepts-agents.md) — sister source in this Issue #12 batch; LangChain's `system_prompt` kwarg mirrors AutoGen's `system_message`, confirming both major frameworks default to plain strings.

## 8. Project Relevance

AutoGen's instruction format — a single plain-string `system_message` constructor argument with no imposed structure — represents the dominant industry baseline for Issue #12. It directly answers the comparison question: **AutoGen does not use XML tags, Markdown sections, or any structured format for agent instructions**. The developer supplies an unformatted natural-language string; AutoGen forwards it unchanged to the LLM. This is the "no-opinion default" position that the EndogenAI project must consciously decide to depart from when adopting a structured XML-tagged format.

For [`.github/agents/`](../../.github/agents/) files in this repository, this finding supports the ADOPT position for **adding structure beyond AutoGen's baseline**. The plain-string default is minimal and portable but sacrifices machine-readability, section-addressability in IDE tooling, and the ability to partially override subsections when composing agents. The fact that AutoGen requires no structure is a feature for simple agents and a limitation for complex, multi-role agents — precisely the scenario the EndogenAI XML format targets.

The `reflect_on_tool_use=True` constructor flag (Claim 5) is also notable for [`docs/guides/agents.md`](../../docs/guides/agents.md): AutoGen externalises behavioural toggles as framework parameters rather than encoding them in the instruction string, whereas the EndogenAI approach encodes behaviour in the instruction document itself (via agent `.md` files). These are complementary strategies: AutoGen targets programmatic assembly; EndogenAI targets human-readable, version-controlled instruction authoring. **ADOPT** the explicit section structure and **REJECT** the AutoGen approach of embedding policy as opaque constructor flags invisible to the instruction text.

## Referenced By

<!-- Populated automatically by scripts/link_source_stubs.py — do not edit manually -->
- [Anthropic Building Effective Agents](../sources/anthropic-building-effective-agents.md)
- [Code Visualstudio Com Docs Copilot Customization Custom Agen](../sources/code-visualstudio-com-docs-copilot-customization-custom-agen.md)
- [Platform Claude Com Docs En Build With Claude Prompt Enginee](../sources/platform-claude-com-docs-en-build-with-claude-prompt-enginee.md)
- [Python Langchain Com Docs Concepts Agents](../sources/python-langchain-com-docs-concepts-agents.md)
- [Xml Agent Instruction Format](../xml-agent-instruction-format.md)
