import json
from pathlib import Path

import pytest

from scripts.check_mcp_quality_gate import main as gate_main


@pytest.mark.io
def test_quality_gate_passes_when_thresholds_met(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    payload = {
        "tool_name": "query_docs",
        "metrics": {
            "performance": {"error_rate_pct": 2.0, "sample_size": 100, "window_calls": 100},
            "semantic": {"faithfulness": 0.82},
        },
    }
    (tmp_path / "mcp-quality-query_docs-2026-03-27.json").write_text(json.dumps(payload), encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        [
            "scripts/check_mcp_quality_gate.py",
            "--input-glob",
            str(tmp_path / "mcp-quality-*.json"),
        ],
    )

    assert gate_main() == 0


@pytest.mark.io
def test_quality_gate_fails_when_thresholds_breached(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    payload = {
        "tool_name": "query_docs",
        "metrics": {
            "performance": {"error_rate_pct": 8.0, "sample_size": 100, "window_calls": 100},
            "semantic": {"faithfulness": 0.70},
        },
    }
    (tmp_path / "mcp-quality-query_docs-2026-03-27.json").write_text(json.dumps(payload), encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        [
            "scripts/check_mcp_quality_gate.py",
            "--input-glob",
            str(tmp_path / "mcp-quality-*.json"),
        ],
    )

    assert gate_main() == 1


@pytest.mark.io
def test_quality_gate_fails_for_insufficient_window(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    payload = {
        "tool_name": "query_docs",
        "metrics": {
            "performance": {"error_rate_pct": 1.0, "sample_size": 20, "window_calls": 100},
            "semantic": {"faithfulness": 0.95},
        },
    }
    (tmp_path / "mcp-quality-query_docs-2026-03-27.json").write_text(json.dumps(payload), encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        [
            "scripts/check_mcp_quality_gate.py",
            "--input-glob",
            str(tmp_path / "mcp-quality-*.json"),
        ],
    )

    assert gate_main() == 1


@pytest.mark.io
def test_quality_gate_fails_for_window_mismatch(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    payload = {
        "tool_name": "query_docs",
        "metrics": {
            "performance": {"error_rate_pct": 1.0, "sample_size": 100, "window_calls": 200},
            "semantic": {"faithfulness": 0.95},
        },
    }
    (tmp_path / "mcp-quality-query_docs-2026-03-27.json").write_text(json.dumps(payload), encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        [
            "scripts/check_mcp_quality_gate.py",
            "--input-glob",
            str(tmp_path / "mcp-quality-*.json"),
        ],
    )

    assert gate_main() == 1
