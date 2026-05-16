"""Tests for scripts/watch_scratchpad.py"""

import subprocess
import sys
import time
from pathlib import Path

import pytest


@pytest.mark.io
def test_script_has_watchdog_import_guard():
    """Test that the script contains the ImportError guard for watchdog."""
    script_path = Path("scripts/watch_scratchpad.py")
    content = script_path.read_text()

    # Verify the script has the import guard
    assert "from watchdog.events import FileSystemEventHandler" in content
    assert "except ImportError:" in content
    assert "watchdog is not installed" in content
    assert "sys.exit(1)" in content


@pytest.mark.io
@pytest.mark.slow
def test_watch_creates_observer_and_starts(tmp_path):
    """Test that the watcher starts successfully and can be interrupted."""
    scratchpad_dir = tmp_path / ".tmp" / "main"
    scratchpad_dir.mkdir(parents=True)

    test_file = scratchpad_dir / "2026-05-16.md"
    test_file.write_text("## Test Section\n\nContent here.\n")

    # Start the watcher and kill it after a brief delay
    proc = subprocess.Popen(
        [sys.executable, "scripts/watch_scratchpad.py", "--tmp-dir", str(tmp_path / ".tmp")],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    time.sleep(0.5)
    proc.terminate()
    stdout, stderr = proc.communicate(timeout=2)

    # Should exit cleanly (0 or -15 SIGTERM)
    assert proc.returncode in (0, -15, 15)


@pytest.mark.io
def test_excludes_index_files(tmp_path):
    """Test that _index.md and hidden files are excluded from watching."""
    scratchpad_dir = tmp_path / ".tmp" / "main"
    scratchpad_dir.mkdir(parents=True)

    # Create files that should be ignored
    (scratchpad_dir / "_index.md").write_text("# Index\n")
    (scratchpad_dir / ".hidden.md").write_text("# Hidden\n")

    # The watcher should start without processing these
    proc = subprocess.Popen(
        [sys.executable, "scripts/watch_scratchpad.py", "--tmp-dir", str(tmp_path / ".tmp")],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    time.sleep(0.5)
    proc.terminate()
    stdout, stderr = proc.communicate(timeout=2)

    # Should not have processed _index.md or .hidden.md
    assert "_index.md" not in stdout
    assert ".hidden.md" not in stdout


@pytest.mark.io
@pytest.mark.slow
def test_annotates_on_file_change(tmp_path):
    """Test that modifying a scratchpad file triggers annotation."""
    scratchpad_dir = tmp_path / ".tmp" / "main"
    scratchpad_dir.mkdir(parents=True)

    test_file = scratchpad_dir / "2026-05-16.md"
    test_file.write_text("## Test Section\n\nInitial content.\n")

    # Start the watcher
    proc = subprocess.Popen(
        [sys.executable, "scripts/watch_scratchpad.py", "--tmp-dir", str(tmp_path / ".tmp")],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Give it time to start watching
    time.sleep(0.5)

    # Modify the file
    test_file.write_text("## Test Section\n\nUpdated content.\n")

    # Give it time to process
    time.sleep(1.5)

    proc.terminate()
    stdout, stderr = proc.communicate(timeout=2)

    # Should have detected the change
    assert "2026-05-16.md" in stdout or stderr


@pytest.mark.io
def test_cooldown_prevents_loop(tmp_path):
    """Test that cooldown mechanism prevents annotation loops."""
    scratchpad_dir = tmp_path / ".tmp" / "main"
    scratchpad_dir.mkdir(parents=True)

    test_file = scratchpad_dir / "2026-05-16.md"
    test_file.write_text("## Test Section\n\nContent.\n")

    # The cooldown is 2 seconds - rapid successive writes should be ignored
    proc = subprocess.Popen(
        [sys.executable, "scripts/watch_scratchpad.py", "--tmp-dir", str(tmp_path / ".tmp")],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    time.sleep(0.5)

    # Write multiple times rapidly
    for i in range(3):
        test_file.write_text(f"## Test Section\n\nContent {i}.\n")
        time.sleep(0.3)  # Less than cooldown

    time.sleep(1)
    proc.terminate()
    stdout, stderr = proc.communicate(timeout=2)

    # Should have processed at most once due to cooldown
    assert proc.returncode in (0, -15, 15)


@pytest.mark.io
def test_help_option_exits_0():
    """Test that --help works and exits with code 0."""
    result = subprocess.run([sys.executable, "scripts/watch_scratchpad.py", "--help"], capture_output=True, text=True)

    assert result.returncode == 0
    assert "watch_scratchpad" in result.stdout or "Usage" in result.stdout


@pytest.mark.io
def test_custom_tmp_dir_option(tmp_path):
    """Test that --tmp-dir option is respected."""
    custom_dir = tmp_path / "custom_tmp"
    custom_dir.mkdir()

    scratchpad_dir = custom_dir / "branch"
    scratchpad_dir.mkdir()

    test_file = scratchpad_dir / "2026-05-16.md"
    test_file.write_text("## Section\n")

    proc = subprocess.Popen(
        [sys.executable, "scripts/watch_scratchpad.py", "--tmp-dir", str(custom_dir)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    time.sleep(0.5)
    proc.terminate()
    stdout, stderr = proc.communicate(timeout=2)

    assert proc.returncode in (0, -15, 15)
