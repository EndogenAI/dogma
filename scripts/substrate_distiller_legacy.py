"""Distill governance/rationale signals from Python sources.

Extracts substrate metadata from module, class, and function docstrings using the
Python AST and computes RDI (Rationale Density Indicator):

    RDI = rationale_token_count / max(implementation_token_count, 1)

Inputs:
- --path: Python file or directory to scan recursively for *.py files
- --format: json | markdown | table
- --threshold: debt threshold for RDI violations
- --fail-on-debt: return exit code 1 when violations are present
- --include-private: include private classes/functions (leading underscore)
- --summary-only: emit summary only

Outputs:
- Structured records containing x-governs, intent/rationale blocks, RDI, and status
- Human-readable table/markdown or machine-readable JSON

Exit codes:
- 0: success (or no violations)
- 1: violations present when --fail-on-debt is set
- 2: invalid args, path errors, or Python parse errors

Usage examples:
    uv run python scripts/substrate_distiller.py --path scripts --format json
    uv run python scripts/substrate_distiller.py --path scripts --fail-on-debt
"""

from __future__ import annotations

import argparse
import ast
import io
import json
import re
import sys
import tokenize
from pathlib import Path
from typing import Any

WORD_RE = re.compile(r"\b[\w'-]+\b")
HEADING_RE = re.compile(r"^\s*##\s+(.+?)\s*$", re.IGNORECASE)
X_GOVERNS_LINE_RE = re.compile(r"^\s*x-governs\s*:\s*(.*?)\s*$", re.IGNORECASE)


def _word_count(text: str) -> int:
    return len(WORD_RE.findall(text or ""))


def _count_implementation_tokens(code: str) -> int:
    """Count lexical implementation tokens while ignoring strings/comments/newlines."""
    if not code.strip():
        return 0

    count = 0
    stream = io.StringIO(code)
    try:
        for tok in tokenize.generate_tokens(stream.readline):
            if tok.type in (tokenize.NAME, tokenize.NUMBER, tokenize.OP):
                count += 1
    except tokenize.TokenError:
        # Fall back to word-level counting for malformed snippets.
        return _word_count(code)
    return count


def _extract_x_governs(docstring: str) -> list[str]:
    if not docstring:
        return []

    lines = docstring.splitlines()
    for idx, line in enumerate(lines):
        m = X_GOVERNS_LINE_RE.match(line)
        if not m:
            continue

        payload = m.group(1).strip()
        if payload.startswith("[") and payload.endswith("]"):
            inner = payload[1:-1]
            vals = [item.strip().strip("\"'") for item in inner.split(",") if item.strip()]
            return vals

        if payload:
            vals = [item.strip().strip("\"'") for item in payload.split(",") if item.strip()]
            return vals

        block_vals: list[str] = []
        for follow in lines[idx + 1 :]:
            stripped = follow.strip()
            if not stripped:
                if block_vals:
                    break
                continue
            if stripped.startswith("## "):
                break
            if stripped.startswith("-"):
                block_vals.append(stripped[1:].strip().strip("\"'"))
                continue
            break
        return block_vals

    return []


def _extract_section(docstring: str, name: str) -> str:
    """Extract a markdown ## section by heading name from a docstring."""
    if not docstring:
        return ""

    lines = docstring.splitlines()
    target = name.strip().lower()
    start = None

    for i, line in enumerate(lines):
        m = HEADING_RE.match(line)
        if m and m.group(1).strip().lower() == target:
            start = i + 1
            break

    if start is None:
        return ""

    block: list[str] = []
    for line in lines[start:]:
        if HEADING_RE.match(line):
            break
        block.append(line)

    return "\n".join(block).strip()


def _classify_rdi(rdi: float) -> str:
    if rdi >= 0.12:
        return "green"
    if rdi >= 0.08:
        return "yellow"
    return "red"


def _iter_targets(path: Path) -> list[Path]:
    excluded_dirs = {".venv", "venv", ".pixi", "__pycache__"}

    if path.is_file():
        if path.suffix != ".py":
            raise ValueError(f"Path is not a Python file: {path}")
        return [path]
    if path.is_dir():
        results: list[Path] = []
        for candidate in path.rglob("*.py"):
            if any(part in excluded_dirs for part in candidate.parts):
                continue
            results.append(candidate)
        return sorted(results)
    raise ValueError(f"Path does not exist: {path}")


def _symbol_record(
    *,
    path: Path,
    relpath: str,
    kind: str,
    symbol: str,
    docstring: str,
    implementation_code: str,
    threshold: float,
) -> dict[str, Any]:
    x_governs = _extract_x_governs(docstring)
    intent = _extract_section(docstring, "Intent")
    rationale = _extract_section(docstring, "Rationale")
    rationale_token_count = _word_count(rationale)
    implementation_token_count = _count_implementation_tokens(implementation_code)
    rdi = rationale_token_count / max(implementation_token_count, 1)
    status = _classify_rdi(rdi)

    debt_reasons: list[str] = []
    if not x_governs:
        debt_reasons.append("missing_x_governs")
    if not rationale.strip():
        debt_reasons.append("missing_rationale")
    if rdi < threshold:
        debt_reasons.append("rdi_below_threshold")

    return {
        "path": relpath,
        "kind": kind,
        "symbol": symbol,
        "x_governs": x_governs,
        "intent": intent,
        "rationale": rationale,
        "rationale_token_count": rationale_token_count,
        "implementation_token_count": implementation_token_count,
        "rdi": round(rdi, 6),
        "status": status,
        "threshold": threshold,
        "has_x_governs": bool(x_governs),
        "has_rationale": bool(rationale.strip()),
        "is_debt": bool(debt_reasons),
        "debt_reasons": debt_reasons,
    }


def distill_path(path: Path, *, threshold: float, include_private: bool) -> dict[str, Any]:
    targets = _iter_targets(path)
    records: list[dict[str, Any]] = []

    for file_path in targets:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(file_path))
        relpath = str(file_path)

        module_doc = ast.get_docstring(tree, clean=False) or ""
        records.append(
            _symbol_record(
                path=file_path,
                relpath=relpath,
                kind="module",
                symbol="<module>",
                docstring=module_doc,
                implementation_code=source,
                threshold=threshold,
            )
        )

        for node in ast.walk(tree):
            if not isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                continue

            if not include_private and getattr(node, "name", "").startswith("_"):
                continue

            if isinstance(node, ast.ClassDef):
                kind = "class"
            elif isinstance(node, ast.AsyncFunctionDef):
                kind = "async_function"
            else:
                kind = "function"

            doc = ast.get_docstring(node, clean=False) or ""
            implementation_code = ast.get_source_segment(source, node) or ""

            records.append(
                _symbol_record(
                    path=file_path,
                    relpath=relpath,
                    kind=kind,
                    symbol=node.name,
                    docstring=doc,
                    implementation_code=implementation_code,
                    threshold=threshold,
                )
            )

    records = sorted(records, key=lambda item: (item["path"], item["kind"], item["symbol"]))

    summary = {
        "files_scanned": len(targets),
        "records": len(records),
        "debt_records": sum(1 for record in records if record["is_debt"]),
        "missing_x_governs": sum(1 for record in records if not record["has_x_governs"]),
        "missing_rationale": sum(1 for record in records if not record["has_rationale"]),
        "status_counts": {
            "green": sum(1 for record in records if record["status"] == "green"),
            "yellow": sum(1 for record in records if record["status"] == "yellow"),
            "red": sum(1 for record in records if record["status"] == "red"),
        },
        "threshold": threshold,
    }

    return {"summary": summary, "records": records}


def _render_json(payload: dict[str, Any], summary_only: bool) -> str:
    data = {"summary": payload["summary"]} if summary_only else payload
    return json.dumps(data, sort_keys=True, indent=2)


def _render_table(payload: dict[str, Any], summary_only: bool) -> str:
    if summary_only:
        summary = payload["summary"]
        return (
            "files_scanned\trecords\tdebt_records\tmissing_x_governs\tmissing_rationale\tgreen\tyellow\tred\tthreshold\n"
            f"{summary['files_scanned']}\t{summary['records']}\t{summary['debt_records']}\t"
            f"{summary['missing_x_governs']}\t{summary['missing_rationale']}\t"
            f"{summary['status_counts']['green']}\t{summary['status_counts']['yellow']}\t"
            f"{summary['status_counts']['red']}\t{summary['threshold']}"
        )

    lines = [
        "path\tkind\tsymbol\tstatus\trdi\thas_x_governs\thas_rationale\tdebt_reasons",
    ]
    for record in payload["records"]:
        lines.append(
            "\t".join(
                [
                    record["path"],
                    record["kind"],
                    record["symbol"],
                    record["status"],
                    str(record["rdi"]),
                    str(record["has_x_governs"]),
                    str(record["has_rationale"]),
                    ",".join(record["debt_reasons"]),
                ]
            )
        )
    return "\n".join(lines)


def _render_markdown(payload: dict[str, Any], summary_only: bool) -> str:
    summary = payload["summary"]
    lines = [
        "## Substrate Distiller Summary",
        "",
        (
            "| files_scanned | records | debt_records | missing_x_governs | "
            "missing_rationale | green | yellow | red | threshold |"
        ),
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        (
            f"| {summary['files_scanned']} | {summary['records']} | {summary['debt_records']} | "
            f"{summary['missing_x_governs']} | {summary['missing_rationale']} | "
            f"{summary['status_counts']['green']} | {summary['status_counts']['yellow']} | "
            f"{summary['status_counts']['red']} | {summary['threshold']} |"
        ),
    ]

    if summary_only:
        return "\n".join(lines)

    lines.extend(
        [
            "",
            "## Records",
            "",
            "| path | kind | symbol | status | rdi | x-governs | debt_reasons |",
            "|---|---|---|---|---:|---|---|",
        ]
    )

    for record in payload["records"]:
        lines.append(
            f"| {record['path']} | {record['kind']} | {record['symbol']} | {record['status']} | "
            f"{record['rdi']} | {', '.join(record['x_governs'])} | {', '.join(record['debt_reasons'])} |"
        )

    return "\n".join(lines)


def render_output(payload: dict[str, Any], fmt: str, summary_only: bool) -> str:
    if fmt == "json":
        return _render_json(payload, summary_only)
    if fmt == "markdown":
        return _render_markdown(payload, summary_only)
    return _render_table(payload, summary_only)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Distill x-governs/intent/rationale substrate signals from Python code."
    )
    parser.add_argument("--path", required=True, help="Python file or directory path to scan")
    parser.add_argument("--format", choices=["json", "markdown", "table"], default="table")
    parser.add_argument("--threshold", type=float, default=0.08, help="RDI debt threshold")
    parser.add_argument("--fail-on-debt", action="store_true", help="Exit 1 when debt records exist")
    parser.add_argument("--include-private", action="store_true", help="Include private classes/functions")
    parser.add_argument("--summary-only", action="store_true", help="Emit only summary output")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    try:
        args = parse_args(argv)
    except SystemExit as exc:
        # argparse may raise SystemExit(None) in edge paths; normalize to error code 2.
        return exc.code if isinstance(exc.code, int) else 2

    if args.threshold < 0:
        print("ERROR: --threshold must be >= 0", file=sys.stderr)
        return 2

    try:
        payload = distill_path(Path(args.path), threshold=args.threshold, include_private=args.include_private)
    except (ValueError, OSError, SyntaxError, UnicodeDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(render_output(payload, args.format, args.summary_only))

    has_debt = payload["summary"]["debt_records"] > 0
    if args.fail_on_debt and has_debt:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
