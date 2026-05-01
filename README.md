# DogmaMCP

> **Values ingrained, sovereignty sustained** — governance framework for endogenous AI workflows

[![Tests](https://github.com/EndogenAI/dogma/actions/workflows/tests.yml/badge.svg)](https://github.com/EndogenAI/dogma/actions/workflows/tests.yml)
[![Coverage](https://codecov.io/gh/EndogenAI/dogma/branch/main/graph/badge.svg)](https://codecov.io/gh/EndogenAI/dogma)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/downloads/)
[![Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

A governance framework that embeds organizational constraints into AI workflows — encoding values, principles, and guardrails as executable substrate so agents operate within your constraints by design, not by policy alone.

**Governance Layer**: [MANIFESTO.md](MANIFESTO.md) • [AGENTS.md](AGENTS.md) | **Quick Start**: [Get Started](#get-started)


---

## Two-Surface Architecture

DogmaMCP consists of two interlocking surfaces that reinforce each other:

**Permanent Substrate** — Encoding layer (MANIFESTO.md, AGENTS.md, scripts/, docs/). Your values and conventions persisted in git, read by every agent before every action. The morphogenetic seed from which all future sessions grow.

**MCP Enforcement Layer** — Runtime tools (MCP server, validation scripts, pre-commit hooks). Executable machinery that prevents agents from violating encoded constraints. Operates on the permanent substrate; designed to fail fast and surface violations immediately.

Together: **substrate + enforcement = governance**. Your principles stay in your repo — no external policy servers, no vendor lock-in. Every agent that reads this repository's AGENTS.md and passes substrate validation operates within your governance boundary.

---

## MCP Toolset

The dogma MCP server exposes 13 governance tools for session management, validation, research, and scaffolding:

| Tool | Purpose | When to Use |
|------|---------|------------|
| `check_substrate` | Full CRD substrate health check | **Session start** — verify repo is healthy before any phase begins |
| `validate_agent_file` | Validate `.agent.md` file against AGENTS.md constraints | Before committing any agent role file |
| `validate_synthesis` | Validate D4 research doc before archiving | Before archiving docs/research/*.md files |
| `scaffold_agent` | Scaffold a new `.agent.md` stub from template | Creating a new custom agent role |
| `scaffold_workplan` | Scaffold a new `docs/plans/` workplan | Multi-phase sessions (≥3 phases or delegations) |
| `run_research_scout` | Fetch and cache external URL (SSRF-safe) | Research phases; pre-warm source cache before web fetches |
| `query_docs` | BM25 semantic search over dogma docs corpus | Before fetching external sources; find what's already documented |
| `prune_scratchpad` | Initialize or inspect session scratchpad | Session start/close; track cross-agent context |
| `detect_user_interrupt` | Check for user STOP/ABORT/CANCEL signals | Before executing any phase action |
| `route_inference_request` | Route inference to local or external providers | Prefer local execution (Local-Compute-First) |
| `normalize_path` | Cross-platform path normalization + env-var expansion | File operations across macOS/Linux/Windows |
| `resolve_env_path` | Read env-var as path and normalize it | Resolving env-vars like `$REPO_ROOT`, `$HOME` to normalized paths |
| `get_trace_health` | Live OTel trace capture telemetry | Observability; validate telemetry pipeline |

**Full documentation**: [mcp_server/README.md](mcp_server/README.md)

---

## MCP Dashboard

Visualize governance telemetry, validation state, and MCP tool invocations in a browser dashboard.

**Key Features**:
- **Tool Call Telemetry** — Track which tools are invoked, when, and success/failure rates
- **Validation Gate Status** — Monitor pre-commit hook runs, agent file compliance, synthesis doc quality
- **Scratchpad Tracking** — View live cross-agent context and session handoff state
- **Phase Telemetry** — Observe workplan phase progression and inter-phase gates
- **Substrate Health** — Real-time CRD health check results + last sync timestamp

**Try it**: `uv run --extra web python scripts/start_dashboard.py` — opens at `http://localhost:5173`

[→ Full Dashboard Docs](mcp_server/README.md#mcp-dashboard)

---

## Get Started

Choose your path:

### Path 1: Use as Template (Quickest)

Adopt dogma as a template for your own endogenic governance framework.

```bash
# Clone and scaffold
cookiecutter gh:EndogenAI/dogma
# Or: uv run python scripts/adopt_wizard.py

cd <your-project>
uv sync
uv run pytest  # verify setup
```

**Next**: Read [docs/guides/getting-started.md](docs/guides/getting-started.md) for step-by-step guide, customization, and example adoption scenarios.

### Path 2: Extend & Contribute

Fork dogma, add features, and submit PRs back to the EndogenAI project.

```bash
git clone https://github.com/EndogenAI/dogma.git
cd dogma
uv sync --extra dev --extra mcp  # Install dev tools (pytest, ruff, pre-commit) + MCP server
uv run pytest

# Create feature branch
git checkout -b feat/your-feature
# Make changes...
git commit -m "feat(docs): describe your change"
git push -u origin feat/your-feature
# Open PR on GitHub
```

**What gets installed:**

| Command | Installs | Use case |
|---------|----------|----------|
| `uv sync` | Base dependencies only (governance scripts, OTel, docs tooling) | Adopters using dogma as a template; don't need dev tools |
| `uv sync --extra dev --extra mcp` | Base + pytest, ruff, pre-commit, MCP server | Contributors; running tests, linting, and MCP server locally |

**Next**: Read [CONTRIBUTING.md](CONTRIBUTING.md) for conventions and review process.

---

## Community

- **GitHub Discussions** — [Ask questions, share patterns](https://github.com/EndogenAI/dogma/discussions)
- **Contributing** — [How to contribute](CONTRIBUTING.md)
- **Code of Conduct** — [Community values](CODE_OF_CONDUCT.md)
- **Contact** — EndogenAI maintainers: [conduct@endogenai.com](mailto:conduct@endogenai.com)

---

## Further Reading

| Document | Purpose |
|----------|---------|
| [MANIFESTO.md](MANIFESTO.md) | Core philosophy and three axioms of endogenic development |
| [AGENTS.md](AGENTS.md) | Operational constraints for all agents working in this repo |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contributor setup, commit discipline, and validation gates |
| [docs/guides/](docs/guides/) | Formalized workflows (session management, MCP setup, agent authoring) |
| [docs/research/](docs/research/) | Research syntheses on governance, AI ethics, and methodology |
| [.github/agents/README.md](.github/agents/README.md) | Agent fleet catalog |

---

## License

[Apache 2.0](LICENSE)