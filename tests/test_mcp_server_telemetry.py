import pytest

pytest.importorskip("mcp.server.fastmcp")

from mcp_server import dogma_server


class _DummySpan:
    def __init__(self) -> None:
        self.attrs: dict[str, str] = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False

    def set_attribute(self, key: str, value: str) -> None:
        self.attrs[key] = value


class _DummyTracer:
    def __init__(self) -> None:
        self.last_span: _DummySpan | None = None

    def start_as_current_span(self, _name: str) -> _DummySpan:
        self.last_span = _DummySpan()
        return self.last_span


class _DummyHistogram:
    def __init__(self) -> None:
        self.records: list[tuple[float, dict[str, str]]] = []

    def record(self, value: float, attributes: dict[str, str]) -> None:
        self.records.append((value, attributes))


def test_run_with_mcp_telemetry_emits_semconv_fields(monkeypatch) -> None:
    tracer = _DummyTracer()
    histogram = _DummyHistogram()
    captured: list[dict] = []
    monkeypatch.setattr(dogma_server, "_TRACER", tracer)
    monkeypatch.setattr(dogma_server, "_OP_DURATION_HISTOGRAM", histogram)
    monkeypatch.setattr(dogma_server._JSONL_QUEUE, "put_nowait", captured.append)

    result = dogma_server._run_with_mcp_telemetry(
        "query_docs",
        lambda: {"ok": False, "errors": ["boom"]},
    )

    assert result["ok"] is False
    assert tracer.last_span is not None
    assert tracer.last_span.attrs["gen_ai.tool.name"] == "query_docs"
    assert tracer.last_span.attrs["gen_ai.operation.name"] == "execute_tool"
    assert tracer.last_span.attrs["error.type"] == "tool_error"
    assert tracer.last_span.attrs["error.message"] == "boom"
    assert len(captured) == 1
    assert captured[0]["error_message"] == "boom"

    assert len(histogram.records) == 1
    _, attrs = histogram.records[0]
    assert attrs["gen_ai.tool.name"] == "query_docs"
    assert attrs["gen_ai.operation.name"] == "execute_tool"


def test_run_with_mcp_telemetry_records_error_on_exception(monkeypatch) -> None:
    tracer = _DummyTracer()
    histogram = _DummyHistogram()
    captured: list[dict] = []
    monkeypatch.setattr(dogma_server, "_TRACER", tracer)
    monkeypatch.setattr(dogma_server, "_OP_DURATION_HISTOGRAM", histogram)
    monkeypatch.setattr(dogma_server._JSONL_QUEUE, "put_nowait", captured.append)

    def _raise() -> dict:
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        dogma_server._run_with_mcp_telemetry("query_docs", _raise)

    assert tracer.last_span is not None
    assert tracer.last_span.attrs["error.type"] == "tool_error"
    assert tracer.last_span.attrs["error.message"] == "boom"
    assert len(captured) == 1
    assert captured[0]["error_type"] == "RuntimeError"
    assert captured[0]["error_message"] == "boom"
    assert len(histogram.records) == 1


def test_run_with_mcp_telemetry_emits_ragas_span_attributes(monkeypatch) -> None:
    tracer = _DummyTracer()
    histogram = _DummyHistogram()
    captured: list[dict] = []
    monkeypatch.setattr(dogma_server, "_TRACER", tracer)
    monkeypatch.setattr(dogma_server, "_OP_DURATION_HISTOGRAM", histogram)
    monkeypatch.setattr(dogma_server._JSONL_QUEUE, "put_nowait", captured.append)

    result = dogma_server._run_with_mcp_telemetry(
        "query_docs",
        lambda: {"ok": True, "results": []},
    )

    assert result["ok"] is True
    assert tracer.last_span is not None

    # Verify all 4 RAGAS span attributes are present and numeric
    ragas_attrs = [
        "gen_ai.faithfulness",
        "gen_ai.answer_relevancy",
        "gen_ai.context_precision",
        "gen_ai.context_recall",
    ]
    for attr in ragas_attrs:
        assert attr in tracer.last_span.attrs
        value = float(tracer.last_span.attrs[attr])
        assert 0.0 <= value <= 1.0
