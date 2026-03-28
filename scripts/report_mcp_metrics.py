#!/usr/bin/env python3
"""Generate a Markdown summary report from MCP metrics JSON artifacts.

Inputs:
- JSON metric artifacts matched by `--input-glob`.

Outputs:
- Markdown report written to `--output`.
- Optional stdout rendering with `--print`.

Exit codes:
- 0: success
- 1: input glob matched no files (raises SystemExit)

Usage:
- uv run python scripts/report_mcp_metrics.py --input-glob "docs/metrics/mcp-quality-*.json"
- uv run python scripts/report_mcp_metrics.py --print
"""

from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render MCP quality metrics as a Markdown table.")
    parser.add_argument("--input-glob", default="docs/metrics/mcp-quality-*.json", help="Glob for metrics JSON files")
    parser.add_argument("--output", default="docs/metrics/mcp-quality-report.md", help="Output markdown path")
    parser.add_argument("--print", action="store_true", help="Print markdown to stdout")
    return parser.parse_args()


def _fmt(value: float | int | None) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def build_markdown(rows: list[dict]) -> str:
    lines = [
        "# MCP Quality Metrics Report",
        "",
        (
            "| Tool | Samples | P95 latency ms | Error % | Faithfulness | "
            "Answer relevance | Context precision | Correctness | Completeness | "
            "Precision | Severity mean | UMUX-lite |"
        ),
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in sorted(rows, key=lambda r: r.get("tool_name", "")):
        perf = row.get("metrics", {}).get("performance", {})
        sem = row.get("metrics", {}).get("semantic", {})
        classical = row.get("metrics", {}).get("classical_quality", {})
        defect = row.get("metrics", {}).get("defect", {})
        ux = row.get("metrics", {}).get("usability_proxy", {})
        lines.append(
            (
                "| {tool} | {samples} | {latency} | {error} | {faith} | {rel} | {prec} | "
                "{correctness} | {completeness} | {precision} | {sev} | {umux} |"
            ).format(
                tool=row.get("tool_name", "n/a"),
                samples=_fmt(perf.get("sample_size")),
                latency=_fmt(perf.get("latency_ms_p95")),
                error=_fmt(perf.get("error_rate_pct")),
                faith=_fmt(sem.get("faithfulness")),
                rel=_fmt(sem.get("answer_relevance")),
                prec=_fmt(sem.get("context_precision")),
                correctness=_fmt(classical.get("correctness")),
                completeness=_fmt(classical.get("completeness")),
                precision=_fmt(classical.get("precision")),
                sev=_fmt(defect.get("severity_level_mean")),
                umux=_fmt(ux.get("umux_lite_equivalent")),
            )
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    files = [Path(p) for p in sorted(glob.glob(args.input_glob))]
    if not files:
        raise SystemExit(f"No metrics files found for glob: {args.input_glob}")

    rows = [json.loads(path.read_text(encoding="utf-8")) for path in files]
    markdown = build_markdown(rows)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")
    if args.print:
        print(markdown)
    else:
        print(f"Wrote report: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
