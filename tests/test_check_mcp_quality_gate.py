"""
test_check_mcp_quality_gate.py — Tests for check_mcp_quality_gate.py

Tests cover:
- Happy path: observations with faithfulness ≥ 0.75 and error_rate ≤ 5% pass
- Threshold breach: low faithfulness or high error_rate fails the gate
- No data: empty cache dir returns exit code 2
- Dry-run mode: shows metrics without failing the gate
- Schema loading: correct threshold values from data/mcp-metrics-schema.yml
"""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

# Ensure the module is imported for coverage tracking
import scripts.check_mcp_quality_gate as check_mcp_quality_gate_module  # noqa: F401
from scripts.check_mcp_quality_gate import (
    check_thresholds,
    load_metrics,
    load_thresholds,
    main,
)


@pytest.mark.io
class TestLoadThresholds:
    """Test load_thresholds()."""

    def test_load_thresholds_success(self, tmp_path):
        """Test successful loading of thresholds from schema YAML."""
        schema_content = """
quality_gate_thresholds:
  fail_if_faithfulness_below: 0.75
  fail_if_tool_error_rate_above_pct: 5.0
"""
        (tmp_path / "data").mkdir()
        (tmp_path / "data" / "mcp-metrics-schema.yml").write_text(schema_content, encoding="utf-8")

        with patch("scripts.check_mcp_quality_gate._get_root", return_value=tmp_path):
            thresholds = load_thresholds(tmp_path)

        assert thresholds["fail_if_faithfulness_below"] == 0.75
        assert thresholds["fail_if_tool_error_rate_above_pct"] == 5.0

    def test_load_thresholds_missing_file(self, tmp_path):
        """Test with missing schema file."""
        with patch("scripts.check_mcp_quality_gate._get_root", return_value=tmp_path):
            thresholds = load_thresholds(tmp_path)

        assert thresholds == {}


@pytest.mark.io
class TestLoadMetrics:
    """Test load_metrics()."""

    def test_load_metrics_success(self, tmp_path):
        """Test successful loading of JSONL metrics."""
        metrics_dir = tmp_path / ".cache" / "mcp-metrics"
        metrics_dir.mkdir(parents=True)

        # Write sample JSONL records
        jsonl_file = metrics_dir / "tool_calls.jsonl"
        observations = [
            {"tool_name": "query_docs", "faithfulness": 0.8, "is_error": False},
            {"tool_name": "query_docs", "faithfulness": 0.85, "is_error": False},
            {"tool_name": "query_docs", "faithfulness": 0.78, "is_error": True},
        ]
        with jsonl_file.open("w", encoding="utf-8") as f:
            for obs in observations:
                f.write(json.dumps(obs) + "\n")

        with patch("scripts.check_mcp_quality_gate._get_root", return_value=tmp_path):
            result = load_metrics(tmp_path, window=100)

        assert result is not None
        assert len(result) == 3
        assert result[0]["tool_name"] == "query_docs"

    def test_load_metrics_empty_dir(self, tmp_path):
        """Test with empty metrics dir."""
        metrics_dir = tmp_path / ".cache" / "mcp-metrics"
        metrics_dir.mkdir(parents=True)

        with patch("scripts.check_mcp_quality_gate._get_root", return_value=tmp_path):
            result = load_metrics(tmp_path, window=100)

        assert result == []

    def test_load_metrics_no_dir(self, tmp_path):
        """Test with missing metrics dir."""
        with patch("scripts.check_mcp_quality_gate._get_root", return_value=tmp_path):
            result = load_metrics(tmp_path, window=100)

        assert result == []

    def test_load_metrics_window_limit(self, tmp_path):
        """Test window limiting (last N records)."""
        metrics_dir = tmp_path / ".cache" / "mcp-metrics"
        metrics_dir.mkdir(parents=True)

        jsonl_file = metrics_dir / "tool_calls.jsonl"
        observations = [{"id": i, "faithfulness": 0.8, "is_error": False} for i in range(150)]
        with jsonl_file.open("w", encoding="utf-8") as f:
            for obs in observations:
                f.write(json.dumps(obs) + "\n")

        with patch("scripts.check_mcp_quality_gate._get_root", return_value=tmp_path):
            result = load_metrics(tmp_path, window=100)

        assert len(result) == 100
        assert result[0]["id"] == 50  # Last 100 records (50-149)


@pytest.mark.io
class TestCheckThresholds:
    """Test check_thresholds()."""

    def test_check_thresholds_pass(self):
        """Test threshold check passes when metrics are within bounds."""
        observations = [
            {"faithfulness": 0.8, "is_error": False},
            {"faithfulness": 0.82, "is_error": False},
            {"faithfulness": 0.78, "is_error": False},
        ]
        thresholds = {
            "fail_if_faithfulness_below": 0.75,
            "fail_if_tool_error_rate_above_pct": 5.0,
        }

        result = check_thresholds(observations, thresholds)
        assert result == 0

    def test_check_thresholds_fail_faithfulness(self):
        """Test threshold check fails when faithfulness is too low."""
        observations = [
            {"faithfulness": 0.6, "is_error": False},
            {"faithfulness": 0.65, "is_error": False},
            {"faithfulness": 0.62, "is_error": False},
        ]
        thresholds = {
            "fail_if_faithfulness_below": 0.75,
            "fail_if_tool_error_rate_above_pct": 5.0,
        }

        result = check_thresholds(observations, thresholds)
        assert result == 1

    def test_check_thresholds_fail_error_rate(self):
        """Test threshold check fails when error rate is too high."""
        observations = [
            {"faithfulness": 0.8, "is_error": True},
            {"faithfulness": 0.82, "is_error": True},
            {"faithfulness": 0.78, "is_error": False},
        ]
        thresholds = {
            "fail_if_faithfulness_below": 0.75,
            "fail_if_tool_error_rate_above_pct": 5.0,
        }

        # Error rate: 2/3 = 66.7% > 5%
        result = check_thresholds(observations, thresholds)
        assert result == 1

    def test_check_thresholds_dry_run(self):
        """Test dry-run mode always returns 0."""
        observations = [
            {"faithfulness": 0.5, "is_error": True},
            {"faithfulness": 0.4, "is_error": True},
        ]
        thresholds = {
            "fail_if_faithfulness_below": 0.75,
            "fail_if_tool_error_rate_above_pct": 5.0,
        }

        result = check_thresholds(observations, thresholds, dry_run=True)
        assert result == 0

    def test_check_thresholds_no_observations(self):
        """Test with no observations."""
        thresholds = {
            "fail_if_faithfulness_below": 0.75,
            "fail_if_tool_error_rate_above_pct": 5.0,
        }

        result = check_thresholds([], thresholds)
        assert result == 2


@pytest.mark.io
class TestMain:
    """Test main() integration."""

    def test_main_pass(self, tmp_path):
        """Test full integration with passing metrics."""
        # Setup schema
        (tmp_path / "data").mkdir()
        schema_content = """
quality_gate_thresholds:
  fail_if_faithfulness_below: 0.75
  fail_if_tool_error_rate_above_pct: 5.0
"""
        (tmp_path / "data" / "mcp-metrics-schema.yml").write_text(schema_content, encoding="utf-8")

        # Setup metrics
        metrics_dir = tmp_path / ".cache" / "mcp-metrics"
        metrics_dir.mkdir(parents=True)
        jsonl_file = metrics_dir / "tool_calls.jsonl"
        observations = [
            {"faithfulness": 0.8, "is_error": False},
            {"faithfulness": 0.85, "is_error": False},
        ]
        with jsonl_file.open("w", encoding="utf-8") as f:
            for obs in observations:
                f.write(json.dumps(obs) + "\n")

        with patch("scripts.check_mcp_quality_gate._get_root", return_value=tmp_path):
            result = main([])

        assert result == 0

    def test_main_fail(self, tmp_path):
        """Test full integration with failing metrics."""
        # Setup schema
        (tmp_path / "data").mkdir()
        schema_content = """
quality_gate_thresholds:
  fail_if_faithfulness_below: 0.75
  fail_if_tool_error_rate_above_pct: 5.0
"""
        (tmp_path / "data" / "mcp-metrics-schema.yml").write_text(schema_content, encoding="utf-8")

        # Setup metrics with low faithfulness
        metrics_dir = tmp_path / ".cache" / "mcp-metrics"
        metrics_dir.mkdir(parents=True)
        jsonl_file = metrics_dir / "tool_calls.jsonl"
        observations = [
            {"faithfulness": 0.6, "is_error": False},
            {"faithfulness": 0.65, "is_error": False},
        ]
        with jsonl_file.open("w", encoding="utf-8") as f:
            for obs in observations:
                f.write(json.dumps(obs) + "\n")

        with patch("scripts.check_mcp_quality_gate._get_root", return_value=tmp_path):
            result = main([])

        assert result == 1

    def test_main_no_data(self, tmp_path):
        """Test with no metrics available."""
        # Setup schema only
        (tmp_path / "data").mkdir()
        schema_content = """
quality_gate_thresholds:
  fail_if_faithfulness_below: 0.75
  fail_if_tool_error_rate_above_pct: 5.0
"""
        (tmp_path / "data" / "mcp-metrics-schema.yml").write_text(schema_content, encoding="utf-8")

        with patch("scripts.check_mcp_quality_gate._get_root", return_value=tmp_path):
            result = main([])

        assert result == 2
