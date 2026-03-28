#!/usr/bin/env python3
"""Fail/Pass gate for MCP quality metrics.

Inputs:
- Per-tool metric artifacts matched by `--input-glob`.

Outputs:
- PASS/FAIL summary lines written to stdout.

Exit codes:
- 0: all tools satisfy thresholds and exact window contract
- 1: missing files, contract mismatch, or threshold failure

Fails when:
- faithfulness < threshold
- error rate > threshold
- sample/window contract is invalid (not exact last-N window)

Usage:
- uv run python scripts/check_mcp_quality_gate.py --input-glob "docs/metrics/mcp-quality-*.json"
"""

from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check MCP quality gate thresholds from metrics artifacts.")
    parser.add_argument("--input-glob", default="docs/metrics/mcp-quality-*.json", help="Glob of metrics JSON files")
    parser.add_argument("--faithfulness-threshold", type=float, default=0.75)
    parser.add_argument("--error-rate-threshold-pct", type=float, default=5.0)
    parser.add_argument("--window-calls", type=int, default=100)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    files = [Path(p) for p in sorted(glob.glob(args.input_glob))]
    if not files:
        print(f"FAIL: no metrics files found for glob {args.input_glob}")
        return 1

    failures: list[str] = []
    for path in files:
        payload = json.loads(path.read_text(encoding="utf-8"))
        tool = payload.get("tool_name", path.name)
        semantic = payload.get("metrics", {}).get("semantic", {})
        perf = payload.get("metrics", {}).get("performance", {})

        faithfulness = semantic.get("faithfulness")
        error_rate = perf.get("error_rate_pct")
        sample_size = perf.get("sample_size")
        artifact_window = perf.get("window_calls")

        if artifact_window is None or int(artifact_window) != args.window_calls:
            failures.append(
                f"{tool}: artifact window_calls={artifact_window} does not match required {args.window_calls}"
            )
            continue

        if sample_size is None or int(sample_size) != args.window_calls:
            failures.append(
                f"{tool}: sample_size={sample_size} does not equal required window_calls={args.window_calls}"
            )
            continue

        if faithfulness is None:
            failures.append(f"{tool}: missing required semantic.faithfulness")
            continue
        if error_rate is None:
            failures.append(f"{tool}: missing required performance.error_rate_pct")
            continue

        if float(faithfulness) < args.faithfulness_threshold:
            failures.append(f"{tool}: faithfulness={faithfulness:.3f} < {args.faithfulness_threshold:.3f}")
        if float(error_rate) > args.error_rate_threshold_pct:
            failures.append(f"{tool}: error_rate_pct={error_rate:.3f} > {args.error_rate_threshold_pct:.3f}")

    if failures:
        print("FAIL")
        for item in failures:
            print(f"- {item}")
        return 1

    print("PASS")
    print("All tools satisfied:")
    print(f"- faithfulness >= {args.faithfulness_threshold:.2f}")
    print(f"- error_rate_pct <= {args.error_rate_threshold_pct:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
