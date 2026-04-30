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

## Browser Inspector Integration (Sprint 23)

Sprint 23 Phase 3 added a browser-local inspector facade in
[web/src/lib/mcp-server.ts](../web/src/lib/mcp-server.ts) with five tools (four inspector tools plus one baseline debug tool):

- `query_dom`
- `get_console_logs`
- `get_component_state`
- `trigger_action`
- `ping` (baseline/debug connectivity check)

Current posture:
- Tool logic is implemented and invocable in-browser.
- The FastAPI sidecar exposes a network MCP transport endpoint
  (`/mcp`, `/mcp/handshake`), allowing these tools to be discovered as a
  separate VS Code MCP server entry when configured as an MCP server.

Use the session guide for setup and invocation patterns:
- [docs/guides/dogma-browser-inspector.md](../docs/guides/dogma-browser-inspector.md)

Reference limitation and validation notes:
- [docs/guides/mcp-dashboard.md#vs-code-mcp-client-status-phase-4](../docs/guides/mcp-dashboard.md#vs-code-mcp-client-status-phase-4)
- [docs/mcp/api-reference.md#browser-inspector-facade-phase-3](../docs/mcp/api-reference.md#browser-inspector-facade-phase-3)

## Live Trace Capture

Every tool call routed through `_run_with_mcp_telemetry()` appends a JSONL record to
`.cache/mcp-metrics/tool_calls.jsonl`.

Record shape:

```json
{"tool_name": "check_substrate", "timestamp_utc": "2026-03-29T...", "latency_ms": 42.1, "is_error": false, "error_type": null, "error_message": null, "source": "live", "tool_version": "0.1.0.0"}
```

For failed calls, `error_type` records the coarse failure class (`tool_error`,
`RuntimeError`, etc.) and `error_message` stores a compact summary of the tool's
structured `errors` payload or the raised exception text. This makes the trace
log diagnostically useful without requiring a separate log join.

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

---

## Troubleshooting

### MCP Server Not Appearing in Client

**Symptoms**: Tools don't appear in Claude Desktop, Cursor, or VS Code after configuring `mcp.json`.

**Solutions**:
1. **Verify configuration path**:
   - Claude Desktop: `~/.claude/claude_desktop_config.json` (not `.claude_desktop_config.json`)
   - Cursor: `.cursor/mcp.json` (project) or `~/.cursor/mcp.json` (global)
   - VS Code: `.vscode/mcp.json` (project-scoped)
2. **Check absolute path in `cwd`**: Use `pwd` in your dogma clone to get the absolute path — relative paths may not resolve correctly
3. **Restart the client**: After saving config, fully restart Claude Desktop, Cursor, or VS Code (not just reload window)
4. **Verify `uv` is in PATH**: Run `which uv` — if not found, install with `pip install uv` or `brew install uv`
5. **Check Python version**: MCP SDK requires Python ≥3.10. Run `python --version` or `uv run python --version`

### Dashboard Won't Start

**Symptoms**: `uv run --extra web python scripts/start_dashboard.py` fails or hangs.

**Solutions**:
1. **Install web dependencies**: Run `uv sync --extra web` first
2. **Port already in use**: Check if port 8000 or 5173 is occupied:
   ```bash
   lsof -i :8000
   lsof -i :5173
   ```
   Kill the occupying process or change ports via environment variables
3. **Node.js version**: Dashboard requires Node 20. Check with `node --version` — install or switch with `nvm use 20` if needed
4. **npm dependencies**: If Vite fails to start, run:
   ```bash
   cd web
   npm install
   npm run dev
   ```

### Dashboard Shows "Offline — showing cached data"

**Symptoms**: Dashboard loads but displays an offline banner.

**Solutions**:
1. **Check sidecar health**: Run `curl -sf http://127.0.0.1:8000/api/health` — should return `{"status": "healthy"}`
2. **CORS origins mismatch**: If running dashboard from a non-standard origin, set `WEBMCP_CORS_ORIGINS`:
   ```bash
   export WEBMCP_CORS_ORIGINS="http://localhost:5173"
   uv run --extra web python scripts/start_dashboard.py
   ```
3. **Firewall or proxy blocking**: Check if local firewall rules block `localhost:8000` connections

### Tools Return Path Traversal Errors

**Symptoms**: Tool calls fail with an error indicating the path "resolves outside the repository root".

**Solutions**:
1. **Use relative paths**: All file paths must be relative to the repository root (e.g., `docs/plans/file.md`, not `/absolute/path/to/file.md`)
2. **Check symlinks**: MCP server resolves symlinks — ensure requested paths do not traverse through symlinks to locations outside the repo
3. **Repository root detection**: The server determines the repository root from its filesystem location — verify the server is running from the expected repository checkout/path

### Research Scout Blocks Valid URLs

**Symptoms**: `run_research_scout` rejects URLs with "SSRF protection triggered".

**Solutions**:
1. **HTTPS only**: Research scout blocks non-https URLs by default (security constraint)
2. **Private IP ranges blocked**: RFC 1918 private ranges (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), loopback (`127.0.0.0/8`), and IPv6 link-local are blocked to prevent SSRF attacks
3. **No localhost/private-network bypass**: `force=True` does **not** create an exception for localhost, loopback, or private-network URLs; it only forces a re-fetch of a URL that is already allowed
4. **Use a different workflow for local testing**: To test content from a local development server, expose it on a publicly reachable HTTPS URL or validate it outside `run_research_scout`; localhost/private-range targets are intentionally blocked by design

### Dashboard Metrics Don't Update

**Symptoms**: Dashboard loads but tool call counts remain static.

**Solutions**:
1. **Verify live trace capture**: Check if `.cache/mcp-metrics/tool_calls.jsonl` exists and is being written to:
   ```bash
   tail -f .cache/mcp-metrics/tool_calls.jsonl
   ```
2. **Trigger a tool call**: Invoke any MCP tool (e.g., `check_substrate()`) to generate a new record
3. **Migration required**: If you see only synthetic seed data, run:
   ```bash
   uv run python scripts/migrate_tool_calls.py
   ```
   This archives old seed records and enables live capture
4. **SSE connection status**: Check dashboard sidebar — should show `LIVE` badge when stream is connected

---

## See Also

- [docs/guides/mcp-dashboard.md](../docs/guides/mcp-dashboard.md) — Dashboard tab descriptions, offline mode, and configuration
- [docs/decisions/ADR-009-webmcp-architecture.md](../docs/decisions/ADR-009-webmcp-architecture.md) — Architecture rationale for SPA + FastAPI design
- [docs/guides/dogma-browser-inspector.md](../docs/guides/dogma-browser-inspector.md) — Browser inspector facade setup and usage
