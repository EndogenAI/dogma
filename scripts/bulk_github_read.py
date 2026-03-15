"""
scripts/bulk_github_read.py — Batch GitHub issue/PR metadata reads.

Purpose
-------
Fetch structured metadata for one or more GitHub issues and/or pull requests,
then format the results as a table, JSON, or CSV. All fetches route through
the ``gh`` CLI via subprocess with list-of-args (never shell=True). Supports
reading individual items by number, or running a GitHub search query.

Inputs
------
- ``--issues NUMBERS``  Comma-separated issue numbers to fetch (e.g. 1,2,3).
- ``--prs NUMBERS``     Comma-separated PR numbers to fetch.
- ``--query QUERY``     GitHub search string (passed to ``gh issue list --search``).
  At least one of the above is required.

Outputs
-------
- stdout: formatted results (table by default; JSON or CSV via ``--format``).
- stderr: error messages on fetch failure.

Flags
-----
--issues NUMBERS   Comma-separated issue numbers.
--prs NUMBERS      Comma-separated PR numbers.
--query QUERY      GitHub search string for issue list.
--fields FIELDS    Comma-separated field names to include in output.
                   Default: number,title,state,labels,milestone,assignee
--format FORMAT    Output format: table | json | csv. Default: table.
--help             Show this help and exit.

Exit codes
----------
0  All fetches succeeded.
1  One or more fetches failed (gh error, network issue, etc.).

Usage examples
--------------
# Fetch issues 1, 5, and 10 as a table
uv run python scripts/bulk_github_read.py --issues 1,5,10

# Fetch PR 42 as JSON
uv run python scripts/bulk_github_read.py --prs 42 --format json

# Search for open bugs and export as CSV
uv run python scripts/bulk_github_read.py --query "is:open label:type:bug" --format csv

# Fetch specific fields only
uv run python scripts/bulk_github_read.py --issues 1,2 --fields number,title,state

# Mix issues and PRs
uv run python scripts/bulk_github_read.py --issues 10,11 --prs 5 --format json
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import subprocess
import sys
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_FIELDS = ["number", "title", "state", "labels", "milestone", "assignee"]

# All fields we ever request from gh JSON output (superset of DEFAULT_FIELDS)
_GH_JSON_FIELDS = "number,title,state,labels,milestone,assignee"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Batch GitHub issue/PR metadata reads — outputs table, JSON, or CSV.",
    )
    parser.add_argument(
        "--issues",
        default=None,
        metavar="NUMBERS",
        help="Comma-separated issue numbers to fetch (e.g. 1,2,3).",
    )
    parser.add_argument(
        "--prs",
        default=None,
        metavar="NUMBERS",
        help="Comma-separated PR numbers to fetch.",
    )
    parser.add_argument(
        "--query",
        default=None,
        metavar="QUERY",
        help="GitHub search string for issue list (passed to gh issue list --search).",
    )
    parser.add_argument(
        "--fields",
        default=",".join(DEFAULT_FIELDS),
        metavar="FIELDS",
        help=(f"Comma-separated field names to include. Default: {','.join(DEFAULT_FIELDS)}"),
    )
    parser.add_argument(
        "--format",
        default="table",
        choices=["table", "json", "csv"],
        help="Output format: table | json | csv. Default: table.",
    )
    return parser


# ---------------------------------------------------------------------------
# Field helpers
# ---------------------------------------------------------------------------


def _parse_fields(fields_str: str) -> list[str]:
    """Split and clean a comma-separated fields string."""
    return [f.strip() for f in fields_str.split(",") if f.strip()]


def _filter_record(data: dict[str, Any], fields: list[str]) -> dict[str, Any]:
    """Return a new dict containing only the requested fields."""
    out: dict[str, Any] = {}
    for field in fields:
        if field in data:
            out[field] = data[field]
        else:
            out[field] = None
    return out


def _simplify_record(record: dict[str, Any]) -> dict[str, Any]:
    """Flatten nested gh JSON structures for readable display/export.

    Only transforms keys that are already present in the record — never adds
    new keys. Transformations applied:

    - labels: list[{name, ...}] → comma-joined string of names
    - milestone: {title, ...} | null → title string or ""
    - assignee: {login, ...} | null → login string or ""
    - assignees: list[{login, ...}] → comma-joined logins (gh pr view uses 'assignees')
    """
    simplified = dict(record)
    # labels — only if key is present
    if "labels" in simplified and isinstance(simplified["labels"], list):
        simplified["labels"] = ", ".join(
            (lbl["name"] if isinstance(lbl, dict) else str(lbl)) for lbl in simplified["labels"]
        )
    # milestone — only if key is present
    if "milestone" in simplified:
        ms = simplified["milestone"]
        if isinstance(ms, dict):
            simplified["milestone"] = ms.get("title", "")
        elif ms is None:
            simplified["milestone"] = ""
    # assignee (issues) — only if key is present
    if "assignee" in simplified:
        asn = simplified["assignee"]
        if isinstance(asn, dict):
            simplified["assignee"] = asn.get("login", "")
        elif asn is None:
            simplified["assignee"] = ""
    # assignees (PRs) — only if key is present
    if "assignees" in simplified and isinstance(simplified["assignees"], list):
        simplified["assignees"] = ", ".join(
            (a["login"] if isinstance(a, dict) else str(a)) for a in simplified["assignees"]
        )
    return simplified


# ---------------------------------------------------------------------------
# Fetch helpers
# ---------------------------------------------------------------------------


class FetchError(Exception):
    """Raised when a gh CLI call fails."""


def _fetch_issue(number: int, fields: list[str]) -> dict[str, Any]:
    """Fetch a single issue by number and return a filtered record dict."""
    cmd = ["gh", "issue", "view", str(number), "--json", _GH_JSON_FIELDS]
    result = subprocess.run(cmd, capture_output=True, text=True)  # noqa: S603
    if result.returncode != 0:
        raise FetchError(f"Issue #{number}: {result.stderr.strip() or result.stdout.strip()}")
    data = json.loads(result.stdout)
    return _filter_record(data, fields)


def _fetch_pr(number: int, fields: list[str]) -> dict[str, Any]:
    """Fetch a single PR by number and return a filtered record dict."""
    # gh pr view returns 'assignees' (plural), not 'assignee' — request it
    pr_json_fields = "number,title,state,labels,milestone,assignees"
    cmd = ["gh", "pr", "view", str(number), "--json", pr_json_fields]
    result = subprocess.run(cmd, capture_output=True, text=True)  # noqa: S603
    if result.returncode != 0:
        raise FetchError(f"PR #{number}: {result.stderr.strip() or result.stdout.strip()}")
    data = json.loads(result.stdout)
    # Normalise 'assignees' → 'assignee' so downstream field filtering is uniform
    if "assignees" in data and "assignee" not in data:
        assignees = data.pop("assignees")
        data["assignee"] = assignees[0] if assignees else None
    return _filter_record(data, fields)


def _search_issues(query: str, fields: list[str]) -> list[dict[str, Any]]:
    """Run a GitHub search query and return a list of filtered record dicts."""
    cmd = [
        "gh",
        "issue",
        "list",
        "--search",
        query,
        "--json",
        _GH_JSON_FIELDS,
        "--limit",
        "100",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)  # noqa: S603
    if result.returncode != 0:
        raise FetchError(f"Search query '{query}': {result.stderr.strip() or result.stdout.strip()}")
    items = json.loads(result.stdout)
    return [_filter_record(item, fields) for item in items]


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------


def _format_json(records: list[dict[str, Any]]) -> str:
    simplified = [_simplify_record(r) for r in records]
    return json.dumps(simplified, indent=2)


def _format_csv(records: list[dict[str, Any]], fields: list[str]) -> str:
    simplified = [_simplify_record(r) for r in records]
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(simplified)
    return buf.getvalue()


def _format_table(records: list[dict[str, Any]], fields: list[str]) -> str:
    simplified = [_simplify_record(r) for r in records]
    if not simplified:
        return "(no results)"
    # Compute column widths
    widths: dict[str, int] = {f: len(f) for f in fields}
    for rec in simplified:
        for f in fields:
            val = str(rec.get(f, "") or "")
            # Truncate long values for table display
            if len(val) > 60:
                val = val[:57] + "..."
            widths[f] = max(widths[f], len(val))

    sep = "  "
    header = sep.join(f.upper().ljust(widths[f]) for f in fields)
    divider = sep.join("-" * widths[f] for f in fields)
    rows = []
    for rec in simplified:
        row_parts = []
        for f in fields:
            val = str(rec.get(f, "") or "")
            if len(val) > 60:
                val = val[:57] + "..."
            row_parts.append(val.ljust(widths[f]))
        rows.append(sep.join(row_parts))

    lines = [header, divider] + rows
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if not args.issues and not args.prs and not args.query:
        parser.error("At least one of --issues, --prs, or --query is required.")

    fields = _parse_fields(args.fields)
    records: list[dict[str, Any]] = []
    any_failed = False

    # --- Fetch issues by number ---
    if args.issues:
        for part in args.issues.split(","):
            part = part.strip()
            if not part:
                continue
            try:
                number = int(part)
            except ValueError:
                print(f"ERROR: Invalid issue number: '{part}'", file=sys.stderr)
                any_failed = True
                continue
            try:
                records.append(_fetch_issue(number, fields))
            except FetchError as exc:
                print(f"ERROR: {exc}", file=sys.stderr)
                any_failed = True

    # --- Fetch PRs by number ---
    if args.prs:
        for part in args.prs.split(","):
            part = part.strip()
            if not part:
                continue
            try:
                number = int(part)
            except ValueError:
                print(f"ERROR: Invalid PR number: '{part}'", file=sys.stderr)
                any_failed = True
                continue
            try:
                records.append(_fetch_pr(number, fields))
            except FetchError as exc:
                print(f"ERROR: {exc}", file=sys.stderr)
                any_failed = True

    # --- Search ---
    if args.query:
        try:
            records.extend(_search_issues(args.query, fields))
        except FetchError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            any_failed = True

    # --- Format & output ---
    fmt = args.format
    if fmt == "json":
        print(_format_json(records))
    elif fmt == "csv":
        print(_format_csv(records, fields), end="")
    else:
        print(_format_table(records, fields))

    return 1 if any_failed else 0


if __name__ == "__main__":
    sys.exit(main())
