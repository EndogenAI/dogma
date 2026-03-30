"""FastAPI sidecar for the MCP Web Dashboard.

Provides a working FastAPI application that exposes MCP metrics endpoints,
including a snapshot builder that aggregates per-tool statistics from
`.cache/mcp-metrics/tool_calls.jsonl`.
"""

import asyncio
import json
import pathlib
import statistics
import threading
import time
import uuid
from collections import deque
from concurrent.futures import Future
from datetime import datetime, timezone

try:
    from fastapi import FastAPI, HTTPException, Request, Response  # type: ignore[import-not-found]
    from fastapi.middleware.cors import CORSMiddleware  # type: ignore[import-not-found]
    from fastapi.responses import JSONResponse, StreamingResponse  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover

    class _StubApp:
        def add_middleware(self, *args, **kwargs) -> None:
            return None

        def get(self, *args, **kwargs):
            def _decorator(func):
                return func

            return _decorator

        def post(self, *args, **kwargs):
            def _decorator(func):
                return func

            return _decorator

    class FastAPI(_StubApp):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__()

    class CORSMiddleware:  # type: ignore[no-redef]
        pass

    class HTTPException(Exception):  # type: ignore[no-redef]
        def __init__(self, status_code: int, detail: str) -> None:
            super().__init__(detail)
            self.status_code = status_code
            self.detail = detail

    class Request:  # type: ignore[no-redef]
        async def json(self) -> dict:
            return {}

    class Response:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs) -> None:
            return None

    class JSONResponse:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs) -> None:
            return None

    class StreamingResponse:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs) -> None:
            return None


METRICS_JSONL_PATH = pathlib.Path(__file__).parent.parent / ".cache/mcp-metrics/tool_calls.jsonl"
MCP_PROTOCOL_VERSION = "2025-03-26"
MCP_SERVER_NAME = "dogma-browser-inspector"
MCP_SERVER_VERSION = "0.2.0"
MCP_REQUEST_TIMEOUT_SECONDS = 10.0
MCP_BROWSER_SESSION_TTL_SECONDS = 60.0
MCP_BROWSER_POLL_MAX_SECONDS = 30.0

_TOOL_DEFINITIONS = [
    {
        "name": "ping",
        "title": "Inspector Connectivity Check",
        "description": "Verify that the browser inspector bridge can service tool calls.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "query_dom",
        "title": "Query DOM",
        "description": "Return a bounded summary of elements matching a CSS selector.",
        "inputSchema": {
            "type": "object",
            "properties": {"selector": {"type": "string", "description": "Valid CSS selector to query."}},
            "required": ["selector"],
            "additionalProperties": False,
        },
    },
    {
        "name": "get_console_logs",
        "title": "Get Console Logs",
        "description": "Return recent buffered console entries, optionally filtered by level.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "level": {
                    "type": "string",
                    "enum": ["debug", "info", "log", "warn", "error"],
                    "description": "Optional console level filter.",
                }
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "get_component_state",
        "title": "Get Component State",
        "description": "Return one registered component snapshot or all registered snapshots.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "component": {
                    "type": "string",
                    "description": "Optional component registration key.",
                }
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "trigger_action",
        "title": "Trigger UI Action",
        "description": "Trigger a constrained click or input event against a matched element.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "type": {"type": "string", "enum": ["click", "input"]},
                "selector": {"type": "string"},
                "value": {"type": "string"},
                "eventType": {"type": "string", "enum": ["input", "change", "both"]},
            },
            "required": ["type", "selector"],
            "additionalProperties": False,
        },
    },
]


def _jsonrpc_result(message_id: object, result: object) -> dict[str, object]:
    return {"jsonrpc": "2.0", "id": message_id, "result": result}


def _jsonrpc_error(message_id: object, code: int, message: str) -> dict[str, object]:
    return {
        "jsonrpc": "2.0",
        "id": message_id,
        "error": {"code": code, "message": message},
    }


def _format_tool_content(payload: object) -> dict[str, object]:
    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(payload, sort_keys=True),
            }
        ],
        "isError": False,
    }


def _format_tool_error(message: str) -> dict[str, object]:
    return {
        "content": [{"type": "text", "text": message}],
        "isError": True,
    }


class BrowserInspectorBridge:
    """Hold the active browser session and relay MCP tool calls to it."""

    def __init__(self) -> None:
        self._session_id: str | None = None
        self._last_seen_monotonic = 0.0
        self._pending_requests: deque[dict[str, object]] = deque()
        self._futures: dict[str, Future[dict[str, object]]] = {}
        self._condition = threading.Condition()

    def _session_is_live(self) -> bool:
        if not self._session_id:
            return False
        return (time.monotonic() - self._last_seen_monotonic) < MCP_BROWSER_SESSION_TTL_SECONDS

    def has_live_session(self) -> bool:
        return self._session_is_live()

    def handshake_payload(self) -> dict[str, object]:
        return {
            "ok": True,
            "protocolVersion": MCP_PROTOCOL_VERSION,
            "server": {"name": MCP_SERVER_NAME, "version": MCP_SERVER_VERSION},
            "transport": "streamable-http+browser-bridge",
            "browserConnected": self._session_is_live(),
            "browserSessionId": self._session_id if self._session_is_live() else None,
            "toolCount": len(_TOOL_DEFINITIONS),
        }

    async def register_browser(self) -> dict[str, object]:
        with self._condition:
            previous_session = self._session_id
            if previous_session is not None:
                self._fail_all_pending("Browser inspector session was replaced by a newer page connection.")

            self._session_id = str(uuid.uuid4())
            self._last_seen_monotonic = time.monotonic()
            self._condition.notify_all()

            return {
                "sessionId": self._session_id,
                "pollMaxSeconds": MCP_BROWSER_POLL_MAX_SECONDS,
                "toolNames": [tool["name"] for tool in _TOOL_DEFINITIONS],
            }

    async def poll_request(self, session_id: str, wait_seconds: float) -> dict[str, object] | None:
        def _wait_for_request() -> dict[str, object] | None:
            with self._condition:
                self._require_session(session_id)
                self._last_seen_monotonic = time.monotonic()

                if not self._pending_requests:
                    self._condition.wait(timeout=wait_seconds)

                self._require_session(session_id)
                self._last_seen_monotonic = time.monotonic()

                if not self._pending_requests:
                    return None

                return self._pending_requests.popleft()

        return await asyncio.to_thread(_wait_for_request)

    async def complete_request(
        self,
        session_id: str,
        request_id: str,
        *,
        ok: bool,
        result: object | None = None,
        error: str | None = None,
    ) -> bool:
        with self._condition:
            self._require_session(session_id)
            self._last_seen_monotonic = time.monotonic()

            future = self._futures.pop(request_id, None)
            if future is None:
                return False

            if ok:
                future.set_result(_format_tool_content(result))
            else:
                future.set_result(_format_tool_error(error or "Browser tool call failed."))
            return True

    async def call_tool(self, tool_name: str, arguments: object) -> dict[str, object]:
        if not self._session_is_live():
            return _format_tool_error(
                "No browser inspector session is connected. Open the dashboard and start BrowserMcpServer first."
            )

        request_id = str(uuid.uuid4())
        future: Future[dict[str, object]] = Future()

        with self._condition:
            if not self._session_is_live() or not self._session_id:
                return _format_tool_error("Browser inspector session expired before the tool call could be queued.")

            self._futures[request_id] = future
            self._pending_requests.append(
                {
                    "requestId": request_id,
                    "toolName": tool_name,
                    "arguments": arguments,
                }
            )
            self._condition.notify_all()

        try:
            return await asyncio.wait_for(asyncio.wrap_future(future), timeout=MCP_REQUEST_TIMEOUT_SECONDS)
        except asyncio.TimeoutError:
            with self._condition:
                self._futures.pop(request_id, None)
            return _format_tool_error(
                f"Browser tool call timed out after {MCP_REQUEST_TIMEOUT_SECONDS:.0f}s waiting for the page bridge."
            )

    def _require_session(self, session_id: str) -> None:
        if self._session_id != session_id or not self._session_is_live():
            raise HTTPException(status_code=404, detail="Browser inspector session not found.")

    def _fail_all_pending(self, message: str) -> None:
        for request_id, future in list(self._futures.items()):
            if not future.done():
                future.set_result(_format_tool_error(message))
            self._futures.pop(request_id, None)
        self._pending_requests.clear()


def _build_snapshot() -> dict:
    """Read METRICS_JSONL_PATH and return aggregated per-tool stats.

    Returns a dict with keys ``snapshot_ts`` (ISO datetime string) and
    ``tools`` (per-tool aggregated metrics).  Returns empty tools dict if
    the JSONL file does not exist.
    """
    path = METRICS_JSONL_PATH
    if not path.exists():
        return {
            "snapshot_ts": datetime.now(timezone.utc).isoformat(),
            "tools": {},
        }

    per_tool: dict[str, list] = {}
    with path.open() as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            tool = record.get("tool_name")
            if not tool:
                continue
            per_tool.setdefault(tool, []).append(record)

    tools_out: dict[str, dict] = {}
    for tool, records in per_tool.items():
        latencies = [r["latency_ms"] for r in records if "latency_ms" in r and r["latency_ms"] is not None]
        error_records = [r for r in records if r.get("is_error")]
        avg_lat = round(statistics.mean(latencies), 2) if latencies else 0.0
        if len(latencies) >= 2:
            p95 = round(statistics.quantiles(latencies, n=20)[-1], 2)
        elif latencies:
            p95 = round(latencies[0], 2)
        else:
            p95 = 0.0
        # Collect up to 10 most recent error events for display
        recent_errors = [
            {
                "ts": r.get("timestamp_utc", ""),
                "latency_ms": r.get("latency_ms"),
                "error_type": r.get("error_type", "tool_error"),
                "message": r.get("error_message") or r.get("message") or r.get("methodology_notes") or "",
                "faithfulness": r.get("faithfulness"),
                "correctness": r.get("correctness"),
                "severity_level": r.get("severity_level"),
            }
            for r in sorted(
                error_records,
                key=lambda x: x.get("timestamp_utc", ""),
                reverse=True,
            )[:10]
        ]
        tools_out[tool] = {
            "invocation_count": len(records),
            "error_count": len(error_records),
            "avg_latency_ms": avg_lat,
            "p95_latency_ms": p95,
            "recent_errors": recent_errors,
        }

    mtime = path.stat().st_mtime
    last_updated = datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat()
    return {
        "snapshot_ts": last_updated,
        "tools": tools_out,
    }


def create_app() -> FastAPI:
    """Create the sidecar app with local CORS policy.

    Hardcoded CORS origin is limited to `http://localhost:5173` for local Vite dev.
    # TODO(v2): WEBMCP_CORS_ORIGINS from env (#506)
    """
    app = FastAPI(title="MCP Dashboard Sidecar", version="0.1.0")
    bridge = BrowserInspectorBridge()

    # TODO(v2): WEBMCP_CORS_ORIGINS from env (#506)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/metrics")
    async def get_metrics() -> dict[str, object]:
        """Return aggregated MCP metrics snapshot."""
        return _build_snapshot()

    @app.get("/api/metrics/stream")
    async def stream_metrics(interval: int = 10) -> StreamingResponse:
        """Stream metrics as Server-Sent Events.

        Browser clients should consume this endpoint with EventSource.
        Query param ``interval`` controls poll frequency in seconds (1–60).
        """
        poll_interval = max(1, min(60, interval))

        async def event_generator():
            try:
                while True:
                    snapshot = _build_snapshot()
                    yield f"data: {json.dumps(snapshot)}\n\n"
                    await asyncio.sleep(poll_interval)
            except asyncio.CancelledError:
                return

        return StreamingResponse(
            content=event_generator(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache"},
        )

    @app.get("/api/health")
    async def health() -> dict[str, object]:
        """Return sidecar health status."""
        path = METRICS_JSONL_PATH
        if not path.exists():
            return {"ok": False, "last_updated": "", "tool_count": 0}

        tool_names: set[str] = set()
        with path.open() as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    name = record.get("tool_name")
                    if name:
                        tool_names.add(name)
                except json.JSONDecodeError:
                    continue

        mtime = path.stat().st_mtime
        last_updated = datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat()
        return {
            "ok": True,
            "last_updated": last_updated,
            "tool_count": len(tool_names),
        }

    @app.get("/mcp/handshake")
    async def mcp_handshake() -> dict[str, object]:
        """Return browser-bridge handshake state for diagnostics and local probes."""
        return bridge.handshake_payload()

    @app.post("/mcp/browser/session")
    async def register_browser_session() -> dict[str, object]:
        """Register the active dashboard page as the browser-side tool executor."""
        return await bridge.register_browser()

    @app.get("/mcp/browser/poll")
    async def poll_browser_request(session_id: str, wait: float = 25.0):
        """Long-poll for the next pending browser tool request."""
        payload = await bridge.poll_request(session_id, max(0.0, min(wait, MCP_BROWSER_POLL_MAX_SECONDS)))
        if payload is None:
            return Response(status_code=204)
        return JSONResponse(payload)

    @app.post("/mcp/browser/respond")
    async def respond_browser_request(request: Request) -> dict[str, object]:
        """Accept the browser-side result for a queued tool request."""
        try:
            payload = await request.json()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON payload")

        if not isinstance(payload, dict):
            raise HTTPException(status_code=400, detail="Payload must be a JSON object")

        session_id = payload.get("sessionId")
        request_id = payload.get("requestId")
        if not isinstance(session_id, str) or not session_id:
            raise HTTPException(status_code=400, detail="sessionId is required")
        if not isinstance(request_id, str) or not request_id:
            raise HTTPException(status_code=400, detail="requestId is required")

        completed = await bridge.complete_request(
            session_id,
            request_id,
            ok=bool(payload.get("ok", False)),
            result=payload.get("result"),
            error=payload.get("error") if isinstance(payload.get("error"), str) else None,
        )
        if not completed:
            raise HTTPException(status_code=404, detail="Pending browser request not found")
        return {"ok": True}

    @app.post("/mcp")
    async def mcp_endpoint(request: Request):
        """Serve a minimal MCP JSON-RPC surface for the browser inspector bridge."""
        try:
            payload = await request.json()
        except json.JSONDecodeError:
            return JSONResponse(_jsonrpc_error(None, -32700, "Parse error"), status_code=400)

        if not isinstance(payload, dict):
            return JSONResponse(_jsonrpc_error(None, -32600, "Invalid request"), status_code=400)

        message_id = payload.get("id")
        method = payload.get("method")

        params_raw = payload.get("params")
        if params_raw is None:
            params: dict[str, object] = {}
        elif isinstance(params_raw, dict):
            params = params_raw
        else:
            return JSONResponse(
                _jsonrpc_error(message_id, -32600, "Invalid request: params must be an object"),
                status_code=400,
            )

        if not isinstance(method, str):
            return JSONResponse(
                _jsonrpc_error(message_id, -32600, "Invalid request: method is required"),
                status_code=400,
            )

        if method == "initialize":
            return JSONResponse(
                _jsonrpc_result(
                    message_id,
                    {
                        "protocolVersion": MCP_PROTOCOL_VERSION,
                        "capabilities": {"tools": {"listChanged": False}},
                        "serverInfo": {"name": MCP_SERVER_NAME, "version": MCP_SERVER_VERSION},
                        "instructions": (
                            "Open the dashboard page and start BrowserMcpServer so the sidecar can relay tool calls."
                        ),
                    },
                )
            )

        if method == "notifications/initialized":
            return Response(status_code=202)

        if method == "ping":
            return JSONResponse(_jsonrpc_result(message_id, {}))

        if method == "tools/list":
            return JSONResponse(_jsonrpc_result(message_id, {"tools": _TOOL_DEFINITIONS}))

        if method == "tools/call":
            tool_name = params.get("name")
            if not isinstance(tool_name, str) or not tool_name:
                return JSONResponse(
                    _jsonrpc_error(message_id, -32602, "tools/call requires params.name"),
                    status_code=400,
                )

            arguments = params.get("arguments", {})
            result = await bridge.call_tool(tool_name, arguments)
            return JSONResponse(_jsonrpc_result(message_id, result))

        if message_id is None:
            return Response(status_code=202)

        return JSONResponse(_jsonrpc_error(message_id, -32601, f"Method not found: {method}"), status_code=404)

    return app


app = create_app()
