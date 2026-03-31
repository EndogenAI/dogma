"""Tests for web/server.py — FastAPI sidecar endpoints.

Covers GET /api/health, GET /api/metrics, GET /api/metrics/stream, and CORS.
Uses starlette.testclient.TestClient (synchronous) to keep tests hermetic.
All tests that touch the filesystem are marked @pytest.mark.io.
"""

import json
import threading
from queue import Queue

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


@pytest.mark.io
def test_cors_comma_separated_origins(tmp_path, monkeypatch):
    """Test that WEBMCP_CORS_ORIGINS accepts comma-separated values."""

    jsonl = tmp_path / "tool_calls.jsonl"
    _write_jsonl(jsonl, _SAMPLE_RECORDS)

    # Set environment variable with multiple origins
    monkeypatch.setenv("WEBMCP_CORS_ORIGINS", "http://example.com:5173,https://other.com")
    client = _make_client(monkeypatch, jsonl)

    # Test first origin
    response = client.get("/api/health", headers={"Origin": "http://example.com:5173"})
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://example.com:5173"

    # Test second origin
    response = client.get("/api/health", headers={"Origin": "https://other.com"})
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "https://other.com"

    # Test blocked origin
    response = client.get("/api/health", headers={"Origin": "http://evil.example.com"})
    assert response.status_code == 200
    acao = response.headers.get("access-control-allow-origin")
    assert acao != "http://evil.example.com"


@pytest.mark.io
def test_cors_empty_env_raises_runtime_error(monkeypatch):
    """Reject empty WEBMCP_CORS_ORIGINS values instead of silently blocking all origins."""

    monkeypatch.setenv("WEBMCP_CORS_ORIGINS", "   ,   ")

    with pytest.raises(RuntimeError, match="WEBMCP_CORS_ORIGINS is set but empty"):
        create_app()


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


# ---------------------------------------------------------------------------
# /mcp handshake + bridge endpoints
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_mcp_handshake_defaults_to_browser_disconnected(tmp_path, monkeypatch):
    client = _make_client(monkeypatch, tmp_path / "nonexistent.jsonl")

    response = client.get("/mcp/handshake")
    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["browserConnected"] is False
    assert payload["toolCount"] == 5


@pytest.mark.io
def test_browser_session_registration_updates_handshake(tmp_path, monkeypatch):
    client = _make_client(monkeypatch, tmp_path / "nonexistent.jsonl")

    register = client.post("/mcp/browser/session")
    assert register.status_code == 200
    session_payload = register.json()
    assert isinstance(session_payload["sessionId"], str)
    assert session_payload["toolNames"] == [
        "ping",
        "query_dom",
        "get_console_logs",
        "get_component_state",
        "trigger_action",
    ]

    handshake = client.get("/mcp/handshake")
    assert handshake.status_code == 200
    assert handshake.json()["browserConnected"] is True


# ---------------------------------------------------------------------------
# /mcp JSON-RPC
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_mcp_initialize_returns_server_capabilities(tmp_path, monkeypatch):
    client = _make_client(monkeypatch, tmp_path / "nonexistent.jsonl")

    response = client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {"name": "pytest", "version": "0.0.0"},
            },
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["result"]["protocolVersion"] == "2025-03-26"
    assert payload["result"]["capabilities"] == {"tools": {"listChanged": False}}
    assert payload["result"]["serverInfo"]["name"] == "dogma-browser-inspector"


@pytest.mark.io
def test_mcp_tools_list_returns_expected_tool_names(tmp_path, monkeypatch):
    client = _make_client(monkeypatch, tmp_path / "nonexistent.jsonl")

    response = client.post("/mcp", json={"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    assert response.status_code == 200
    tools = response.json()["result"]["tools"]
    assert [tool["name"] for tool in tools] == [
        "ping",
        "query_dom",
        "get_console_logs",
        "get_component_state",
        "trigger_action",
    ]


@pytest.mark.io
def test_mcp_tools_call_returns_bridge_error_without_browser_session(tmp_path, monkeypatch):
    client = _make_client(monkeypatch, tmp_path / "nonexistent.jsonl")

    response = client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "query_dom", "arguments": {"selector": ".app-title"}},
        },
    )
    assert response.status_code == 200
    result = response.json()["result"]
    assert result["isError"] is True
    assert "No browser inspector session is connected" in result["content"][0]["text"]


@pytest.mark.io
def test_mcp_tools_call_round_trips_through_browser_bridge(tmp_path, monkeypatch):
    client = _make_client(monkeypatch, tmp_path / "nonexistent.jsonl")
    session_id = client.post("/mcp/browser/session").json()["sessionId"]
    results: Queue[dict[str, object]] = Queue()

    def _call_tool() -> None:
        response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {"name": "query_dom", "arguments": {"selector": ".app-title"}},
            },
        )
        results.put({"status_code": response.status_code, "json": response.json()})

    thread = threading.Thread(target=_call_tool)
    thread.start()

    poll = client.get(f"/mcp/browser/poll?session_id={session_id}&wait=1")
    assert poll.status_code == 200
    payload = poll.json()
    assert payload["toolName"] == "query_dom"
    assert payload["arguments"] == {"selector": ".app-title"}

    response = client.post(
        "/mcp/browser/respond",
        json={
            "sessionId": session_id,
            "requestId": payload["requestId"],
            "ok": True,
            "result": {"count": 1, "elements": [{"tag": "span", "text": "MCP Dashboard"}]},
        },
    )
    assert response.status_code == 200
    assert response.json() == {"ok": True}

    thread.join(timeout=5)
    assert not thread.is_alive()
    result = results.get(timeout=1)
    assert result["status_code"] == 200
    body = result["json"]
    assert body["result"]["isError"] is False
    content = body["result"]["content"][0]["text"]
    assert '"count": 1' in content
    assert "MCP Dashboard" in content


@pytest.mark.io
def test_mcp_malformed_json_returns_parse_error(tmp_path, monkeypatch):
    client = _make_client(monkeypatch, tmp_path / "nonexistent.jsonl")

    response = client.post(
        "/mcp",
        content='{"jsonrpc":"2.0","id":1,',
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 400
    payload = response.json()
    assert payload == {
        "jsonrpc": "2.0",
        "id": None,
        "error": {"code": -32700, "message": "Parse error"},
    }


@pytest.mark.io
def test_mcp_invalid_request_shape_returns_invalid_request(tmp_path, monkeypatch):
    client = _make_client(monkeypatch, tmp_path / "nonexistent.jsonl")

    response = client.post("/mcp", json=[{"jsonrpc": "2.0", "method": "ping"}])

    assert response.status_code == 400
    payload = response.json()
    assert payload == {
        "jsonrpc": "2.0",
        "id": None,
        "error": {"code": -32600, "message": "Invalid request"},
    }


@pytest.mark.io
def test_browser_session_replacement_invalidates_old_session(tmp_path, monkeypatch):
    client = _make_client(monkeypatch, tmp_path / "nonexistent.jsonl")

    first_session = client.post("/mcp/browser/session").json()["sessionId"]
    second_session = client.post("/mcp/browser/session").json()["sessionId"]

    stale_poll = client.get(f"/mcp/browser/poll?session_id={first_session}&wait=0")
    assert stale_poll.status_code == 404

    active_poll = client.get(f"/mcp/browser/poll?session_id={second_session}&wait=0")
    assert active_poll.status_code == 204
