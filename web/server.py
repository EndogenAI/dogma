"""FastAPI sidecar stub for the MCP Web Dashboard.

This module defines API endpoint signatures only for Phase 2 architecture scaffolding.
The app currently configures CORS with a hardcoded frontend origin for local development:
`http://localhost:5173`.
"""

try:
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
    async def get_metrics() -> dict[str, str]:
        """Return metrics payload stub.

        Endpoint signature placeholder for future MCP metrics aggregation.
        """
        raise NotImplementedError("Phase 2 stub: implement in Phase 3")

    @app.get("/api/metrics/stream")
    async def stream_metrics() -> StreamingResponse:
        """Stream metrics as Server-Sent Events.

        Browser clients should consume this endpoint with EventSource.
        This is a signature-level scaffold for a future live stream implementation.
        """
        raise NotImplementedError("Phase 2 stub: implement in Phase 3")

    @app.get("/api/health")
    async def health() -> dict[str, str]:
        """Return sidecar health status stub."""
        raise NotImplementedError("Phase 2 stub: implement in Phase 3")

    return app


app = create_app()
