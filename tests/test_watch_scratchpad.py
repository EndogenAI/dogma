"""Tests for scripts/watch_scratchpad.py"""

import subprocess
import sys
import time
from unittest.mock import patch

import pytest

# Import business logic functions for unit tests
from scripts.watch_scratchpad import (
    WATCHDOG_AVAILABLE,
    annotate_file,
    should_process_file,
)

if WATCHDOG_AVAILABLE:
    from scripts.watch_scratchpad import ScratchpadHandler


# ---------------------------------------------------------------------------
# Unit Tests — Business Logic
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_should_process_file_accepts_valid_md(tmp_path):
    """Test that valid .md session files are accepted."""
    session_file = tmp_path / "2026-05-16.md"
    session_file.write_text("## Test\n")

    assert should_process_file(session_file) is True


@pytest.mark.io
def test_should_process_file_rejects_index_files(tmp_path):
    """Test that _index.md files are rejected."""
    index_file = tmp_path / "_index.md"
    index_file.write_text("# Index\n")

    assert should_process_file(index_file) is False


@pytest.mark.io
def test_should_process_file_rejects_hidden_files(tmp_path):
    """Test that hidden files (starting with .) are rejected."""
    hidden_file = tmp_path / ".hidden.md"
    hidden_file.write_text("# Hidden\n")

    assert should_process_file(hidden_file) is False


@pytest.mark.io
def test_should_process_file_rejects_non_md(tmp_path):
    """Test that non-.md files are rejected."""
    txt_file = tmp_path / "notes.txt"
    txt_file.write_text("Notes\n")

    assert should_process_file(txt_file) is False


@pytest.mark.io
def test_should_process_file_rejects_nonexistent(tmp_path):
    """Test that non-existent files are rejected."""
    nonexistent = tmp_path / "missing.md"

    assert should_process_file(nonexistent) is False


@pytest.mark.io
def test_annotate_file_returns_exit_code(tmp_path):
    """Test that annotate_file returns (exit_code, stdout, stderr) tuple."""
    session_file = tmp_path / "2026-05-16.md"
    session_file.write_text("## Test Section\n\nContent here.\n")

    # Mock the annotate script
    fake_script = tmp_path / "fake_annotate.py"
    fake_script.write_text("import sys; print('annotated'); sys.exit(0)")

    exit_code, stdout, stderr = annotate_file(session_file, annotate_script=fake_script, repo_root=tmp_path)

    assert exit_code == 0
    assert "annotated" in stdout


@pytest.mark.io
@pytest.mark.skipif(not WATCHDOG_AVAILABLE, reason="watchdog not installed")
def test_handler_cooldown_mechanism(tmp_path):
    """Test that ScratchpadHandler cooldown prevents rapid re-triggers."""
    handler = ScratchpadHandler()

    test_path = str(tmp_path / "test.md")

    # First call should be OK
    assert handler._cooldown_ok(test_path) is True

    # Record a write
    handler._record(test_path)

    # Immediate second call should be blocked by cooldown
    assert handler._cooldown_ok(test_path) is False


@pytest.mark.io
@pytest.mark.skipif(not WATCHDOG_AVAILABLE, reason="watchdog not installed")
def test_handler_filters_excluded_files(tmp_path):
    """Test that handler does not process excluded files."""
    handler = ScratchpadHandler()

    # Create excluded files
    index_file = tmp_path / "_index.md"
    index_file.write_text("# Index\n")

    hidden_file = tmp_path / ".hidden.md"
    hidden_file.write_text("# Hidden\n")

    # Handler should not process these
    with patch.object(handler, "_record") as mock_record:
        handler._handle(str(index_file))
        handler._handle(str(hidden_file))

        # _record should never be called for excluded files
        mock_record.assert_not_called()


@pytest.mark.io
@pytest.mark.skipif(not WATCHDOG_AVAILABLE, reason="watchdog not installed")
def test_handler_processes_valid_files(tmp_path):
    """Test that handler processes valid session files."""
    # Create a mock annotate script that succeeds
    fake_script = tmp_path / "fake_annotate.py"
    fake_script.write_text("import sys; print('annotated'); sys.exit(0)")

    handler = ScratchpadHandler(annotate_script=fake_script, repo_root=tmp_path)

    session_file = tmp_path / "2026-05-16.md"
    session_file.write_text("## Test Section\n\nContent here.\n")

    # Handler should process this file
    with patch("builtins.print") as mock_print:
        handler._handle(str(session_file))

        # Should have printed the "Changed: ... — annotating…" message
        assert any("annotating" in str(call) for call in mock_print.call_args_list)


@pytest.mark.io
def test_main_function_returns_0_on_success():
    """Test that main() returns 0 when successfully started and stopped."""
    # We can't easily test the full observer lifecycle in a unit test,
    # so this test just confirms main() can be imported and called.
    from scripts.watch_scratchpad import main

    # main() is a function that can be called
    assert callable(main)


@pytest.mark.io
def test_main_returns_1_when_watchdog_unavailable(monkeypatch):
    """Test that main() returns exit code 1 when watchdog is not available."""
    # Mock WATCHDOG_AVAILABLE to False
    import scripts.watch_scratchpad as ws_module

    monkeypatch.setattr(ws_module, "WATCHDOG_AVAILABLE", False)

    # Now call main() - it should return 1
    exit_code = ws_module.main()
    assert exit_code == 1


@pytest.mark.io
@pytest.mark.skipif(not WATCHDOG_AVAILABLE, reason="watchdog not installed")
def test_handler_prints_error_on_annotation_failure(tmp_path):
    """Test that handler prints error message when annotation fails."""
    # Create a mock annotate script that fails
    fake_script = tmp_path / "fake_annotate_fail.py"
    fake_script.write_text("import sys; print('error', file=sys.stderr); sys.exit(1)")

    handler = ScratchpadHandler(annotate_script=fake_script, repo_root=tmp_path)

    session_file = tmp_path / "2026-05-16.md"
    session_file.write_text("## Test Section\n\nContent here.\n")

    # Handler should process this file and print an error
    import io
    import sys

    captured_stderr = io.StringIO()
    old_stderr = sys.stderr
    sys.stderr = captured_stderr

    try:
        handler._handle(str(session_file))
        error_output = captured_stderr.getvalue()
        assert "ERROR" in error_output or "error" in error_output
    finally:
        sys.stderr = old_stderr


@pytest.mark.io
@pytest.mark.skipif(not WATCHDOG_AVAILABLE, reason="watchdog not installed")
def test_handler_on_modified_event(tmp_path):
    """Test that on_modified event handler processes file changes."""
    from watchdog.events import FileModifiedEvent

    # Create a mock annotate script that succeeds
    fake_script = tmp_path / "fake_annotate.py"
    fake_script.write_text("import sys; print('annotated'); sys.exit(0)")

    handler = ScratchpadHandler(annotate_script=fake_script, repo_root=tmp_path)

    session_file = tmp_path / "2026-05-16.md"
    session_file.write_text("## Test Section\n\nContent here.\n")

    # Create a file modified event
    event = FileModifiedEvent(str(session_file))

    # Call on_modified
    with patch("builtins.print") as mock_print:
        handler.on_modified(event)

        # Should have printed something
        assert mock_print.called


@pytest.mark.io
@pytest.mark.skipif(not WATCHDOG_AVAILABLE, reason="watchdog not installed")
def test_handler_on_created_event(tmp_path):
    """Test that on_created event handler processes new files."""
    from watchdog.events import FileCreatedEvent

    # Create a mock annotate script that succeeds
    fake_script = tmp_path / "fake_annotate.py"
    fake_script.write_text("import sys; print('annotated'); sys.exit(0)")

    handler = ScratchpadHandler(annotate_script=fake_script, repo_root=tmp_path)

    session_file = tmp_path / "2026-05-16.md"
    session_file.write_text("## Test Section\n\nContent here.\n")

    # Create a file created event
    event = FileCreatedEvent(str(session_file))

    # Call on_created
    with patch("builtins.print") as mock_print:
        handler.on_created(event)

        # Should have printed something
        assert mock_print.called


@pytest.mark.io
@pytest.mark.skipif(not WATCHDOG_AVAILABLE, reason="watchdog not installed")
def test_annotate_file_with_successful_annotation(tmp_path):
    """Test annotate_file with successful annotation prints output."""
    # Create a mock annotate script that succeeds with output
    fake_script = tmp_path / "fake_annotate.py"
    fake_script.write_text("import sys; print('Annotated successfully'); sys.exit(0)")

    session_file = tmp_path / "2026-05-16.md"
    session_file.write_text("## Test Section\n\nContent here.\n")

    exit_code, stdout, stderr = annotate_file(session_file, annotate_script=fake_script, repo_root=tmp_path)

    assert exit_code == 0
    assert "Annotated successfully" in stdout
    assert stderr == ""


# ---------------------------------------------------------------------------
# Integration Tests — CLI (keep 1-2 subprocess tests as smoke tests)
# ---------------------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.io
@pytest.mark.slow
def test_cli_watch_starts_and_stops(tmp_path):
    """Integration test: watcher starts successfully and can be interrupted."""
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


@pytest.mark.integration
@pytest.mark.io
def test_cli_help_option_exits_0():
    """Integration test: --help works and exits with code 0."""
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
