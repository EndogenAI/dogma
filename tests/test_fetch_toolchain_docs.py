"""
tests/test_fetch_toolchain_docs.py — Tests for scripts/fetch_toolchain_docs.py

Verifies that the script:
- Parses top-level subcommands from `gh help` output correctly
- Builds per-subcommand Markdown with the expected structure
- Writes index.md and aggregate gh.md when mocked output is provided
- Respects --check (skip if fresh) and --force (always regenerate)
- Exits 1 with a clear error if `gh` is not on PATH
- Skips failing subcommands and continues rather than aborting
- Creates the output directory if it does not exist

All file I/O tests are marked @pytest.mark.io.
No real `gh` binary is required — all subprocess calls are mocked.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path
from unittest.mock import patch

import pytest

# Make scripts/ importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import fetch_toolchain_docs as ftd  # noqa: E402

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_GH_HELP = """\
Work seamlessly with GitHub from the command line.

USAGE
  gh <command> <subcommand> [flags]

CORE COMMANDS
  issue:    Manage issues
  pr:       Manage pull requests
  repo:     Create, clone, fork, and view repositories

ADDITIONAL COMMANDS
  label:    Manage labels

FLAGS
  --help    Show help for command
  --version Show gh version

EXAMPLES
  $ gh issue list

LEARN MORE
  Use gh <command> <subcommand> --help for more information
"""

SAMPLE_ISSUE_HELP = """\
Work with GitHub issues.

USAGE
  gh issue <command> [flags]

CORE COMMANDS
  create:   Create a new issue
  list:     List issues in a repository
  view:     View details of an issue

FLAGS
  -R, --repo [HOST/]OWNER/REPO   Select another repository
  --help                          Show help for command

EXAMPLES
  $ gh issue list --label bug
  $ gh issue create --title "My Issue" --body-file body.md
"""


# ---------------------------------------------------------------------------
# Unit tests: parsers and formatters
# ---------------------------------------------------------------------------


def test_parse_top_level_subcommands_extracts_core_commands():
    pairs = ftd.parse_top_level_subcommands(SAMPLE_GH_HELP)
    names = [name for name, _ in pairs]
    assert "issue" in names
    assert "pr" in names
    assert "repo" in names
    assert "label" in names


def test_parse_top_level_subcommands_deduplicates():
    """Repeated subcommand names should only appear once."""
    duplicated = SAMPLE_GH_HELP + "\n  issue:    Duplicate entry\n"
    pairs = ftd.parse_top_level_subcommands(duplicated)
    names = [name for name, _ in pairs]
    assert names.count("issue") == 1


def test_parse_top_level_subcommands_returns_descriptions():
    pairs = ftd.parse_top_level_subcommands(SAMPLE_GH_HELP)
    mapping = dict(pairs)
    assert "Manage issues" in mapping["issue"]
    assert "Manage pull requests" in mapping["pr"]


def test_build_subcommand_markdown_structure():
    md = ftd.build_subcommand_markdown("gh issue", SAMPLE_ISSUE_HELP, "Manage issues")
    assert md.startswith("# gh issue")
    assert "## Usage" in md
    assert "## Flags" in md
    assert "## Examples" in md


def test_build_subcommand_markdown_fallback_description():
    """When preamble is empty, fallback description should appear in the heading."""
    sparse_help = "USAGE\n  gh sparse [flags]\n"
    md = ftd.build_subcommand_markdown("sparse", sparse_help, "Fallback desc")
    assert "Fallback desc" in md


def test_build_subcommand_markdown_flags_table():
    md = ftd.build_subcommand_markdown("issue", SAMPLE_ISSUE_HELP, "")
    # The flags table should be present and contain at least the --help flag
    assert "## Flags" in md
    assert "| Flag | Description |" in md
    assert "--help" in md


def test_build_subcommand_markdown_examples():
    md = ftd.build_subcommand_markdown("issue", SAMPLE_ISSUE_HELP, "")
    assert "gh issue list" in md or "gh issue create" in md


def test_cache_is_fresh_missing_file(tmp_path):
    assert ftd._cache_is_fresh(tmp_path / "nonexistent.md") is False


@pytest.mark.io
def test_cache_is_fresh_new_file(tmp_path):
    p = tmp_path / "index.md"
    p.write_text("hello")
    assert ftd._cache_is_fresh(p, max_age_hours=24) is True


@pytest.mark.io
def test_cache_is_fresh_old_file(tmp_path):
    p = tmp_path / "index.md"
    p.write_text("hello")
    # Back-date the file by 25 hours
    old_mtime = time.time() - (25 * 3600)
    import os

    os.utime(p, (old_mtime, old_mtime))
    assert ftd._cache_is_fresh(p, max_age_hours=24) is False


# ---------------------------------------------------------------------------
# Integration-style tests: fetch_gh_docs with mocked subprocess
# ---------------------------------------------------------------------------


def _make_run_side_effect(subcommand_help: str = SAMPLE_ISSUE_HELP):
    """Return a side-effect function for _run that returns canned help text."""

    def side_effect(args):
        if args == ["gh", "help"]:
            return SAMPLE_GH_HELP, 0
        # Any `gh <sub> --help` call returns the sample help
        return subcommand_help, 0

    return side_effect


@pytest.mark.io
def test_fetch_gh_docs_missing_gh_binary(tmp_path):
    """Should exit 1 and print an error if gh is not on PATH."""
    with patch("fetch_toolchain_docs.shutil.which", return_value=None):
        rc = ftd.fetch_gh_docs(tmp_path)
    assert rc == 1


@pytest.mark.io
def test_fetch_gh_docs_creates_output_directory(tmp_path):
    """Output directory should be created if it does not exist."""
    out = tmp_path / "deep" / "nested"
    with (
        patch("fetch_toolchain_docs.shutil.which", return_value="/usr/bin/gh"),
        patch("fetch_toolchain_docs._run", side_effect=_make_run_side_effect()),
    ):
        rc = ftd.fetch_gh_docs(out)
    assert rc == 0
    assert (out / "gh").is_dir()


@pytest.mark.io
def test_fetch_gh_docs_writes_index_and_aggregate(tmp_path):
    """index.md and gh.md should be written on a successful run."""
    with (
        patch("fetch_toolchain_docs.shutil.which", return_value="/usr/bin/gh"),
        patch("fetch_toolchain_docs._run", side_effect=_make_run_side_effect()),
    ):
        rc = ftd.fetch_gh_docs(tmp_path)
    assert rc == 0
    assert (tmp_path / "gh" / "index.md").exists()
    assert (tmp_path / "gh.md").exists()


@pytest.mark.io
def test_fetch_gh_docs_writes_per_subcommand_files(tmp_path):
    """A .md file should be written for each parsed subcommand."""
    with (
        patch("fetch_toolchain_docs.shutil.which", return_value="/usr/bin/gh"),
        patch("fetch_toolchain_docs._run", side_effect=_make_run_side_effect()),
    ):
        rc = ftd.fetch_gh_docs(tmp_path)
    assert rc == 0
    assert (tmp_path / "gh" / "issue.md").exists()
    assert (tmp_path / "gh" / "pr.md").exists()


@pytest.mark.io
def test_fetch_gh_docs_check_skips_when_fresh(tmp_path):
    """--check should return 0 and skip generation when cache is fresh."""
    index = tmp_path / "gh" / "index.md"
    index.parent.mkdir(parents=True)
    index.write_text("existing content")

    with (
        patch("fetch_toolchain_docs.shutil.which", return_value="/usr/bin/gh"),
        patch("fetch_toolchain_docs._run") as mock_run,
    ):
        rc = ftd.fetch_gh_docs(tmp_path, check=True, force=False)

    assert rc == 0
    mock_run.assert_not_called()  # nothing should be fetched


@pytest.mark.io
def test_fetch_gh_docs_force_regenerates_even_when_fresh(tmp_path):
    """--force should regenerate even if cache is fresh."""
    index = tmp_path / "gh" / "index.md"
    index.parent.mkdir(parents=True)
    index.write_text("stale content")

    with (
        patch("fetch_toolchain_docs.shutil.which", return_value="/usr/bin/gh"),
        patch("fetch_toolchain_docs._run", side_effect=_make_run_side_effect()),
    ):
        rc = ftd.fetch_gh_docs(tmp_path, check=True, force=True)

    assert rc == 0
    # File should be rewritten (no longer "stale content")
    assert index.read_text() != "stale content"


@pytest.mark.io
def test_fetch_gh_docs_skips_failing_subcommand(tmp_path):
    """A failing subcommand help call should be skipped, not abort the run."""
    call_count = 0

    def selective_failure(args):
        nonlocal call_count
        if args == ["gh", "help"]:
            return SAMPLE_GH_HELP, 0
        call_count += 1
        # Fail for the first subcommand (issue), succeed for the rest
        if "issue" in args:
            return "", 1
        return SAMPLE_ISSUE_HELP, 0

    with (
        patch("fetch_toolchain_docs.shutil.which", return_value="/usr/bin/gh"),
        patch("fetch_toolchain_docs._run", side_effect=selective_failure),
    ):
        rc = ftd.fetch_gh_docs(tmp_path)

    assert rc == 0
    # issue.md should not exist (was skipped)
    assert not (tmp_path / "gh" / "issue.md").exists()
    # other files should exist
    assert (tmp_path / "gh" / "pr.md").exists()


@pytest.mark.io
def test_fetch_gh_docs_dry_run_writes_nothing(tmp_path):
    """--dry-run should not write any files."""
    with (
        patch("fetch_toolchain_docs.shutil.which", return_value="/usr/bin/gh"),
        patch("fetch_toolchain_docs._run", side_effect=_make_run_side_effect()),
    ):
        rc = ftd.fetch_gh_docs(tmp_path, dry_run=True)

    assert rc == 0
    # No files written
    assert not list(tmp_path.rglob("*.md"))
