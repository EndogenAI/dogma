"""
scripts/seed_research_recommendations.py — Batch-create tracking issues from research doc recommendations.

Purpose
-------
Reads YAML frontmatter from one or more research Markdown docs (``docs/research/*.md``),
extracts recommendations that have no tracking issue yet (``linked_issue`` is ``null``
or starts with ``TBD``), and feeds a ``bulk_github_operations.py``-compatible JSON ops
spec into ``bulk_github_operations.py`` for batch issue creation.

This script implements the **source generator** side of the two-part batch-issue pipeline:
  1. **seed_research_recommendations.py** (this script) — reads research frontmatter → emits JSON ops spec
  2. **bulk_github_operations.py** — consumes the ops spec → calls ``gh issue create`` per op

Inputs
------
- One or more Markdown research docs (``--input FILE [FILE ...]``) with YAML frontmatter
  containing a ``recommendations`` list. Each recommendation may have:
  - ``id``: stable string identifier
  - ``title``: human-readable title (required; used as issue title)
  - ``status``: adoption status (e.g. ``accepted-for-adoption``)
  - ``linked_issue``: ``null``, ``TBD-*``, or an integer (existing issue number → skip)
  - ``area`` (optional): area label (e.g. ``docs``, ``scripts``, ``agents``, ``tests``)

Outputs
-------
- Without ``--output``: pipes the generated JSON ops spec to
  ``uv run python scripts/bulk_github_operations.py`` via stdin.
- With ``--output FILE``: writes the JSON ops spec to FILE and exits without invoking
  ``bulk_github_operations.py``. Caller can then inspect and invoke the engine separately.

Flags
-----
--input FILE [FILE ...]     One or more research Markdown docs to scan (required).
--milestone TITLE_OR_NUM    Milestone title or number to assign to all created issues.
--default-area LABEL        Area label (without the ``area:`` prefix) to use when a
                            recommendation has no ``area`` field. Required if any
                            recommendation in the input docs has no ``area`` field.
--critical-ids ID1,ID2,...  Comma-separated recommendation IDs that get
                            ``priority:critical`` instead of ``priority:high``.
--output FILE               Write the JSON ops spec to FILE instead of piping to
                            ``bulk_github_operations.py``.
--dry-run                   Generate the spec and pass ``--dry-run`` through to
                            ``bulk_github_operations.py`` (no issues created).
--repo OWNER/REPO           Target repository. Default: ``EndogenAI/dogma``.

Exit codes
----------
0  All operations succeeded (or --dry-run completed, or --output written).
1  Subprocess or I/O error during execution.
2  Parse/validation failure (malformed frontmatter, missing --default-area, etc.).

Usage examples
--------------
# Dry-run: preview which issues would be created (no API calls)
uv run python scripts/seed_research_recommendations.py \\
    --input docs/research/my-research.md --dry-run

# Create tracking issues for all untracked recommendations in a doc
uv run python scripts/seed_research_recommendations.py \\
    --input docs/research/my-research.md \\
    --milestone "Sprint 20" \\
    --default-area docs

# Scan multiple docs, mark two recommendations as critical priority
uv run python scripts/seed_research_recommendations.py \\
    --input docs/research/doc-a.md docs/research/doc-b.md \\
    --critical-ids intent-bound-readiness-contract,capability-matrix-requirement \\
    --default-area scripts

# Write spec to file — inspect before executing
uv run python scripts/seed_research_recommendations.py \\
    --input docs/research/my-research.md \\
    --output /tmp/ops.json --dry-run
uv run python scripts/bulk_github_operations.py --input /tmp/ops.json --dry-run
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

# ---------------------------------------------------------------------------
# Frontmatter extraction
# ---------------------------------------------------------------------------


def _extract_frontmatter(text: str, source_path: str) -> dict[str, Any]:
    """Return the parsed YAML frontmatter dict from a Markdown file's text.

    Raises SystemExit(2) with a human-readable message on parse errors or if
    the document has no frontmatter delimiters.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        sys.exit(
            f"[seed_research_recommendations] ERROR: {source_path}: "
            "no YAML frontmatter found (file must start with '---')"
        )

    end_idx: int | None = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        sys.exit(
            f"[seed_research_recommendations] ERROR: {source_path}: "
            "frontmatter opening '---' found but closing '---' is missing"
        )

    frontmatter_text = "\n".join(lines[1:end_idx])
    try:
        data = yaml.safe_load(frontmatter_text)
    except yaml.YAMLError as exc:
        sys.exit(f"[seed_research_recommendations] ERROR: {source_path}: malformed YAML frontmatter: {exc}")

    if not isinstance(data, dict):
        sys.exit(f"[seed_research_recommendations] ERROR: {source_path}: frontmatter did not parse to a mapping")

    return data


# ---------------------------------------------------------------------------
# Recommendation filtering
# ---------------------------------------------------------------------------


def _is_untracked(linked_issue: Any) -> bool:
    """Return True if a recommendation needs a tracking issue."""
    if linked_issue is None:
        return True
    if isinstance(linked_issue, str) and linked_issue.upper().startswith("TBD"):
        return True
    return False


# ---------------------------------------------------------------------------
# Issue body builder
# ---------------------------------------------------------------------------


def _build_issue_body(filename: str, title: str, closes_issue: int | None) -> str:
    """Return an issue body string following the standard template."""
    closes_str = (
        "#closes_issue"
        if closes_issue is None  # fallback; should not occur
        else f"#{closes_issue}"
    )
    return (
        "## Source\n\n"
        f"Derived from `docs/research/{filename}` § {title}"
        f" (closes tracking for {closes_str}).\n\n"
        "## Summary\n\n"
        f"{title}\n\n"
        "## Deliverables\n\n"
        f"- [ ] See `docs/research/{filename}` § {title} for acceptance criteria.\n\n"
        "## Reference\n\n"
        f"See `docs/research/{filename}` § Recommendations for full context.\n"
    )


# ---------------------------------------------------------------------------
# Ops spec builder
# ---------------------------------------------------------------------------


def _build_ops(
    input_paths: list[Path],
    default_area: str | None,
    critical_ids: set[str],
    milestone: str | None,
    repo: str,
) -> list[dict[str, Any]]:
    """Read each input file and build a list of issue-create op dicts."""
    ops: list[dict[str, Any]] = []

    for path in input_paths:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            print(
                f"[seed_research_recommendations] ERROR: cannot read {path}: {exc}",
                file=sys.stderr,
            )
            sys.exit(1)

        frontmatter = _extract_frontmatter(text, str(path))
        filename = path.name
        closes_issue: int | None = frontmatter.get("closes_issue")

        recommendations = frontmatter.get("recommendations") or []
        if not isinstance(recommendations, list):
            sys.exit(f"[seed_research_recommendations] ERROR: {path}: 'recommendations' must be a list")

        for rec in recommendations:
            if not isinstance(rec, dict):
                sys.exit(f"[seed_research_recommendations] ERROR: {path}: each recommendation entry must be a mapping")

            linked_issue = rec.get("linked_issue")
            if not _is_untracked(linked_issue):
                continue  # already has a tracking issue — skip

            rec_id = rec.get("id", "")
            title = rec.get("title")
            if not title:
                sys.exit(
                    f"[seed_research_recommendations] ERROR: {path}: "
                    f"recommendation id='{rec_id}' is missing a 'title' field"
                )

            # Resolve area label
            area = rec.get("area") or default_area
            if not area:
                print(
                    f"[seed_research_recommendations] ERROR: recommendation "
                    f"id='{rec_id}' in {path} has no 'area' field and "
                    "--default-area was not provided.",
                    file=sys.stderr,
                )
                sys.exit(2)

            # Build label list
            priority = "priority:critical" if rec_id in critical_ids else "priority:high"
            labels: list[str] = ["source:research", "type:feature", priority, f"area:{area}"]

            # Build body
            body = _build_issue_body(filename, title, closes_issue)

            # Build params
            params: dict[str, Any] = {
                "title": title,
                "body": body,
                "labels": labels,
                "repo": repo,
            }
            if milestone is not None:
                params["milestone"] = milestone

            ops.append({"op": "issue-create", "target": None, "params": params})

    return ops


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Read research doc YAML frontmatter, extract untracked recommendations, "
            "and feed a bulk_github_operations.py-compatible JSON ops spec for batch "
            "issue creation."
        ),
    )
    parser.add_argument(
        "--input",
        nargs="+",
        metavar="FILE",
        required=True,
        help="One or more research Markdown docs to scan.",
    )
    parser.add_argument(
        "--milestone",
        metavar="TITLE_OR_NUMBER",
        default=None,
        help="Milestone title or number to assign to all created issues.",
    )
    parser.add_argument(
        "--default-area",
        metavar="LABEL",
        default=None,
        help=("Area label (without 'area:' prefix) to use when a recommendation has no 'area' field."),
    )
    parser.add_argument(
        "--critical-ids",
        metavar="ID1,ID2,...",
        default="",
        help=("Comma-separated recommendation IDs that should get 'priority:critical' instead of 'priority:high'."),
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        default=None,
        help=("Write the generated JSON ops spec to FILE instead of piping to bulk_github_operations.py."),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help=("Generate the spec and pass --dry-run through to bulk_github_operations.py (no issues created)."),
    )
    parser.add_argument(
        "--repo",
        metavar="OWNER/REPO",
        default="EndogenAI/dogma",
        help="Target GitHub repository. Default: EndogenAI/dogma.",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    input_paths = [Path(p) for p in args.input]
    for p in input_paths:
        if not p.exists():
            print(
                f"[seed_research_recommendations] ERROR: input file not found: {p}",
                file=sys.stderr,
            )
            sys.exit(1)

    critical_ids: set[str] = (
        {s.strip() for s in args.critical_ids.split(",") if s.strip()} if args.critical_ids else set()
    )

    ops = _build_ops(
        input_paths=input_paths,
        default_area=args.default_area,
        critical_ids=critical_ids,
        milestone=args.milestone,
        repo=args.repo,
    )

    if not ops:
        print("[seed_research_recommendations] No untracked recommendations found. Nothing to do.")
        sys.exit(0)

    spec_json = json.dumps(ops, indent=2)

    if args.output:
        out_path = Path(args.output)
        out_path.write_text(spec_json, encoding="utf-8")
        print(
            f"[seed_research_recommendations] Wrote {len(ops)} op(s) to {out_path}. "
            "Run: uv run python scripts/bulk_github_operations.py "
            f"--input {out_path}{' --dry-run' if args.dry_run else ''}"
        )
        sys.exit(0)

    # Pipe to bulk_github_operations.py
    cmd = ["uv", "run", "python", "scripts/bulk_github_operations.py"]
    if args.dry_run:
        cmd.append("--dry-run")

    try:
        result = subprocess.run(
            cmd,
            input=spec_json,
            capture_output=False,
            text=True,
            check=False,
        )
    except FileNotFoundError as exc:
        print(
            f"[seed_research_recommendations] ERROR: failed to invoke bulk_github_operations.py: {exc}",
            file=sys.stderr,
        )
        sys.exit(1)

    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
