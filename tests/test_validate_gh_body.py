"""Tests for scripts/validate_gh_body.py"""

import subprocess
import sys

import pytest


@pytest.mark.io
def test_body_file_usage_passes(tmp_path):
    """Test that --body-file usage passes."""
    test_script = tmp_path / "test.py"
    test_script.write_text("""
#!/usr/bin/env python3
import subprocess

body_file = "/tmp/issue_body.md"
subprocess.run(['gh', 'issue', 'create', '--body-file', body_file])
""")

    result = subprocess.run(
        [sys.executable, "scripts/validate_gh_body.py", str(test_script)], capture_output=True, text=True
    )

    assert result.returncode == 0
    assert "correctly" in result.stdout


@pytest.mark.io
def test_multiline_body_fails(tmp_path):
    """Test that multi-line --body string fails."""
    test_script = tmp_path / "test.sh"
    test_script.write_text("""
#!/bin/bash
gh issue create --body "This is a multi-line
body that will cause problems
with shell quoting"
""")

    result = subprocess.run(
        [sys.executable, "scripts/validate_gh_body.py", str(test_script)], capture_output=True, text=True
    )

    assert result.returncode == 1
    assert "violations found" in result.stdout.lower()
    assert "test.sh" in result.stdout


@pytest.mark.io
def test_single_line_body_passes(tmp_path):
    """Test that single-line --body is acceptable."""
    test_script = tmp_path / "test.py"
    test_script.write_text("""
#!/usr/bin/env python3
import subprocess

subprocess.run(['gh', 'issue', 'create', '--title', 'Bug', '--body', 'Short description'])
""")

    result = subprocess.run(
        [sys.executable, "scripts/validate_gh_body.py", str(test_script)], capture_output=True, text=True
    )

    assert result.returncode == 0


@pytest.mark.io
def test_pr_create_with_multiline_fails(tmp_path):
    """Test that PR create with multi-line body fails."""
    test_script = tmp_path / "test.sh"
    test_script.write_text("""
gh pr create --title "Fix bug" --body "Line one
Line two
Line three"
""")

    result = subprocess.run(
        [sys.executable, "scripts/validate_gh_body.py", str(test_script)], capture_output=True, text=True
    )

    assert result.returncode == 1
    assert "pr create" in result.stdout.lower() or "violations" in result.stdout.lower()


@pytest.mark.io
def test_directory_scan(tmp_path):
    """Test scanning a directory."""
    good_script = tmp_path / "good.py"
    good_script.write_text("gh issue create --body-file /tmp/body.md")

    bad_script = tmp_path / "bad.py"
    bad_script.write_text('gh issue create --body "Multi\nLine\nContent"')

    result = subprocess.run(
        [sys.executable, "scripts/validate_gh_body.py", str(tmp_path)], capture_output=True, text=True
    )

    # Should detect bad.py violation
    assert result.returncode == 1
    assert "bad.py" in result.stdout


@pytest.mark.io
def test_no_paths_defaults_to_scripts_docs():
    """Test that no arguments defaults to checking scripts/ and docs/."""
    result = subprocess.run([sys.executable, "scripts/validate_gh_body.py"], capture_output=True, text=True)

    # Should run (exit 0 or 1), not error out
    assert result.returncode in [0, 1]


@pytest.mark.io
def test_nonexistent_path_warns(tmp_path):
    """Test that nonexistent path produces warning."""
    nonexistent = tmp_path / "does_not_exist"

    result = subprocess.run(
        [sys.executable, "scripts/validate_gh_body.py", str(nonexistent), str(tmp_path)], capture_output=True, text=True
    )

    # Should warn but continue with valid paths
    assert "does not exist" in result.stderr or "Warning" in result.stderr
