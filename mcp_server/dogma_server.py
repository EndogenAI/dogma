"""mcp_server/dogma_server.py — FastMCP server exposing dogma governance tools.

Registers 12 tools via @mcp.tool():
    validate_agent_file      — Validate a .agent.md file against AGENTS.md constraints.
    validate_synthesis       — Validate a D4 synthesis document.
    check_substrate          — Run a full CRD substrate health check.
    scaffold_agent           — Scaffold a new .agent.md stub from template.
    scaffold_workplan        — Scaffold a new docs/plans/ workplan from template.
    run_research_scout       — Fetch and cache an external URL (SSRF-safe).
    query_docs               — BM25 query over the dogma documentation corpus.
    prune_scratchpad         — Initialise or inspect the session scratchpad.
    detect_user_interrupt    — Check whether a user message contains an interruption signal.
    normalize_path           — Normalize a cross-platform path string, expanding env-var tokens.
    resolve_env_path         — Read an env-var expected to hold a path and normalize it.
    route_inference_request  — Route inference requests to local or external providers.

Transport: stdio (default for Claude Desktop / Cursor / VS Code MCP clients).

Usage (standalone):
    uv run python -m mcp_server.dogma_server

Claude Desktop config (~/.claude/claude_desktop_config.json):
    {
      "mcpServers": {
        "dogma-governance": {
          "command": "uv",
          "args": ["run", "python", "-m", "mcp_server.dogma_server"],
          "cwd": "/path/to/dogma"
        }
      }
    }

See mcp_server/README.md for full setup, Cursor config, and environment variables.
"""

from __future__ import annotations

import json
import logging as _logging
import pathlib
import queue
import threading
import time
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from mcp.server.fastmcp import FastMCP

try:
    from opentelemetry import metrics as _otel_metrics
    from opentelemetry import trace as _otel_trace
except ImportError:  # pragma: no cover - optional dependency
    _otel_metrics = None
    _otel_trace = None

from mcp_server._version import TOOL_VERSION as _TOOL_VERSION
from mcp_server.tools.cross_platform_tools import normalize_path as _normalize_path
from mcp_server.tools.cross_platform_tools import resolve_env_path as _resolve_env_path
from mcp_server.tools.inference import route_inference_request as _route_inference_request
from mcp_server.tools.research import query_docs as _query_docs
from mcp_server.tools.research import run_research_scout as _run_research_scout
from mcp_server.tools.scaffolding import scaffold_agent as _scaffold_agent
from mcp_server.tools.scaffolding import scaffold_workplan as _scaffold_workplan
from mcp_server.tools.scratchpad import detect_user_interrupt as _detect_user_interrupt
from mcp_server.tools.scratchpad import prune_scratchpad as _prune_scratchpad
from mcp_server.tools.validation import check_substrate as _check_substrate
from mcp_server.tools.validation import validate_agent_file as _validate_agent_file
from mcp_server.tools.validation import validate_synthesis as _validate_synthesis

_logger = _logging.getLogger(__name__)

_INSTRUCTIONS = """\
You are connected to the dogma governance toolset.

All tools operate against the dogma repository that is running this server.
File paths must be relative to or absolute within the repository root.
URLs passed to run_research_scout must use https:// and resolve to public hostnames.

Governance axioms (MANIFESTO.md):
  1. Endogenous-First — read existing docs before acting
  2. Algorithms-Before-Tokens — prefer deterministic tools over repeated prompting
  3. Local-Compute-First — minimize remote API calls

Common workflow:
  1. check_substrate() — confirm the repository is in a healthy state
  2. query_docs("topic") — find relevant guidance before making changes
  3. validate_agent_file() / validate_synthesis() — validate changes before committing
  4. scaffold_agent() / scaffold_workplan() — create new governance artefacts
  5. prune_scratchpad() — initialise today's session scratchpad for cross-agent handoffs
  6. detect_user_interrupt(message) — check for STOP/ABORT/CANCEL signals before each phase
"""

mcp = FastMCP("dogma-governance", instructions=_INSTRUCTIONS)

# ---------------------------------------------------------------------------
# JSONL trace writer — non-blocking background daemon
# ---------------------------------------------------------------------------

_JSONL_PATH = pathlib.Path(".cache/mcp-metrics/tool_calls.jsonl")
_JSONL_QUEUE: queue.Queue = queue.Queue(maxsize=0)  # unbounded

# Module-level counters — thread-safe for int assignment under CPython GIL
_WRITE_SUCCESS_COUNT: int = 0
_WRITE_FAIL_COUNT: int = 0


def _jsonl_writer(
    jsonl_queue: queue.Queue | None = None,
    jsonl_path: pathlib.Path | None = None,
) -> None:
    """Background daemon: drain _JSONL_QUEUE and append records to JSONL file.

    Counters _WRITE_SUCCESS_COUNT / _WRITE_FAIL_COUNT track write outcomes.
    OSError is logged as WARNING but never propagates to the tool caller.
    """
    global _WRITE_SUCCESS_COUNT, _WRITE_FAIL_COUNT  # noqa: PLW0603
    active_queue = _JSONL_QUEUE if jsonl_queue is None else jsonl_queue
    active_path = _JSONL_PATH if jsonl_path is None else jsonl_path

    active_path.parent.mkdir(parents=True, exist_ok=True)
    while True:
        record = active_queue.get()
        if record is None:  # sentinel — clean shutdown
            break
        try:
            with active_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(record, ensure_ascii=False) + "\n")
            _WRITE_SUCCESS_COUNT += 1
        except OSError as exc:
            _WRITE_FAIL_COUNT += 1
            _logger.warning(
                "mcp-jsonl-writer: write failed (path=%s, error=%s: %s)",
                active_path,
                type(exc).__name__,
                exc,
            )


_writer_thread = threading.Thread(
    target=_jsonl_writer,
    args=(_JSONL_QUEUE, _JSONL_PATH),
    daemon=True,
    name="mcp-jsonl-writer",
)
_writer_thread.start()

_TRACER = _otel_trace.get_tracer("dogma.mcp.server") if _otel_trace else None
_METER = _otel_metrics.get_meter("dogma.mcp.server") if _otel_metrics else None
_OP_DURATION_HISTOGRAM = (
    _METER.create_histogram(
        "mcp.server.operation.duration",
        unit="s",
        description="Duration of MCP tool-call operations in seconds",
    )
    if _METER
    else None
)


def _configure_telemetry() -> None:
    """Configure OTel TracerProvider and MeterProvider based on DOGMA_OTEL_EXPORTER env var.

    DOGMA_OTEL_EXPORTER=otlp (default) — OTLP gRPC exporter to localhost:4317.
    DOGMA_OTEL_EXPORTER=jsonl         — no-op OTel provider; spans go to JSONL only.
    """
    import os

    exporter_mode = os.environ.get("DOGMA_OTEL_EXPORTER", "otlp").lower()
    if exporter_mode == "jsonl" or _otel_trace is None:
        return  # Leave global no-op provider in place; JSONL path handles capture.

    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
    span_exporter = OTLPSpanExporter(endpoint=endpoint, insecure=True)
    tracer_provider = TracerProvider()
    tracer_provider.add_span_processor(BatchSpanProcessor(span_exporter))
    _otel_trace.set_tracer_provider(tracer_provider)

    metric_exporter = OTLPMetricExporter(endpoint=endpoint, insecure=True)
    reader = PeriodicExportingMetricReader(metric_exporter, export_interval_millis=10_000)
    meter_provider = MeterProvider(metric_readers=[reader])
    _otel_metrics.set_meter_provider(meter_provider)

    # Re-bind module-level tracer/meter to the newly configured providers.
    global _TRACER, _METER, _OP_DURATION_HISTOGRAM  # noqa: PLW0603
    _TRACER = _otel_trace.get_tracer("dogma.mcp.server")
    _METER = _otel_metrics.get_meter("dogma.mcp.server")
    _OP_DURATION_HISTOGRAM = _METER.create_histogram(
        "mcp.server.operation.duration",
        unit="s",
        description="Duration of MCP tool-call operations in seconds",
    )


_configure_telemetry()


def _summarize_error_value(value: Any, *, max_items: int = 3, max_chars: int = 240) -> str | None:
    """Return a compact, JSON-safe error summary for trace records."""
    if value is None:
        return None
    if isinstance(value, str):
        return value[:max_chars]
    if isinstance(value, dict):
        message = value.get("message")
        if isinstance(message, str) and message:
            return message[:max_chars]
        try:
            return json.dumps(value, ensure_ascii=False, sort_keys=True)[:max_chars]
        except TypeError:
            return str(value)[:max_chars]
    if isinstance(value, list):
        # Collapse long error lists into a short semicolon-joined summary for JSONL telemetry.
        parts: list[str] = []
        for item in value[:max_items]:
            rendered = _summarize_error_value(item, max_items=1, max_chars=max_chars)
            if rendered:
                parts.append(rendered)
        if not parts:
            return None
        summary = "; ".join(parts)
        if len(value) > max_items:
            summary += f" (+{len(value) - max_items} more)"
        return summary[:max_chars]
    return str(value)[:max_chars]


def _summarize_tool_result_error(result: dict[str, Any]) -> str | None:
    """Return the best available human-readable error summary from a tool result."""
    summary = (
        _summarize_error_value(result.get("errors"))
        or _summarize_error_value(result.get("error"))
        or _summarize_error_value(result.get("message"))
    )
    if summary:
        return summary
    if result.get("ok") is False:
        return "The tool reported a problem but did not include any details."
    return None


def _run_with_mcp_telemetry(tool_name: str, call: Callable[[], dict]) -> dict:
    """Run tool call with MCP semconv span/metric emission when OTel is available."""
    attributes = {
        "gen_ai.tool.name": tool_name,
        "gen_ai.operation.name": "execute_tool",
    }
    started = time.perf_counter()

    if _TRACER:
        with _TRACER.start_as_current_span("mcp.server.execute_tool") as span:
            span.set_attribute("gen_ai.tool.name", tool_name)
            span.set_attribute("gen_ai.operation.name", "execute_tool")
            _trace_is_error: bool = False
            _trace_error_type: str | None = None
            _trace_error_message: str | None = None
            try:
                result = call()
                _trace_is_error = bool(result.get("ok") is False or result.get("errors"))
                _trace_error_type = "tool_error" if _trace_is_error else None
                _trace_error_message = _summarize_tool_result_error(result)
                if _trace_is_error:
                    span.set_attribute("error.type", "tool_error")
                    if _trace_error_message:
                        span.set_attribute("error.message", _trace_error_message)
                return result
            except Exception as exc:
                _trace_is_error = True
                _trace_error_type = type(exc).__name__
                _trace_error_message = str(exc)
                span.set_attribute("error.type", "tool_error")
                span.set_attribute("error.message", _trace_error_message)
                raise
            finally:
                duration_s = time.perf_counter() - started
                if _OP_DURATION_HISTOGRAM:
                    _OP_DURATION_HISTOGRAM.record(duration_s, attributes)
                # Emit the same compact record shape with and without OTel so downstream reports stay uniform.
                _JSONL_QUEUE.put_nowait(
                    {
                        "tool_name": tool_name,
                        "timestamp_utc": datetime.now(UTC).isoformat(),
                        "latency_ms": round(duration_s * 1000, 3),
                        "is_error": _trace_is_error,
                        "error_type": _trace_error_type,
                        "error_message": _trace_error_message,
                        "source": "live",
                        "tool_version": _TOOL_VERSION,
                    }
                )

    _trace_is_error: bool = False
    _trace_error_type: str | None = None
    _trace_error_message: str | None = None
    try:
        result = call()
        _trace_is_error = bool(result.get("ok") is False or result.get("errors"))
        _trace_error_type = "tool_error" if _trace_is_error else None
        _trace_error_message = _summarize_tool_result_error(result)
        return result
    except Exception as exc:
        _trace_is_error = True
        _trace_error_type = type(exc).__name__
        _trace_error_message = str(exc)
        raise
    finally:
        duration_s = time.perf_counter() - started
        if _OP_DURATION_HISTOGRAM:
            _OP_DURATION_HISTOGRAM.record(duration_s, attributes)
        # Keep the fallback path aligned with the traced path for JSONL consumers and tests.
        _JSONL_QUEUE.put_nowait(
            {
                "tool_name": tool_name,
                "timestamp_utc": datetime.now(UTC).isoformat(),
                "latency_ms": round(duration_s * 1000, 3),
                "is_error": _trace_is_error,
                "error_type": _trace_error_type,
                "error_message": _trace_error_message,
                "source": "live",
                "tool_version": _TOOL_VERSION,
            }
        )


# ---------------------------------------------------------------------------
# Validation tools
# ---------------------------------------------------------------------------


@mcp.tool()
def validate_agent_file(file_path: str) -> dict:
    """Validate a .agent.md or SKILL.md file against AGENTS.md encoding constraints.

    Args:
        file_path: Absolute or repo-relative path to the .agent.md or SKILL.md file.

    Returns:
        {"ok": bool, "errors": list[str], "file_path": str}
    """
    return _run_with_mcp_telemetry("validate_agent_file", lambda: _validate_agent_file(file_path))


@mcp.tool()
def validate_synthesis(file_path: str, min_lines: int = 80) -> dict:
    """Validate a D4 research synthesis document before archiving.

    Args:
        file_path: Absolute or repo-relative path to the synthesis Markdown file.
        min_lines: Minimum non-blank line count (default: 80).

    Returns:
        {"ok": bool, "errors": list[str], "file_path": str}
    """
    return _run_with_mcp_telemetry("validate_synthesis", lambda: _validate_synthesis(file_path, min_lines))


@mcp.tool()
def check_substrate() -> dict:
    """Run a full CRD substrate health check (MANIFESTO.md, AGENTS.md, key scripts).

    Returns:
        {"ok": bool, "errors": list[str], "report": str}
    """
    return _run_with_mcp_telemetry("check_substrate", _check_substrate)


# ---------------------------------------------------------------------------
# Scaffolding tools
# ---------------------------------------------------------------------------


@mcp.tool()
def scaffold_agent(
    name: str,
    description: str,
    area: str = "scripts",
    posture: str = "creator",
) -> dict:
    """Scaffold a new .agent.md stub in .github/agents/ using the project template.

    Args:
        name: Display name for the agent (e.g. 'Research Scout').
        description: One-line summary ≤ 200 characters.
        area: Area prefix used in the filename (e.g. 'research').
        posture: Tool posture — 'readonly', 'creator', or 'full'.

    Returns:
        {"ok": bool, "output_path": str | None, "errors": list[str]}
    """
    return _run_with_mcp_telemetry(
        "scaffold_agent",
        lambda: _scaffold_agent(name, description, area, posture),
    )


@mcp.tool()
def scaffold_workplan(slug: str, issues: str = "") -> dict:
    """Scaffold a new docs/plans/<date>-<slug>.md workplan from template.

    Args:
        slug: Dash-separated slug for the workplan (e.g. 'my-feature-sprint').
        issues: Comma-separated issue numbers (e.g. '42,43'). Optional.

    Returns:
        {"ok": bool, "output_path": str | None, "errors": list[str]}
    """
    return _run_with_mcp_telemetry("scaffold_workplan", lambda: _scaffold_workplan(slug, issues))


# ---------------------------------------------------------------------------
# Research tools
# ---------------------------------------------------------------------------


@mcp.tool()
def run_research_scout(url: str, force: bool = False) -> dict:
    """Fetch and cache an external URL via the dogma source cache.

    The URL is SSRF-validated before any network request is made.
    Cached result is stored in .cache/sources/ as distilled Markdown.

    Args:
        url: The https:// URL to fetch and cache.
        force: If True, re-fetch even if the URL is already cached.

    Returns:
        {"ok": bool, "url": str, "cache_path": str | None, "errors": list[str]}
    """
    return _run_with_mcp_telemetry("run_research_scout", lambda: _run_research_scout(url, force))


@mcp.tool()
def query_docs(query: str, scope: str = "all", top_n: int = 5) -> dict:
    """BM25 query over the dogma documentation corpus.

    Args:
        query: The search query string.
        scope: Corpus scope — 'manifesto', 'agents', 'guides', 'research',
               'toolchain', 'skills', or 'all'.
        top_n: Number of top results to return (default: 5).

    Returns:
        {"ok": bool, "results": list[dict], "errors": list[str]}
    """
    return _run_with_mcp_telemetry("query_docs", lambda: _query_docs(query, scope, top_n))


# ---------------------------------------------------------------------------
# Session management tools
# ---------------------------------------------------------------------------


@mcp.tool()
def prune_scratchpad(branch: str = "", dry_run: bool = False) -> dict:
    """Initialise or inspect the session scratchpad for the current branch.

    Creates .tmp/<branch>/<today>.md if it does not exist (--init mode).
    Use dry_run=True to check status without writing.

    Args:
        branch: Branch slug (auto-detected from git if empty).
        dry_run: If True, only checks status without creating or modifying files.

    Returns:
        {"ok": bool, "file_path": str | None, "exists": bool,
         "lines": int | None, "errors": list[str]}
    """
    return _run_with_mcp_telemetry("prune_scratchpad", lambda: _prune_scratchpad(branch, dry_run))


@mcp.tool()
def detect_user_interrupt(message: str) -> dict:
    """Check whether a user message contains an interruption signal.

    Detects: STOP, DO NOT CONTINUE, ABORT, ABORT THIS TASK, CANCEL, PAUSE EXECUTION, HOLD

    Call this before each phase action. If interrupted=True, immediately exit the
    current phase and return control to the user per AGENTS.md § Instruction Hierarchy.

    Args:
        message: The user's most recent chat message to check.

    Returns:
        {"ok": bool, "interrupted": bool, "signal": str | None, "errors": list[str]}
    """
    return _run_with_mcp_telemetry("detect_user_interrupt", lambda: _detect_user_interrupt(message))


# ---------------------------------------------------------------------------
# Cross-platform tools
# ---------------------------------------------------------------------------


@mcp.tool()
def normalize_path(path_str: str) -> dict[str, Any]:
    """Normalize a cross-platform path string, expanding environment-variable tokens.

    Expands tokens such as $HOME and $PWD via os.path.expandvars, then normalizes
    the result using os.path.abspath(os.path.normpath(...)).

    Args:
        path_str: A raw path string, potentially containing env-var tokens.

    Returns:
        Dict following {ok, errors, result} contract.
    """

    def _call() -> dict[str, Any]:
        try:
            res = _normalize_path(path_str)
            return {"ok": True, "errors": [], "result": res}
        except Exception as exc:
            return {"ok": False, "errors": [str(exc)], "result": ""}

    return _run_with_mcp_telemetry("normalize_path", _call)


@mcp.tool()
def resolve_env_path(key: str, default: str = "") -> dict[str, Any]:
    """Read an environment variable expected to hold a path and normalize it.

    If the variable is set and non-empty, expands and normalizes it. If the
    variable is unset or empty, returns `default`.

    Args:
        key: Environment variable name (e.g. 'REPO_ROOT', 'HOME').
        default: Value to return when the variable is not set or is empty.

    Returns:
        Normalized path string, or `default` if the variable is absent/empty.
    """
    return _run_with_mcp_telemetry("resolve_env_path", lambda: _resolve_env_path(key, default))


# ---------------------------------------------------------------------------
# Inference routing
# ---------------------------------------------------------------------------


@mcp.tool()
def route_inference_request(
    prompt: str,
    model_id: str,
    max_tokens: int = 512,
    temperature: float = 0.7,
) -> dict[str, Any]:
    """Route an inference request to the appropriate provider based on model_id.

    Reads data/inference-providers.yml and selects a provider, preferring local
    providers (Local-Compute-First principle). Does not execute the request —
    returns routing metadata only.

    Args:
        prompt: The prompt text to send to the model.
        model_id: Model identifier (e.g., 'llama3.2', 'claude-3-5-haiku-20241022').
        max_tokens: Maximum tokens to generate (default: 512).
        temperature: Sampling temperature 0.0-1.0 (default: 0.7).

    Returns:
        {"ok": bool, "provider": str | None, "endpoint": str | None,
         "local": bool, "cost_tier": str | None, "response": str | None,
         "errors": list[str]}
    """
    return _run_with_mcp_telemetry(
        "route_inference_request",
        lambda: _route_inference_request(prompt, model_id, max_tokens, temperature),
    )


# ---------------------------------------------------------------------------
# Trace capture observability
# ---------------------------------------------------------------------------


@mcp.tool()
def get_trace_health() -> dict:
    """Return live JSONL trace capture health counters.

    Returns:
        {
          "ok": bool,
          "write_success_count": int,
          "write_fail_count": int,
          "jsonl_path": str,
          "jsonl_exists": bool,
                    "errors": list[str],
        }
    """
    return _run_with_mcp_telemetry(
        "get_trace_health",
        lambda: {
            "ok": _WRITE_FAIL_COUNT == 0,
            "write_success_count": _WRITE_SUCCESS_COUNT,
            "write_fail_count": _WRITE_FAIL_COUNT,
            "jsonl_path": str(_JSONL_PATH),
            "jsonl_exists": _JSONL_PATH.exists(),
            "errors": (
                [f"JSONL trace capture has recorded {_WRITE_FAIL_COUNT} write failure(s)."]
                if _WRITE_FAIL_COUNT > 0
                else []
            ),
        },
    )


if __name__ == "__main__":
    mcp.run()
