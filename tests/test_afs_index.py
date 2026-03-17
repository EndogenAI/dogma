"""tests/test_afs_index.py — Tests for scripts/afs_index.py (B' FTS5 index)

Tests cover:
    - init: creates DB with correct FTS5 schema
    - index: parses scratchpad .md files and inserts rows
    - query: FTS5 keyword search returns matching rows
    - status: returns correct coverage stats
    - parse_scratchpad: section extraction from .md content
    - error handling: missing DB, missing files
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from scripts.afs_index import (
    index_files,
    init_db,
    main,
    parse_scratchpad,
    query_index,
    resolve_db_path,
    status_report,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def tmp_branch_dir(tmp_path):
    """Create a temporary .tmp/<branch>/ directory."""
    branch_dir = tmp_path / "tmp" / "feat-test-branch"
    branch_dir.mkdir(parents=True)
    return branch_dir


@pytest.fixture()
def sample_md(tmp_branch_dir):
    """Write a minimal scratchpad .md file and return its path."""
    md = tmp_branch_dir / "2026-03-17.md"
    md.write_text(
        "# Session — feat-test-branch / 2026-03-17\n\n"
        "## Session Start\n\nGoverning axiom: Algorithms Before Tokens.\n\n"
        "## Phase 2 — Scripting ⬜\n\nImplementing afs_index.py for issue #129.\n\n"
        "## Phase 2 Review Output\n\nAPPROVED.\n\n"
        "## Session Summary\n\nPhase 2 complete. Blockers: none.\n",
        encoding="utf-8",
    )
    return md


@pytest.fixture()
def db_path(tmp_branch_dir):
    """Return a DB path within the temp branch dir."""
    return tmp_branch_dir / ".scratchpad_index.db"


# ---------------------------------------------------------------------------
# resolve_db_path
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_resolve_db_path_explicit(tmp_path):
    explicit = str(tmp_path / "custom.db")
    result = resolve_db_path(tmp_path, None, explicit)
    assert result == Path(explicit)


@pytest.mark.io
def test_resolve_db_path_branch(tmp_path):
    result = resolve_db_path(tmp_path, "my-branch", None)
    assert result == tmp_path / "my-branch" / ".scratchpad_index.db"


# ---------------------------------------------------------------------------
# init_db
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_init_db_creates_file(db_path):
    init_db(db_path)
    assert db_path.exists()


@pytest.mark.io
def test_init_db_fts5_table(db_path):
    init_db(db_path)
    conn = sqlite3.connect(str(db_path))
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    conn.close()
    assert "sessions" in tables
    assert "_meta" in tables


@pytest.mark.io
def test_init_db_idempotent(db_path):
    """Calling init twice should not raise."""
    init_db(db_path)
    init_db(db_path)
    assert db_path.exists()


# ---------------------------------------------------------------------------
# parse_scratchpad
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_parse_scratchpad_returns_rows(sample_md):
    rows = parse_scratchpad(sample_md)
    assert len(rows) >= 2  # at least the full-file row + some section rows


@pytest.mark.io
def test_parse_scratchpad_date_from_filename(sample_md):
    rows = parse_scratchpad(sample_md)
    assert all(r["date"] == "2026-03-17" for r in rows)


@pytest.mark.io
def test_parse_scratchpad_branch_from_parent(sample_md):
    rows = parse_scratchpad(sample_md)
    assert all(r["branch"] == "feat-test-branch" for r in rows)


@pytest.mark.io
def test_parse_scratchpad_phase_extracted(sample_md):
    rows = parse_scratchpad(sample_md)
    phase_rows = [r for r in rows if r["phase"]]
    assert any("Phase 2" in r["phase"] for r in phase_rows)


@pytest.mark.io
def test_parse_scratchpad_full_file_row(sample_md):
    rows = parse_scratchpad(sample_md)
    # First row is always the full-file row with empty phase
    full_row = rows[0]
    assert full_row["phase"] == ""
    assert "afs_index" in full_row["content"]


# ---------------------------------------------------------------------------
# index_files
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_index_files_inserts_rows(db_path, sample_md):
    init_db(db_path)
    count = index_files(db_path, [sample_md])
    assert count > 0


@pytest.mark.io
def test_index_files_idempotent(db_path, sample_md):
    """Re-indexing the same file should not duplicate rows."""
    init_db(db_path)
    index_files(db_path, [sample_md])
    count_first = index_files(db_path, [sample_md])
    conn = sqlite3.connect(str(db_path))
    total = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
    conn.close()
    assert count_first == total  # same count after second index


@pytest.mark.io
def test_index_files_skips_missing(db_path, tmp_path):
    init_db(db_path)
    missing = tmp_path / "nonexistent.md"
    count = index_files(db_path, [missing])
    assert count == 0


# ---------------------------------------------------------------------------
# query_index
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_query_returns_results(db_path, sample_md):
    init_db(db_path)
    index_files(db_path, [sample_md])
    results = query_index(db_path, "afs_index")
    assert len(results) >= 1


@pytest.mark.io
def test_query_no_results(db_path, sample_md):
    init_db(db_path)
    index_files(db_path, [sample_md])
    results = query_index(db_path, "xylophone_NONEXISTENT_WORD_123")
    assert results == []


@pytest.mark.io
def test_query_phase_field(db_path, sample_md):
    init_db(db_path)
    index_files(db_path, [sample_md])
    results = query_index(db_path, "Phase 2", field="phase")
    assert len(results) >= 1


@pytest.mark.io
def test_query_missing_db_exits(tmp_path):
    missing_db = tmp_path / "missing.db"
    with pytest.raises(SystemExit) as exc_info:
        query_index(missing_db, "anything")
    assert exc_info.value.code == 1


@pytest.mark.io
def test_query_invalid_field_exits(tmp_path):
    db = tmp_path / "test.db"
    init_db(db)
    with pytest.raises(SystemExit) as exc_info:
        query_index(db, "test", field="injected; DROP TABLE sessions;--")
    assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# status_report
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_status_missing_db(tmp_path):
    report = status_report(tmp_path / "missing.db")
    assert report["exists"] is False


@pytest.mark.io
def test_status_after_index(db_path, sample_md):
    init_db(db_path)
    index_files(db_path, [sample_md])
    report = status_report(db_path)
    assert report["exists"] is True
    assert report["total_rows"] > 0
    assert "feat-test-branch" in report["branches"]
    assert "2026-03-17" in report["dates_indexed"]
    assert report["last_indexed"] is not None


# ---------------------------------------------------------------------------
# main (CLI integration)
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_main_init(tmp_path):
    db = tmp_path / "branch" / ".scratchpad_index.db"
    rc = main(["init", "--db-path", str(db)])
    assert rc == 0
    assert db.exists()


@pytest.mark.io
def test_main_status_no_db(tmp_path, capsys):
    db = tmp_path / "noexist.db"
    rc = main(["status", "--db-path", str(db)])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert rc == 0
    assert data["exists"] is False


@pytest.mark.io
def test_main_index_and_query(tmp_path, tmp_branch_dir, sample_md):
    # Init DB
    db = tmp_branch_dir / ".scratchpad_index.db"
    main(["init", "--db-path", str(db)])
    # Index
    rc = main(["index", "--tmp-dir", str(tmp_path / "tmp"), "--branch", "feat-test-branch", "--db-path", str(db)])
    assert rc == 0
    # Query
    rc = main(["query", "--q", "afs_index", "--db-path", str(db)])
    assert rc == 0


@pytest.mark.io
def test_main_query_json(tmp_path, tmp_branch_dir, sample_md, capsys):
    db = tmp_branch_dir / ".scratchpad_index.db"
    main(["init", "--db-path", str(db)])
    capsys.readouterr()  # clear init output
    main(["index", "--tmp-dir", str(tmp_path / "tmp"), "--branch", "feat-test-branch", "--db-path", str(db)])
    capsys.readouterr()  # clear index output
    rc = main(["query", "--q", "Scripting", "--field", "content", "--format", "json", "--db-path", str(db)])
    assert rc == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert isinstance(data, list)
