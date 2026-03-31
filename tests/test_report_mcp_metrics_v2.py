"""Tests for scripts/report_mcp_metrics_v2.py."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# Import the script module
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import report_mcp_metrics_v2 as report_script


@pytest.fixture
def sample_jsonl(tmp_path: Path) -> Path:
    """Create a sample JSONL file with known values."""
    jsonl_path = tmp_path / "test_metrics.jsonl"
    records = [
        {
            "tool_name": "query_docs",
            "timestamp_utc": "2026-03-30T10:00:00+00:00",
            "latency_ms": 50.0,
            "is_error": False,
        },
        {
            "tool_name": "query_docs",
            "timestamp_utc": "2026-03-30T10:01:00+00:00",
            "latency_ms": 60.0,
            "is_error": False,
        },
        {
            "tool_name": "query_docs",
            "timestamp_utc": "2026-03-30T10:02:00+00:00",
            "latency_ms": 100.0,
            "is_error": True,
            "error_type": "tool_error",
            "error_message": "docs index unavailable",
        },
        {
            "tool_name": "validate_synthesis",
            "timestamp_utc": "2026-03-30T10:03:00+00:00",
            "latency_ms": 80.0,
            "is_error": False,
        },
        {
            "tool_name": "validate_synthesis",
            "timestamp_utc": "2026-03-30T10:04:00+00:00",
            "latency_ms": 90.0,
            "is_error": False,
        },
    ]
    with jsonl_path.open("w") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")
    return jsonl_path


@pytest.mark.io
def test_read_jsonl(sample_jsonl: Path):
    """Test JSONL file reading."""
    records = report_script.read_jsonl(str(sample_jsonl))
    assert len(records) == 5
    assert records[0]["tool_name"] == "query_docs"
    assert records[0]["latency_ms"] == 50.0


@pytest.mark.io
def test_aggregate_metrics(sample_jsonl: Path):
    """Test metric aggregation logic."""
    records = report_script.read_jsonl(str(sample_jsonl))
    metrics = report_script.aggregate_metrics(records)

    # Check global stats
    assert metrics["total_calls"] == 5
    assert metrics["global_success_rate"] == 80.0  # 4 success / 5 total

    # Check per-tool stats
    query_stats = metrics["tool_stats"]["query_docs"]
    assert query_stats["call_count"] == 3
    assert query_stats["success_count"] == 2
    assert query_stats["success_rate"] == pytest.approx(66.67, rel=0.01)
    assert query_stats["mean_duration_ms"] == pytest.approx(70.0)  # (50 + 60 + 100) / 3
    assert query_stats["max_duration_ms"] == 100.0
    assert metrics["error_stats"]["query_docs"]["error_count"] == 1
    assert metrics["error_stats"]["query_docs"]["error_types"] == {"tool_error": 1}
    assert metrics["error_stats"]["query_docs"]["error_messages"] == {"docs index unavailable": 1}

    validate_stats = metrics["tool_stats"]["validate_synthesis"]
    assert validate_stats["call_count"] == 2
    assert validate_stats["success_rate"] == 100.0
    assert validate_stats["mean_duration_ms"] == pytest.approx(85.0)  # (80 + 90) / 2


@pytest.mark.io
def test_handle_missing_latency(tmp_path: Path):
    """Test handling records without latency_ms field."""
    jsonl_path = tmp_path / "no_latency.jsonl"
    records = [
        {"tool_name": "query_docs", "timestamp_utc": "2026-03-30T10:00:00+00:00", "is_error": False},
        {
            "tool_name": "query_docs",
            "timestamp_utc": "2026-03-30T10:01:00+00:00",
            "latency_ms": 50.0,
            "is_error": False,
        },
    ]
    with jsonl_path.open("w") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")

    loaded = report_script.read_jsonl(str(jsonl_path))
    metrics = report_script.aggregate_metrics(loaded)

    # Should compute mean only from records with latency_ms
    assert metrics["tool_stats"]["query_docs"]["mean_duration_ms"] == 50.0
    assert metrics["tool_stats"]["query_docs"]["max_duration_ms"] == 50.0


@pytest.mark.io
def test_p95_calculation_insufficient_samples(tmp_path: Path):
    """Test p95 returns None when <20 samples."""
    jsonl_path = tmp_path / "few_samples.jsonl"
    records = [
        {
            "tool_name": "query_docs",
            "timestamp_utc": f"2026-03-30T10:{i:02d}:00+00:00",
            "latency_ms": float(i),
            "is_error": False,
        }
        for i in range(10)
    ]
    with jsonl_path.open("w") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")

    loaded = report_script.read_jsonl(str(jsonl_path))
    metrics = report_script.aggregate_metrics(loaded)

    # Should return None for p95 with <20 samples
    assert metrics["tool_stats"]["query_docs"]["p95_duration_ms"] is None


@pytest.mark.io
def test_p95_calculation_sufficient_samples(tmp_path: Path):
    """Test p95 calculation with ≥20 samples."""
    jsonl_path = tmp_path / "many_samples.jsonl"
    records = [
        {
            "tool_name": "query_docs",
            "timestamp_utc": f"2026-03-30T10:{i:02d}:00+00:00",
            "latency_ms": float(i * 10),
            "is_error": False,
        }
        for i in range(25)
    ]
    with jsonl_path.open("w") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")

    loaded = report_script.read_jsonl(str(jsonl_path))
    metrics = report_script.aggregate_metrics(loaded)

    # Should compute p95 using linear interpolation:
    # 25 values [0, 10, 20, ..., 240]; index at 95th percentile = 0.95 * 24 = 22.8
    # interpolate between sorted[22]=220 and sorted[23]=230 → 220 + 0.8*(230-220) = 228.0
    assert metrics["tool_stats"]["query_docs"]["p95_duration_ms"] is not None
    assert metrics["tool_stats"]["query_docs"]["p95_duration_ms"] == pytest.approx(228.0, rel=0.1)


@pytest.mark.io
def test_markdown_rendering(sample_jsonl: Path, tmp_path: Path):
    """Test markdown report generation."""
    records = report_script.read_jsonl(str(sample_jsonl))
    metrics = report_script.aggregate_metrics(records)
    markdown = report_script.build_markdown(metrics, str(sample_jsonl))

    # Check key sections exist
    assert "# MCP Metrics Report" in markdown
    assert "## Summary Statistics" in markdown
    assert "## Per-Tool Breakdown" in markdown
    assert "## Error Summary" in markdown
    assert "## Top 5 Slowest Calls" in markdown

    # Check values appear
    assert "Total Records**: 5" in markdown
    assert "80.0%" in markdown  # Global success rate
    assert "docs index unavailable (1)" in markdown


@pytest.mark.io
def test_format_value_null_safe():
    """Test null-safe value formatting."""
    assert report_script.format_value(None) == "N/A"
    assert report_script.format_value(42.3456, decimals=1) == "42.3"
    assert report_script.format_value(100.0, decimals=2) == "100.00"


@pytest.mark.io
def test_missing_input_file():
    """Test handling of missing input file."""
    with pytest.raises(FileNotFoundError, match="Input file not found"):
        report_script.read_jsonl("/nonexistent/path.jsonl")


@pytest.mark.io
def test_empty_jsonl(tmp_path: Path):
    """Test handling of empty JSONL file."""
    empty_path = tmp_path / "empty.jsonl"
    empty_path.touch()

    records = report_script.read_jsonl(str(empty_path))
    assert len(records) == 0
