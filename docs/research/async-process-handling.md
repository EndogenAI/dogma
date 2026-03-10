---
title: Async Process Handling in Agent Workflows
status: Final
---

# Async Process Handling in Agent Workflows

**Research Question**: How should agents and sub-agents handle async/long-running terminal
processes (e.g., model downloads, Docker container startup, `pytest` runs, `npm install`)
without hanging or silently failing?

**Date**: 2026-03-07 | **Issue**: #7

---

## 1. Executive Summary

Long-running terminal processes are endemic to AI-development workflows. Without explicit
handling, they produce three failure modes:

1. **Silent failure** — process exits non-zero; agent never checks exit code; subsequent
   steps run against a broken state.
2. **Hung session** — agent blocks indefinitely waiting for a background process that has
   already finished or crashed.
3. **Re-discovery burn** — no durable record of what ran; next session re-runs the same
   work from scratch.

The VS Code Copilot agent tool set provides three primitives for terminal interaction:
`run_in_terminal` (blocking or background), `get_terminal_output` (polling snapshot), and
`await_terminal` (blocking wait with timeout). Used correctly these three tools cover all
four async handling patterns documented in §3.

**Key finding**: No async handling guidelines currently exist in `AGENTS.md`. Absent
explicit policy, agents default to indefinite blocking, which produces hung sessions on
operations with unpredictable runtime (model downloads, container health checks). Concrete
timeout defaults and a clear abort policy eliminate this class of failure.

---

## 2. Hypothesis Validation

### H1: Synchronous blocking with a finite timeout is sufficient for most agent operations

**Finding: Confirmed.** The majority of agent-initiated long-running operations
(package installs, pytest suites, container startup) have well-understood upper bounds.
Encoding those bounds as explicit `timeout` values in `run_in_terminal` / `await_terminal`
calls converts an indefinite wait into a deterministic timeout → structured abort.

Caveat: model downloads are unbounded by nature (file size varies, network varies).
These must use a background + poll pattern, not blocking wait.

### H2: "Zero error output" reliably indicates success for terminal commands

**Finding: Refuted.** This is documented as a known failure mode in `AGENTS.md` ("Zero
error output is not confirmation of success"). Network timeouts, output truncation, and
silent API failures all produce clean exits. Exit code checking and explicit status-API
verification are necessary complements to output inspection.

### H3: Observable status APIs (Docker, Ollama, etc.) provide better readiness signals than process output parsing

**Finding: Confirmed.** Polling a `/health` or status CLI command decouples readiness
detection from log format changes and avoids brittle output-string matching. The specific
check commands are catalogued in §4.

### H4: A reusable script wrapper for common long-running operations is warranted

**Finding: Partially confirmed.** Operations in the "model download" and "container
readiness" categories recur across sessions and could benefit from a thin wrapper that
encodes timeout defaults and structured exit codes. Operations like `pytest` and
`npm install` are already well-handled by `run_in_terminal` with a timeout value.
See §8 (Script Candidate Spec) for a bounded scope.

---

## 3. Pattern Catalog

### Pattern 1 — Synchronous Wait with Timeout

**Use when**: The process is expected to complete within a known ceiling. Exit code matters.

**Tool**: `run_in_terminal` with `timeout` (milliseconds) and `isBackground: false`

```json
{
  "command": "uv run pytest tests/ -q",
  "explanation": "Run full test suite",
  "goal": "Verify tests pass",
  "isBackground": false,
  "timeout": 120000
}
```

**After the call**: Check the exit code in the output. A non-zero exit is a hard stop —
do not proceed to subsequent steps. Surface the failure to the user.

**Never**: Omit `timeout` for commands whose runtime is unbounded. Default blocking is
indefinite; VS Code will eventually kill the context window without returning control.

---

### Pattern 2 — Background Launch + Interval Poll

**Use when**: The process is long-running, you need to do other work while it runs, or
runtime is genuinely unbounded (model downloads).

**Tools**: `run_in_terminal` with `isBackground: true` → capture `id` →
loop `get_terminal_output` with a backoff interval.

**Algorithm**:
1. Launch with `isBackground: true`. Capture the returned terminal `id`.
2. Wait an initial delay appropriate to the operation (see §5).
3. Call `get_terminal_output(id)`. Parse output for a success marker or error marker.
4. If neither found and `attempts < MAX_ATTEMPTS`, wait `INTERVAL_SECONDS` and repeat.
5. On success marker: proceed. On error marker: abort and surface. On max attempts: abort.

**Retry cap**: `MAX_ATTEMPTS = 10` with `INTERVAL_SECONDS = 30` covers most operations
(5 minutes total polling window). Adjust initial delay per operation type (§5).

**Polling markers**:

| Operation | Success marker | Error marker |
|-----------|---------------|--------------|
| `npm install` | `added N packages` | `npm error` |
| `pytest` | `passed` / `no tests ran` | `FAILED` / `ERROR` |
| Docker pull | `Pull complete` / `Status: Downloaded` | `Error response` |
| Ollama pull | `success` | `error` |
| `pip install` / `uv sync` | `Successfully installed` / `Resolved` | `ERROR` |

---

### Pattern 3 — Observable Status API

**Use when**: A service must be running and healthy before the agent proceeds (not just
that the launch command exited zero).

**Tools**: `run_in_terminal` with the service's CLI or HTTP check, inside a poll loop.

**Canonical check commands**:

| Service | Check command | Success indicator |
|---------|--------------|-------------------|
| Docker daemon | `docker info` | exit 0 |
| Docker container | `docker inspect --format '{{.State.Health.Status}}' <name>` | `healthy` |
| Ollama | `ollama list` | exit 0, or `curl -s http://localhost:11434/api/tags` → JSON |
| Ollama model loaded | `curl -s http://localhost:11434/api/tags \| python3 -c "import sys,json; print(any(m['name'].startswith('<model>') for m in json.load(sys.stdin)['models']))"` | `True` |
| Local HTTP service | `curl -sf http://localhost:<port>/health` | exit 0 |
| PostgreSQL | `pg_isready -h localhost -p 5432` | `accepting connections` |
| Redis | `redis-cli ping` | `PONG` |

**Poll wrapper** (pseudo-code for agent reasoning):
```
for attempt in 1..MAX_ATTEMPTS:
    result = run_in_terminal(check_command, timeout=5000, isBackground=false)
    if success_indicator in result.output:
        break
    if attempt == MAX_ATTEMPTS:
        abort("Service did not become healthy after N attempts")
    sleep(INTERVAL_SECONDS)
```

---

### Pattern 4 — VS Code Task `problemMatcher` for Background Readiness

**Use when**: A long-running background task (e.g., a dev server, file watcher) should
signal readiness without the agent polling output manually.

**Mechanism**: Define a `problemMatcher` in `.vscode/tasks.json` whose `background.beginsPattern`
and `background.endsPattern` regex values match log lines from the process. VS Code marks
the task as "active" once the `beginsPattern` fires and "ready" once `endsPattern` fires.

```json
{
  "label": "Start Dev Server",
  "type": "shell",
  "command": "uv run python -m http.server 8080",
  "isBackground": true,
  "problemMatcher": {
    "owner": "custom",
    "pattern": { "regexp": "." },
    "background": {
      "beginsPattern": "Serving HTTP",
      "endsPattern": "Serving HTTP on .+port (\\d+)"
    }
  }
}
```

**Agent perspective**: Use this pattern for persistent services the agent expects to be
running at session start (file watchers, local inference servers). Agents cannot directly
observe VS Code task state — they detect readiness via Pattern 3 (status API check) after
triggering the task.

**Canonical example in this repo**: `Watch Scratchpad` task (`watch_scratchpad.py`) —
documented in `scripts/README.md`. Uses `isBackground: true` and is triggered at session
start. Agents do not wait on it; they assume it is running and detect its effects
(annotated headings) as the success signal.

---

### Pattern 5 — `await_terminal` (Blocking Wait with Timeout)

**Use when**: A background terminal was launched and you want to block until it completes
or until a timeout expires, then branch on the result.

**Tool**: `await_terminal(id, timeout)` — returns output, exit code, or timeout status.

```json
{
  "id": "<terminal-id-from-run_in_terminal>",
  "timeout": 300000
}
```

**Decision tree after `await_terminal` returns**:
- Exit code `0` + expected output → success, proceed
- Exit code non-zero → hard failure, surface to user; do NOT retry automatically
- `timeout` status → operation took longer than ceiling; abort; surface to user with
  the partial output for diagnosis

**Difference from get_terminal_output**: `await_terminal` blocks until completion or
timeout. Use it when you want a clean "done or failed" result and have no parallel work.
Use `get_terminal_output` (Pattern 2) when you want to continue other work while polling.

---

## 4. Observable Status APIs — Extended Reference

See §3 Pattern 3 for canonical check commands per service. Extended notes:

**Ollama**:
- Daemon readiness: `curl -sf http://localhost:11434/` returns `Ollama is running`
- Model availability: `ollama list` and grep for model name
- Load test (model must respond): `ollama run <model> "" --nowordwrap` for a null prompt

**Docker**:
- `HEALTHCHECK` in Dockerfile is the authoritative readiness signal when present
- Containers without `HEALTHCHECK` use `docker inspect .State.Status == running` as a
  weaker proxy (process started, not necessarily ready to serve)
- `docker compose ps` with `--format json` provides structured state across all services

**LM Studio**:
- Exposes OpenAI-compatible API at `http://localhost:1234/v1`
- Readiness check: `curl -sf http://localhost:1234/v1/models` → JSON list

**Local HTTP services (general)**:
- `curl -sf --max-time 3 http://localhost:<port>/health` — fail fast per attempt
- Combine with retry loop; do not use a single long timeout on the HTTP call itself

---

## 5. Timeout Reference Table

Defaults below assume a modern development laptop (M-series Mac or equivalent x86).
All values are **ceilings** (abort if exceeded), not expected durations.

| Operation | Tool | Recommended Timeout | Initial Poll Delay |
|-----------|------|--------------------|--------------------|
| `uv sync` / `pip install` (cached) | Pattern 1 | 60 s | — |
| `uv sync` / `pip install` (cold, network) | Pattern 2 | 5 min total poll | 15 s |
| `npm install` (cached) | Pattern 1 | 90 s | — |
| `npm install` (cold, node_modules absent) | Pattern 2 | 10 min total poll | 30 s |
| `pytest` full suite (< 100 tests) | Pattern 1 | 120 s | — |
| `pytest` full suite (> 500 tests) | Pattern 1 | 600 s | — |
| Docker pull (small, < 500 MB) | Pattern 2 | 5 min total poll | 20 s |
| Docker pull (large, > 2 GB) | Pattern 2 | 30 min total poll | 60 s |
| Docker container startup (no healthcheck) | Pattern 3 | 10 retries × 5 s | 5 s |
| Docker container startup (with healthcheck) | Pattern 3 | 30 retries × 5 s | 5 s |
| Ollama model pull (3B–8B model) | Pattern 2 | 15 min total poll | 60 s |
| Ollama model pull (70B+ model) | Pattern 2 | 90 min total poll | 120 s |
| Ollama daemon startup | Pattern 3 | 10 retries × 3 s | 2 s |
| `git clone` (small repo) | Pattern 1 | 60 s | — |
| `git clone` (large repo / LFS) | Pattern 2 | 10 min total poll | 30 s |
| `uv run pytest` single file | Pattern 1 | 30 s | — |
| `gh` CLI operations | Pattern 1 | 30 s | — |

**How to apply**: If an operation has a well-known ceiling and can run to completion
synchronously, use Pattern 1 and set `timeout` to the ceiling value in milliseconds
(`seconds × 1000`). If the runtime is unbounded or highly variable, use Pattern 2.

---

## 6. Retry and Abort Policy

### When to retry

Retry (once) only when the failure is plausibly transient:
- Network timeout on a fetch/pull operation
- Docker daemon not yet started (retry with a delay)
- A health check returned an intermediate state (e.g., `starting`)

**Maximum retries**: 1 automatic retry after a transient failure. A second failure is
treated as a hard failure and surfaced to the user.

### When to abort immediately (no retry)

- Non-zero exit code from a deterministic operation (`pytest`, `ruff`, `uv lock`)
- `npm error` / `pip` resolution failure — retrying will not fix a dependency conflict
- `await_terminal` returned timeout status after the ceiling was already generous
- The user explicitly set a `--no-retry` flag

### What to surface to the user

When aborting, provide:
1. The command that failed
2. The exit code (if available) or "timeout" if time-exceeded
3. The last N lines of terminal output (as captured by `get_terminal_output`)
4. A suggested next step (e.g., "run `docker info` to verify daemon is running")

Do NOT silently swallow the failure and proceed to the next step.

---

## 7. VS Code Tool Usage Patterns

### `run_in_terminal` — key parameters

| Parameter | Required | Notes |
|-----------|----------|-------|
| `command` | yes | Shell command string |
| `explanation` | recommended | Shown to user before execution |
| `goal` | recommended | Short label for the operation |
| `isBackground` | yes | `false` for blocking; `true` for background launch |
| `timeout` | yes (blocking) | Milliseconds; omitting = indefinite block (avoid) |

**Always set `timeout` for blocking calls.** An omitted timeout means the agent will block
until the VS Code process terminates or the context window is exhausted.

### `get_terminal_output` — usage

- Returns a snapshot of output collected so far; safe to call repeatedly
- Does not block; returns immediately with whatever output exists
- Use inside a poll loop (Pattern 2) with an explicit sleep between calls
- Output may be truncated for very verbose processes; use `tail -n 50` in the command
  itself to limit noise

### `await_terminal` — usage

- Blocks until the background terminal exits or `timeout` milliseconds elapse
- Returns: `{ output, exitCode }` on completion; `{ output, timeout: true }` on timeout
- Always handle the timeout case explicitly — do not assume exit means success
- Load this deferred tool before use: search for `await_terminal` in tool registry first

---

## 8. Script Candidate Spec (D3)

### `scripts/wait_for_service.py`

**Purpose**: Thin wrapper that polls a service check command at a configurable interval
until success or timeout. Encodes the timeout defaults from §5 for common services.

**Inputs** (CLI flags):
- `--check <cmd>` — shell command to run as the readiness check (must exit 0 on success)
- `--service <name>` — named service preset (ollama, docker, http); loads defaults from a
  lookup table; overridden by explicit flags
- `--timeout <seconds>` — total polling ceiling (default: 300)
- `--interval <seconds>` — seconds between poll attempts (default: 5)
- `--success-pattern <regex>` — optional: require output to match regex in addition to exit 0
- `--dry-run` — print resolved config and exit without polling

**Outputs**:
- Exit 0 — service became ready within timeout
- Exit 1 — timeout exceeded; last check output written to stderr
- Exit 2 — configuration error (unknown preset, invalid arguments)

**Usage examples**:
```bash
# Wait for Ollama daemon
uv run python scripts/wait_for_service.py --service ollama --timeout 30

# Wait for a custom HTTP service with a 2-minute ceiling
uv run python scripts/wait_for_service.py \
    --check "curl -sf http://localhost:8080/health" \
    --timeout 120 --interval 5

# Wait for Docker container
uv run python scripts/wait_for_service.py \
    --check "docker inspect --format '{{.State.Health.Status}}' mycontainer" \
    --success-pattern "healthy" \
    --timeout 60
```

**Tests required**:
- `test_wait_for_service.py` covering: success on first attempt, success after N attempts,
  timeout exceeded, check command non-zero exit, dry-run output, preset lookup, invalid args

**Implementation note**: This is a spec only — do not implement until issue #7 is closed
and a dedicated scripting session is scheduled. The spec is included here so the
Executive Scripter agent has a bounded, pre-researched scope.

---

## 9. Recommendations

1. **Add `timeout` to every `run_in_terminal` blocking call** — treat omission as a bug.
   Default ceiling: 120 s unless the operation type warrants a higher value (§5).

2. **Use Pattern 2 (background + poll) for model downloads** — these are the only class
   of operations with genuinely unbounded runtime in this fleet.

3. **Verify post-process state, not just exit code** — for service startups, always follow
   launch with a Pattern 3 health check. Zero exit from a `docker compose up` does not
   mean containers are healthy.

4. **Cap automatic retries at 1** — more retries without diagnosis compound failures and
   burn tokens on a session that cannot succeed.

5. **Implement specialized polling scripts** — concrete example: [`scripts/wait_for_github_run.py`](../../scripts/wait_for_github_run.py)
   encodes Pattern 2 for GitHub Actions runs. Use this as a template for other operations
   with recurrent polling needs (Ollama, Docker, etc.).

6. **Add async handling guidelines to `AGENTS.md`** — the root file is the authoritative
   constraint source for all agents; per-instance reinvention of timeout values is the
   failure mode this research eliminates.
