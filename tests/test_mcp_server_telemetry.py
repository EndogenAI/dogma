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
    monkeypatch.setattr(dogma_server, "_TRACER", tracer)
    monkeypatch.setattr(dogma_server, "_OP_DURATION_HISTOGRAM", histogram)

    result = dogma_server._run_with_mcp_telemetry(
        "query_docs",
        lambda: {"ok": False, "errors": ["boom"]},
    )

    assert result["ok"] is False
    assert tracer.last_span is not None
    assert tracer.last_span.attrs["gen_ai.tool.name"] == "query_docs"
    assert tracer.last_span.attrs["gen_ai.operation.name"] == "execute_tool"
    assert tracer.last_span.attrs["error.type"] == "tool_error"

    assert len(histogram.records) == 1
    _, attrs = histogram.records[0]
    assert attrs["gen_ai.tool.name"] == "query_docs"
    assert attrs["gen_ai.operation.name"] == "execute_tool"


def test_run_with_mcp_telemetry_records_error_on_exception(monkeypatch) -> None:
    tracer = _DummyTracer()
    histogram = _DummyHistogram()
    monkeypatch.setattr(dogma_server, "_TRACER", tracer)
    monkeypatch.setattr(dogma_server, "_OP_DURATION_HISTOGRAM", histogram)

    def _raise() -> dict:
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        dogma_server._run_with_mcp_telemetry("query_docs", _raise)

    assert tracer.last_span is not None
    assert tracer.last_span.attrs["error.type"] == "tool_error"
    assert len(histogram.records) == 1
