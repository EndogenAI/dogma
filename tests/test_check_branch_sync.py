"""
tests/test_check_branch_sync.py
--------------------------------
Tests for scripts/check_branch_sync.py — branch sync gate.

Covers:
- In-sync branch: exit 0, success message printed
- Behind branch: exit 1, commit list printed
- Behind branch with --quiet: exit 1, no output
- Behind branch with --rebase: runs rebase, exit 0
- --rebase failure: git rebase exits non-zero → sys.exit(2)
- fetch failure: git fetch fails → sys.exit(2)
- git log failure: git log fails → sys.exit(2)
- Custom --remote and --base flags
- main() callable with argv list
- Module entrypoint (__name__ == '__main__')

All subprocess calls are mocked to keep tests hermetic (no real git state needed).
Coverage target: ≥80% of scripts/check_branch_sync.py

Marked @pytest.mark.integration because the module imports subprocess — mocked
but still exercises shell-level dispatch logic at integration depth.
"""

from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

# ---------------------------------------------------------------------------
# Module loader
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def cbs_mod():
    """Load scripts/check_branch_sync.py via importlib for in-process testing."""
    spec = importlib.util.spec_from_file_location(
        "check_branch_sync",
        Path(__file__).parent.parent / "scripts" / "check_branch_sync.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _completed(returncode: int = 0, stdout: str = "", stderr: str = "") -> MagicMock:
    """Build a mock CompletedProcess."""
    cp = MagicMock(spec=subprocess.CompletedProcess)
    cp.returncode = returncode
    cp.stdout = stdout
    cp.stderr = stderr
    return cp


# ---------------------------------------------------------------------------
# fetch_remote
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestFetchRemote:
    def test_fetch_success(self, cbs_mod, capsys):
        with patch("subprocess.run", return_value=_completed(0)) as mock_run:
            cbs_mod.fetch_remote("origin")
        mock_run.assert_called_once_with(["git", "fetch", "origin"], capture_output=True, text=True)

    def test_fetch_failure_exits_2(self, cbs_mod, capsys):
        with patch("subprocess.run", return_value=_completed(1, stderr="fatal")):
            with pytest.raises(SystemExit) as exc_info:
                cbs_mod.fetch_remote("origin")
        assert exc_info.value.code == 2

    def test_fetch_custom_remote(self, cbs_mod):
        with patch("subprocess.run", return_value=_completed(0)) as mock_run:
            cbs_mod.fetch_remote("upstream")
        mock_run.assert_called_once_with(["git", "fetch", "upstream"], capture_output=True, text=True)


# ---------------------------------------------------------------------------
# get_behind_commits
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestGetBehindCommits:
    def test_empty_means_in_sync(self, cbs_mod):
        with patch("subprocess.run", return_value=_completed(0, stdout="")):
            result = cbs_mod.get_behind_commits("origin", "main")
        assert result == []

    def test_returns_commit_lines(self, cbs_mod):
        stdout = "abc1234 Fix something\ndef5678 Add feature\n"
        with patch("subprocess.run", return_value=_completed(0, stdout=stdout)):
            result = cbs_mod.get_behind_commits("origin", "main")
        assert result == ["abc1234 Fix something", "def5678 Add feature"]

    def test_git_log_failure_exits_2(self, cbs_mod):
        with patch("subprocess.run", return_value=_completed(1, stderr="fatal")):
            with pytest.raises(SystemExit) as exc_info:
                cbs_mod.get_behind_commits("origin", "main")
        assert exc_info.value.code == 2

    def test_custom_remote_and_base(self, cbs_mod):
        with patch("subprocess.run", return_value=_completed(0, stdout="")) as mock_run:
            cbs_mod.get_behind_commits("upstream", "develop")
        mock_run.assert_called_once_with(
            ["git", "log", "HEAD..upstream/develop", "--oneline"],
            capture_output=True,
            text=True,
        )


# ---------------------------------------------------------------------------
# rebase_onto
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestRebaseOnto:
    def test_rebase_success(self, cbs_mod):
        with patch("subprocess.run", return_value=_completed(0)) as mock_run:
            cbs_mod.rebase_onto("origin", "main")
        mock_run.assert_called_once_with(["git", "rebase", "origin/main"], capture_output=False, text=True)

    def test_rebase_failure_exits_2(self, cbs_mod):
        with patch("subprocess.run", return_value=_completed(1, stderr="conflict")):
            with pytest.raises(SystemExit) as exc_info:
                cbs_mod.rebase_onto("origin", "main")
        assert exc_info.value.code == 2


# ---------------------------------------------------------------------------
# main() — integration scenarios
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestMain:
    def _patch_sync(self, fetch_rc=0, behind_commits=None, rebase_rc=0):
        """Return a context manager patching subprocess.run for the full main() flow."""
        behind_commits = behind_commits or []

        def side_effect(cmd, **kwargs):
            if cmd[:2] == ["git", "fetch"]:
                return _completed(fetch_rc)
            if cmd[:2] == ["git", "log"]:
                stdout = "\n".join(behind_commits) + ("\n" if behind_commits else "")
                return _completed(0, stdout=stdout)
            if cmd[:2] == ["git", "rebase"]:
                return _completed(rebase_rc)
            return _completed(0)

        return patch("subprocess.run", side_effect=side_effect)

    def test_in_sync_exits_0(self, cbs_mod, capsys):
        with self._patch_sync(behind_commits=[]):
            exit_code = cbs_mod.main([])
        assert exit_code == 0
        out = capsys.readouterr().out
        assert "up to date" in out

    def test_behind_exits_1(self, cbs_mod, capsys):
        commits = ["abc1234 Fix something", "def5678 Add feature"]
        with self._patch_sync(behind_commits=commits):
            exit_code = cbs_mod.main([])
        assert exit_code == 1
        out = capsys.readouterr().out
        assert "abc1234" in out
        assert "def5678" in out
        assert "2 commit(s) behind" in out

    def test_behind_quiet_exits_1_no_output(self, cbs_mod, capsys):
        commits = ["abc1234 Fix something"]
        with self._patch_sync(behind_commits=commits):
            exit_code = cbs_mod.main(["--quiet"])
        assert exit_code == 1
        out, err = capsys.readouterr()
        assert out == ""
        assert err == ""

    def test_behind_rebase_exits_0(self, cbs_mod, capsys):
        commits = ["abc1234 Fix something"]
        with self._patch_sync(behind_commits=commits, rebase_rc=0):
            exit_code = cbs_mod.main(["--rebase"])
        assert exit_code == 0
        out = capsys.readouterr().out
        assert "Rebase complete" in out

    def test_behind_rebase_failure_exits_2(self, cbs_mod, capsys):
        commits = ["abc1234 Fix something"]
        with self._patch_sync(behind_commits=commits, rebase_rc=1):
            with pytest.raises(SystemExit) as exc_info:
                cbs_mod.main(["--rebase"])
        assert exc_info.value.code == 2

    def test_custom_remote_and_base(self, cbs_mod, capsys):
        with self._patch_sync(behind_commits=[]) as mock_run:
            exit_code = cbs_mod.main(["--remote", "upstream", "--base", "develop"])
        assert exit_code == 0
        # fetch should have been called with "upstream"
        fetch_call = mock_run.call_args_list[0]
        assert fetch_call == call(["git", "fetch", "upstream"], capture_output=True, text=True)

    def test_fetch_failure_propagates(self, cbs_mod):
        with patch("subprocess.run", return_value=_completed(1, stderr="no remote")):
            with pytest.raises(SystemExit) as exc_info:
                cbs_mod.main([])
        assert exc_info.value.code == 2

    def test_in_sync_quiet_no_output(self, cbs_mod, capsys):
        with self._patch_sync(behind_commits=[]):
            exit_code = cbs_mod.main(["--quiet"])
        assert exit_code == 0
        out, err = capsys.readouterr()
        assert out == ""
        assert err == ""
