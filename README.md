# EndogenAI Workflows

[![Tests](https://github.com/EndogenAI/Workflows/actions/workflows/tests.yml/badge.svg)](https://github.com/EndogenAI/Workflows/actions/workflows/tests.yml)

The authoritative source for **endogenic / agentic product design and development** workflows, best practices, agent files, and automation scripts.

> **Endogenic development** is the practice of building AI-assisted systems from the inside out — scaffolding from existing knowledge, encoding operational wisdom as scripts and agents, and letting the system grow intelligently from a morphogenetic seed rather than through vibe-driven prompting.

---

## Contents

- [What Is This Repo?](#what-is-this-repo)
- [Core Principles](#core-principles)
- [Quick Start](#quick-start)
- [File Directory](#file-directory)
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
| [`.github/agents/`](.github/agents/) | VS Code Copilot custom agent files |
| [`scripts/`](scripts/) | Reusable automation and utility scripts |
| [`docs/`](docs/) | Guides, protocols, and best practice documentation |

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

## Quick Start

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

## Related

- [AccessiTech/EndogenAI](https://github.com/AccessiTech/EndogenAI) — the experimental MCP framework where these patterns were pioneered
- [PR #41: Programmatic-First Principle](https://github.com/AccessiTech/EndogenAI/pull/41) — the defining PR for the programmatic-first workflow
- [Issue #35: Running Locally](https://github.com/AccessiTech/EndogenAI/issues/35) — the priority issue that inspired this repo

---

## License

Apache 2.0 — see [`LICENSE`](LICENSE).