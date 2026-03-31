import importlib
import json
import queue
from pathlib import Path
from unittest.mock import patch

import pytest

_mcp_available = importlib.util.find_spec("mcp") is not None
_requires_mcp = pytest.mark.skipif(not _mcp_available, reason="mcp extra not installed")


@_requires_mcp
@pytest.mark.io
def test_jsonl_writer_drains_queue_and_writes_parseable_line(tmp_path: Path) -> None:
    dogma_server = importlib.import_module("mcp_server.dogma_server")
    jsonl_path = tmp_path / "tool_calls.jsonl"
    local_queue: queue.Queue = queue.Queue()

    payload = {
        "tool_name": "test_tool",
        "timestamp_utc": "2026-03-29T00:00:00+00:00",
        "latency_ms": 1.23,
        "is_error": False,
        "error_type": None,
        "error_message": None,
        "source": "live",
        "tool_version": "0.0.0.0",
    }
    local_queue.put(payload)
    local_queue.put(None)

    with (
        patch("mcp_server.dogma_server._JSONL_PATH", jsonl_path),
        patch("mcp_server.dogma_server._JSONL_QUEUE", local_queue),
    ):
        dogma_server._jsonl_writer()

    lines = jsonl_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    parsed = json.loads(lines[0])
    assert parsed == payload


@_requires_mcp
def test_run_with_mcp_telemetry_non_error_enqueues_expected_payload() -> None:
    dogma_server = importlib.import_module("mcp_server.dogma_server")
    captured: list[dict] = []

    def _capture(item: dict) -> None:
        captured.append(item)

    def tool_fn() -> dict:
        return {"ok": True, "result": "val"}

    with patch.object(dogma_server._JSONL_QUEUE, "put_nowait", side_effect=_capture):
        result = dogma_server._run_with_mcp_telemetry("test_tool", tool_fn)

    assert result == {"ok": True, "result": "val"}
    assert len(captured) == 1
    payload = captured[0]
    assert payload["tool_name"] == "test_tool"
    assert payload["is_error"] is False
    assert payload["error_type"] is None
    assert payload["error_message"] is None
    assert payload["source"] == "live"
    assert payload["latency_ms"] >= 0


@_requires_mcp
def test_run_with_mcp_telemetry_error_enqueues_error_and_reraises() -> None:
    dogma_server = importlib.import_module("mcp_server.dogma_server")
    captured: list[dict] = []

    def _capture(item: dict) -> None:
        captured.append(item)

    def tool_fn() -> dict:
        raise RuntimeError("boom")

    with patch.object(dogma_server._JSONL_QUEUE, "put_nowait", side_effect=_capture):
        with pytest.raises(RuntimeError, match="boom"):
            dogma_server._run_with_mcp_telemetry("error_tool", tool_fn)

    assert len(captured) == 1
    payload = captured[0]
    assert payload["tool_name"] == "error_tool"
    assert payload["is_error"] is True
    assert payload["error_type"] == "RuntimeError"
    assert payload["error_message"] == "boom"


@_requires_mcp
def test_run_with_mcp_telemetry_tool_error_enqueues_structured_error_message() -> None:
    dogma_server = importlib.import_module("mcp_server.dogma_server")
    captured: list[dict] = []

    def _capture(item: dict) -> None:
        captured.append(item)

    def tool_fn() -> dict:
        return {"ok": False, "errors": ["index unavailable", {"message": "backend offline"}]}

    with patch.object(dogma_server._JSONL_QUEUE, "put_nowait", side_effect=_capture):
        result = dogma_server._run_with_mcp_telemetry("query_docs", tool_fn)

    assert result["ok"] is False
    assert len(captured) == 1
    payload = captured[0]
    assert payload["is_error"] is True
    assert payload["error_type"] == "tool_error"
    assert payload["error_message"] == "index unavailable; backend offline"


@_requires_mcp
def test_get_trace_health_success_state() -> None:
    dogma_server = importlib.import_module("mcp_server.dogma_server")
    jsonl_path = dogma_server._JSONL_PATH

    with (
        patch("mcp_server.dogma_server._WRITE_SUCCESS_COUNT", 3),
        patch("mcp_server.dogma_server._WRITE_FAIL_COUNT", 0),
        patch("mcp_server.dogma_server._JSONL_PATH", jsonl_path),
    ):
        jsonl_path.parent.mkdir(parents=True, exist_ok=True)
        jsonl_path.write_text("", encoding="utf-8")
        health = dogma_server.get_trace_health()

    assert health["ok"] is True
    assert health["write_success_count"] == 3
    assert health["write_fail_count"] == 0
    assert health["jsonl_exists"] is True


@_requires_mcp
def test_get_trace_health_failure_state() -> None:
    dogma_server = importlib.import_module("mcp_server.dogma_server")

    with patch("mcp_server.dogma_server._WRITE_FAIL_COUNT", 1):
        health = dogma_server.get_trace_health()

    assert health["ok"] is False


@pytest.mark.io
def test_migrate_tool_calls_dry_run_leaves_source_unchanged(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    migrate_tool_calls = importlib.import_module("scripts.migrate_tool_calls")

    metrics_dir = tmp_path / ".cache" / "mcp-metrics"
    metrics_dir.mkdir(parents=True, exist_ok=True)
    src = metrics_dir / "tool_calls.jsonl"
    dst = metrics_dir / "tool_calls.synthetic.bak.jsonl"

    original = '{"id":1}\n{"id":2}\n'
    src.write_text(original, encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("sys.argv", ["scripts/migrate_tool_calls.py", "--dry-run"])

    rc = migrate_tool_calls.main()

    assert rc == 0
    assert src.read_text(encoding="utf-8") == original
    assert not dst.exists()


@pytest.mark.io
def test_check_branch_counter_zero_returns_zero(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    check_branch_counter = importlib.import_module("scripts.check_branch_counter")

    version_path = tmp_path / "mcp_server" / "_version.py"
    version_path.parent.mkdir(parents=True, exist_ok=True)
    version_path.write_text("BRANCH_COUNTER: int = 0\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)

    assert check_branch_counter.main() == 0


@pytest.mark.io
def test_check_branch_counter_non_zero_returns_one(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    check_branch_counter = importlib.import_module("scripts.check_branch_counter")

    version_path = tmp_path / "mcp_server" / "_version.py"
    version_path.parent.mkdir(parents=True, exist_ok=True)
    version_path.write_text("BRANCH_COUNTER: int = 3\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)

    assert check_branch_counter.main() == 1
