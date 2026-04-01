#!/usr/bin/env python3
"""
check_mcp_quality_gate.py — Validate MCP metrics against quality thresholds.

Purpose:
    Reads JSONL observation records from .cache/mcp-metrics/, computes aggregate metrics
    (faithfulness mean, error_rate %), and compares them against thresholds defined in
    data/mcp-metrics-schema.yml. Implements the MCP Quality Gate as a programmatic check.

RAGAS Metric Mapping (Sprint 22 Phase 7):
    The following RAGAS metrics apply to MCP tool call observability:
    - faithfulness: Does the tool output match factual grounding? (0.0–1.0)
    - response_completeness: Does the tool output cover all required information? (0.0–1.0)
    - parameter_efficiency: Are tool parameters minimal and relevant? (0.0–1.0)
    - output_completeness: Does the output include all expected fields? (0.0–1.0)

    These metrics are extracted from JSONL records when present; missing values are skipped.

Nielsen Usability Heuristics as MCP Observability Interpretation Guidance:
    1. Visibility of system status — OTel span duration/latency (covered in Phase 4)
    2. Match between system and real world — tool_name clarity (naming conventions)
    3. User control and freedom — tool error recovery (is_error, retries)
    4. Consistency and standards — parameter schemas (validated pre-call)
    5. Error prevention — parameter validation (MCP layer)
    6. Recognition rather than recall — span attributes (tool metadata)
    7. Flexibility and efficiency — parameter_efficiency metric (RAGAS)
    8. Aesthetic and minimalist design — output_completeness metric (RAGAS)
    9. Help users recognize/diagnose/recover — error messages (is_error + error_type)
    10. Help and documentation — tool docstrings (not measured)

    Existing OTel spans capture visibility (H1), error recovery (H3, H9), and latency (H1).
    RAGAS metrics complement with response quality (faithfulness, completeness).

Inputs:
    --evaluation-window N  — Number of most recent records to evaluate (default: 100).
    --dry-run              — Show what would be checked without failing the gate.
    --json                 — Emit structured JSON output to stdout instead of human-readable text.

Outputs:
    Prints a summary of metrics and threshold violations to stdout (or JSON if --json).
    Exit code 0 if thresholds pass; 1 if thresholds breached; 2 if no data or I/O error.

JSON Output Schema (--json flag):
    {
        "status": "pass" | "fail" | "no_data",
        "sample_size": int,
        "metrics": {
            "faithfulness_mean": float | null,
            "error_rate_pct": float,
            "response_completeness_mean": float | null,
            "parameter_efficiency_mean": float | null,
            "output_completeness_mean": float | null
        },
        "violations": [str],
        "baselines": {
            "faithfulness_mean": {"mean": float, "variance": float} | null,
            "error_rate_pct": {"mean": float, "variance": float} | null,
            "response_completeness_mean": {"mean": float, "variance": float} | null,
            "parameter_efficiency_mean": {"mean": float, "variance": float} | null,
            "output_completeness_mean": {"mean": float, "variance": float} | null
        }
    }

Usage:
    # Default evaluation (last 100 records):
    uv run python scripts/check_mcp_quality_gate.py

    # Custom evaluation window:
    uv run python scripts/check_mcp_quality_gate.py --evaluation-window 200

    # Dry-run to preview metrics without failing:
    uv run python scripts/check_mcp_quality_gate.py --dry-run

    # JSON output for CI integration:
    uv run python scripts/check_mcp_quality_gate.py --json

Exit codes:
    0 — success: all thresholds pass
    1 — threshold breach (faithfulness < 0.75 or error_rate > 5%)
    2 — no data available or I/O error
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from statistics import mean

import yaml


def _get_root() -> Path:
    """Return the workspace root (parent of scripts/). Monkeypatched in tests."""
    return Path(__file__).resolve().parent.parent


def load_thresholds(root: Path) -> dict:
    """Load quality_gate_thresholds from data/mcp-metrics-schema.yml.

    Returns:
        Dict with keys: fail_if_faithfulness_below, fail_if_tool_error_rate_above_pct.
        Returns empty dict on error.
    """
    schema_path = root / "data" / "mcp-metrics-schema.yml"
    try:
        with schema_path.open("r", encoding="utf-8") as f:
            schema = yaml.safe_load(f)
        return schema.get("quality_gate_thresholds", {})
    except Exception as exc:
        print(f"ERROR: Failed to load {schema_path}: {exc}", file=sys.stderr)
        return {}


def load_calibration_baselines(root: Path) -> dict:
    """Load calibration_baseline from data/governance-thresholds.yml.

    Returns:
        Dict with per-metric baselines (mean, variance). Empty dict if not found or on error.
        Expected structure: {
            "faithfulness_mean": {"mean": float, "variance": float},
            "error_rate_pct": {"mean": float, "variance": float}
        }
    """
    thresholds_path = root / "data" / "governance-thresholds.yml"
    try:
        with thresholds_path.open("r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        baseline = config.get("calibration_baseline", {})
        # Return the full baseline dict; caller will check for per-metric entries
        return baseline
    except Exception as exc:
        print(f"WARNING: Failed to load {thresholds_path}: {exc}", file=sys.stderr)
        return {}


def load_metrics(root: Path, window: int) -> list[dict] | None:
    """Load last N JSONL records from .cache/mcp-metrics/.

    Args:
        root: Workspace root path.
        window: Number of most recent records to load.

    Returns:
        List of observation dicts, or None on I/O error. Empty list if dir exists but is empty.
    """
    metrics_dir = root / ".cache" / "mcp-metrics"
    if not metrics_dir.exists():
        return []

    observations = []
    try:
        # Read all .jsonl files in directory
        for jsonl_file in sorted(metrics_dir.glob("*.jsonl")):
            with jsonl_file.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        observations.append(json.loads(line))
    except Exception as exc:
        print(f"ERROR: Failed to read metrics from {metrics_dir}: {exc}", file=sys.stderr)
        return None

    # Return last N records
    return observations[-window:] if window > 0 else observations


def check_thresholds(
    observations: list[dict],
    thresholds: dict,
    baselines: dict,
    dry_run: bool = False,
    json_output: bool = False,
) -> tuple[int, dict | None]:
    """Compute metrics and check against thresholds or calibration baselines.

    Args:
        observations: List of JSONL observation records.
        thresholds: Dict with fail_if_faithfulness_below, fail_if_tool_error_rate_above_pct.
        baselines: Dict with per-metric calibration baselines (mean, variance).
        dry_run: If True, print results but always return 0.
        json_output: If True, return structured dict instead of printing.

    Returns:
        Tuple of (exit_code, json_dict). json_dict is None if json_output=False.
        Exit code: 0 if thresholds pass, 1 if breached, 2 if no data.
    """
    if not observations:
        if json_output:
            result = {
                "status": "no_data",
                "sample_size": 0,
                "metrics": {},
                "violations": [],
                "baselines": {},
            }
            return (0 if dry_run else 2, result)
        else:
            print("WARNING: No observations to evaluate.", file=sys.stderr)
            return (0 if dry_run else 2, None)

    # Extract metric values — validate each entry to avoid ValueError on bad input
    faithfulness_values = []
    response_completeness_values = []
    parameter_efficiency_values = []
    output_completeness_values = []

    for r in observations:
        # Faithfulness
        raw = r.get("faithfulness")
        if raw is not None:
            try:
                faithfulness_values.append(float(raw))
            except (ValueError, TypeError):
                if not json_output:
                    print(
                        f"WARNING: skipping invalid faithfulness value {raw!r} in record {r}",
                        file=sys.stderr,
                    )

        # Response completeness
        raw = r.get("response_completeness")
        if raw is not None:
            try:
                response_completeness_values.append(float(raw))
            except (ValueError, TypeError):
                if not json_output:
                    print(
                        f"WARNING: skipping invalid response_completeness value {raw!r}",
                        file=sys.stderr,
                    )

        # Parameter efficiency
        raw = r.get("parameter_efficiency")
        if raw is not None:
            try:
                parameter_efficiency_values.append(float(raw))
            except (ValueError, TypeError):
                if not json_output:
                    print(
                        f"WARNING: skipping invalid parameter_efficiency value {raw!r}",
                        file=sys.stderr,
                    )

        # Output completeness
        raw = r.get("output_completeness")
        if raw is not None:
            try:
                output_completeness_values.append(float(raw))
            except (ValueError, TypeError):
                if not json_output:
                    print(
                        f"WARNING: skipping invalid output_completeness value {raw!r}",
                        file=sys.stderr,
                    )

    # Count errors
    error_count = sum(1 for r in observations if bool(r.get("is_error")))
    sample_size = len(observations)
    error_rate_pct = (error_count / sample_size * 100.0) if sample_size > 0 else 0.0

    # Compute metric means
    faithfulness_mean = mean(faithfulness_values) if faithfulness_values else None
    response_completeness_mean = mean(response_completeness_values) if response_completeness_values else None
    parameter_efficiency_mean = mean(parameter_efficiency_values) if parameter_efficiency_values else None
    output_completeness_mean = mean(output_completeness_values) if output_completeness_values else None

    # Get static thresholds (fallback)
    min_faithfulness = thresholds.get("fail_if_faithfulness_below", 0.75)
    max_error_rate = thresholds.get("fail_if_tool_error_rate_above_pct", 5.0)

    # Print summary (text mode only)
    if not json_output:
        print(f"MCP Quality Gate Evaluation (n={sample_size}):")

    violations = []

    # Helper to check a metric against baseline or static threshold
    def _check_metric(
        metric_name: str,
        metric_value: float | None,
        baseline_key: str,
        static_threshold: float | None = None,
        lower_is_better: bool = False,
    ):
        if metric_value is None:
            if not json_output:
                print(f"  {metric_name}: N/A (no data)")
            return

        baseline = baselines.get(baseline_key, {})
        if "mean" in baseline and "variance" in baseline:
            # Use delta-vs-variance logic
            baseline_mean = baseline["mean"]
            baseline_var = baseline["variance"]
            variance_threshold = baseline_var * 2
            delta = metric_value - baseline_mean
            if not json_output:
                print(
                    f"  {metric_name}: {metric_value:.3f} "
                    f"(baseline: {baseline_mean:.3f}, delta: {delta:+.3f}, "
                    f"variance threshold: {variance_threshold:.3f})"
                )
            if lower_is_better:
                if delta > variance_threshold:  # Higher is worse
                    violations.append(
                        f"{baseline_key} delta {delta:.3f} exceeds "
                        f"variance threshold +{variance_threshold:.3f} (above baseline)"
                    )
            else:
                if delta < -variance_threshold:  # Lower is worse
                    violations.append(
                        f"{baseline_key} delta {delta:.3f} exceeds "
                        f"variance threshold {-variance_threshold:.3f} (below baseline)"
                    )
        elif static_threshold is not None:
            # Use static threshold
            if not json_output:
                op = "≤" if lower_is_better else "≥"
                print(f"  {metric_name}: {metric_value:.3f} (threshold: {op}{static_threshold})")
            if lower_is_better:
                if metric_value > static_threshold:
                    violations.append(f"{baseline_key} {metric_value:.3f} > {static_threshold}")
            else:
                if metric_value < static_threshold:
                    violations.append(f"{baseline_key} {metric_value:.3f} < {static_threshold}")
        else:
            # No threshold — informational only
            if not json_output:
                print(f"  {metric_name}: {metric_value:.3f} (no threshold)")

    # Check faithfulness
    _check_metric("Faithfulness (mean)", faithfulness_mean, "faithfulness_mean", min_faithfulness)

    # Check RAGAS complement metrics (placeholder baselines — no static thresholds yet)
    _check_metric("Response completeness (mean)", response_completeness_mean, "response_completeness_mean")
    _check_metric("Parameter efficiency (mean)", parameter_efficiency_mean, "parameter_efficiency_mean")
    _check_metric("Output completeness (mean)", output_completeness_mean, "output_completeness_mean")

    # Check error rate (lower is better)
    if not json_output:
        baseline_error = baselines.get("error_rate_pct", {})
        if "mean" in baseline_error and "variance" in baseline_error:
            baseline_mean = baseline_error["mean"]
            baseline_var = baseline_error["variance"]
            variance_threshold = baseline_var * 2
            delta = error_rate_pct - baseline_mean
            print(
                f"  Error rate: {error_rate_pct:.1f}% "
                f"(baseline: {baseline_mean:.1f}%, delta: {delta:+.1f}%, "
                f"variance threshold: {variance_threshold:.1f}%)"
            )
            if delta > variance_threshold:
                violations.append(
                    f"error_rate delta {delta:.1f}% exceeds "
                    f"variance threshold +{variance_threshold:.1f}% (above baseline)"
                )
        else:
            print(f"  Error rate: {error_rate_pct:.1f}% (threshold: ≤{max_error_rate}%)")
            if error_rate_pct > max_error_rate:
                violations.append(f"error_rate {error_rate_pct:.1f}% > {max_error_rate}%")
    else:
        # JSON mode — still check error rate for violations
        baseline_error = baselines.get("error_rate_pct", {})
        if "mean" in baseline_error and "variance" in baseline_error:
            baseline_mean = baseline_error["mean"]
            baseline_var = baseline_error["variance"]
            variance_threshold = baseline_var * 2
            delta = error_rate_pct - baseline_mean
            if delta > variance_threshold:
                violations.append(
                    f"error_rate delta {delta:.1f}% exceeds "
                    f"variance threshold +{variance_threshold:.1f}% (above baseline)"
                )
        else:
            if error_rate_pct > max_error_rate:
                violations.append(f"error_rate {error_rate_pct:.1f}% > {max_error_rate}%")

    # Return results
    if json_output:
        result = {
            "status": "fail" if violations else "pass",
            "sample_size": sample_size,
            "metrics": {
                "faithfulness_mean": faithfulness_mean,
                "error_rate_pct": error_rate_pct,
                "response_completeness_mean": response_completeness_mean,
                "parameter_efficiency_mean": parameter_efficiency_mean,
                "output_completeness_mean": output_completeness_mean,
            },
            "violations": violations,
            "baselines": {
                "faithfulness_mean": baselines.get("faithfulness_mean"),
                "error_rate_pct": baselines.get("error_rate_pct"),
                "response_completeness_mean": baselines.get("response_completeness_mean"),
                "parameter_efficiency_mean": baselines.get("parameter_efficiency_mean"),
                "output_completeness_mean": baselines.get("output_completeness_mean"),
            },
        }
        return (0 if dry_run else (1 if violations else 0), result)
    else:
        if violations:
            print("\nTHRESHOLD VIOLATIONS:")
            for v in violations:
                print(f"  ✗ {v}")
            return (0 if dry_run else 1, None)
        print("\n✓ All thresholds pass")
        return (0, None)


def main(argv: list[str] | None = None) -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate MCP metrics against quality gate thresholds.")
    parser.add_argument(
        "--evaluation-window",
        type=int,
        default=100,
        help="Number of most recent records to evaluate (default: 100)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show metrics without failing the gate",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit structured JSON output instead of human-readable text",
    )
    args = parser.parse_args(argv)

    root = _get_root()

    # Load thresholds
    thresholds = load_thresholds(root)
    if not thresholds:
        if args.json:
            result = {
                "status": "no_data",
                "sample_size": 0,
                "metrics": {},
                "violations": ["Failed to load thresholds from schema"],
                "baselines": {},
            }
            print(json.dumps(result, indent=2))
        else:
            print("ERROR: Failed to load thresholds from schema.", file=sys.stderr)
        return 2

    # Load calibration baselines
    baselines = load_calibration_baselines(root)

    # Load metrics
    observations = load_metrics(root, args.evaluation_window)
    if observations is None:
        if args.json:
            result = {
                "status": "no_data",
                "sample_size": 0,
                "metrics": {},
                "violations": ["Failed to read metrics from cache"],
                "baselines": {},
            }
            print(json.dumps(result, indent=2))
        return 2

    if not observations:
        if args.json:
            result = {
                "status": "no_data",
                "sample_size": 0,
                "metrics": {},
                "violations": [],
                "baselines": baselines,
            }
            print(json.dumps(result, indent=2))
        else:
            print("INFO: No MCP metrics found in .cache/mcp-metrics/", file=sys.stderr)
        return 0 if args.dry_run else 2

    # Check thresholds
    exit_code, result = check_thresholds(observations, thresholds, baselines, args.dry_run, args.json)

    if args.json and result is not None:
        print(json.dumps(result, indent=2))

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
