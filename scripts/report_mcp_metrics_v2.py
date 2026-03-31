#!/usr/bin/env python3
"""Generate markdown report from MCP metrics JSONL (stdin or file).

Reads raw JSONL tool-call observations and computes aggregate metrics per tool.
Minimum viable pipeline for Sprint 20 — stdlib only, no external dependencies.

Inputs:
- JSONL file path via `--input` (default: .cache/mcp-metrics/tool_calls.jsonl)
- Each line: {"tool_name": str, "timestamp_utc": str, "latency_ms": float, "is_error": bool, ...}

Outputs:
- Markdown report to stdout or `--output` path
- Summary stats: total calls, success rate, mean duration
- Per-tool breakdown: call count, success %, mean/p95/max duration
- Top 5 slowest calls

Exit codes:
- 0: success
- 1: input file missing or invalid JSON
- 2: no records found

Usage:
- uv run python scripts/report_mcp_metrics_v2.py
- uv run python scripts/report_mcp_metrics_v2.py --input .cache/mcp-metrics/tool_calls.jsonl --output /tmp/report.md
- cat .cache/mcp-metrics/tool_calls.jsonl | uv run python scripts/report_mcp_metrics_v2.py --input -
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate MCP metrics report from JSONL")
    parser.add_argument(
        "--input",
        default=".cache/mcp-metrics/tool_calls.jsonl",
        help="JSONL input file (or '-' for stdin)",
    )
    parser.add_argument("--output", help="Output markdown file (default: stdout)")
    return parser.parse_args()


def read_jsonl(path: str) -> list[dict]:
    """Read JSONL line-by-line; handle large files."""
    records = []
    if path == "-":
        for line in sys.stdin:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    else:
        input_path = Path(path)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {path}")
        with input_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
    return records


def compute_p95(values: list[float]) -> float | None:
    """Compute 95th percentile; require ≥20 samples."""
    if len(values) < 20:
        return None
    sorted_values = sorted(values)
    idx = int(0.95 * (len(sorted_values) - 1))
    return sorted_values[idx]


def aggregate_metrics(records: list[dict]) -> dict:
    """Compute per-tool and global aggregates."""
    tool_records = defaultdict(list)
    for r in records:
        tool_name = r.get("tool_name", "unknown")
        tool_records[tool_name].append(r)

    tool_stats = {}
    for tool_name, tool_recs in tool_records.items():
        call_count = len(tool_recs)
        success_count = sum(1 for r in tool_recs if not r.get("is_error", False))
        success_rate = (success_count / call_count * 100) if call_count > 0 else 0.0

        # Latency stats (handle missing latency_ms gracefully)
        latencies = [r["latency_ms"] for r in tool_recs if "latency_ms" in r and r["latency_ms"] is not None]
        mean_duration = mean(latencies) if latencies else None
        max_duration = max(latencies) if latencies else None
        p95_duration = compute_p95(latencies) if latencies else None

        tool_stats[tool_name] = {
            "call_count": call_count,
            "success_count": success_count,
            "success_rate": success_rate,
            "mean_duration_ms": mean_duration,
            "max_duration_ms": max_duration,
            "p95_duration_ms": p95_duration,
        }

    # Global aggregates
    total_calls = len(records)
    global_success_count = sum(1 for r in records if not r.get("is_error", False))
    global_success_rate = (global_success_count / total_calls * 100) if total_calls > 0 else 0.0
    all_latencies = [r["latency_ms"] for r in records if "latency_ms" in r and r["latency_ms"] is not None]
    mean_duration_global = mean(all_latencies) if all_latencies else None

    return {
        "tool_stats": tool_stats,
        "total_calls": total_calls,
        "global_success_rate": global_success_rate,
        "mean_duration_global": mean_duration_global,
        "all_records": records,  # Keep for slowest calls
    }


def format_value(value: float | None, decimals: int = 1) -> str:
    """Null-safe formatting."""
    if value is None:
        return "N/A"
    return f"{value:.{decimals}f}"


def build_markdown(metrics: dict, input_path: str) -> str:
    """Render markdown report."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# MCP Metrics Report",
        "",
        f"**Report Date**: {now}",
        f"**Input**: {input_path}",
        f"**Total Records**: {metrics['total_calls']:,}",
        "",
        "## Summary Statistics",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Total Calls | {metrics['total_calls']:,} |",
        f"| Success Rate | {format_value(metrics['global_success_rate'])}% |",
        f"| Mean Duration | {format_value(metrics['mean_duration_global'])} ms |",
        "",
        "## Per-Tool Breakdown",
        "",
        "| Tool | Call Count | Success % | Mean (ms) | P95 (ms) | Max (ms) |",
        "|------|-----------|-----------|-----------|----------|----------|",
    ]

    # Sort by call count descending
    for tool_name, stats in sorted(metrics["tool_stats"].items(), key=lambda x: x[1]["call_count"], reverse=True):
        lines.append(
            f"| {tool_name} | {stats['call_count']:,} | {format_value(stats['success_rate'])}% | "
            f"{format_value(stats['mean_duration_ms'])} | {format_value(stats['p95_duration_ms'])} | "
            f"{format_value(stats['max_duration_ms'])} |"
        )

    # Top 5 slowest calls
    lines.extend(["", "## Top 5 Slowest Calls", "", "| Tool | Duration (ms) | Timestamp | Status |"])
    lines.append("|------|--------------|-----------|--------|")

    slowest = sorted(
        [r for r in metrics["all_records"] if "latency_ms" in r and r["latency_ms"] is not None],
        key=lambda r: r["latency_ms"],
        reverse=True,
    )[:5]

    for r in slowest:
        status = "error" if r.get("is_error", False) else "success"
        timestamp = r.get("timestamp_utc", "N/A")
        lines.append(f"| {r.get('tool_name', 'unknown')} | {format_value(r['latency_ms'])} | {timestamp} | {status} |")

    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()

    try:
        records = read_jsonl(args.input)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in input: {e}", file=sys.stderr)
        return 1

    if not records:
        print("Error: No records found in input", file=sys.stderr)
        return 2

    metrics = aggregate_metrics(records)
    markdown = build_markdown(metrics, args.input)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
        print(f"Report written to: {output_path}")
    else:
        print(markdown)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
