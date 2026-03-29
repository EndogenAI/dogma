"""Tests for web/server.py — FastAPI sidecar endpoints.

Covers GET /api/health, GET /api/metrics, GET /api/metrics/stream, and CORS.
Uses starlette.testclient.TestClient (synchronous) to keep tests hermetic.
All tests that touch the filesystem are marked @pytest.mark.io.
"""

import json

import pytest
from starlette.testclient import TestClient

import web.server as srv
from web.server import create_app

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SAMPLE_RECORDS = [
    {"tool_name": "check_substrate", "latency_ms": 500.0, "is_error": False},
    {"tool_name": "check_substrate", "latency_ms": 600.0, "is_error": True},
    {"tool_name": "validate_agent_file", "latency_ms": 400.0, "is_error": False},
]


def _write_jsonl(path, records):
    path.write_text("\n".join(json.dumps(r) for r in records) + "\n")


def _make_client(monkeypatch, path):
    """Patch METRICS_JSONL_PATH and return a TestClient wrapping a fresh app."""
    monkeypatch.setattr(srv, "METRICS_JSONL_PATH", path)
    return TestClient(create_app())


# ---------------------------------------------------------------------------
# /api/health
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_health_file_exists(tmp_path, monkeypatch):
    jsonl = tmp_path / "tool_calls.jsonl"
    _write_jsonl(jsonl, _SAMPLE_RECORDS)
    client = _make_client(monkeypatch, jsonl)

    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["tool_count"] == 2


@pytest.mark.io
def test_health_file_missing(tmp_path, monkeypatch):
    client = _make_client(monkeypatch, tmp_path / "nonexistent.jsonl")

    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is False
    assert data["tool_count"] == 0


# ---------------------------------------------------------------------------
# /api/metrics
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_metrics_snapshot(tmp_path, monkeypatch):
    jsonl = tmp_path / "tool_calls.jsonl"
    _write_jsonl(jsonl, _SAMPLE_RECORDS)
    client = _make_client(monkeypatch, jsonl)

    response = client.get("/api/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "snapshot_ts" in data
    tools = data["tools"]
    assert "check_substrate" in tools
    assert "validate_agent_file" in tools
    cs = tools["check_substrate"]
    assert isinstance(cs["invocation_count"], int)
    assert isinstance(cs["avg_latency_ms"], float)


@pytest.mark.io
def test_metrics_file_missing(tmp_path, monkeypatch):
    client = _make_client(monkeypatch, tmp_path / "nonexistent.jsonl")

    response = client.get("/api/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "snapshot_ts" in data
    assert data["tools"] == {}


# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_cors_header(tmp_path, monkeypatch):
    jsonl = tmp_path / "tool_calls.jsonl"
    _write_jsonl(jsonl, _SAMPLE_RECORDS)
    client = _make_client(monkeypatch, jsonl)

    response = client.get("/api/health", headers={"Origin": "http://localhost:5173"})
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"


@pytest.mark.io
def test_cors_blocked(tmp_path, monkeypatch):
    jsonl = tmp_path / "tool_calls.jsonl"
    _write_jsonl(jsonl, _SAMPLE_RECORDS)
    client = _make_client(monkeypatch, jsonl)

    response = client.get("/api/health", headers={"Origin": "http://evil.example.com"})
    assert response.status_code == 200
    acao = response.headers.get("access-control-allow-origin")
    assert acao != "http://evil.example.com"


# ---------------------------------------------------------------------------
# /api/metrics/stream (SSE)
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_metrics_stream_yields_event(tmp_path, monkeypatch):
    import asyncio as _asyncio

    record = {"tool_name": "check_substrate", "latency_ms": 500.0, "is_error": False}
    jsonl = tmp_path / "tool_calls.jsonl"
    jsonl.write_text(json.dumps(record) + "\n")

    monkeypatch.setattr(srv, "METRICS_JSONL_PATH", jsonl)

    # Patch asyncio.sleep so the infinite generator yields exactly one event then stops.
    # The generator's `except asyncio.CancelledError: return` clause handles cleanup.
    async def _cancel_sleep(_n: float) -> None:
        raise _asyncio.CancelledError()

    monkeypatch.setattr(_asyncio, "sleep", _cancel_sleep)

    client = TestClient(create_app())
    response = client.get("/api/metrics/stream?interval=1")
    assert response.status_code == 200

    body = response.text
    assert body.startswith("data: ")
    first_line = body.splitlines()[0]
    payload = json.loads(first_line.removeprefix("data: ").strip())
    assert "snapshot_ts" in payload
    assert "tools" in payload
