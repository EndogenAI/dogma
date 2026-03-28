import json
from pathlib import Path

import pytest

from scripts.capture_mcp_metrics import (
    CANONICAL_TOOLS,
    summarize_tool,
)
from scripts.capture_mcp_metrics import (
    main as capture_main,
)


@pytest.mark.io
def test_summarize_tool_aggregates_basic_metrics() -> None:
    observations = [
        {
            "tool_name": "query_docs",
            "latency_ms": 120.0,
            "is_error": False,
            "faithfulness": 0.9,
            "answer_relevance": 0.8,
            "context_precision": 0.7,
            "correctness": 1.0,
            "completeness": 0.9,
            "precision": 0.8,
            "severity_level": 1.0,
            "umux_lite_equivalent": 70.0,
        },
        {
            "tool_name": "query_docs",
            "latency_ms": 180.0,
            "is_error": True,
            "faithfulness": 0.7,
            "answer_relevance": 0.6,
            "context_precision": 0.5,
            "correctness": 0.6,
            "completeness": 0.5,
            "precision": 0.7,
            "severity_level": 2.0,
            "umux_lite_equivalent": 66.0,
        },
    ]

    summary = summarize_tool("query_docs", observations)

    assert summary.sample_size == 2
    assert summary.tool_error_count == 1
    assert summary.error_rate_pct == 50.0
    assert summary.faithfulness == pytest.approx(0.8)
    assert summary.answer_relevance == pytest.approx(0.7)
    assert summary.context_precision == pytest.approx(0.6)
    assert summary.correctness == pytest.approx(0.8)
    assert summary.completeness == pytest.approx(0.7)
    assert summary.precision == pytest.approx(0.75)
    assert summary.severity_level_mean == pytest.approx(1.5)
    assert summary.umux_lite_equivalent == pytest.approx(68.0)


@pytest.mark.io
def test_capture_main_writes_all_tools(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    input_jsonl = tmp_path / "tool_calls.jsonl"
    input_jsonl.write_text(
        "\n".join(
            [
                json.dumps({"tool_name": "query_docs", "latency_ms": 100, "is_error": False}),
                json.dumps({"tool_name": "check_substrate", "latency_ms": 200, "is_error": True}),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    output_dir = tmp_path / "metrics"
    monkeypatch.setattr(
        "sys.argv",
        [
            "scripts/capture_mcp_metrics.py",
            "--all",
            "--input-jsonl",
            str(input_jsonl),
            "--output-dir",
            str(output_dir),
            "--date",
            "2026-03-27",
        ],
    )

    exit_code = capture_main()
    assert exit_code == 0

    written = sorted(output_dir.glob("mcp-quality-*-2026-03-27.json"))
    assert len(written) == len(CANONICAL_TOOLS)

    query_payload = json.loads((output_dir / "mcp-quality-query_docs-2026-03-27.json").read_text(encoding="utf-8"))
    assert query_payload["tool_name"] == "query_docs"
    assert query_payload["metrics"]["performance"]["sample_size"] == 1
    assert query_payload["metrics"]["performance"]["window_calls"] == 100


@pytest.mark.io
def test_summarize_tool_uses_last_100_calls() -> None:
    observations = []
    for i in range(120):
        observations.append(
            {
                "tool_name": "query_docs",
                "latency_ms": float(i),
                "is_error": False,
                "faithfulness": 0.8,
            }
        )

    summary = summarize_tool("query_docs", observations, window_calls=100)
    assert summary.sample_size == 100
    # Window should contain i=20..119, so p95 should be from this tail range.
    assert summary.latency_ms_p95 is not None
    assert summary.latency_ms_p95 >= 110.0
