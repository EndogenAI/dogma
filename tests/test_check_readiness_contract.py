"""Tests for scripts/check_readiness_contract.py"""

import subprocess
import sys

import pytest


@pytest.mark.io
def test_ready_with_matrix_passes(tmp_path):
    """Test that readiness claim with capability matrix passes."""
    test_file = tmp_path / "test.md"
    test_file.write_text("""
# Project Status

Ready — capability matrix:
- Retrieval ✅
- Generation ✅
- E2E ✅

All systems ready.
""")

    result = subprocess.run(
        [sys.executable, "scripts/check_readiness_contract.py", "--scope", str(test_file)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "properly scoped" in result.stdout


@pytest.mark.io
def test_ready_without_matrix_fails(tmp_path):
    """Test that unqualified readiness claim fails."""
    test_file = tmp_path / "test.md"
    test_file.write_text("""
# Project Status

The system is ready for deployment.
All tests pass.
""")

    result = subprocess.run(
        [sys.executable, "scripts/check_readiness_contract.py", "--scope", str(test_file)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "violations found" in result.stdout.lower()
    assert "ready" in result.stdout.lower()


@pytest.mark.io
def test_scoped_ready_with_dash_passes(tmp_path):
    """Test that scoped readiness (ready — ...) passes."""
    test_file = tmp_path / "test.md"
    test_file.write_text("""
# Status

Ready — Retrieval only; generation in progress.
""")

    result = subprocess.run(
        [sys.executable, "scripts/check_readiness_contract.py", "--scope", str(test_file)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0


@pytest.mark.io
def test_code_blocks_ignored(tmp_path):
    """Test that readiness claims in code blocks are ignored."""
    test_file = tmp_path / "test.md"
    test_file.write_text("""
# Example

```python
# System is ready
print("ready")
```

This capability matrix shows:
- Feature A ✅
""")

    result = subprocess.run(
        [sys.executable, "scripts/check_readiness_contract.py", "--scope", str(test_file)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0


@pytest.mark.io
def test_directory_scan(tmp_path):
    """Test scanning entire directory."""
    (tmp_path / "good.md").write_text("Ready — capability: X ✅")
    (tmp_path / "bad.md").write_text("System is complete and ready.")

    result = subprocess.run(
        [sys.executable, "scripts/check_readiness_contract.py", "--scope", str(tmp_path)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "bad.md" in result.stdout


@pytest.mark.io
def test_nonexistent_path_fails(tmp_path):
    """Test that nonexistent path returns error exit code."""
    nonexistent = tmp_path / "does_not_exist.md"

    result = subprocess.run(
        [sys.executable, "scripts/check_readiness_contract.py", "--scope", str(nonexistent)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "does not exist" in result.stderr
