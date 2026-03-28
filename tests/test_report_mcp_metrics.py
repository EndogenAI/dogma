import json
from pathlib import Path

import pytest

from scripts.report_mcp_metrics import (
    build_markdown,
)
from scripts.report_mcp_metrics import (
    main as report_main,
)


def test_build_markdown_contains_table_rows() -> None:
    rows = [
        {
            "tool_name": "query_docs",
            "metrics": {
                "performance": {"sample_size": 2, "latency_ms_p95": 120.0, "error_rate_pct": 0.0},
                "semantic": {"faithfulness": 0.9, "answer_relevance": 0.8, "context_precision": 0.7},
                "classical_quality": {"correctness": 1.0, "completeness": 0.9, "precision": 0.95},
                "defect": {"severity_level_mean": 1.0},
                "usability_proxy": {"umux_lite_equivalent": 70.0},
            },
        }
    ]

    md = build_markdown(rows)
    assert "| Tool | Samples |" in md
    assert "Correctness" in md
    assert "query_docs" in md
    assert "1.000" in md


@pytest.mark.io
def test_report_main_writes_output(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    input_file = tmp_path / "mcp-quality-query_docs-2026-03-27.json"
    input_file.write_text(
        json.dumps(
            {
                "tool_name": "query_docs",
                "metrics": {
                    "performance": {"sample_size": 1, "latency_ms_p95": 50.0, "error_rate_pct": 0.0},
                    "semantic": {"faithfulness": 0.8, "answer_relevance": 0.8, "context_precision": 0.8},
                    "classical_quality": {"correctness": 1.0, "completeness": 1.0, "precision": 1.0},
                    "defect": {"severity_level_mean": 1.0},
                    "usability_proxy": {"umux_lite_equivalent": 68.0},
                },
            }
        ),
        encoding="utf-8",
    )

    output = tmp_path / "report.md"
    monkeypatch.setattr(
        "sys.argv",
        [
            "scripts/report_mcp_metrics.py",
            "--input-glob",
            str(tmp_path / "mcp-quality-*.json"),
            "--output",
            str(output),
        ],
    )

    rc = report_main()
    assert rc == 0
    assert output.exists()
    assert "MCP Quality Metrics Report" in output.read_text(encoding="utf-8")
