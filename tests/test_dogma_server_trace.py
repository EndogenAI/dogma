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

    dogma_server._jsonl_writer(local_queue, jsonl_path)

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
    # Phase 9A — verify RAGAS fields are present (per data/mcp-metrics-schema.yml)
    assert "faithfulness" in payload
    assert "answer_relevance" in payload
    assert "context_precision" in payload
    assert "context_recall" in payload
    assert 0.0 <= payload["faithfulness"] <= 1.0
    assert 0.0 <= payload["answer_relevance"] <= 1.0
    assert 0.0 <= payload["context_precision"] <= 1.0
    assert 0.0 <= payload["context_recall"] <= 1.0


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

    # Verify error telemetry was enqueued before re-raise (Copilot comment #3035069946)
    assert len(captured) == 1
    payload = captured[0]
    assert payload["tool_name"] == "error_tool"
    assert payload["is_error"] is True
    assert payload["error_type"] == "RuntimeError"
    assert payload["error_message"] == "boom"
    assert payload["latency_ms"] >= 0


@_requires_mcp
def test_configure_telemetry_jsonl_mode_skips_otlp() -> None:
    dogma_server = importlib.import_module("mcp_server.dogma_server")
    original_tracer = dogma_server._TRACER

    with (
        patch.dict("os.environ", {"DOGMA_OTEL_EXPORTER": "jsonl"}),
        patch("opentelemetry.exporter.otlp.proto.grpc.trace_exporter.OTLPSpanExporter") as mock_span,
        patch("opentelemetry.exporter.otlp.proto.grpc.metric_exporter.OTLPMetricExporter") as mock_metric,
    ):
        dogma_server._configure_telemetry()
        mock_span.assert_not_called()
        mock_metric.assert_not_called()

    assert dogma_server._TRACER is original_tracer


@_requires_mcp
@pytest.mark.integration
def test_start_otel_stack_help_exits_cleanly() -> None:
    import subprocess as _subprocess

    result = _subprocess.run(
        ["uv", "run", "python", "scripts/start_otel_stack.py", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "stop" in result.stdout.lower()


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
def test_run_with_mcp_telemetry_tool_error_without_details_enqueues_fallback_message() -> None:
    dogma_server = importlib.import_module("mcp_server.dogma_server")
    captured: list[dict] = []

    def _capture(item: dict) -> None:
        captured.append(item)

    def tool_fn() -> dict:
        return {"ok": False}

    with patch.object(dogma_server._JSONL_QUEUE, "put_nowait", side_effect=_capture):
        result = dogma_server._run_with_mcp_telemetry("get_trace_health", tool_fn)

    assert result["ok"] is False
    assert len(captured) == 1
    payload = captured[0]
    assert payload["is_error"] is True
    assert payload["error_type"] == "tool_error"
    assert payload["error_message"] == "The tool reported a problem but did not include any details."


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
    assert health["errors"] == ["JSONL trace capture has recorded 1 write failure(s)."]


@_requires_mcp
def test_get_trace_health_enqueues_telemetry_row() -> None:
    dogma_server = importlib.import_module("mcp_server.dogma_server")
    captured: list[dict] = []

    def _capture(item: dict) -> None:
        captured.append(item)

    with patch.object(dogma_server._JSONL_QUEUE, "put_nowait", side_effect=_capture):
        health = dogma_server.get_trace_health()

    assert health["jsonl_path"] == str(dogma_server._JSONL_PATH)
    assert len(captured) == 1


@_requires_mcp
def test_compute_ragas_heuristics_error_case() -> None:
    """Phase 9A — test RAGAS heuristics for error cases."""
    dogma_server = importlib.import_module("mcp_server.dogma_server")

    # Error case — expect low scores
    metrics = dogma_server._compute_ragas_heuristics(is_error=True, latency_s=0.5)
    assert metrics["faithfulness"] == 0.40
    assert metrics["answer_relevancy"] == 0.35
    assert metrics["context_precision"] == 0.45
    assert metrics["context_recall"] == 0.30


@_requires_mcp
def test_compute_ragas_heuristics_fast_success() -> None:
    """Phase 9A — test RAGAS heuristics for fast successful calls."""
    dogma_server = importlib.import_module("mcp_server.dogma_server")

    # Fast success — expect high scores
    metrics = dogma_server._compute_ragas_heuristics(is_error=False, latency_s=0.5)
    assert metrics["faithfulness"] == 0.90
    assert metrics["answer_relevancy"] == 0.85
    assert metrics["context_precision"] == 0.88
    assert metrics["context_recall"] == 0.87


@_requires_mcp
def test_compute_ragas_heuristics_slow_success() -> None:
    """Phase 9A — test RAGAS heuristics for slow successful calls."""
    dogma_server = importlib.import_module("mcp_server.dogma_server")

    # Slow success — expect moderate scores
    metrics = dogma_server._compute_ragas_heuristics(is_error=False, latency_s=1.5)
    assert metrics["faithfulness"] == 0.75
    assert metrics["answer_relevancy"] == 0.72
    assert metrics["context_precision"] == 0.78
    assert metrics["context_recall"] == 0.70


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


# ---------------------------------------------------------------------------
# Additional coverage tests (Sprint 22 — Test Coverage Enhancement)
# ---------------------------------------------------------------------------


@_requires_mcp
def test_summarize_error_value_handles_dict_with_message() -> None:
    """Coverage: _summarize_error_value dict path (line 215)."""
    dogma_server = importlib.import_module("mcp_server.dogma_server")
    error_dict = {"message": "Something went wrong", "code": 500}
    result = dogma_server._summarize_error_value(error_dict)
    assert result == "Something went wrong"


@_requires_mcp
def test_summarize_error_value_handles_dict_without_message() -> None:
    """Coverage: _summarize_error_value dict JSON fallback (line 218)."""
    dogma_server = importlib.import_module("mcp_server.dogma_server")
    error_dict = {"code": 404, "status": "not_found"}
    result = dogma_server._summarize_error_value(error_dict)
    assert "code" in result
    assert "404" in result


@_requires_mcp
def test_summarize_error_value_handles_non_serializable_dict() -> None:
    """Coverage: _summarize_error_value TypeError fallback (line 220)."""
    dogma_server = importlib.import_module("mcp_server.dogma_server")

    class CustomObject:
        def __str__(self) -> str:
            return "CustomObject instance"

    error_dict = {"obj": CustomObject()}
    result = dogma_server._summarize_error_value(error_dict)
    assert result is not None
    assert len(result) <= 240


@_requires_mcp
def test_summarize_error_value_handles_list_with_many_items() -> None:
    """Coverage: _summarize_error_value list truncation (line 232)."""
    dogma_server = importlib.import_module("mcp_server.dogma_server")
    error_list = ["error1", "error2", "error3", "error4", "error5"]
    result = dogma_server._summarize_error_value(error_list)
    assert "+2 more" in result


@_requires_mcp
def test_summarize_error_value_handles_empty_list() -> None:
    """Coverage: _summarize_error_value empty list path (line 230)."""
    dogma_server = importlib.import_module("mcp_server.dogma_server")
    result = dogma_server._summarize_error_value([])
    assert result is None


@_requires_mcp
def test_configure_telemetry_otlp_mode() -> None:
    """Coverage: _configure_telemetry OTLP path (lines 173-195)."""
    dogma_server = importlib.import_module("mcp_server.dogma_server")

    with (
        patch.dict("os.environ", {"DOGMA_OTEL_EXPORTER": "otlp", "OTEL_EXPORTER_OTLP_ENDPOINT": "http://test:4317"}),
        patch("opentelemetry.exporter.otlp.proto.grpc.trace_exporter.OTLPSpanExporter") as mock_span,
        patch("opentelemetry.exporter.otlp.proto.grpc.metric_exporter.OTLPMetricExporter") as mock_metric,
        patch("opentelemetry.sdk.trace.TracerProvider"),
        patch("opentelemetry.sdk.metrics.MeterProvider"),
    ):
        dogma_server._configure_telemetry()
        # Verify OTLP exporters were instantiated
        mock_span.assert_called_once()
        mock_metric.assert_called_once()


@_requires_mcp
@pytest.mark.io
def test_jsonl_writer_handles_oserror(tmp_path: Path) -> None:
    """Coverage: _jsonl_writer OSError handling (lines 130-132)."""
    dogma_server = importlib.import_module("mcp_server.dogma_server")
    test_queue: queue.Queue = queue.Queue()
    test_path = tmp_path / "readonly" / "tool_calls.jsonl"

    # Create readonly parent to trigger OSError
    readonly_dir = tmp_path / "readonly"
    readonly_dir.mkdir()
    readonly_dir.chmod(0o444)  # Read-only directory

    # Queue a record that will fail to write, then sentinel
    test_queue.put({"test": "data"})
    test_queue.put(None)

    original_fail_count = dogma_server._WRITE_FAIL_COUNT

    # Run the writer (should log warning but not crash)
    dogma_server._jsonl_writer(test_queue, test_path)

    # Verify failure was counted
    assert dogma_server._WRITE_FAIL_COUNT > original_fail_count

    # Cleanup: restore permissions
    readonly_dir.chmod(0o755)


@_requires_mcp
@pytest.mark.io
def test_run_with_mcp_telemetry_with_tracer_active(tmp_path: Path) -> None:
    """Coverage: _run_with_mcp_telemetry with active tracer (lines 285-341)."""
    dogma_server = importlib.import_module("mcp_server.dogma_server")

    # Set up a real tracer for this test
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))

    captured: list[dict] = []

    def _capture(item: dict) -> None:
        captured.append(item)

    def tool_fn() -> dict:
        return {"ok": True, "result": "test"}

    with (
        patch.object(dogma_server, "_TRACER", provider.get_tracer("test")),
        patch.object(dogma_server._JSONL_QUEUE, "put_nowait", side_effect=_capture),
    ):
        result = dogma_server._run_with_mcp_telemetry("test_tool", tool_fn)

    assert result == {"ok": True, "result": "test"}
    assert len(captured) == 1
    assert captured[0]["is_error"] is False


@_requires_mcp
def test_run_with_mcp_telemetry_without_tracer() -> None:
    """Coverage: _run_with_mcp_telemetry fallback path without tracer (lines 341-361)."""
    dogma_server = importlib.import_module("mcp_server.dogma_server")

    captured: list[dict] = []

    def _capture(item: dict) -> None:
        captured.append(item)

    def tool_fn() -> dict:
        return {"ok": True, "result": "test_no_tracer"}

    with (
        patch.object(dogma_server, "_TRACER", None),  # Disable tracer
        patch.object(dogma_server._JSONL_QUEUE, "put_nowait", side_effect=_capture),
    ):
        result = dogma_server._run_with_mcp_telemetry("no_tracer_tool", tool_fn)

    assert result == {"ok": True, "result": "test_no_tracer"}
    assert len(captured) == 1
    assert captured[0]["tool_name"] == "no_tracer_tool"
    assert captured[0]["is_error"] is False


@_requires_mcp
def test_mcp_tool_wrappers_coverage() -> None:
    """Coverage: All @mcp.tool() wrappers (lines 394-618)."""
    dogma_server = importlib.import_module("mcp_server.dogma_server")

    # Mock the underlying tool functions to avoid file I/O
    # Note: dogma_server imports these as _scaffold_agent, _validate_agent_file, etc.
    # so we must patch them on the dogma_server module, not the tools modules
    with (
        patch.object(dogma_server, "_validate_agent_file", return_value={"ok": True, "errors": []}),
        patch.object(dogma_server, "_validate_synthesis", return_value={"ok": True, "errors": []}),
        patch.object(dogma_server, "_check_substrate", return_value={"ok": True, "errors": []}),
        patch.object(dogma_server, "_scaffold_agent", return_value={"ok": True}),
        patch.object(dogma_server, "_scaffold_workplan", return_value={"ok": True}),
        patch.object(dogma_server, "_run_research_scout", return_value={"ok": True}),
        patch.object(dogma_server, "_query_docs", return_value={"ok": True, "results": []}),
        patch.object(dogma_server, "_prune_scratchpad", return_value={"ok": True}),
        patch.object(dogma_server, "_detect_user_interrupt", return_value={"ok": True, "interrupted": False}),
        patch.object(dogma_server, "_normalize_path", return_value="/test/path"),
        patch.object(
            dogma_server, "_resolve_env_path", return_value={"ok": True, "errors": [], "result": "/test/path"}
        ),
        patch.object(dogma_server, "_route_inference_request", return_value={"ok": True}),
        patch.object(dogma_server._JSONL_QUEUE, "put_nowait"),
    ):
        # Call each tool wrapper to exercise the telemetry path
        dogma_server.validate_agent_file("test.agent.md")
        dogma_server.validate_synthesis("test.md")
        dogma_server.check_substrate()
        dogma_server.scaffold_agent("Test", "Test agent")
        dogma_server.scaffold_workplan("test")
        dogma_server.run_research_scout("https://example.com")
        dogma_server.query_docs("test query")
        dogma_server.prune_scratchpad()
        dogma_server.detect_user_interrupt("test message")
        dogma_server.normalize_path("/test")
        dogma_server.resolve_env_path("HOME")
        dogma_server.route_inference_request("test prompt", "llama3.2")


@_requires_mcp
def test_run_with_mcp_telemetry_exception_without_tracer() -> None:
    """Coverage: Exception path in non-tracer code (lines 350-354)."""
    dogma_server = importlib.import_module("mcp_server.dogma_server")

    captured: list[dict] = []

    def _capture(item: dict) -> None:
        captured.append(item)

    def tool_fn() -> dict:
        raise ValueError("test_error_no_tracer")

    with (
        patch.object(dogma_server, "_TRACER", None),  # Disable tracer to hit fallback path
        patch.object(dogma_server._JSONL_QUEUE, "put_nowait", side_effect=_capture),
        pytest.raises(ValueError, match="test_error_no_tracer"),
    ):
        dogma_server._run_with_mcp_telemetry("error_no_tracer", tool_fn)

    # Verify error telemetry was enqueued
    assert len(captured) == 1
    assert captured[0]["is_error"] is True
    assert captured[0]["error_type"] == "ValueError"
    assert captured[0]["error_message"] == "test_error_no_tracer"


@_requires_mcp
def test_normalize_path_exception_handling() -> None:
    """Coverage: normalize_path exception handler (lines 566-567)."""
    dogma_server = importlib.import_module("mcp_server.dogma_server")

    # Patch where it's imported, not where it's defined
    with (
        patch.object(dogma_server, "_normalize_path", side_effect=RuntimeError("path error")),
        patch.object(dogma_server._JSONL_QUEUE, "put_nowait"),
    ):
        result = dogma_server.normalize_path("/test")

    # The wrapper converts exceptions to error responses
    assert result["ok"] is False
    assert len(result["errors"]) > 0
    assert "path error" in result["errors"][0]
    assert result["result"] == ""


@_requires_mcp
def test_summarize_error_value_list_with_no_valid_summaries() -> None:
    """Coverage: list path where no items produce summaries (line 232 edge case)."""
    dogma_server = importlib.import_module("mcp_server.dogma_server")

    # List with only None values
    error_list = [None, None, None]
    result = dogma_server._summarize_error_value(error_list)

    # Should return None when no items produce valid summaries
    assert result is None
