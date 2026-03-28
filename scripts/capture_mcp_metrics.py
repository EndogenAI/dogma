#!/usr/bin/env python3
"""Capture MCP quality metrics from JSONL tool-call observations.

Inputs:
- JSONL observations (`--input-jsonl`) where each line is a JSON object.
- Tool selection (`--tool` or `--all`).

Outputs:
- One JSON metrics artifact per tool in `--output-dir`.

Exit codes:
- 0: success
- 1: invalid CLI arguments or runtime failure

Usage:
- uv run python scripts/capture_mcp_metrics.py --all --dry-run
- uv run python scripts/capture_mcp_metrics.py --tool query_docs --input-jsonl .cache/mcp-metrics/tool_calls.jsonl
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from statistics import mean

CANONICAL_TOOLS = [
    "check_substrate",
    "validate_agent_file",
    "validate_synthesis",
    "scaffold_agent",
    "scaffold_workplan",
    "run_research_scout",
    "query_docs",
    "prune_scratchpad",
]


@dataclass
class ToolSummary:
    tool_name: str
    sample_size: int
    latency_ms_p95: float | None
    error_rate_pct: float | None
    tool_error_count: int
    faithfulness: float | None
    answer_relevance: float | None
    context_precision: float | None
    correctness: float | None
    completeness: float | None
    precision: float | None
    severity_level_mean: float | None
    umux_lite_equivalent: float | None


def _p95(values: list[float]) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    idx = max(0, min(len(ordered) - 1, int(round(0.95 * (len(ordered) - 1)))))
    return ordered[idx]


def _to_ms(record: dict) -> float | None:
    if "latency_ms" in record and record["latency_ms"] is not None:
        return float(record["latency_ms"])
    if "latency_s" in record and record["latency_s"] is not None:
        return float(record["latency_s"]) * 1000.0
    return None


def summarize_tool(tool_name: str, observations: list[dict], window_calls: int = 100) -> ToolSummary:
    tool_obs = [r for r in observations if r.get("tool_name") == tool_name]
    if window_calls > 0:
        tool_obs = tool_obs[-window_calls:]
    latencies = [v for r in tool_obs if (v := _to_ms(r)) is not None]
    faithfulness = [float(r["faithfulness"]) for r in tool_obs if r.get("faithfulness") is not None]
    answer_rel = [float(r["answer_relevance"]) for r in tool_obs if r.get("answer_relevance") is not None]
    context_prec = [float(r["context_precision"]) for r in tool_obs if r.get("context_precision") is not None]
    severity = [float(r["severity_level"]) for r in tool_obs if r.get("severity_level") is not None]
    umux = [float(r["umux_lite_equivalent"]) for r in tool_obs if r.get("umux_lite_equivalent") is not None]
    correctness = [float(r["correctness"]) for r in tool_obs if r.get("correctness") is not None]
    completeness = [float(r["completeness"]) for r in tool_obs if r.get("completeness") is not None]
    precision = [float(r["precision"]) for r in tool_obs if r.get("precision") is not None]

    error_count = sum(1 for r in tool_obs if bool(r.get("is_error")))
    sample_size = len(tool_obs)
    error_rate = (error_count / sample_size * 100.0) if sample_size else None

    return ToolSummary(
        tool_name=tool_name,
        sample_size=sample_size,
        latency_ms_p95=_p95(latencies),
        error_rate_pct=error_rate,
        tool_error_count=error_count,
        faithfulness=(mean(faithfulness) if faithfulness else None),
        answer_relevance=(mean(answer_rel) if answer_rel else None),
        context_precision=(mean(context_prec) if context_prec else None),
        correctness=(mean(correctness) if correctness else None),
        completeness=(mean(completeness) if completeness else None),
        precision=(mean(precision) if precision else None),
        severity_level_mean=(mean(severity) if severity else None),
        umux_lite_equivalent=(mean(umux) if umux else None),
    )


def load_observations(input_jsonl: Path) -> list[dict]:
    if not input_jsonl.exists():
        print(f"ERROR: input file {input_jsonl} does not exist", file=__import__("sys").stderr)
        __import__("sys").exit(1)
    rows: list[dict] = []
    for raw in input_jsonl.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    if not rows:
        print(f"ERROR: input file {input_jsonl} is empty", file=__import__("sys").stderr)
        __import__("sys").exit(1)
    return rows


def summary_to_dict(summary: ToolSummary, run_id: str, timestamp_utc: str, window_calls: int) -> dict:
    return {
        "schema_version": 1,
        "tool_name": summary.tool_name,
        "tool_version": "v1",
        "run_id": run_id,
        "timestamp_utc": timestamp_utc,
        "metrics": {
            "performance": {
                "latency_ms_p95": summary.latency_ms_p95,
                "error_rate_pct": summary.error_rate_pct,
                "tool_error_count": summary.tool_error_count,
                "sample_size": summary.sample_size,
                "window_calls": window_calls,
            },
            "semantic": {
                "faithfulness": summary.faithfulness,
                "answer_relevance": summary.answer_relevance,
                "context_precision": summary.context_precision,
            },
            "classical_quality": {
                "correctness": summary.correctness,
                "completeness": summary.completeness,
                "precision": summary.precision,
            },
            "defect": {
                "severity_level_mean": summary.severity_level_mean,
            },
            "usability_proxy": {
                "umux_lite_equivalent": summary.umux_lite_equivalent,
            },
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture MCP quality metrics per tool from JSONL observations.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--tool", choices=CANONICAL_TOOLS, help="Capture metrics for one tool")
    group.add_argument("--all", action="store_true", help="Capture metrics for all canonical tools")
    parser.add_argument(
        "--input-jsonl",
        default=".cache/mcp-metrics/tool_calls.jsonl",
        help="Path to JSONL observations",
    )
    parser.add_argument("--output-dir", default="docs/metrics", help="Output directory for per-tool metrics files")
    parser.add_argument("--date", default=datetime.now(UTC).date().isoformat(), help="Date stamp for filenames")
    parser.add_argument("--window-calls", type=int, default=100, help="Aggregate over last N calls per tool")
    parser.add_argument("--dry-run", action="store_true", help="Preview actions without writing files")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    tools = CANONICAL_TOOLS if args.all else [args.tool]
    input_path = Path(args.input_jsonl)
    output_dir = Path(args.output_dir)

    observations = load_observations(input_path)
    run_id = f"mcp-metrics-{args.date}"
    timestamp_utc = datetime.now(UTC).isoformat()

    outputs: list[tuple[Path, dict]] = []
    for tool in tools:
        summary = summarize_tool(tool, observations, window_calls=args.window_calls)
        payload = summary_to_dict(summary, run_id=run_id, timestamp_utc=timestamp_utc, window_calls=args.window_calls)
        out_path = output_dir / f"mcp-quality-{tool}-{args.date}.json"
        outputs.append((out_path, payload))

    if args.dry_run:
        print(json.dumps({"input": str(input_path), "output_count": len(outputs), "tools": tools}, indent=2))
        return 0

    output_dir.mkdir(parents=True, exist_ok=True)
    for path, payload in outputs:
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(outputs)} file(s) to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
