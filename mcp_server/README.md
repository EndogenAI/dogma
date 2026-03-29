# dogma MCP Server

Exposes the dogma governance toolset as an [MCP](https://modelcontextprotocol.io/) server
using [FastMCP](https://github.com/jlowin/fastmcp). Provides 13 tools for validating,
scaffolding, researching, managing sessions, routing inference, and normalizing cross-platform paths within the dogma repository.

---

## Tools

| Tool | Description |
|------|-------------|
| `validate_agent_file` | Validate a `.agent.md` file against AGENTS.md constraints |
| `validate_synthesis` | Validate a D4 synthesis doc before archiving |
| `check_substrate` | Full CRD substrate health check |
| `scaffold_agent` | Scaffold a new `.agent.md` stub from template |
| `scaffold_workplan` | Scaffold a new `docs/plans/` workplan from template |
| `run_research_scout` | Fetch and cache an external URL (SSRF-safe) |
| `query_docs` | BM25 query over the dogma documentation corpus |
| `prune_scratchpad` | Initialise or inspect the session scratchpad |
| `detect_user_interrupt` | **Per-phase** — check for user STOP/ABORT/CANCEL signals before any phase action; returns `interrupted: true` if detected |
| `route_inference_request` | Route inference requests to local or external providers based on model_id (Local-Compute-First) |
| `get_trace_health` | Return live JSONL trace capture health counters (write_success_count, write_fail_count, jsonl_exists) |

---

## Cross-Platform Tools

| Tool | Description | Inputs | Output |
|------|-------------|--------|--------|
| `normalize_path` | Normalize a path string cross-platform, expanding env-var tokens (`$HOME`, `$PWD`) via `os.path.expandvars` then `pathlib.Path` | `path_str: str` | Normalized path string |
| `resolve_env_path` | Read an env-var expected to hold a path, normalize it; returns `default` if unset | `key: str`, `default: str = ""` | Normalized path or default |

---

## Inference Routing

| Tool | Description | Inputs | Output |
|------|-------------|--------|--------|
| `route_inference_request` | Route inference request to appropriate provider; prefers local providers (Local-Compute-First principle) | `prompt: str`, `model_id: str`, `max_tokens: int = 512`, `temperature: float = 0.7` | `{"ok": bool, "provider": str \| None, "endpoint": str \| None, "local": bool, "cost_tier": str \| None, "response": str \| None, "errors": list[str]}` |

Reads provider configuration from `data/inference-providers.yml`. Returns routing metadata only; does not execute the request.

---

## MCP Dashboard

Visualise MCP tool call telemetry from `.cache/mcp-metrics/tool_calls.jsonl` in a
browser dashboard.

**Quick start**: `uv run --extra web python scripts/start_dashboard.py` — opens the Svelte SPA at
`http://localhost:5173` and the FastAPI sidecar at `http://localhost:8000`.

See [docs/guides/mcp-dashboard.md](../docs/guides/mcp-dashboard.md) for the full setup
guide, tab descriptions, and offline mode.

## Live Trace Capture

Every tool call routed through `_run_with_mcp_telemetry()` appends a JSONL record to
`.cache/mcp-metrics/tool_calls.jsonl`.

Record shape:

```json
{"tool_name": "check_substrate", "timestamp_utc": "2026-03-29T...", "latency_ms": 42.1, "is_error": false, "error_type": null, "source": "live", "tool_version": "0.1.0.0"}
```

`tool_version` format is `{pkg_version}.{BRANCH_COUNTER}` from `mcp_server/_version.py`.
`BRANCH_COUNTER` must be `0` before merging to `main`.

Migration: run `uv run python scripts/migrate_tool_calls.py` once to archive the 800
synthetic seed records before enabling live capture.

Design rationale: [docs/research/mcp-live-trace-design.md](../docs/research/mcp-live-trace-design.md).

---

## Prerequisites

```bash
# Install the mcp optional dependency group
uv sync --extra mcp --extra web
```

Requires Python 3.10+ (mcp SDK constraint).

---

## Claude Desktop Setup

Add to `~/.claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "dogma-governance": {
      "command": "uv",
      "args": ["run", "python", "-m", "mcp_server.dogma_server"],
      "cwd": "/absolute/path/to/your/dogma-clone"
    }
  }
}
```

Restart Claude Desktop after saving. The server appears under **Tools** in the sidebar.

---

## Cursor Setup

Add to `.cursor/mcp.json` (project-scoped) or `~/.cursor/mcp.json` (global):

```json
{
  "mcpServers": {
    "dogma-governance": {
      "command": "uv",
      "args": ["run", "python", "-m", "mcp_server.dogma_server"],
      "cwd": "/absolute/path/to/your/dogma-clone"
    }
  }
}
```

---

## VS Code + GitHub Copilot Setup

Add to `.vscode/mcp.json`:

```json
{
  "servers": {
    "dogma-governance": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "python", "-m", "mcp_server.dogma_server"]
    }
  }
}
```

---

## Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Default | Description |
|----------|---------|-------------|
| `DOGMA_MCP_PORT` | `8000` | Port for HTTP transport mode (if using SSE/HTTP) |
| `DOGMA_MCP_AUTH_TOKEN` | _(empty)_ | Optional bearer token for HTTP transport auth |

The default transport is **stdio**, which does not use `DOGMA_MCP_PORT`. These variables
are reserved for future HTTP transport support.

---

## Security Model

- **Path traversal protection**: all file path arguments are resolved and checked against
  `REPO_ROOT` before any script is invoked. Paths outside the repo root are rejected.
- **SSRF protection**: `run_research_scout` validates URLs before fetching — blocks
  RFC 1918 private ranges, loopback, IPv6 link-local, and non-https schemes.
- **Subprocess isolation**: all tools invoke existing dogma scripts via `sys.executable`
  with an explicit argument list (no `shell=True`). Environment is inherited from the
  launched server process.

---

## Running in HTTP Mode (Advanced)

To expose the server over HTTP (e.g. for remote MCP clients):

```bash
DOGMA_MCP_PORT=8000 uv run python -m mcp_server.dogma_server --transport streamable-http
```

> **Note**: HTTP mode is not authenticated by default. Use `DOGMA_MCP_AUTH_TOKEN` and a
> reverse proxy with TLS for production deployments.

---

## Development

```bash
# Run tests
uv run pytest tests/test_mcp_server.py -v

# Lint
uv run ruff check mcp_server/

# Type-check (optional)
uv run mypy mcp_server/
```

---

## Module Reference (Concise)

### `mcp_server/dogma_server.py`
- `mcp`: FastMCP app instance (`dogma-governance`)
- Registers 8 tool functions from `mcp_server/tools/*`

### `mcp_server/_security.py`
- `validate_repo_path(file_path: str) -> Path`
  - Rejects paths outside repository root (path traversal guard)
- `validate_url(url: str) -> str`
  - Enforces https-only and blocks private/loopback/link-local targets (SSRF guard)

### `mcp_server/tools/validation.py`
- `validate_agent_file(file_path: str) -> dict`
  - Runs `scripts/validate_agent_files.py` on a repo-scoped path
- `validate_synthesis(file_path: str, min_lines: int = 80) -> dict`
  - Runs `scripts/validate_synthesis.py` with line threshold
- `check_substrate() -> dict`
  - Runs `scripts/check_substrate_health.py` and returns report summary

### `mcp_server/tools/scaffolding.py`
- `scaffold_agent(name: str, description: str, area: str = "general", posture: str = "readonly") -> dict`
  - Wraps `scripts/scaffold_agent.py` with input validation
- `scaffold_workplan(slug: str, issues: str = "") -> dict`
  - Wraps `scripts/scaffold_workplan.py` for plan skeleton creation

### `mcp_server/tools/research.py`
- `run_research_scout(url: str, force: bool = False) -> dict`
  - URL validation + `scripts/fetch_source.py`
- `query_docs(query: str, scope: str = "all", top_n: int = 5) -> dict`
  - Wraps `scripts/query_docs.py` for BM25 search results

### `mcp_server/tools/scratchpad.py`
- `prune_scratchpad(branch: str = "", dry_run: bool = False) -> dict`
  - Wraps `scripts/prune_scratchpad.py` (`--init`/`--check-only`)
  - Supports explicit branch-targeted daily scratchpad path via `--file`
