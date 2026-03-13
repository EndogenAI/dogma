# Running Locally — Token Reduction Guide

> *"We need to burn the big candle at both ends so we can light many little candles at a single end."*
> — EndogenAI Issue #35

---

## Why Local Compute?

Cloud LLM inference is expensive — in tokens, API cost, and environmental impact. Running as much inference as possible locally:

- **Reduces token burn** for repetitive or context-heavy tasks
- **Eliminates rate limits** and API costs for local development
- **Improves privacy** — code never leaves your machine
- **Enables offline development**

The endogenic approach compounds this: by encoding context as scripts, you reduce the number of tokens needed per session regardless of where the inference runs.

---

## Strategy A: Encode Context as Scripts (Highest ROI)

Before reaching for a local model, reduce the token footprint of your sessions:

1. **Run `scripts/prune_scratchpad.py --init`** at session start — don't let the scratchpad grow unbounded
2. **Check `scripts/`** before doing anything interactively — a script that already exists costs zero tokens
3. **Start `watch_scratchpad.py`** — auto-annotation costs zero agent tokens
4. **Use the `--dry-run` pattern** on scripts to verify without burning tokens on corrections

This alone can cut session token usage significantly before any local inference is involved.

---

## Strategy B: Local Models for Copilot

### VS Code Copilot with Local Models

VS Code Copilot can route requests to local models via OpenAI-compatible APIs.

**Recommended local inference servers:**

| Tool | Best for | Notes |
|------|---------|-------|
| [Ollama](https://ollama.ai) | Quick setup, wide model support | `ollama pull <model>` |
| [LM Studio](https://lmstudio.ai) | GUI, easy model management | OpenAI-compatible API on `localhost:1234` |
| [llama.cpp](https://github.com/ggerganov/llama.cpp) | Maximum control, low overhead | Requires more setup |

**Configuration** — VS Code Language Models editor (UI path):

1. Open Chat (⌃⌘I) → model picker dropdown → **Manage Models**
2. Select **Add Models** → choose **Ollama** from the provider list
3. VS Code discovers locally-running models automatically
4. Select the model in the chat model picker

**Requirements**: Ollama must be running (`ollama serve`), a Copilot plan (minimum: Free) is required, and internet access is still needed for some Copilot service requests.

**Current constraints** (Q1 2026):
- Local models work for chat only — inline suggestions cannot use local models
- BYOK is only available for Copilot Individual (not Business/Enterprise)
- Models must support tool calling to be usable in agent mode

For custom endpoints (VS Code Insiders, 1.104+):

```json
// settings.json
"github.copilot.chat.customOAIModels": [
  {
    "id": "llama3.2",
    "name": "Llama 3.2 (Local)",
    "endpoint": "http://localhost:11434/v1",
    "modelName": "llama3.2"
  }
]
```

For full setup guide and model selection rationale, see [`docs/research/local-copilot-models.md`](../research/local-copilot-models.md).

### Model Selection Strategy

| Task type | Recommended model tier |
|-----------|------------------------|
| Quick completions, boilerplate | Small local model (7B–13B) |
| Complex reasoning, architecture decisions | Claude Sonnet / GPT-4 class |
| Code review, validation | Medium local model (13B–34B) |

Use the **Auto** model selection in VS Code Copilot Chat to get ~10% token savings by routing simple tasks to smaller models automatically.

---

## Strategy C: Locally Networked Compute

If you have access to a machine with a capable GPU (e.g., Apple Silicon M-series):

1. Install Ollama or LM Studio on the powerful machine
2. Expose the API on the local network (e.g., `OLLAMA_HOST=0.0.0.0 ollama serve`)
3. Point VS Code on your development machine to the network address

VS Code has **native MCP server support** (1.103+): configure servers in `.vscode/mcp.json` and they are automatically available in chat.

```json
// .vscode/mcp.json — workspace-scoped, commit to share with team
{
  "servers": {
    "filesystem": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "${workspaceFolder}"],
      "sandboxEnabled": true,
      "sandbox": { "filesystem": { "allowWrite": ["${workspaceFolder}"] } }
    },
    "gpu-machine": {
      "type": "http",
      "url": "http://192.168.1.100:11434/mcp"
    }
  }
}
```

**Sandboxing** (macOS/Linux): enable `sandboxEnabled: true` to restrict stdio servers to configured filesystem paths and network domains. Auto-approves tool calls within the sandbox.

For architecture recommendations and the endogenic MCP server design, see [`docs/research/local-mcp-frameworks.md`](../research/local-mcp-frameworks.md).

---

## Strategy D: Token-Efficient Agent Practices

Regardless of where inference runs, these practices reduce token consumption:

| Practice | Token impact |
|---------|-------------|
| Read `AGENTS.md` once per session, not per task | Saves repeated context loading |
| Use session scratchpad for inter-agent handoffs | Avoids re-explaining context |
| Invoke `Executive Scripter` for repeated tasks | Encodes knowledge so future sessions start cheaper |
| Use `--dry-run` before destructive operations | Avoids token cost of fixing mistakes |
| Write specific delegation prompts with explicit exclusions | Prevents agents from over-reading files |

---

## Quick Reference: Local Setup

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a coding model
ollama pull codellama
ollama pull deepseek-coder

# Start the server (listens on localhost:11434 by default)
ollama serve

# Test
curl http://localhost:11434/api/generate -d '{"model": "codellama", "prompt": "hello"}'
```

---

## Strategy E: Tier Routing — Which Task Gets Which Model

Not all tasks require a frontier model. Explicitly classifying tasks before dispatching them
to a model is the highest-leverage cost-reduction practice after script encoding.

| Task Category | Min Tier | Recommended |
|---|---|---|
| Synthesis, architecture planning, PR review | Frontier | Claude Sonnet 3.7, o3 |
| Code generation, code review | Mid | GPT-4o, Gemini 2.0 Flash |
| Structured editing (YAML, JSON, frontmatter) | Mid / Local | GPT-4o-mini, 13B local |
| Boilerplate generation, test stubs | Local / Free | Codellama 13B, DeepSeek-Coder |
| File search, grep, context gathering | Local / Free | Any 7B+ |

**Target allocation**: aim for ~45% of agent turns at Local/Free tier, ~35% Mid, ~20%
Frontier. Shifting even a small percentage of turns from Frontier to Local meaningfully
reduces monthly cost and rate-limit pressure.

**GitHub Copilot tiers at a glance** (Q1 2026 — verify current quotas at GitHub docs):
- **Free**: ~50 chat messages/month, mid-tier models only
- **Pro (~$10/month)**: unlimited chat, all models including frontier; premium models
  (o1, o3, Claude 3.7) are rate-limited even on Pro
- **Local (Ollama/LM Studio)**: zero marginal cost for the tasks listed above

For the full rationale, model capability map, and lazy escalation pattern, see the
[LLM Tier Strategy research doc](../research/llm-tier-strategy.md).

---

## Research Docs

Detailed synthesis documents for local compute topics:

| Topic | Document | Status |
|-------|----------|--------|
| VS Code Copilot with local models | [`docs/research/local-copilot-models.md`](../research/local-copilot-models.md) | Draft |
| Locally distributed MCP frameworks | [`docs/research/local-mcp-frameworks.md`](../research/local-mcp-frameworks.md) | Draft |
| Benchmarking local vs. cloud token usage | Open — see [issue #5 D3](https://github.com/EndogenAI/dogma/issues/5) | Not started |

See [GitHub Issues labeled `research`](https://github.com/EndogenAI/dogma/issues?q=label%3Aresearch) for current status.
