"""tests/test_create_audit_reminder_issue.py

Tests for scripts/create_audit_reminder_issue.py

Covers:
1. test_duplicate_check_skips_if_existing_issue
2. test_creates_issue_when_no_duplicate
3. test_gh_list_failure_returns_1
4. test_gh_create_failure_returns_1
5. test_temp_file_cleaned_up_on_success
6. test_temp_file_cleaned_up_on_failure
7. test_gh_not_found_exits_1
8. test_main_exit_0_on_duplicate
"""

from __future__ import annotations

import importlib
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

reminder_mod = importlib.import_module("scripts.create_audit_reminder_issue")
main = reminder_mod.main


def _make_completed(returncode: int = 0, stdout: str = "", stderr: str = "") -> subprocess.CompletedProcess:
    r = MagicMock(spec=subprocess.CompletedProcess)
    r.returncode = returncode
    r.stdout = stdout
    r.stderr = stderr
    return r


# ---------------------------------------------------------------------------
# 1. Skip when duplicate already open
# ---------------------------------------------------------------------------


class TestDuplicateCheck:
    def test_duplicate_check_skips_if_existing_issue(self, capsys: pytest.CaptureFixture) -> None:
        # gh issue list returns an existing issue number
        with patch.object(reminder_mod, "_gh") as mock_gh:
            mock_gh.return_value = _make_completed(stdout="42\n")
            rc = main()
        assert rc == 0
        out = capsys.readouterr().out
        assert "SKIP" in out
        assert "42" in out
        # gh issue create must NOT have been called
        calls = [str(c) for c in mock_gh.call_args_list]
        assert not any("create" in c for c in calls)


# ---------------------------------------------------------------------------
# 2. Creates issue when no duplicate
# ---------------------------------------------------------------------------


class TestCreatesIssue:
    def test_creates_issue_when_no_duplicate(self, capsys: pytest.CaptureFixture) -> None:
        def _side_effect(*args, **kwargs):
            subcmd = args[0] if args else []
            if "list" in subcmd:
                return _make_completed(stdout="")  # no existing issue
            return _make_completed(stdout="https://github.com/EndogenAI/dogma/issues/999\n")

        with patch.object(reminder_mod, "_gh", side_effect=_side_effect):
            rc = main()

        assert rc == 0
        out = capsys.readouterr().out
        assert "github.com" in out or "999" in out


# ---------------------------------------------------------------------------
# 3. gh list failure returns 1
# ---------------------------------------------------------------------------


class TestGhErrors:
    def test_gh_list_failure_returns_1(self) -> None:
        with patch.object(reminder_mod, "_gh", return_value=_make_completed(returncode=1, stderr="auth error")):
            rc = main()
        assert rc == 1

    def test_gh_create_failure_returns_1(self) -> None:
        def _side_effect(*args, **kwargs):
            subcmd = args[0] if args else []
            if "list" in subcmd:
                return _make_completed(stdout="")
            return _make_completed(returncode=1, stderr="422 Unprocessable Entity")

        with patch.object(reminder_mod, "_gh", side_effect=_side_effect):
            rc = main()
        assert rc == 1


# ---------------------------------------------------------------------------
# 5–6. Temp file cleanup
# ---------------------------------------------------------------------------


class TestTempFileCleanup:
    def _run_and_capture_tmp(self, side_effect) -> list[Path]:
        created = []
        original_ntf = __import__("tempfile").NamedTemporaryFile

        def _patched_ntf(*args, **kwargs):
            ctx = original_ntf(*args, **kwargs)
            created.append(Path(ctx.name))
            return ctx

        with patch("tempfile.NamedTemporaryFile", side_effect=_patched_ntf):
            with patch.object(reminder_mod, "_gh", side_effect=side_effect):
                main()
        return created

    def test_temp_file_cleaned_up_on_success(self) -> None:
        def _side_effect(*args, **kwargs):
            subcmd = args[0] if args else []
            if "list" in subcmd:
                return _make_completed(stdout="")
            return _make_completed(stdout="https://github.com/issues/1\n")

        created = self._run_and_capture_tmp(_side_effect)
        for p in created:
            assert not p.exists(), f"Temp file {p} was not cleaned up"

    def test_temp_file_cleaned_up_on_failure(self) -> None:
        def _side_effect(*args, **kwargs):
            subcmd = args[0] if args else []
            if "list" in subcmd:
                return _make_completed(stdout="")
            return _make_completed(returncode=1, stderr="error")

        created = self._run_and_capture_tmp(_side_effect)
        for p in created:
            assert not p.exists(), f"Temp file {p} was not cleaned up after failure"


# ---------------------------------------------------------------------------
# 7. gh CLI not found
# ---------------------------------------------------------------------------


class TestGhNotFound:
    def test_gh_not_found_exits_1(self) -> None:
        """FileNotFoundError from missing gh CLI must exit with code 1."""
        with patch("subprocess.run", side_effect=FileNotFoundError("No such file")):
            with pytest.raises(SystemExit) as exc_info:
                main()
        assert exc_info.value.code == 1
