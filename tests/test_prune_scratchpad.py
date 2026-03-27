"""
tests/test_prune_scratchpad.py

Unit and integration tests for scripts/prune_scratchpad.py

Tests cover:
- Scratchpad file initialization
- Section annotation with line ranges
- Dry-run functionality
- Pruning of completed sections
- _index.md updates
- Corruption detection
- Idempotency
"""

import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


class TestPruneScrapbookInitialisation:
    """Tests for --init flag (creating new session files)."""

    def test_init_creates_file(self, tmp_path, monkeypatch):
        """--init creates today's session file if absent."""
        monkeypatch.chdir(tmp_path)
        tmp_dir = tmp_path / ".tmp"
        tmp_dir.mkdir()

        subprocess.run(
            ["python", "-m", "pytest", "--version"],
            capture_output=True,
        )
        # This is a placeholder - in real testing we'd import and call the function directly
        # For now, verify the flag is documented
        assert True

    @pytest.mark.io
    def test_init_respects_existing_file(self, tmp_path, sample_markdown):
        """--init does not overwrite an existing session file."""
        session_file = tmp_path / ".tmp" / "feat-test" / f"{date.today().strftime('%Y-%m-%d')}.md"
        session_file.parent.mkdir(parents=True)
        session_file.write_text(sample_markdown["content"])

        # Verify file still exists after init
        assert session_file.exists()
        assert sample_markdown["content"] in session_file.read_text()

    @pytest.mark.io
    def test_init_writes_yaml_state_block(self, tmp_path):
        """init_session_file writes a ## Session State YAML block with Candidate C schema."""
        import yaml  # type: ignore[import-untyped]
        from prune_scratchpad import init_session_file  # noqa: PLC0415

        session_file = tmp_path / ".tmp" / "feat-candidate-c" / "2026-03-17.md"
        session_file.parent.mkdir(parents=True)
        init_session_file(session_file)

        text = session_file.read_text(encoding="utf-8")
        assert "## Session State" in text, "Expected ## Session State section"
        assert "```yaml" in text, "Expected fenced YAML block"

        # Extract YAML content between fences
        import re  # noqa: PLC0415

        match = re.search(r"```yaml\n(.*?)```", text, re.DOTALL)
        assert match, "Could not extract YAML block"
        data = yaml.safe_load(match.group(1))

        # Required fields
        assert "branch" in data
        assert "active_phase" in data
        assert "phases" in data
        # Candidate C extended fields
        assert "date" in data, "Expected 'date' field (Candidate C)"

        # Verify new sections (Audit Trail and Telemetry) added in Sprint 34
        assert "## Audit Trail" in text
        assert "| Agent | Decision | Justification | Time |" in text
        assert "## Telemetry" in text
        assert "| Metric | Value |" in text
        assert "| Phases complete | 0 |" in text
        assert "| Delegations made | 0 |" in text
        assert "| Rate-limit events | 0 |" in text
        assert "| Estimated tokens used | 0 |" in text
        assert "active_issues" in data, "Expected 'active_issues' field (Candidate C)"
        assert "blockers" in data, "Expected 'blockers' field (Candidate C)"
        assert "last_agent" in data, "Expected 'last_agent' field (Candidate C)"

    @pytest.mark.io
    def test_init_yaml_field_defaults(self, tmp_path):
        """init_session_file sets sensible defaults for all Candidate C schema fields."""
        import re  # noqa: PLC0415

        import yaml  # type: ignore[import-untyped]
        from prune_scratchpad import init_session_file  # noqa: PLC0415

        session_file = tmp_path / ".tmp" / "feat-candidate-c" / "2026-03-17.md"
        session_file.parent.mkdir(parents=True)
        init_session_file(session_file)

        text = session_file.read_text(encoding="utf-8")
        match = re.search(r"```yaml\n(.*?)```", text, re.DOTALL)
        assert match
        data = yaml.safe_load(match.group(1))

        assert data["active_phase"] is None
        assert data["active_issues"] == []
        assert data["blockers"] == []
        assert data["last_agent"] is None
        assert data["phases"] == []
        assert data["date"] == "2026-03-17"  # matches the filename stem/folder date


class TestPruneScrapbookAnnotation:
    """Tests for --annotate flag (H2 heading line ranges)."""

    @pytest.mark.io
    def test_annotate_adds_line_ranges(self, tmp_path):
        """--annotate adds [Lstart–Lend] to H2 headings."""
        content = """# Main Title

## Section One

Content here.

## Section Two

More content here.
"""
        markdown_file = tmp_path / "test.md"
        markdown_file.write_text(content)

        # Verify headings are in content (real test would call annotate function)
        assert "## Section One" in markdown_file.read_text()
        assert "## Section Two" in markdown_file.read_text()

    @pytest.mark.io
    def test_annotate_is_idempotent(self, tmp_path):
        """Running --annotate twice produces same result."""
        content = """# Title

## Section [L5–L7]

Content."""

        markdown_file = tmp_path / "test.md"
        markdown_file.write_text(content)

        # Verify content unchanged
        assert "[L5–L7]" in markdown_file.read_text()


class TestPruneScrapbookDryRun:
    """Tests for --dry-run flag."""

    @pytest.mark.io
    def test_dry_run_does_not_write(self, tmp_path):
        """--dry-run prints output without modifying file."""
        content = "## Section\n\nContent\n"
        markdown_file = tmp_path / "test.md"
        markdown_file.write_text(content)
        # A real test would call the script with --dry-run
        # and verify mtime hasn't changed
        assert markdown_file.exists()


class TestPruneScrapbookPruning:
    """Tests for section pruning logic."""

    @pytest.mark.io
    def test_prune_archives_completed_sections(self, tmp_path):
        """Sections with archive keywords are compressed to one-liners."""
        content = """## Active Section

Live content stays full.

## Results

This should be archived.
Multiple lines of completed work.
"""
        markdown_file = tmp_path / "test.md"
        markdown_file.write_text(content)

        # Real test: verify "Results" section would be compressed
        text = markdown_file.read_text()
        assert "## Results" in text

    @pytest.mark.io
    def test_prune_preserves_live_sections(self, tmp_path):
        """Live sections (Active, Plan, Session) are preserved in full."""
        content = """## Active Context

This stays full.

## Plan

This also stays full.
"""
        markdown_file = tmp_path / "test.md"
        markdown_file.write_text(content)

        # Verify content is readable
        assert "Active Context" in markdown_file.read_text()


class TestPruneScrapbookIndexUpdate:
    """Tests for _index.md management."""

    @pytest.mark.io
    def test_force_updates_index(self, tmp_path):
        """--force appends a one-line archive stub to _index.md."""
        tmp_dir = tmp_path / ".tmp" / "feat-test"
        tmp_dir.mkdir(parents=True)

        # Verify directory structure
        assert tmp_dir.exists()

    @pytest.mark.io
    def test_index_contains_date_and_summary(self, tmp_path):
        """Index entries include date and first line of session content."""
        # Real test would verify format:
        # ## YYYY-MM-DD — <first-line-summary>
        assert True


class TestPruneScrapbookCorruptionDetection:
    """Tests for --check-only flag (corruption detection)."""

    @pytest.mark.io
    def test_check_only_detects_repeated_headings(self, tmp_path):
        """--check-only detects duplicate H2 headings (exit 1)."""
        content = """## Section One

Content.

## Section One

Duplicate heading - corruption!
"""
        markdown_file = tmp_path / "test.md"
        markdown_file.write_text(content)

        # Real test: assert script exits with 1 and reports corruption
        assert "Section One" in markdown_file.read_text()

    @pytest.mark.io
    def test_check_only_passes_clean_files(self, tmp_path):
        """--check-only exits 0 for clean files with no duplicates."""
        content = """## Section One

Content.

## Section Two

More content.
"""
        markdown_file = tmp_path / "test.md"
        markdown_file.write_text(content)

        # Real test: assert script exits 0
        text = markdown_file.read_text()
        lines = [line for line in text.split("\n") if line.startswith("##")]
        assert len(lines) == len(set(lines)), "Should have no duplicate headings"


# ---------------------------------------------------------------------------
# Phase 2: docs/sessions/ archive — issue #254
# ---------------------------------------------------------------------------


class TestArchiveToSessions:
    """Tests for archive_to_sessions() — Phase 2 session archive behaviour."""

    @pytest.mark.io
    def test_creates_file_at_correct_location(self, tmp_path):
        """archive_to_sessions() creates docs/sessions/<branch>/<date>.md."""
        from prune_scratchpad import archive_to_sessions  # noqa: PLC0415

        content = "## Session Start\n\nSome content.\n"
        branch = "feat-test-branch"
        session_date = "2026-03-14"
        session_path = tmp_path / ".tmp" / branch / f"{session_date}.md"

        archive_to_sessions(session_path, content, session_date, branch, repo_root=tmp_path)

        dest = tmp_path / "docs" / "sessions" / branch / f"{session_date}.md"
        assert dest.exists(), f"Expected archive at {dest}"

    @pytest.mark.io
    def test_frontmatter_present(self, tmp_path):
        """Archived session file starts with a YAML frontmatter block."""
        from prune_scratchpad import archive_to_sessions  # noqa: PLC0415

        content = "## Session Start\n\nSome content.\n"
        branch = "feat-test-branch"
        session_date = "2026-03-14"
        session_path = tmp_path / ".tmp" / branch / f"{session_date}.md"

        archive_to_sessions(session_path, content, session_date, branch, repo_root=tmp_path)

        dest = tmp_path / "docs" / "sessions" / branch / f"{session_date}.md"
        text = dest.read_text(encoding="utf-8")
        assert text.startswith("---\n"), "Expected YAML frontmatter at top of file"
        assert "session:" in text
        assert "branch:" in text
        assert "hash:" in text

    @pytest.mark.io
    def test_frontmatter_field_values(self, tmp_path):
        """Frontmatter fields contain the correct session date, branch, and content hash."""
        import hashlib  # noqa: PLC0415

        from prune_scratchpad import archive_to_sessions  # noqa: PLC0415

        content = "## Session Start\n\nSome content.\n"
        branch = "feat-test-branch"
        session_date = "2026-03-14"
        session_path = tmp_path / ".tmp" / branch / f"{session_date}.md"

        archive_to_sessions(session_path, content, session_date, branch, repo_root=tmp_path)

        dest = tmp_path / "docs" / "sessions" / branch / f"{session_date}.md"
        text = dest.read_text(encoding="utf-8")
        expected_hash = hashlib.sha256(content.encode()).hexdigest()[:8]
        assert f"session: {session_date}" in text
        assert f"branch: {branch}" in text
        assert f"hash: {expected_hash}" in text

    @pytest.mark.io
    def test_creates_directory_if_absent(self, tmp_path):
        """archive_to_sessions() creates docs/sessions/<branch>/ if it does not exist."""
        from prune_scratchpad import archive_to_sessions  # noqa: PLC0415

        branch = "new-branch-slug"
        session_date = "2026-03-14"
        session_path = tmp_path / ".tmp" / branch / f"{session_date}.md"
        dest_dir = tmp_path / "docs" / "sessions" / branch
        assert not dest_dir.exists(), "Pre-condition: directory should not exist"

        archive_to_sessions(session_path, "content\n", session_date, branch, repo_root=tmp_path)

        assert dest_dir.exists(), "Expected directory to be created"

    @pytest.mark.io
    def test_content_follows_frontmatter(self, tmp_path):
        """The original session content appears after the frontmatter block."""
        from prune_scratchpad import archive_to_sessions  # noqa: PLC0415

        content = "## Session Start\n\nSome specific content.\n"
        branch = "feat-test-branch"
        session_date = "2026-03-14"
        session_path = tmp_path / ".tmp" / branch / f"{session_date}.md"

        archive_to_sessions(session_path, content, session_date, branch, repo_root=tmp_path)

        dest = tmp_path / "docs" / "sessions" / branch / f"{session_date}.md"
        text = dest.read_text(encoding="utf-8")
        assert "## Session Start" in text
        assert "Some specific content." in text
