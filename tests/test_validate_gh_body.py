"""Tests for scripts/validate_gh_body.py"""

import subprocess
import sys

import pytest

# Import business logic functions directly
from scripts.validate_gh_body import check_file_content, scan_paths


class TestMain:
    """Unit tests for main() CLI function."""

    def test_main_with_valid_path(self, tmp_path, monkeypatch):
        """Test main() with valid path containing no violations."""
        test_script = tmp_path / "test.py"
        test_script.write_text("gh issue create --body-file /tmp/body.md")

        # Mock sys.argv
        monkeypatch.setattr("sys.argv", ["validate_gh_body.py", str(tmp_path)])

        # Import and run main
        from scripts.validate_gh_body import main

        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 0

    def test_main_with_violations(self, tmp_path, monkeypatch):
        """Test main() with violations exits 1."""
        test_script = tmp_path / "test.sh"
        test_script.write_text('gh issue create --body "Multi\nLine"')

        monkeypatch.setattr("sys.argv", ["validate_gh_body.py", str(tmp_path)])

        from scripts.validate_gh_body import main

        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 1

    def test_main_with_nonexistent_path(self, tmp_path, monkeypatch):
        """Test main() with all nonexistent paths exits 2."""
        nonexistent = tmp_path / "does_not_exist"

        monkeypatch.setattr("sys.argv", ["validate_gh_body.py", str(nonexistent)])

        from scripts.validate_gh_body import main

        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 2


class TestCheckFileContent:
    """Unit tests for check_file_content() function."""

    def test_body_file_usage_no_violations(self, tmp_path):
        """Test that --body-file usage returns no violations."""
        test_script = tmp_path / "test.py"
        test_script.write_text("""
#!/usr/bin/env python3
import subprocess

body_file = "/tmp/issue_body.md"
subprocess.run(['gh', 'issue', 'create', '--body-file', body_file])
""")

        violations = check_file_content(test_script)
        assert violations == []

    def test_multiline_body_detected(self, tmp_path):
        """Test that multi-line --body string is detected."""
        test_script = tmp_path / "test.sh"
        test_script.write_text("""
#!/bin/bash
gh issue create --body "This is a multi-line
body that will cause problems
with shell quoting"
""")

        violations = check_file_content(test_script)
        assert len(violations) > 0
        assert any("gh" in snippet for _, snippet in violations)

    def test_single_line_body_no_violations(self, tmp_path):
        """Test that single-line --body is acceptable."""
        test_script = tmp_path / "test.py"
        test_script.write_text("""
#!/usr/bin/env python3
import subprocess

subprocess.run(['gh', 'issue', 'create', '--title', 'Bug', '--body', 'Short description'])
""")

        violations = check_file_content(test_script)
        assert violations == []

    def test_pr_create_multiline_detected(self, tmp_path):
        """Test that PR create with multi-line body is detected."""
        test_script = tmp_path / "test.sh"
        test_script.write_text("""
gh pr create --title "Fix bug" --body "Line one
Line two
Line three"
""")

        violations = check_file_content(test_script)
        assert len(violations) > 0

    def test_body_variable_with_newline_detected(self, tmp_path):
        """Test that --body with variable containing \\n is detected."""
        test_script = tmp_path / "test.sh"
        test_script.write_text("""
body="Line 1\\nLine 2"
gh issue create --body "$body"
""")

        violations = check_file_content(test_script)
        assert len(violations) > 0

    def test_unreadable_file_raises_exception(self, tmp_path):
        """Test that unreadable file raises exception."""
        test_script = tmp_path / "unreadable.py"
        test_script.write_text("content")
        test_script.chmod(0o000)  # Remove all permissions

        try:
            with pytest.raises(Exception):
                check_file_content(test_script)
        finally:
            test_script.chmod(0o644)  # Restore permissions for cleanup


class TestScanPaths:
    """Unit tests for scan_paths() function."""

    def test_directory_scan(self, tmp_path):
        """Test scanning a directory for violations."""
        good_script = tmp_path / "good.py"
        good_script.write_text("gh issue create --body-file /tmp/body.md")

        bad_script = tmp_path / "bad.py"
        bad_script.write_text('gh issue create --body "Multi\nLine\nContent"')

        violations = scan_paths([tmp_path])

        # Should detect bad.py violation
        assert len(violations) > 0
        assert any("bad.py" in str(path) for path in violations.keys())

    def test_single_file_scan(self, tmp_path):
        """Test scanning a single file."""
        test_file = tmp_path / "test.py"
        test_file.write_text('gh issue create --body "Multi\nLine"')

        violations = scan_paths([test_file])

        assert test_file in violations
        assert len(violations[test_file]) > 0

    def test_cache_and_site_dirs_skipped(self, tmp_path):
        """Test that .cache and site directories are skipped."""
        cache_dir = tmp_path / ".cache"
        cache_dir.mkdir()
        cache_file = cache_dir / "test.py"
        cache_file.write_text('gh issue create --body "Multi\nLine"')

        violations = scan_paths([tmp_path])

        # .cache files should not appear in violations
        assert cache_file not in violations


@pytest.mark.integration
class TestValidateGhBodyIntegration:
    """Integration tests using subprocess (smoke tests)."""

    def test_cli_integration_multiline_fails(self, tmp_path):
        """Integration test: CLI detects multi-line violations."""
        test_script = tmp_path / "test.sh"
        test_script.write_text("""
gh issue create --body "Multi-line
content here"
""")

        result = subprocess.run(
            [sys.executable, "scripts/validate_gh_body.py", str(test_script)], capture_output=True, text=True
        )

        assert result.returncode == 1
        assert "violations found" in result.stdout.lower()

    def test_cli_integration_body_file_passes(self, tmp_path):
        """Integration test: CLI accepts --body-file usage."""
        test_script = tmp_path / "test.py"
        test_script.write_text("gh issue create --body-file /tmp/body.md")

        result = subprocess.run(
            [sys.executable, "scripts/validate_gh_body.py", str(test_script)], capture_output=True, text=True
        )

        assert result.returncode == 0
        assert "correctly" in result.stdout
