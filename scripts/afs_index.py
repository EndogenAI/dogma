"""scripts/afs_index.py — B' Hybrid SQLite FTS5 Keyword Index for Session Scratchpads

Purpose:
    Implements the B' hybrid scratchpad architecture: SQLite FTS5 as a
    query-optimised index over Markdown session files. Agents continue writing
    via ``replace_string_in_file``; this script maintains a queryable index for
    the two highest-frequency query patterns:

        Q1: active phase  — SELECT phase, status FROM sessions WHERE phase MATCH ?
        Q5: open blockers — SELECT content FROM sessions WHERE content MATCH 'blocker OR blocked'

    The ``.db`` file is gitignored; Markdown ``.md`` files remain the source of
    truth and continue to be committed as session records.

Design: Candidate B' (Sprint 15 scratchpad architecture research)
Reference: ``docs/research/scratchpad-architecture-decision.md``
Reference: GitHub issue #129

Inputs:
    COMMAND (positional):
        init   — create / migrate the .db file for the current branch's .tmp/ dir
        index  — (re)index all .md session files under a branch .tmp/ dir
        query  — run a keyword query against the FTS5 index
        status — show per-file index coverage stats

    --tmp-dir PATH   Base .tmp/ directory (default: .tmp/ at repo root)
    --branch  SLUG   Branch slug to use (default: auto-detect from git)
    --db-path PATH   Explicit .db path (overrides --tmp-dir/--branch derivation)
    --q TEXT         Keyword query string (required for ``query`` command)
    --field FIELD    Field to match against: phase|status|content (default: content)
    --format json|table  Output format for query results (default: table)

Outputs:
    init:   creates ``.tmp/<branch>/.scratchpad_index.db`` with FTS5 schema
    index:  populates / refreshes the FTS5 virtual table rows from .md files
    query:  prints matching rows (table or JSON)
    status: prints coverage stats (files indexed, total rows, last updated)

Exit codes:
    0 — success
    1 — argument error, DB error, or no matching files

Usage:
    uv run python scripts/afs_index.py init
    uv run python scripts/afs_index.py index
    uv run python scripts/afs_index.py query --q "Phase 3"
    uv run python scripts/afs_index.py query --q "blocker OR blocked" --field content
    uv run python scripts/afs_index.py status
    uv run python scripts/afs_index.py index --branch feat-my-branch
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DEFAULT_TMP_DIR = REPO_ROOT / ".tmp"

# ---------------------------------------------------------------------------
# FTS5 schema
# ---------------------------------------------------------------------------

SCHEMA_DDL = """
CREATE VIRTUAL TABLE IF NOT EXISTS sessions USING fts5(
    date,
    branch,
    phase,
    status,
    content
);

CREATE TABLE IF NOT EXISTS _meta (
    key   TEXT PRIMARY KEY,
    value TEXT
);
"""

# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------


def _git_branch() -> str | None:
    """Return the current git branch slug (/ replaced with -)."""
    try:
        raw = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        return raw.replace("/", "-") if raw and raw != "HEAD" else None
    except Exception:
        return None


# ---------------------------------------------------------------------------
# DB resolution
# ---------------------------------------------------------------------------


def resolve_db_path(tmp_dir: Path, branch: str | None, db_path: str | None) -> Path:
    """Resolve the .db file path from CLI args."""
    if db_path:
        return Path(db_path)
    b = branch or _git_branch()
    if not b:
        print("ERROR: cannot detect branch; use --branch or --db-path", file=sys.stderr)
        sys.exit(1)
    return tmp_dir / b / ".scratchpad_index.db"


# ---------------------------------------------------------------------------
# Scratchpad parsing
# ---------------------------------------------------------------------------

# Matches ## Section Heading lines (excluding ### sub-headings)
_H2_RE = re.compile(r"^## (.+)$", re.MULTILINE)
# Extract phase name from headings like "Phase 2 — ...", "Phase 2 Review ..."
_PHASE_RE = re.compile(r"Phase\s+\d+[^—\n]*", re.IGNORECASE)
# Status markers in headings
_STATUS_RE = re.compile(r"(✅|⬜|⏳|not started|in progress|complete|approved|pending)", re.IGNORECASE)


def _extract_phase(heading: str) -> str:
    m = _PHASE_RE.search(heading)
    return m.group(0).strip() if m else ""


def _extract_status(heading: str) -> str:
    m = _STATUS_RE.search(heading)
    return m.group(0).strip() if m else ""


def parse_scratchpad(path: Path) -> list[dict]:
    """Parse a .md scratchpad file into a list of section dicts for FTS5 indexing.

    Returns a list of {date, branch, phase, status, content} dicts,
    one per H2 section (plus a synthetic 'full-file' row for whole-file search).
    """
    text = path.read_text(encoding="utf-8", errors="replace")

    # Derive date from filename stem (YYYY-MM-DD.md)
    date_str = path.stem if re.match(r"\d{4}-\d{2}-\d{2}", path.stem) else ""

    # Derive branch from parent directory name
    branch = path.parent.name

    rows: list[dict] = []

    # Split into H2 sections
    sections = _H2_RE.split(text)
    # sections = [preamble, heading1, body1, heading2, body2, ...]
    # first element is preamble (before first ##); not indexed separately

    # Always add a whole-file row for full-text search
    rows.append(
        {
            "date": date_str,
            "branch": branch,
            "phase": "",
            "status": "",
            "content": text,
        }
    )

    # Add per-section rows
    it = iter(sections[1:])
    for heading in it:
        body = next(it, "")
        rows.append(
            {
                "date": date_str,
                "branch": branch,
                "phase": _extract_phase(heading),
                "status": _extract_status(heading),
                "content": f"## {heading}\n{body}",
            }
        )

    return rows


# ---------------------------------------------------------------------------
# Database operations
# ---------------------------------------------------------------------------


def open_db(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path) -> None:
    """Create the FTS5 virtual table and metadata table if they don't exist."""
    conn = open_db(db_path)
    conn.executescript(SCHEMA_DDL)
    conn.execute(
        "INSERT OR IGNORE INTO _meta (key, value) VALUES (?, ?)",
        ("schema_version", "1"),
    )
    conn.commit()
    conn.close()
    print(f"Initialised index: {db_path}")


def index_files(db_path: Path, md_files: list[Path]) -> int:
    """(Re)index the given .md files. Returns count of rows inserted."""
    conn = open_db(db_path)
    total = 0
    for md in md_files:
        if not md.exists():
            continue
        # Delete existing rows for this file (keyed by date+branch)
        date_str = md.stem
        branch = md.parent.name
        # Skip files whose stem does not match YYYY-MM-DD — parse_scratchpad()
        # sets date to "" for non-conforming filenames, which would accumulate
        # orphaned duplicate rows on re-index.
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
            continue
        conn.execute(
            "DELETE FROM sessions WHERE date = ? AND branch = ?",
            (date_str, branch),
        )
        rows = parse_scratchpad(md)
        conn.executemany(
            "INSERT INTO sessions (date, branch, phase, status, content) VALUES (?, ?, ?, ?, ?)",
            [(r["date"], r["branch"], r["phase"], r["status"], r["content"]) for r in rows],
        )
        total += len(rows)
    conn.execute(
        "INSERT OR REPLACE INTO _meta (key, value) VALUES (?, ?)",
        ("last_indexed", datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()
    return total


VALID_FIELDS: frozenset[str] = frozenset({"date", "branch", "phase", "status", "content"})


def query_index(db_path: Path, q: str, field: str = "content") -> list[dict]:
    """Run a parameterized FTS5 query and return matching rows as dicts."""
    if field not in VALID_FIELDS:
        print(f"ERROR: invalid field '{field}'. Must be one of: {sorted(VALID_FIELDS)}", file=sys.stderr)
        sys.exit(1)
    if not db_path.exists():
        print(f"ERROR: index not found at {db_path}. Run: afs_index.py init", file=sys.stderr)
        sys.exit(1)
    conn = open_db(db_path)
    # Use field-scoped FTS5 query: field MATCH 'query'
    # field is validated against VALID_FIELDS above before use in the f-string
    sql = (  # noqa: S608
        "SELECT date, branch, phase, status, "
        "snippet(sessions, 4, '[', ']', '...', 32) AS excerpt "
        f"FROM sessions WHERE {field} MATCH ?"
    )
    rows = [dict(r) for r in conn.execute(sql, (q,)).fetchall()]
    conn.close()
    return rows


def status_report(db_path: Path) -> dict:
    """Return coverage stats for the index."""
    if not db_path.exists():
        return {"exists": False, "db_path": str(db_path)}
    conn = open_db(db_path)
    total = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
    branches = [r[0] for r in conn.execute("SELECT DISTINCT branch FROM sessions").fetchall()]
    dates = [r[0] for r in conn.execute("SELECT DISTINCT date FROM sessions ORDER BY date DESC").fetchall()]
    last_indexed = conn.execute("SELECT value FROM _meta WHERE key = 'last_indexed'").fetchone()
    conn.close()
    return {
        "exists": True,
        "db_path": str(db_path),
        "total_rows": total,
        "branches": branches,
        "dates_indexed": dates,
        "last_indexed": last_indexed[0] if last_indexed else None,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _find_md_files(tmp_dir: Path, branch: str | None) -> list[Path]:
    """Return all .md session files for a branch (or all branches)."""
    if branch:
        target = tmp_dir / branch
        if not target.exists():
            print(f"ERROR: branch directory not found: {target}", file=sys.stderr)
            sys.exit(1)
        return sorted(p for p in target.glob("*.md") if not p.name.startswith("_"))
    # All branches
    return sorted(p for p in tmp_dir.rglob("*.md") if not p.name.startswith("_"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="afs_index.py",
        description="B' hybrid SQLite FTS5 index for .tmp/ session scratchpads.",
    )
    parser.add_argument(
        "command",
        choices=["init", "index", "query", "status"],
        help="Operation to perform",
    )
    parser.add_argument("--tmp-dir", default=str(DEFAULT_TMP_DIR), help="Base .tmp/ directory")
    parser.add_argument("--branch", help="Branch slug (default: auto-detect)")
    parser.add_argument("--db-path", help="Explicit .db file path")
    parser.add_argument("--q", help="Keyword query (required for 'query' command)")
    parser.add_argument(
        "--field",
        default="content",
        choices=["phase", "status", "content", "date", "branch"],
        help="FTS5 field to match against (default: content)",
    )
    parser.add_argument(
        "--format",
        default="table",
        choices=["table", "json"],
        help="Output format for query results (default: table)",
    )

    args = parser.parse_args(argv)
    tmp_dir = Path(args.tmp_dir)
    db_path = resolve_db_path(tmp_dir, args.branch, args.db_path)

    if args.command == "init":
        init_db(db_path)
        return 0

    if args.command == "index":
        init_db(db_path)
        md_files = _find_md_files(tmp_dir, args.branch or _git_branch())
        count = index_files(db_path, md_files)
        print(f"Indexed {count} rows from {len(md_files)} files → {db_path}")
        return 0

    if args.command == "query":
        if not args.q:
            parser.error("--q TEXT is required for the 'query' command")
        results = query_index(db_path, args.q, args.field)
        if args.format == "json":
            print(json.dumps(results, indent=2))
        else:
            if not results:
                print("No results.")
                return 0
            col_w = 20
            print(f"{'DATE':<12} {'BRANCH':<30} {'PHASE':<{col_w}} {'STATUS':<12} EXCERPT")
            print("-" * 110)
            for r in results:
                print(
                    f"{r['date']:<12} {r['branch'][:30]:<30} {r.get('phase', '')[:col_w]:<{col_w}} "
                    f"{r.get('status', '')[:12]:<12} {r.get('excerpt', '')[:60]}"
                )
        return 0

    if args.command == "status":
        report = status_report(db_path)
        print(json.dumps(report, indent=2))
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
