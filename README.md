# DogmaMCP

> Governance that lives in code, rooted in compliance docs - encoded, sovereignty sustained.

[![Tests](https://github.com/EndogenAI/dogma/actions/workflows/tests.yml/badge.svg)](https://github.com/EndogenAI/dogma/actions/workflows/tests.yml)
[![Docs](https://github.com/EndogenAI/dogma/actions/workflows/docs.yml/badge.svg)](https://endogenai.github.io/dogma/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Version](https://img.shields.io/github/v/tag/EndogenAI/dogma?label=version)](https://github.com/EndogenAI/dogma/releases)

A governance framework that embeds organizational constraints into AI workflows — for **endogenic / agentic** development

> **Endogenic development** is the practice of building AI-assisted systems from the inside out — scaffolding from existing knowledge, encoding operational wisdom as scripts and agents, and letting the system grow intelligently from a morphogenetic seed rather than through vibe-driven prompting.

---

## Contents

- [What Is This Repo?](#what-is-this-repo)
- [Why DogmaMCP?](#why-dogmamcp)
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

**DogmaMCP** is a governance framework and MCP server that embeds organizational values directly into AI agent workflows — ensuring AI systems operate within your constraints by design, not by policy alone.

Instead of relying on post-hoc audits or manual oversight, DogmaMCP encodes your principles, conventions, and constraints as executable substrate: agent role files, validation scripts, and runtime enforcement tools that agents read and obey before every action.

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

## Why DogmaMCP?

### The Problem

AI coding agents are powerful, but they often violate organizational values in subtle ways:
- Rewriting code that breaks established conventions
- Introducing dependencies that conflict with security policies
- Generating documentation that misrepresents product positioning
- Bypassing governance constraints through prompt manipulation

Post-hoc review catches mistakes, but at the cost of wasted cycles, broken trust, and accumulated technical debt.

### The Solution

DogmaMCP shifts values enforcement from the **policy layer** (rules written in docs that agents may ignore) to the **architecture layer** (constraints enforced in legible guardrails, and code enforcing agent behavior).

Your principles become executable:
- **Agent role files** that define authority boundaries and escalation paths
- **Validation scripts** that gate commits before they reach version control
- **MCP tools** that enforce conventions at runtime (e.g., path safety, schema compliance)

### Key Benefits

| Benefit | What It Means |
|---------|---------------|
| **Sovereignty** | Your values stay in your repo — no external policy servers or vendor-controlled guardrails |
| **Auditability** | Every agent decision is logged to inspectable scratchpad files with full context trails |
| **Portability** | Fork, customize, and adopt in minutes — no platform lock-in or API dependencies |
| **Composability** | Mix and match agent roles, validation rules, and MCP tools to fit your workflow |

### Use Cases

**Regulated industries**: Encode compliance constraints as pre-commit hooks: `no_phi_in_logs.py` blocks commits containing patient identifiers, `soc2_data_retention.py` enforces log retention policies

**Open-source maintainers**: Prevent agents from introducing unlicensed dependencies or violating contribution guidelines through automated substrate checks.

**Product teams**: Align agent-generated documentation with brand positioning by encoding tone, terminology, and messaging guardrails as agent role files.

---

## Architecture

**DogmaMCP** is an **infrastructural AI harness** built from four interlocking substrates. Together, they form a system where the whole is greater than the sum of its parts — each substrate reinforces the others, creating a governance framework that embeds organizational values directly into AI workflows.

### The Four-Substrate Model

The architecture distinguishes **EndogenAI** (the open-source methodology and community advancing endogenic development practices) from **dogmaMCP** (the technical harness that implements those practices). DogmaMCP consists of four substrates:

#### 1. Policy Docs

The client's dogma — values, principles, and constraints encoded as policy documentation.

**Examples:** `MANIFESTO.md` (core axioms: Endogenous-First, Algorithms Before Tokens, Local Compute-First), `AGENTS.md` (operational constraints for all agents), `CONTRIBUTING.md` (contributor guidance).

**Purpose:** Establish what matters and why. Policy docs are the constitutional layer — they define the system's identity and values before any code runs.

#### 2. Design / Technical Docs

The client's initial extension of dogma — connecting policy to implementation by documenting workflows, conventions, and technical patterns. This substrate establishes the **endogenous foundation** by encoding how principles translate into practice.

**Examples:** `docs/guides/` (workflow documentation), `docs/toolchain/` (CLI tool references), `docs/decisions/` (ADRs documenting design choices).

**Purpose:** Bridge abstract principles and concrete execution. Design docs answer: *"How do we apply our values in this specific context?"*

#### 3. Agent Files

Text-based guardrail information that AI agents **reference before every action** — a combination of verbal instructions, YAML-structured metadata, and BDI (Beliefs-Desires-Intentions) sections that define role boundaries, tool restrictions, and escalation paths.

**Examples:** `.github/agents/*.agent.md` (Custom Agent role files), `.github/skills/*.md` (reusable workflow procedures), per-directory `AGENTS.md` redirection notices.

**Purpose:** Make governance **legible** to AI systems. Agent files encode *who does what* and *how tasks are done* in a format agents read natively — turning policy into operational behavior.

#### 4. Enforcement Scripts

Automation integrated into the MCP server or running independently — encodes dogmatic adherence as deterministic, repeatable operations rather than interactive repetition. These scripts gate commits, validate schemas, and enforce conventions programmatically.

**Examples:** `scripts/validate_agent_files.py` (CI gate on agent file compliance), `scripts/validate_synthesis.py` (research doc schema enforcement), pre-commit hooks (ruff format, no-heredoc-writes), MCP server tools (`check_substrate`, `validate_agent_file`).

**Purpose:** Shift enforcement from **policy layer** (rules written in docs that agents may ignore) to **architecture layer** (constraints enforced in code). This is Algorithms Before Tokens in action: encode the rule once, enforce it deterministically.

### How the Substrates Work Together

The four substrates form a reinforcing cycle:

1. **Policy Docs** define values and constraints
2. **Design Docs** translate those values into documented workflows
3. **Agent Files** make workflows legible and actionable for AI systems
4. **Enforcement Scripts** validate adherence programmatically at runtime and commit-time

When a violation occurs, it surfaces at multiple layers:
- An agent reads its role file (Substrate 3) and sees the constraint
- A pre-commit hook (Substrate 4) blocks the violating commit
- The policy doc (Substrate 1) is updated to clarify the constraint for future sessions
- The design doc (Substrate 2) documents the failure mode and corrective pattern

This is governance that lives in code, rooted in compliance docs — **encoded, sovereignty sustained.**

### MCP Enforcement Layer

The MCP server exposes governance tools that span all four substrates:

| Tool | Substrate(s) | Purpose |
|------|-------------|---------|
| `check_substrate` | All four | Validate repo health at session start |
| `validate_agent_file` | 3 (Agent Files) | Check `.agent.md` compliance before commit |
| `validate_synthesis` | 2 (Design Docs) | Verify research doc schema |
| `scaffold_agent` | 3 (Agent Files) | Create new agent stub from template |
| `query_docs` | 1, 2 (Policy + Design) | BM25 search over full docs corpus |
| `route_inference_request` | 4 (Enforcement) | Local-first inference routing |

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

### Adopt DogmaMCP in Your Project (🚧 WIP)

**Prerequisites**: Python 3.11+, [uv](https://github.com/astral-sh/uv) installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)

Two paths to adoption:

```bash
# Option 1: Cookiecutter template (recommended for new projects)
uvx cookiecutter gh:EndogenAI/dogma

# Option 2: Adoption wizard (recommended for existing repos)
cd /path/to/your-repo
uv run python /path/to/dogma/scripts/adopt_wizard.py
```

The adoption wizard interactively scaffolds agent files, validation scripts, and MCP server configuration tailored to your project's structure.

For full fork initialization guidance, see [Product Fork Initialization Guide](docs/guides/product-fork-initialization.md).

### Contribute to DogmaMCP

Contributions welcome! Fork this repo, create a feature branch, and open a PR. See [CONTRIBUTING.md](CONTRIBUTING.md) for commit conventions and pre-commit setup.

### Using the Agent Fleet

DogmaMCP ships with 15+ custom agent role files for VS Code Copilot. To use them:

1. Open a repo that has adopted DogmaMCP (or this repo itself) in VS Code
2. Open Copilot Chat
3. Invoke any agent with `@<agent-name>` (e.g., `@executive-scripter`)

Each agent operates within defined authority boundaries and handoff paths, preventing scope creep and unauthorized actions.

See [`docs/guides/agents.md`](docs/guides/agents.md) for the complete agent catalog and authoring guide.

### Running Validation Scripts

All scripts use `uv run` for deterministic environment management:

```bash
# Initialize a session scratchpad (portable working memory)
uv run python scripts/prune_scratchpad.py --init

# Start the scratchpad watcher (auto-annotates headings with line ranges)
uv run python scripts/watch_scratchpad.py

# Validate agent files before committing
uv run python scripts/validate_agent_files.py --all
```

See [`scripts/README.md`](scripts/README.md) for the full script catalog.

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

> **Note**: Dashboard visual (screenshot/GIF) deferred post-W2. See [mcp_server/README.md](mcp_server/README.md) for full setup and feature documentation.

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
- **Security** — Report vulnerabilities per [SECURITY.md](SECURITY.md)
- **Code of Conduct** — See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) (aligned with [MANIFESTO.md](MANIFESTO.md) values)

---

## Related

- [AccessiTech/EndogenAI](https://github.com/AccessiTech/EndogenAI) — the experimental MCP framework where these patterns were pioneered
- [PR #41: Programmatic-First Principle](https://github.com/AccessiTech/EndogenAI/pull/41) — the defining PR for the programmatic-first workflow
- [Issue #35: Running Locally](https://github.com/AccessiTech/EndogenAI/issues/35) — the priority issue that inspired this repo

---

## License

Apache 2.0 — see [`LICENSE`](LICENSE).