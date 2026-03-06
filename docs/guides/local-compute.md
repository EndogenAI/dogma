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

**Configuration** (VS Code settings):

```json
{
  "github.copilot.chat.experimental.completionContext": true
}
```

> **Research needed**: The exact VS Code Copilot local model configuration is an active research area. See [GitHub Issue: Local VS Code Copilot Setup](https://github.com/EndogenAI/Workflows/issues) for the latest findings.

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

> **Research needed**: Secure local network MCP distribution is an open research question. See the related issue for current findings.

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

## Open Research Tasks

The following are open questions tracked as GitHub Issues:

- [ ] Exact VS Code Copilot local model configuration steps
- [ ] Optimal model selection for different agent task types
- [ ] Secure local network distribution of MCP frameworks
- [ ] Benchmarking token usage: local vs. cloud for common agent workflows

See the [GitHub Issues](https://github.com/EndogenAI/Workflows/issues?q=label%3Aresearch) for current status.
