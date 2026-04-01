#!/usr/bin/env python3
"""
check_mcp_quality_gate.py — Validate MCP metrics against quality thresholds.

Purpose:
    Reads JSONL observation records from .cache/mcp-metrics/, computes aggregate metrics
    (faithfulness mean, error_rate %), and compares them against thresholds defined in
    data/mcp-metrics-schema.yml. Implements the MCP Quality Gate as a programmatic check.

Inputs:
    --evaluation-window N  — Number of most recent records to evaluate (default: 100).
    --dry-run              — Show what would be checked without failing the gate.

Outputs:
    Prints a summary of metrics and threshold violations to stdout.
    Exit code 0 if thresholds pass; 1 if thresholds breached; 2 if no data or I/O error.

Usage:
    # Default evaluation (last 100 records):
    uv run python scripts/check_mcp_quality_gate.py

    # Custom evaluation window:
    uv run python scripts/check_mcp_quality_gate.py --evaluation-window 200

    # Dry-run to preview metrics without failing:
    uv run python scripts/check_mcp_quality_gate.py --dry-run

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
) -> int:
    """Compute metrics and check against thresholds or calibration baselines.

    Args:
        observations: List of JSONL observation records.
        thresholds: Dict with fail_if_faithfulness_below, fail_if_tool_error_rate_above_pct.
        baselines: Dict with per-metric calibration baselines (mean, variance).
        dry_run: If True, print results but always return 0.

    Returns:
        0 if thresholds pass, 1 if breached, 2 if no data.
    """
    if not observations:
        print("WARNING: No observations to evaluate.", file=sys.stderr)
        return 0 if dry_run else 2

    # Extract faithfulness values — validate each entry to avoid ValueError on bad input
    faithfulness_values = []
    for r in observations:
        raw = r.get("faithfulness")
        if raw is None:
            continue
        try:
            faithfulness_values.append(float(raw))
        except (ValueError, TypeError):
            print(
                f"WARNING: skipping invalid faithfulness value {raw!r} in record {r}",
                file=sys.stderr,
            )

    # Count errors
    error_count = sum(1 for r in observations if bool(r.get("is_error")))
    sample_size = len(observations)
    error_rate_pct = (error_count / sample_size * 100.0) if sample_size > 0 else 0.0

    # Compute faithfulness mean
    faithfulness_mean = mean(faithfulness_values) if faithfulness_values else None

    # Get static thresholds (fallback)
    min_faithfulness = thresholds.get("fail_if_faithfulness_below", 0.75)
    max_error_rate = thresholds.get("fail_if_tool_error_rate_above_pct", 5.0)

    # Print summary
    print(f"MCP Quality Gate Evaluation (n={sample_size}):")

    violations = []

    # Check faithfulness_mean — use calibration baseline if available
    if faithfulness_mean is not None:
        baseline_faith = baselines.get("faithfulness_mean", {})
        if "mean" in baseline_faith and "variance" in baseline_faith:
            # Use delta-vs-variance logic
            baseline_mean = baseline_faith["mean"]
            baseline_var = baseline_faith["variance"]
            variance_threshold = baseline_var * 2
            delta = faithfulness_mean - baseline_mean
            print(
                f"  Faithfulness (mean): {faithfulness_mean:.3f} "
                f"(baseline: {baseline_mean:.3f}, delta: {delta:+.3f}, "
                f"variance threshold: {variance_threshold:.3f})"
            )
            if delta < -variance_threshold:  # Negative delta = performance degraded
                violations.append(
                    f"faithfulness delta {delta:.3f} exceeds variance threshold "
                    f"{-variance_threshold:.3f} (below baseline)"
                )
        else:
            # Use static threshold
            print(f"  Faithfulness (mean): {faithfulness_mean:.3f} (threshold: ≥{min_faithfulness})")
            if faithfulness_mean < min_faithfulness:
                violations.append(f"faithfulness {faithfulness_mean:.3f} < {min_faithfulness}")
    else:
        print("  Faithfulness (mean): N/A (no data)")

    # Check error_rate_pct — use calibration baseline if available
    baseline_error = baselines.get("error_rate_pct", {})
    if "mean" in baseline_error and "variance" in baseline_error:
        # Use delta-vs-variance logic
        baseline_mean = baseline_error["mean"]
        baseline_var = baseline_error["variance"]
        variance_threshold = baseline_var * 2
        delta = error_rate_pct - baseline_mean
        print(
            f"  Error rate: {error_rate_pct:.1f}% "
            f"(baseline: {baseline_mean:.1f}%, delta: {delta:+.1f}%, "
            f"variance threshold: {variance_threshold:.1f}%)"
        )
        if delta > variance_threshold:  # Positive delta = more errors
            violations.append(
                f"error_rate delta {delta:.1f}% exceeds variance threshold +{variance_threshold:.1f}% (above baseline)"
            )
    else:
        # Use static threshold
        print(f"  Error rate: {error_rate_pct:.1f}% (threshold: ≤{max_error_rate}%)")
        if error_rate_pct > max_error_rate:
            violations.append(f"error_rate {error_rate_pct:.1f}% > {max_error_rate}%")

    if violations:
        print("\nTHRESHOLD VIOLATIONS:")
        for v in violations:
            print(f"  ✗ {v}")
        return 0 if dry_run else 1

    print("\n✓ All thresholds pass")
    return 0


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
    args = parser.parse_args(argv)

    root = _get_root()

    # Load thresholds
    thresholds = load_thresholds(root)
    if not thresholds:
        print("ERROR: Failed to load thresholds from schema.", file=sys.stderr)
        return 2

    # Load calibration baselines
    baselines = load_calibration_baselines(root)

    # Load metrics
    observations = load_metrics(root, args.evaluation_window)
    if observations is None:
        return 2

    if not observations:
        print("INFO: No MCP metrics found in .cache/mcp-metrics/", file=sys.stderr)
        return 0 if args.dry_run else 2

    # Check thresholds
    return check_thresholds(observations, thresholds, baselines, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
