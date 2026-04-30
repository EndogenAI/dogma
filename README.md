# EndogenAI Workflows

> **Values ingrained, sovereignty sustained**

[![Tests](https://github.com/EndogenAI/dogma/actions/workflows/tests.yml/badge.svg)](https://github.com/EndogenAI/dogma/actions/workflows/tests.yml)
[![Docs](https://github.com/EndogenAI/dogma/actions/workflows/docs.yml/badge.svg)](https://endogenai.github.io/dogma/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

The authoritative source for **endogenic / agentic product design and development** workflows, best practices, agent files, and automation scripts.

> **Endogenic development** is the practice of building AI-assisted systems from the inside out — scaffolding from existing knowledge, encoding operational wisdom as scripts and agents, and letting the system grow intelligently from a morphogenetic seed rather than through vibe-driven prompting.

---

## Contents

- [What Is This Repo?](#what-is-this-repo)
- [Architecture](#architecture)
- [Core Principles](#core-principles)
- [MCP Toolset](#mcp-toolset)
- [Quick Start](#quick-start)
- [File Directory](#file-directory)
- [Community](#community)
- [Related](#related)
- [License](#license)


---

## What Is This Repo?

This repo holds the canonical reference for how we work with AI coding agents. It is a living manifesto, a workflow library, and a scripts catalog — not an application codebase.

**Contents:**

| Path | Purpose |
|------|---------|
| [`MANIFESTO.md`](MANIFESTO.md) | Core philosophy and dogma of endogenic development |
| [`AGENTS.md`](AGENTS.md) | Root guidance for all AI coding agents operating in this repo |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | How to contribute to this repo |
| [`docs/glossary.md`](docs/glossary.md) | Canonical definitions for all key project terminology |
| [`.github/agents/`](.github/agents/) | VS Code Copilot custom agent files |
| [`scripts/`](scripts/) | Reusable automation and utility scripts |
| [`docs/`](docs/) | Guides, protocols, and best practice documentation |

---

## Architecture

**dogma** operates as a **two-surface system**:

1. **Permanent substrate** — committed files encoding institutional knowledge:
   - `MANIFESTO.md` (core philosophy)
   - `AGENTS.md` (operational constraints)
   - `.github/agents/` (agent role files)
   - `scripts/` (automation and enforcement)
   - `docs/guides/` (workflow documentation)

2. **MCP enforcement layer** — runtime toolset for validating, scaffolding, and routing:
   - Substrate health checks (`check_substrate`)
   - Agent file validation (`validate_agent_file`)
   - Research synthesis validation (`validate_synthesis`)
   - Session scratchpad management (`prune_scratchpad`)
   - BM25 corpus queries (`query_docs`)
   - Local-first inference routing (`route_inference_request`)

The substrate encodes what to do; the MCP layer enforces it at runtime.

---

## Core Principles

### 1. Endogenous-First

Scaffold from existing system knowledge — do not author from scratch in isolation. Every new file, agent, or script should derive from what the system already knows about itself.

### 2. Programmatic-First

If you have performed a task twice interactively, the third time is a script. Repeated or automatable tasks must be encoded as committed scripts or automation before being performed again by hand. See [`docs/guides/programmatic-first.md`](docs/guides/programmatic-first.md).

### 3. Documentation-First

Every change to a workflow, agent, or script must be accompanied by clear documentation. The docs folder is as important as the code.

### 4. Local Compute First

Prefer running locally. Minimize token usage by encoding knowledge as scripts, caching context, and using local models where possible. See the [Running Locally](docs/guides/local-compute.md) guide.

---

## MCP Toolset

The dogma MCP server exposes 13 governance tools. Connect via VS Code MCP integration, Claude Desktop, or any MCP client.

| Tool | Purpose |
|------|--------|
| `check_substrate` | Run at session start to validate repo health |
| `validate_agent_file` | Check `.agent.md` compliance before committing |
| `validate_synthesis` | Verify D4 research doc schema before archiving |
| `scaffold_agent` | Create new agent stub from template |
| `scaffold_workplan` | Create new `docs/plans/` skeleton |
| `run_research_scout` | Fetch and cache external URLs (SSRF-safe) |
| `query_docs` | BM25 search over full docs corpus |
| `prune_scratchpad` | Initialize or inspect session scratchpad |
| `route_inference_request` | Route to local or external providers (Local-Compute-First) |
| `normalize_path` | Cross-platform path normalization |
| `resolve_env_path` | Env-var path resolution with defaults |
| `detect_user_interrupt` | Check for STOP/ABORT signals before phase actions |
| `get_trace_health` | Return JSONL trace capture health counters |

See [mcp_server/README.md](mcp_server/README.md) for setup and tool reference.

---

## Quick Start

### Adopt dogma in your project

Use dogma as a cookiecutter template or run the adoption wizard:

```bash
# Option 1: cookiecutter
cookiecutter gh:EndogenAI/dogma

# Option 2: adoption wizard (interactive)
cd /path/to/your-repo
uv run python /path/to/dogma/scripts/adopt_wizard.py
```

For full fork initialization, see [Product Fork Initialization Guide](docs/guides/product-fork-initialization.md).

### Contribute to dogma

Fork this repo, create a feature branch, and open a PR. See [CONTRIBUTING.md](CONTRIBUTING.md) for commit conventions and pre-commit setup.

### Using the Agent Fleet

The `.github/agents/` directory contains VS Code Copilot custom agents. To use them:

1. Open this repo (or any consuming repo that references these agents) in VS Code
2. Open Copilot Chat
3. Use `@<agent-name>` to invoke any agent in the fleet

See [`docs/guides/agents.md`](docs/guides/agents.md) for the complete guide.

### Running Scripts

All scripts are invoked via `uv run`:

```bash
# Initialize a scratchpad session file for today
uv run python scripts/prune_scratchpad.py --init

# Start the scratchpad watcher (auto-annotates session files on change)
uv run python scripts/watch_scratchpad.py
```

See [`scripts/README.md`](scripts/README.md) for the full catalog.

---

## File Directory

```
.github/
  agents/                  # VS Code Copilot custom agent files (.agent.md)
    AGENTS.md              # Agent authoring rules and conventions
    README.md              # Agent fleet catalog
    executive-scripter.agent.md
    executive-automator.agent.md
  ISSUE_TEMPLATE/          # GitHub issue templates
  pull_request_template.md

docs/
  glossary.md              # Canonical definitions for all key project terminology
  guides/
    agents.md              # How to author and use agents
    programmatic-first.md  # The programmatic-first principle
    session-management.md  # Cross-agent scratchpad and session protocols
    local-compute.md       # Running locally and reducing token usage

scripts/
  README.md                # Script catalog
  prune_scratchpad.py      # Scratchpad session file manager
  watch_scratchpad.py      # File watcher for auto-annotating session files

AGENTS.md                  # Root agent guidance (programmatic-first, commit discipline)
CONTRIBUTING.md            # Contribution guidelines
MANIFESTO.md               # Endogenic development philosophy and dogma
```

---

## MCP Dashboard

<!-- TODO: Add dashboard screenshot/GIF here -->

A browser dashboard for visualising MCP tool call telemetry from `.cache/mcp-metrics/tool_calls.jsonl`.

**Quick start**:
```bash
uv sync --extra web
uv run --extra web python scripts/start_dashboard.py
```
Then open `http://localhost:5173`.

- **Overview tab** — total invocations, error rate %, avg latency
- **Tools tab** — per-tool breakdown with latency and error stats
- **Errors tab** — tools with non-zero error counts
- **Sidebar** — real-time LIVE/STALE/ERROR connection status

Offline fallback: dashboard loads from bundled fixture when sidecar is unreachable.
See [mcp_server/README.md](mcp_server/README.md) and [docs/guides/mcp-dashboard.md](docs/guides/mcp-dashboard.md) for full docs.

---

## Scratchpad Working Memory

Every agent session writes to `.tmp/<branch>/<date>.md` — an **inspectable, exportable, portable working memory** substrate that persists phase outputs, audit trails, and telemetry across compaction events and multi-day sprints. Query prior sessions with `uv run python scripts/query_sessions.py "<keyword>"`, export to JSON/YAML with `scripts/export_scratchpad.py`, and link session events to commits via `scripts/log_session_event.py`. See [docs/guides/scratchpad-architecture.md](docs/guides/scratchpad-architecture.md) for the full architecture guide.

---

## Community

- **Discussions** — [github.com/EndogenAI/dogma/discussions](https://github.com/EndogenAI/dogma/discussions)
- **Contributing** — See [CONTRIBUTING.md](CONTRIBUTING.md) for commit conventions and workflow
- **Code of Conduct** — See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) (aligned with [MANIFESTO.md](MANIFESTO.md) values)

---

## Related

- [AccessiTech/EndogenAI](https://github.com/AccessiTech/EndogenAI) — the experimental MCP framework where these patterns were pioneered
- [PR #41: Programmatic-First Principle](https://github.com/AccessiTech/EndogenAI/pull/41) — the defining PR for the programmatic-first workflow
- [Issue #35: Running Locally](https://github.com/AccessiTech/EndogenAI/issues/35) — the priority issue that inspired this repo

---

## License

Apache 2.0 — see [`LICENSE`](LICENSE).