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
    load_calibration_baselines,
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
class TestLoadCalibrationBaselines:
    """Test load_calibration_baselines()."""

    def test_load_calibration_baselines_success(self, tmp_path):
        """Test successful loading of calibration baselines from YAML."""
        thresholds_content = """
calibration_baseline:
  faithfulness_mean:
    mean: 0.85
    variance: 0.01
  error_rate_pct:
    mean: 2.5
    variance: 1.2
"""
        (tmp_path / "data").mkdir()
        (tmp_path / "data" / "governance-thresholds.yml").write_text(thresholds_content, encoding="utf-8")

        with patch("scripts.check_mcp_quality_gate._get_root", return_value=tmp_path):
            baselines = load_calibration_baselines(tmp_path)

        assert "faithfulness_mean" in baselines
        assert baselines["faithfulness_mean"]["mean"] == 0.85
        assert baselines["faithfulness_mean"]["variance"] == 0.01
        assert "error_rate_pct" in baselines
        assert baselines["error_rate_pct"]["mean"] == 2.5
        assert baselines["error_rate_pct"]["variance"] == 1.2

    def test_load_calibration_baselines_missing_file(self, tmp_path):
        """Test with missing governance-thresholds file."""
        with patch("scripts.check_mcp_quality_gate._get_root", return_value=tmp_path):
            baselines = load_calibration_baselines(tmp_path)

        assert baselines == {}


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

        exit_code, _ = check_thresholds(observations, thresholds, {})
        assert exit_code == 0

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

        exit_code, _ = check_thresholds(observations, thresholds, {})
        assert exit_code == 1

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
        exit_code, _ = check_thresholds(observations, thresholds, {})
        assert exit_code == 1

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

        exit_code, _ = check_thresholds(observations, thresholds, {}, dry_run=True)
        assert exit_code == 0

    def test_check_thresholds_no_observations(self):
        """Test with no observations."""
        thresholds = {
            "fail_if_faithfulness_below": 0.75,
            "fail_if_tool_error_rate_above_pct": 5.0,
        }

        exit_code, _ = check_thresholds([], thresholds, {})
        assert exit_code == 2

    def test_calibration_baseline_within_variance_passes(self):
        """Test that metrics within calibration variance pass the gate."""
        # Mock calibration baseline: mean=54.698, variance=2450.113
        # Current metric = mean + variance (56.698 + 2450.113 = 2506.811)
        # This is delta = 2452.113, which is < variance × 2 (4900.226), so should PASS
        observations = [
            {"faithfulness": 0.8, "is_error": False},
            {"faithfulness": 0.82, "is_error": False},
            {"faithfulness": 0.85, "is_error": False},
        ]
        thresholds = {
            "fail_if_faithfulness_below": 0.75,
            "fail_if_tool_error_rate_above_pct": 5.0,
        }
        calibration_baselines = {
            "faithfulness_mean": {
                "mean": 0.81,  # Mean of observations is ~0.823
                "variance": 0.01,  # Delta ~0.013 < variance × 2 (0.02)
            }
        }

        exit_code, _ = check_thresholds(observations, thresholds, calibration_baselines)
        assert exit_code == 0

    def test_calibration_baseline_exceeds_variance_fails(self):
        """Test that metrics exceeding calibration variance × 2 fail the gate."""
        # Current metric = mean + (variance × 3)
        # This exceeds variance × 2 threshold, so should FAIL
        observations = [
            {"faithfulness": 0.5, "is_error": False},
            {"faithfulness": 0.52, "is_error": False},
            {"faithfulness": 0.48, "is_error": False},
        ]
        thresholds = {
            "fail_if_faithfulness_below": 0.75,
            "fail_if_tool_error_rate_above_pct": 5.0,
        }
        calibration_baselines = {
            "faithfulness_mean": {
                "mean": 0.85,  # Mean of observations is 0.5, delta = 0.35
                "variance": 0.05,  # variance × 2 = 0.1, so delta 0.35 > 0.1 → FAIL
            }
        }

        exit_code, _ = check_thresholds(observations, thresholds, calibration_baselines)
        assert exit_code == 1


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


@pytest.mark.io
class TestRAGASMetrics:
    """Test RAGAS complement metric extraction and baseline checks (Phase 7)."""

    def test_ragas_metrics_extraction(self):
        """Test extraction of response_completeness, parameter_efficiency, output_completeness."""
        observations = [
            {
                "faithfulness": 0.8,
                "response_completeness": 0.9,
                "parameter_efficiency": 0.85,
                "output_completeness": 0.92,
                "is_error": False,
            },
            {
                "faithfulness": 0.82,
                "response_completeness": 0.88,
                "parameter_efficiency": 0.83,
                "output_completeness": 0.91,
                "is_error": False,
            },
        ]
        thresholds = {
            "fail_if_faithfulness_below": 0.75,
            "fail_if_tool_error_rate_above_pct": 5.0,
        }

        exit_code, result = check_thresholds(observations, thresholds, {}, json_output=True)
        assert exit_code == 0
        assert result is not None
        assert result["metrics"]["response_completeness_mean"] == pytest.approx(0.89, abs=0.01)
        assert result["metrics"]["parameter_efficiency_mean"] == pytest.approx(0.84, abs=0.01)
        assert result["metrics"]["output_completeness_mean"] == pytest.approx(0.915, abs=0.01)

    def test_ragas_metrics_missing_values_skipped(self):
        """Test that missing RAGAS metric values are skipped gracefully."""
        observations = [
            {"faithfulness": 0.8, "is_error": False},  # No RAGAS metrics
            {
                "faithfulness": 0.82,
                "response_completeness": 0.9,
                "is_error": False,
            },  # Partial
        ]
        thresholds = {
            "fail_if_faithfulness_below": 0.75,
            "fail_if_tool_error_rate_above_pct": 5.0,
        }

        exit_code, result = check_thresholds(observations, thresholds, {}, json_output=True)
        assert exit_code == 0
        assert result is not None
        assert result["metrics"]["response_completeness_mean"] == 0.9  # Only 1 value
        assert result["metrics"]["parameter_efficiency_mean"] is None  # No values
        assert result["metrics"]["output_completeness_mean"] is None  # No values

    def test_ragas_baseline_checks(self):
        """Test RAGAS metrics checked against calibration baselines."""
        observations = [
            {
                "faithfulness": 0.8,
                "response_completeness": 0.5,  # Well below baseline
                "parameter_efficiency": 0.75,
                "output_completeness": 0.78,
                "is_error": False,
            },
        ]
        thresholds = {
            "fail_if_faithfulness_below": 0.75,
            "fail_if_tool_error_rate_above_pct": 5.0,
        }
        baselines = {
            "response_completeness_mean": {
                "mean": 0.85,  # Current 0.5, delta = -0.35
                "variance": 0.05,  # variance × 2 = 0.1, so delta 0.35 > 0.1 → FAIL
            },
        }

        exit_code, result = check_thresholds(observations, thresholds, baselines, json_output=True)
        assert exit_code == 1  # Should fail due to response_completeness below baseline
        assert len(result["violations"]) > 0
        assert any("response_completeness" in v for v in result["violations"])

    def test_json_output_format_validation(self):
        """Test JSON output schema matches documented format."""
        observations = [
            {
                "faithfulness": 0.8,
                "response_completeness": 0.9,
                "parameter_efficiency": 0.85,
                "output_completeness": 0.92,
                "is_error": False,
            },
        ]
        thresholds = {
            "fail_if_faithfulness_below": 0.75,
            "fail_if_tool_error_rate_above_pct": 5.0,
        }
        baselines = {
            "faithfulness_mean": {"mean": 0.8, "variance": 0.01},
        }

        exit_code, result = check_thresholds(observations, thresholds, baselines, json_output=True)

        # Validate schema structure
        assert "status" in result
        assert result["status"] in ["pass", "fail", "no_data"]
        assert "sample_size" in result
        assert result["sample_size"] == 1
        assert "metrics" in result
        assert "faithfulness_mean" in result["metrics"]
        assert "error_rate_pct" in result["metrics"]
        assert "response_completeness_mean" in result["metrics"]
        assert "parameter_efficiency_mean" in result["metrics"]
        assert "output_completeness_mean" in result["metrics"]
        assert "violations" in result
        assert isinstance(result["violations"], list)
        assert "baselines" in result
        assert "faithfulness_mean" in result["baselines"]
        assert result["baselines"]["faithfulness_mean"] == {"mean": 0.8, "variance": 0.01}
