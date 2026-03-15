"""
tests/test_orientation_snapshot.py

Unit tests for scripts/orientation_snapshot.py

Tests cover:
- Snapshot is generated and written to the output path
- --branch flag includes scratchpad ## Session Summary section
- Missing branch directory is handled gracefully (no error)
- --dry-run prints to stdout without writing a file
- Snapshot stays < 200 lines
- build_snapshot() is importable and returns a string
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from orientation_snapshot import (  # noqa: E402
    _extract_session_summary,
    build_snapshot,
    main,
)

# ---------------------------------------------------------------------------
# Core snapshot generation
# ---------------------------------------------------------------------------


class TestSnapshotGeneration:
    """Snapshot is created at the expected path."""

    @pytest.mark.io
    def test_snapshot_written_to_default_path(self, tmp_path, monkeypatch):
        """main() writes orientation-snapshot.md to the specified output path."""
        monkeypatch.chdir(tmp_path)
        output = tmp_path / ".cache" / "github" / "orientation-snapshot.md"
        with (
            patch("orientation_snapshot._collect_issue_counts", return_value="## Issues\n- high: 2"),
            patch("orientation_snapshot._collect_recent_commits", return_value="## Commits\n- abc123"),
            patch("orientation_snapshot._collect_active_branches", return_value="## Branches\n- main"),
            patch("orientation_snapshot._collect_milestone_summary", return_value="## Milestones\n- M1"),
        ):
            code = main(["--output", str(output)])
        assert code == 0
        assert output.exists()

    @pytest.mark.io
    def test_snapshot_contains_expected_sections(self, tmp_path, monkeypatch):
        """Generated snapshot includes all standard section headings."""
        monkeypatch.chdir(tmp_path)
        output = tmp_path / "snapshot.md"
        with (
            patch("orientation_snapshot._collect_issue_counts", return_value="## Open Issues by Priority\n- high: 3"),
            patch("orientation_snapshot._collect_recent_commits", return_value="## Recent Commits (last 5)\n- abc"),
            patch("orientation_snapshot._collect_active_branches", return_value="## Active Branches\n- main"),
            patch("orientation_snapshot._collect_milestone_summary", return_value="## Current Milestones\n- none"),
        ):
            main(["--output", str(output)])
        content = output.read_text()
        assert "Orientation Snapshot" in content
        assert "Issues" in content
        assert "Commits" in content
        assert "Branches" in content

    def test_build_snapshot_returns_string(self):
        """build_snapshot() returns a non-empty string."""
        with (
            patch("orientation_snapshot._collect_issue_counts", return_value="## Issues\n- 0"),
            patch("orientation_snapshot._collect_recent_commits", return_value="## Commits\n"),
            patch("orientation_snapshot._collect_active_branches", return_value="## Branches\n"),
            patch("orientation_snapshot._collect_milestone_summary", return_value="## Milestones\n"),
        ):
            result = build_snapshot()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_snapshot_under_200_lines(self, tmp_path):
        """Snapshot is always < 200 lines."""
        # Build a snapshot with artificially long sections
        long_section = "## Issues\n" + "\n".join(f"- item {i}" for i in range(300))
        with (
            patch("orientation_snapshot._collect_issue_counts", return_value=long_section),
            patch("orientation_snapshot._collect_recent_commits", return_value="## Commits\n"),
            patch("orientation_snapshot._collect_active_branches", return_value="## Branches\n"),
            patch("orientation_snapshot._collect_milestone_summary", return_value="## Milestones\n"),
        ):
            content = build_snapshot()
        assert len(content.splitlines()) < 200


# ---------------------------------------------------------------------------
# --branch flag — scratchpad session summary extraction
# ---------------------------------------------------------------------------


class TestBranchFlag:
    """--branch includes latest ## Session Summary from the scratchpad."""

    @pytest.mark.io
    def test_branch_section_included_in_snapshot(self, tmp_path, monkeypatch):
        """When --branch is set, snapshot includes scratchpad session summary."""
        monkeypatch.chdir(tmp_path)
        branch = "feat/test-branch"
        slug = "feat-test-branch"
        scratchpad_dir = tmp_path / ".tmp" / slug
        scratchpad_dir.mkdir(parents=True)
        scratchpad = scratchpad_dir / "2026-03-14.md"
        scratchpad.write_text(
            "## Session Start\n\nSome start notes.\n\n## Session Summary\n\nPhase 1 complete. Next: Phase 2.\n"
        )

        output = tmp_path / "snapshot.md"
        with (
            patch("orientation_snapshot._collect_issue_counts", return_value="## Issues\n"),
            patch("orientation_snapshot._collect_recent_commits", return_value="## Commits\n"),
            patch("orientation_snapshot._collect_active_branches", return_value="## Branches\n"),
            patch("orientation_snapshot._collect_milestone_summary", return_value="## Milestones\n"),
        ):
            code = main(["--branch", branch, "--output", str(output)])
        assert code == 0
        content = output.read_text()
        assert "Phase 1 complete" in content
        assert "Session Summary" in content

    @pytest.mark.io
    def test_extract_session_summary_returns_content(self, tmp_path, monkeypatch):
        """_extract_session_summary returns the last ## Session Summary block."""
        monkeypatch.chdir(tmp_path)
        slug = "feat-my-feature"
        scratchpad_dir = tmp_path / ".tmp" / slug
        scratchpad_dir.mkdir(parents=True)
        (scratchpad_dir / "2026-03-14.md").write_text(
            "## Work Log\n\nDone X.\n\n## Session Summary\n\nAll done. Next: deploy.\n"
        )
        result = _extract_session_summary("feat/my-feature")
        assert "All done" in result
        assert "Session Summary" in result

    @pytest.mark.io
    def test_extract_session_summary_multiple_summaries(self, tmp_path, monkeypatch):
        """_extract_session_summary returns the LAST ## Session Summary block."""
        monkeypatch.chdir(tmp_path)
        slug = "feat-multi"
        scratchpad_dir = tmp_path / ".tmp" / slug
        scratchpad_dir.mkdir(parents=True)
        (scratchpad_dir / "2026-03-14.md").write_text(
            "## Session Summary\n\nFirst summary.\n\n"
            "## Work\n\nMore work.\n\n"
            "## Session Summary\n\nSecond summary — latest.\n"
        )
        result = _extract_session_summary("feat/multi")
        assert "Second summary" in result


# ---------------------------------------------------------------------------
# Missing branch — graceful handling
# ---------------------------------------------------------------------------


class TestMissingBranch:
    """Missing scratchpad directory for a branch is handled gracefully."""

    @pytest.mark.io
    def test_missing_branch_no_error(self, tmp_path, monkeypatch):
        """--branch with no scratchpad directory exits 0 without raising."""
        monkeypatch.chdir(tmp_path)
        output = tmp_path / "snapshot.md"
        with (
            patch("orientation_snapshot._collect_issue_counts", return_value="## Issues\n"),
            patch("orientation_snapshot._collect_recent_commits", return_value="## Commits\n"),
            patch("orientation_snapshot._collect_active_branches", return_value="## Branches\n"),
            patch("orientation_snapshot._collect_milestone_summary", return_value="## Milestones\n"),
        ):
            code = main(["--branch", "feat/nonexistent-branch", "--output", str(output)])
        assert code == 0

    @pytest.mark.io
    def test_missing_branch_note_in_snapshot(self, tmp_path, monkeypatch):
        """Snapshot notes that no scratchpad directory was found for the branch."""
        monkeypatch.chdir(tmp_path)
        result = _extract_session_summary("feat/nonexistent-branch")
        # Should return a noting string, not raise
        assert isinstance(result, str)
        assert "nonexistent-branch" in result or "no scratchpad" in result.lower()

    @pytest.mark.io
    def test_extract_no_summary_in_file(self, tmp_path, monkeypatch):
        """File exists but has no ## Session Summary — returns descriptive note."""
        monkeypatch.chdir(tmp_path)
        slug = "feat-no-summary"
        scratchpad_dir = tmp_path / ".tmp" / slug
        scratchpad_dir.mkdir(parents=True)
        (scratchpad_dir / "2026-03-14.md").write_text("## Work Log\n\nNo summary here.\n")
        result = _extract_session_summary("feat/no-summary")
        assert isinstance(result, str)
        assert "Session Summary" in result or "no" in result.lower()


# ---------------------------------------------------------------------------
# --dry-run
# ---------------------------------------------------------------------------


class TestDryRun:
    """--dry-run prints to stdout without writing a file."""

    @pytest.mark.io
    def test_dry_run_prints_content(self, tmp_path, monkeypatch, capsys):
        """--dry-run outputs snapshot to stdout."""
        monkeypatch.chdir(tmp_path)
        with (
            patch("orientation_snapshot._collect_issue_counts", return_value="## Issues\n- 1"),
            patch("orientation_snapshot._collect_recent_commits", return_value="## Commits\n"),
            patch("orientation_snapshot._collect_active_branches", return_value="## Branches\n"),
            patch("orientation_snapshot._collect_milestone_summary", return_value="## Milestones\n"),
        ):
            code = main(["--dry-run"])
        assert code == 0
        captured = capsys.readouterr()
        assert "Orientation Snapshot" in captured.out

    @pytest.mark.io
    def test_dry_run_does_not_write_file(self, tmp_path, monkeypatch):
        """--dry-run does not write any file."""
        monkeypatch.chdir(tmp_path)
        with (
            patch("orientation_snapshot._collect_issue_counts", return_value="## Issues\n"),
            patch("orientation_snapshot._collect_recent_commits", return_value="## Commits\n"),
            patch("orientation_snapshot._collect_active_branches", return_value="## Branches\n"),
            patch("orientation_snapshot._collect_milestone_summary", return_value="## Milestones\n"),
        ):
            main(["--dry-run"])
        # Default output file should NOT be written
        default_out = tmp_path / ".cache" / "github" / "orientation-snapshot.md"
        assert not default_out.exists()
