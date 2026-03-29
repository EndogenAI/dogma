"""FastAPI sidecar stub for the MCP Web Dashboard.

This module defines API endpoint signatures only for Phase 2 architecture scaffolding.
The app currently configures CORS with a hardcoded frontend origin for local development:
`http://localhost:5173`.
"""

import pathlib

try:
    import asyncio
    import json
    import statistics
    from datetime import datetime, timezone

    from fastapi import FastAPI  # type: ignore[import-not-found]
    from fastapi.middleware.cors import CORSMiddleware  # type: ignore[import-not-found]
    from fastapi.responses import StreamingResponse  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover

    class _StubApp:
        def add_middleware(self, *args, **kwargs) -> None:
            return None

        def get(self, *args, **kwargs):
            def _decorator(func):
                return func

            return _decorator

    class FastAPI(_StubApp):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__()

    class CORSMiddleware:  # type: ignore[no-redef]
        pass

    class StreamingResponse:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs) -> None:
            return None


METRICS_JSONL_PATH = pathlib.Path(__file__).parent.parent / ".cache/mcp-metrics/tool_calls.jsonl"


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
        latencies = [r["latency_ms"] for r in records if "latency_ms" in r]
        errors = sum(1 for r in records if r.get("is_error"))
        avg_lat = round(statistics.mean(latencies), 2) if latencies else 0.0
        if len(latencies) >= 2:
            p95 = round(statistics.quantiles(latencies, n=20)[-1], 2)
        elif latencies:
            p95 = round(latencies[0], 2)
        else:
            p95 = 0.0
        tools_out[tool] = {
            "invocation_count": len(records),
            "error_count": errors,
            "avg_latency_ms": avg_lat,
            "p95_latency_ms": p95,
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
    # TODO(v2): CORS_ALLOWED_ORIGINS from env (#506)
    """
    app = FastAPI(title="MCP Dashboard Sidecar", version="0.1.0-stub")

    # TODO(v2): CORS_ALLOWED_ORIGINS from env (#506)
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

    return app


app = create_app()
