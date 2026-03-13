---
title: "Running VS Code Copilot with Local Models"
status: "Draft"
---

# Running VS Code Copilot with Local Models

> **Status**: Draft
> **Research Question**: How do we configure VS Code GitHub Copilot to use local LLM inference (Ollama, LM Studio) instead of cloud APIs?
> **Date**: 2026-03-07
> **Related**: [`docs/guides/local-compute.md`](../guides/local-compute.md) · [`docs/research/dev-workflow-automations.md`](dev-workflow-automations.md)

---

## 1. Executive Summary

VS Code Copilot supports **Bring Your Own Model Key (BYOK)** via its Language Models editor, which allows routing chat requests to locally-running OpenAI-compatible inference servers such as Ollama and LM Studio. As of VS Code 1.104 (Q1 2026), the integration is production-stable for Copilot Individual plans. Key constraints: local models apply only to chat (not inline suggestions), still require an internet connection and a Copilot plan (including the free tier), and must support tool calling to be usable in agent mode.

The integration is straightforward: install Ollama or LM Studio, pull a model, open the Language Models editor, and add Ollama as a provider. VS Code discovers available models automatically and surfaces them in the chat model picker. For agent-capable workflows, the model must support tool calling (e.g., `llama3.2`, `qwen2.5-coder`).

**Endogenic relevance**: This directly implements the Local Compute-First axiom from `MANIFESTO.md`. For repetitive tasks (annotation, classification, stub generation), a locally-running 7B–8B model achieves zero marginal inference cost per session.

---

## 2. Hypothesis Validation

### H1 — Local models can replace cloud models for common agent tasks

**Supported** with caveats. Ollama models accessible via BYOK can handle:
- Structured editing (YAML/JSON/frontmatter modification)
- Boilerplate generation and test stubs
- File search and summarization
- Simple classification and annotation

**Not supported** without cloud fallback:
- Complex multi-step reasoning (architecture decisions, synthesis)
- Inline code completions (local models cannot serve inline suggestions)
- Agent mode (requires tool-calling capable model)

The boundary is clear: tasks at the "Local/Free" tier of the `docs/guides/local-compute.md` strategy table are viable. Frontier-tier tasks remain cloud-bound.

### H2 — BYOK configuration is production-stable for Copilot Individual

**Confirmed**. As of VS Code 1.104, the Ollama provider is a built-in option in the Language Models editor. Configuration is UI-driven; no manual JSON editing required unless using OpenAI-compatible custom endpoints (`github.copilot.chat.customOAIModels` setting, VS Code Insiders only as of this writing).

**Constraint**: BYOK is not available for Copilot Business or Enterprise users — GitHub states it will be extended to those plans later.

### H3 — VS Code Insiders vs. Stable matters for local model features

**Partially confirmed**. The custom OpenAI-compatible endpoint setting (`customOAIModels`) was VS Code Insiders-only as of 1.104. The Ollama built-in provider was available in Stable. Feature availability is actively shifting; verify against VS Code release notes at time of implementation.

### H4 — Local model setup requires minimal configuration

**Confirmed** for chat use. Steps:
1. Install Ollama: `curl -fsSL https://ollama.com/install.sh | sh`
2. Pull a model: `ollama pull llama3.2` (tool-calling support)
3. Start server: `ollama serve` (defaults to `localhost:11434`)
4. In VS Code: open model picker → Manage Models → Add Models → Ollama → VS Code discovers local models

No API key is required. No JSON editing required for the happy path.

---

## 3. Pattern Catalog

### Pattern 1 — Ollama as Local Chat Model Provider

**Setup**:
```bash
# Install Ollama (macOS/Linux)
curl -fsSL https://ollama.com/install.sh | sh

# Tool-calling capable models (required for agent mode)
ollama pull llama3.2          # 3B — fast, good tool calling
ollama pull qwen2.5-coder:7b  # 7B — strong for code tasks
ollama pull codellama         # 7B — Llama-tuned for code

# Start server (default: localhost:11434, OpenAI-compatible API)
ollama serve

# Verify
curl http://localhost:11434/api/tags
```

**VS Code configuration** (UI path):
1. Open Chat (⌃⌘I) → model picker → **Manage Models**
2. Select **Add Models** → choose **Ollama**
3. VS Code discovers running models automatically
4. Select the model from the picker in chat

**VS Code configuration** (JSON fallback, for custom endpoints):
```json
// settings.json — Insiders only as of 1.104
"github.copilot.chat.customOAIModels": [
  {
    "id": "llama3.2",
    "name": "Llama 3.2 (Local)",
    "endpoint": "http://localhost:11434/v1",
    "modelName": "llama3.2"
  }
]
```

### Pattern 2 — LM Studio as Local Chat Provider

LM Studio runs an OpenAI-compatible server on `localhost:1234` by default. Enable the server in LM Studio → Developer → Start Server. Then add as a custom OpenAI-compatible endpoint in VS Code using the `customOAIModels` setting (Insiders) or the Language Models editor Add Models flow.

### Pattern 3 — Networked Ollama (multi-machine)

If Ollama runs on a separate GPU machine (e.g., Apple Silicon Mac or Linux workstation), expose it on the local network:

```bash
# On the GPU machine — expose on all interfaces
OLLAMA_HOST=0.0.0.0 ollama serve

# On the dev machine — point VS Code to the network address
# (use customOAIModels setting with endpoint = http://<gpu-machine-ip>:11434/v1)
```

Security note: no authentication is required by default on Ollama's HTTP API. Restrict network access via firewall rules. Do not expose Ollama to the public internet.

### Pattern 4 — Model Selection by Task Type

| Task | Min VRAM | Recommended local model | Notes |
|------|----------|------------------------|-------|
| Structured editing (YAML/JSON) | 4 GB | `llama3.2:3b` | Fast, good instruction following |
| Code generation / review | 8 GB | `qwen2.5-coder:7b` | Strong code benchmark |
| Research annotation / classification | 4 GB | `llama3.2:3b` | Adequate for short-context classification |
| Agent mode (tool calling required) | 8 GB | `llama3.2` or `qwen2.5-coder` | Must support tool calling |
| Architecture / synthesis | N/A | Cloud fallback | Local 7B models insufficient |

---

## 4. Constraints and Open Questions

### Current Limitations (as of Q1 2026)

- **Inline suggestions**: Local models cannot provide inline code completions in VS Code. Only cloud models can serve the inline suggestion API. The `InlineCompletionItemProvider` extension API is available for third-party integrations.
- **Internet required**: Even when using a local model for chat, VS Code still routes some requests to the Copilot service (embeddings, repository indexing, query refinement). A direct offline mode does not exist yet.
- **Copilot plan required**: You must have at least the Copilot Free plan to use local models in chat.
- **Business/Enterprise**: BYOK is not available for organizational Copilot plans yet (planned for later).

### Open Questions

- **Token usage benchmarks**: How much does using Ollama for structured editing tasks actually reduce the premium request count per session? (Issue #5 D3 — formal benchmark needed)
- **VS Code Insiders vs. Stable**: Which `customOAIModels` features have graduated to Stable? Track VS Code release notes.
- **MCP servers + local models**: Can an agent configured to use a local chat model still invoke MCP tools effectively? Tool-calling capability is model-dependent.

---

## 5. Recommendations for Endogenic Fleet

1. **Adopt Ollama as default local inference for structured editing tasks** — update `docs/guides/local-compute.md` Strategy B with the verified configuration steps above
2. **Model default**: `llama3.2:3b` for fast annotation/classification; `qwen2.5-coder:7b` for code generation tasks
3. **For agent mode**: verify tool calling works with the chosen model before relying on it in multi-step workflows
4. **Benchmark task**: run a formal comparison of premium request usage with vs. without local model for common agent tasks (implementation of D3 from issue #5)
5. **Inline completions**: accept the current gap — no local alternative; focus local inference on chat-based agent tasks

---

## References

- [VS Code Language Models documentation](https://code.visualstudio.com/docs/copilot/customization/language-models) — source for BYOK, Ollama setup, model picker
- [Ollama documentation](https://ollama.ai) — model catalog, installation, API reference
- [`docs/guides/local-compute.md`](../guides/local-compute.md) — endogenic local compute guide (update target for implementation)
- [GitHub Issue #5](https://github.com/EndogenAI/dogma/issues/5) — tracking issue for this research arc
