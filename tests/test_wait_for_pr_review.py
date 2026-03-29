"""Tests for wait_for_pr_review.py."""

import os
import subprocess
import sys
from unittest.mock import MagicMock, patch

import pytest

# Add scripts directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from wait_for_pr_review import get_pr_state, main


class TestGetPrState:
    """Test get_pr_state function."""

    @patch("subprocess.run")
    def test_no_reviews_yet(self, mock_run):
        """pending=[copilot], reviews=[] → state returned correctly."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"reviewRequests": [{"login": "copilot"}], "reviews": []}\n',
        )
        state = get_pr_state(510, "owner/repo")
        assert state is not None
        assert state["pending"] == ["copilot"]
        assert state["reviews"] == []

    @patch("subprocess.run")
    def test_all_reviews_landed(self, mock_run):
        """pending=[], reviews=[{id, body, state, author}] → parsed correctly."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=(
                '{"reviewRequests": [], "reviews": [{"id": "r1", "body": "lgtm", '
                '"state": "APPROVED", "author": {"login": "copilot"}}]}\n'
            ),
        )
        state = get_pr_state(510, "owner/repo")
        assert state is not None
        assert state["pending"] == []
        assert len(state["reviews"]) == 1
        assert state["reviews"][0] == {
            "id": "r1",
            "body": "lgtm",
            "state": "APPROVED",
            "author": "copilot",
        }

    @patch("subprocess.run")
    def test_gh_cli_error(self, mock_run):
        """returncode=1 → None."""
        mock_run.return_value = MagicMock(returncode=1, stderr="pull request not found")
        assert get_pr_state(999, "owner/repo") is None

    @patch("subprocess.run")
    def test_invalid_json(self, mock_run):
        """Invalid JSON response → None."""
        mock_run.return_value = MagicMock(returncode=0, stdout="not json\n")
        assert get_pr_state(510, "owner/repo") is None

    @patch("subprocess.run")
    def test_timeout(self, mock_run):
        """TimeoutExpired → None."""
        mock_run.side_effect = subprocess.TimeoutExpired("cmd", 30)
        assert get_pr_state(510, "owner/repo") is None

    @patch("subprocess.run")
    def test_missing_key(self, mock_run):
        """Missing reviewRequests key → None."""
        mock_run.return_value = MagicMock(returncode=0, stdout='{"reviews": []}\n')
        assert get_pr_state(510, "owner/repo") is None

    @patch("subprocess.run")
    def test_file_not_found(self, mock_run):
        """FileNotFoundError (gh CLI missing) → None."""
        mock_run.side_effect = FileNotFoundError("gh: command not found")
        assert get_pr_state(510, "owner/repo") is None

    @patch("subprocess.run")
    def test_correct_args_passed(self, mock_run):
        """gh called with --json reviewRequests,reviews."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"reviewRequests": [], "reviews": []}\n',
        )
        get_pr_state(42, "myorg/myrepo")
        call_args = mock_run.call_args[0][0]
        assert "gh" in call_args
        assert "42" in [str(a) for a in call_args]
        assert "--repo" in call_args
        assert "myorg/myrepo" in call_args
        assert "--json" in call_args
        json_idx = call_args.index("--json")
        json_fields = call_args[json_idx + 1]
        assert "reviewRequests" in json_fields
        assert "reviews" in json_fields


class TestMain:
    """Test main polling logic."""

    @patch("wait_for_pr_review.get_pr_state")
    def test_all_already_landed(self, mock_state, capsys):
        """initial_pending=[], reviews=[one review with body] → exit 0 immediately."""
        mock_state.return_value = {
            "pending": [],
            "reviews": [{"id": "r1", "body": "lgtm", "state": "APPROVED", "author": "copilot"}],
        }
        with patch.object(sys, "argv", ["wait_for_pr_review.py", "510"]):
            result = main()
        assert result == 0
        captured = capsys.readouterr()
        assert "✓" in captured.out
        assert "510" in captured.out
        # Exits before the polling loop — only baseline call made
        assert mock_state.call_count == 1

    @patch("wait_for_pr_review.get_pr_state")
    @patch("time.sleep")
    def test_nothing_at_startup_exits_immediately(self, mock_sleep, mock_state, capsys):
        """initial_pending=[], reviews=[] → fallback, 1 review appears → exit 0."""
        baseline = {"pending": [], "reviews": []}
        poll1 = {
            "pending": [],
            "reviews": [{"id": "r1", "body": "lgtm", "state": "COMMENTED", "author": "copilot"}],
        }
        mock_state.side_effect = [baseline, poll1]
        with patch.object(sys, "argv", ["wait_for_pr_review.py", "510", "--timeout-secs", "60"]):
            result = main()
        assert result == 0
        captured = capsys.readouterr()
        assert "auto-detect unavailable" in captured.out
        assert "✓" in captured.out

    @patch("wait_for_pr_review.get_pr_state")
    @patch("time.sleep")
    def test_pending_then_lands(self, mock_sleep, mock_state, capsys):
        """initial_pending=[copilot], first poll: still pending; second poll: pending=[], new review → exit 0."""
        baseline = {"pending": ["copilot"], "reviews": []}
        poll1 = {"pending": ["copilot"], "reviews": []}
        poll2 = {
            "pending": [],
            "reviews": [{"id": "r1", "body": "LGTM!", "state": "APPROVED", "author": "copilot"}],
        }
        mock_state.side_effect = [baseline, poll1, poll2]
        with patch.object(sys, "argv", ["wait_for_pr_review.py", "510", "--timeout-secs", "60"]):
            result = main()
        assert result == 0
        captured = capsys.readouterr()
        assert "✓" in captured.out
        # One sleep between poll1 and poll2
        assert mock_sleep.call_count == 1

    @patch("wait_for_pr_review.get_pr_state")
    @patch("time.sleep")
    def test_timeout(self, mock_sleep, mock_state, capsys):
        """Pending never empties → exit 1."""
        mock_state.return_value = {"pending": ["copilot"], "reviews": []}
        with patch.object(
            sys,
            "argv",
            ["wait_for_pr_review.py", "510", "--timeout-secs", "1", "--interval-secs", "0"],
        ):
            result = main()
        assert result == 1
        captured = capsys.readouterr()
        assert "Timed out" in captured.out

    @patch("wait_for_pr_review.get_pr_state")
    @patch("time.sleep")
    def test_consecutive_errors_exit_2(self, mock_sleep, mock_state, capsys):
        """3 consecutive None returns → exit 2."""
        mock_state.return_value = None
        with patch.object(
            sys,
            "argv",
            ["wait_for_pr_review.py", "510", "--timeout-secs", "60"],
        ):
            result = main()
        assert result == 2
        captured = capsys.readouterr()
        assert "consecutive fetch errors" in captured.out

    @patch("wait_for_pr_review.get_pr_state")
    @patch("time.sleep")
    def test_filter_empty_body(self, mock_sleep, mock_state, capsys):
        """Review with empty body not counted as new; only real review triggers exit."""
        baseline = {"pending": ["copilot"], "reviews": []}
        poll1 = {
            "pending": [],
            "reviews": [{"id": "r1", "body": "", "state": "COMMENTED", "author": "copilot"}],
        }
        poll2 = {
            "pending": [],
            "reviews": [
                {"id": "r1", "body": "", "state": "COMMENTED", "author": "copilot"},
                {"id": "r2", "body": "Here is my review", "state": "COMMENTED", "author": "copilot"},
            ],
        }
        mock_state.side_effect = [baseline, poll1, poll2]
        with patch.object(sys, "argv", ["wait_for_pr_review.py", "510", "--timeout-secs", "60"]):
            result = main()
        assert result == 0
        # poll1 should not have triggered exit (empty body filtered out)
        assert mock_state.call_count == 3

    @patch("wait_for_pr_review.get_pr_state")
    @patch("time.sleep")
    def test_filter_by_state(self, mock_sleep, mock_state, capsys):
        """--states APPROVED only; COMMENTED review not counted as qualifying."""
        baseline = {"pending": ["copilot"], "reviews": []}
        poll1 = {
            "pending": [],
            "reviews": [{"id": "r1", "body": "looks ok", "state": "COMMENTED", "author": "copilot"}],
        }
        poll2 = {
            "pending": [],
            "reviews": [
                {"id": "r1", "body": "looks ok", "state": "COMMENTED", "author": "copilot"},
                {"id": "r2", "body": "approved!", "state": "APPROVED", "author": "copilot"},
            ],
        }
        mock_state.side_effect = [baseline, poll1, poll2]
        with patch.object(
            sys,
            "argv",
            ["wait_for_pr_review.py", "510", "--timeout-secs", "60", "--states", "APPROVED"],
        ):
            result = main()
        assert result == 0
        # poll1 should not have triggered exit (COMMENTED filtered by --states APPROVED)
        assert mock_state.call_count == 3

    @patch("wait_for_pr_review.get_pr_state")
    def test_custom_repo(self, mock_state, capsys):
        """--repo passed through to get_pr_state."""
        mock_state.return_value = {
            "pending": [],
            "reviews": [{"id": "r1", "body": "lgtm", "state": "APPROVED", "author": "user"}],
        }
        with patch.object(sys, "argv", ["wait_for_pr_review.py", "42", "--repo", "other/repo"]):
            result = main()
        assert result == 0
        mock_state.assert_called_with(42, "other/repo")

    @pytest.mark.io
    def test_help_flag(self):
        """--help exits cleanly with usage info."""
        result = subprocess.run(
            [sys.executable, "scripts/wait_for_pr_review.py", "--help"],
            capture_output=True,
            text=True,
            cwd=os.path.join(os.path.dirname(__file__), ".."),
        )
        assert result.returncode == 0
        assert "pr" in result.stdout.lower()
