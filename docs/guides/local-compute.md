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

### Structural Test & Enforcement-Proximity

Local compute is not merely a cost tier — it is oversight infrastructure. The **structural test** is the authoritative decision rule: before choosing cloud execution, ask whether cloud residency transfers enforcement authority, oversight access, or governance guarantees to an external party. If yes, local is preferred regardless of cost or convenience. The **enforcement-proximity principle** (from [`docs/research/lcf-oversight-infrastructure.md`](../research/infrastructure/lcf-oversight-infrastructure.md)) states that governance mechanisms must be co-located with what they govern: a validator that runs locally cannot be bypassed by an API outage or provider policy change, whereas a cloud-only enforcement point inherits a structural availability dependency at every enforcement boundary. Apply both tests before delegating any enforcement-critical operation to a cloud service.

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

For full setup guide and model selection rationale, see [`docs/research/local-copilot-models.md`](../research/models/local-copilot-models.md).

### Model Selection Strategy

| Task type | Recommended model tier |
|-----------|------------------------|
| Quick completions, boilerplate | Small local model (7B–13B) |
| Complex reasoning, architecture decisions | Claude Sonnet / GPT-4 class |
| Code review, validation | Medium local model (13B–34B) |

Use the **Auto** model selection in VS Code Copilot Chat to get ~10% token savings by routing simple tasks to smaller models automatically.

---

## Strategy D: Deployment Registry & Multi-Provider Routing

**Structural Resilience Control**: To mitigate rate limits and provider outages, the repository uses a multi-provider routing strategy. Instead of a single API key, agents can route requests through a **deployment registry** that includes primary and fallback providers.

- **Source**: [`docs/research/agent-fleet-model-diversity-and-structured-formats.md`](../research/agent-fleet-model-diversity-and-structured-formats.md) § Recommendation 2
- **Implementation**: [`data/deployment-registry.yml`](../../data/deployment-registry.yml)

The registry encodes a **deployment-level cooldown pattern** (LiteLLM-style). When a request to a provider (e.g., Anthropic Direct) returns a 429 Rate Limit error, the orchestrator cools down that deployment and immediately routes the next request to a healthy alternative (e.g., Vertex AI). This ensures that sessions proceed without sleepy retries or manual intervention.

For more on rate-limit mitigation, see the [`rate-limit-resilience` skill](../../.github/skills/rate-limit-resilience/SKILL.md).

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

For architecture recommendations and the endogenic MCP server design, see [`docs/research/local-mcp-frameworks.md`](../research/agents/local-mcp-frameworks.md).

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
[LLM Tier Strategy research doc](../research/models/llm-tier-strategy.md).

---

## Research Docs

Detailed synthesis documents for local compute topics:

| Topic | Document | Status |
|-------|----------|--------|
| VS Code Copilot with local models | [`docs/research/local-copilot-models.md`](../research/models/local-copilot-models.md) | Draft |
| Locally distributed MCP frameworks | [`docs/research/local-mcp-frameworks.md`](../research/agents/local-mcp-frameworks.md) | Draft |
| Benchmarking local vs. cloud token usage | Open — see [issue #5 D3](https://github.com/EndogenAI/dogma/issues/5) | Not started |

See [GitHub Issues labeled `research`](https://github.com/EndogenAI/dogma/issues?q=label%3Aresearch) for current status.

---

## Practitioner Testimonials — Local Model Substitution

**Source**: Nolen Jonker, "I cancelled ChatGPT, Gemini, and Perplexity to run one local model, and I don't miss them," *XDA Developers*, March 17, 2026. <https://www.xda-developers.com/cancelled-chatgpt-gemini-perplexity-to-run-one-local-model/>

A practitioner switched from multiple cloud AI subscriptions to a single local model
(gpt-oss 20B via LM Studio on Intel Core i7-13700, 16 GB RAM). Field-reported findings:

**Works well locally:**
- Explaining concepts ("explain like I'm 5") and brainstorming
- General writing, math, and light summarisation
- Quick information retrieval and quiz/question-answering
- Minor scripting tasks with simple, well-scoped prompts

**Still needs a frontier model:**
- Complex multi-step processes run end-to-end without manual decomposition
- Large-context document summarisation (cloud services retain quality lead)
- Deep agentic tool use and complex code generation (community reports: gpt-oss 20B poor at tooling)
- Web search without additional MCP setup

**Friction points practitioners report:**
- Multi-part queries must be broken into single-topic chunks; local models handle ambiguity less gracefully than cloud
- Less adaptive to conversational context — requires more explicit direction per turn
- Model selection is the critical gate: general-purpose 20B models fall short for coding; architecture-specific models (e.g., Qwen3.5 30B) are required but may not run on consumer CPUs
- Community debate on reliability: multiple commenters note significant variance in tool-calling quality across models

**Implication for Local-Compute-First axiom**: High-volume, well-defined tasks (explaining, brainstorming, short summaries) are fully viable locally and validate the Local-Compute-First principle for casual use patterns. For agentic and tool-calling workloads, model selection is the binding constraint — not the local runtime itself. See [Strategy E](#strategy-e-tier-routing--which-task-gets-which-model) for the full routing decision table.
