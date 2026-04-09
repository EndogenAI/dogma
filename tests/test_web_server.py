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
# Phase 9B — RAGAS extraction pipeline tests
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_metrics_snapshot_includes_ragas_fields(tmp_path, monkeypatch):
    """Phase 9B — verify RAGAS fields are extracted and forwarded to /api/metrics."""
    jsonl = tmp_path / "tool_calls.jsonl"
    records = [
        {
            "tool_name": "check_substrate",
            "latency_ms": 500.0,
            "is_error": False,
            "faithfulness": 0.90,
            "answer_relevancy": 0.85,
            "context_precision": 0.88,
            "context_recall": 0.87,
        },
        {
            "tool_name": "check_substrate",
            "latency_ms": 600.0,
            "is_error": False,
            "faithfulness": 0.75,
            "answer_relevancy": 0.72,
            "context_precision": 0.78,
            "context_recall": 0.70,
        },
    ]
    _write_jsonl(jsonl, records)
    client = _make_client(monkeypatch, jsonl)

    response = client.get("/api/metrics")
    assert response.status_code == 200
    data = response.json()
    tools = data["tools"]
    assert "check_substrate" in tools

    cs = tools["check_substrate"]
    # Verify RAGAS fields are present and averaged correctly
    assert "faithfulness" in cs
    assert "answer_relevancy" in cs
    assert "context_precision" in cs
    assert "context_recall" in cs

    # Average of 0.90 and 0.75 = 0.825, rounded to 3 decimals
    assert cs["faithfulness"] == 0.825
    assert cs["answer_relevancy"] == 0.785
    assert cs["context_precision"] == 0.83
    assert cs["context_recall"] == 0.785


@pytest.mark.io
def test_metrics_snapshot_gracefully_handles_missing_ragas_fields(tmp_path, monkeypatch):
    """Phase 9B — verify pipeline handles missing RAGAS fields gracefully (returns None)."""
    jsonl = tmp_path / "tool_calls.jsonl"
    records = [
        {
            "tool_name": "query_docs",
            "latency_ms": 300.0,
            "is_error": False,
            # No RAGAS fields — old records before Phase 9A
        },
    ]
    _write_jsonl(jsonl, records)
    client = _make_client(monkeypatch, jsonl)

    response = client.get("/api/metrics")
    assert response.status_code == 200
    data = response.json()
    tools = data["tools"]
    assert "query_docs" in tools

    qd = tools["query_docs"]
    # All RAGAS fields should be None when missing from records
    assert qd["faithfulness"] is None
    assert qd["answer_relevancy"] is None
    assert qd["context_precision"] is None
    assert qd["context_recall"] is None


@pytest.mark.io
def test_metrics_snapshot_partial_ragas_coverage(tmp_path, monkeypatch):
    """Phase 9B — verify pipeline computes averages only from records with RAGAS fields."""
    jsonl = tmp_path / "tool_calls.jsonl"
    records = [
        {
            "tool_name": "scaffold_agent",
            "latency_ms": 400.0,
            "is_error": False,
            "faithfulness": 0.80,
            "answer_relevancy": 0.75,
            "context_precision": 0.70,
            "context_recall": 0.68,
        },
        {
            "tool_name": "scaffold_agent",
            "latency_ms": 450.0,
            "is_error": False,
            # Missing RAGAS fields — should not affect average
        },
    ]
    _write_jsonl(jsonl, records)
    client = _make_client(monkeypatch, jsonl)

    response = client.get("/api/metrics")
    assert response.status_code == 200
    data = response.json()
    tools = data["tools"]
    assert "scaffold_agent" in tools

    sa = tools["scaffold_agent"]
    # Average should be computed only from the first record
    assert sa["faithfulness"] == 0.8
    assert sa["answer_relevancy"] == 0.75
    assert sa["context_precision"] == 0.7
    assert sa["context_recall"] == 0.68


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


@pytest.mark.integration
def test_browser_poll_returns_204_when_session_replaced_during_wait(tmp_path, monkeypatch):
    """When a new session registration replaces the active one while a poll is
    waiting, the in-flight poll must return 204 (graceful no-work) rather than
    404.  This covers the HMR / page-reload race: register_browser() calls
    notify_all() which wakes the waiting poll; the poll sees the session was
    replaced and returns None instead of raising HTTPException(404)."""
    import time as _time

    client = _make_client(monkeypatch, tmp_path / "nonexistent.jsonl")
    session_id = client.post("/mcp/browser/session").json()["sessionId"]

    poll_status: dict[str, int] = {}

    def _do_poll() -> None:
        poll_status["status_code"] = client.get(f"/mcp/browser/poll?session_id={session_id}&wait=2").status_code

    poll_thread = threading.Thread(target=_do_poll)
    poll_thread.start()

    # Allow the poll thread to enter the condition.wait() before we replace the session.
    _time.sleep(0.1)

    # Registering a new session calls notify_all(), waking the in-flight poll.
    client.post("/mcp/browser/session")

    poll_thread.join(timeout=5)
    assert not poll_thread.is_alive(), "Poll thread did not complete within 5 s"
    assert poll_status["status_code"] == 204
