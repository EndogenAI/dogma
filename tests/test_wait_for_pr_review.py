"""Tests for wait_for_pr_review.py."""

import os
import subprocess
import sys
from unittest.mock import MagicMock, patch

import pytest

# Add scripts directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from wait_for_pr_review import get_review_count, main


class TestGetReviewCount:
    """Test get_review_count function."""

    @patch("subprocess.run")
    def test_no_reviews_yet(self, mock_run):
        """Test PR with no reviews returns 0."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"latestReviews": []}\n',
        )
        count = get_review_count(510, "owner/repo")
        assert count == 0

    @patch("subprocess.run")
    def test_one_review_present(self, mock_run):
        """Test PR with one review returns 1."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=(
                '{"latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "COMMENTED"}]}\n'
            ),
        )
        count = get_review_count(510, "owner/repo")
        assert count == 1

    @patch("subprocess.run")
    def test_multiple_reviews(self, mock_run):
        """Test PR with multiple reviews returns correct count."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"latestReviews": [{"state": "COMMENTED"}, {"state": "APPROVED"}]}\n',
        )
        count = get_review_count(510, "owner/repo")
        assert count == 2

    @patch("subprocess.run")
    def test_gh_cli_error(self, mock_run):
        """Test gh CLI error returns None."""
        mock_run.return_value = MagicMock(returncode=1, stderr="pull request not found")
        count = get_review_count(999, "owner/repo")
        assert count is None

    @patch("subprocess.run")
    def test_invalid_json(self, mock_run):
        """Test invalid JSON response returns None."""
        mock_run.return_value = MagicMock(returncode=0, stdout="not json\n")
        count = get_review_count(510, "owner/repo")
        assert count is None

    @patch("subprocess.run")
    def test_timeout(self, mock_run):
        """Test subprocess timeout returns None."""
        mock_run.side_effect = subprocess.TimeoutExpired("cmd", 30)
        count = get_review_count(510, "owner/repo")
        assert count is None

    @patch("subprocess.run")
    def test_missing_key(self, mock_run):
        """Test missing latestReviews key returns 0 (treats as empty list)."""
        mock_run.return_value = MagicMock(returncode=0, stdout='{"other": "data"}\n')
        count = get_review_count(510, "owner/repo")
        assert count == 0

    @patch("subprocess.run")
    def test_correct_args_passed(self, mock_run):
        """Test gh is called with correct arguments."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"latestReviews": []}\n',
        )
        get_review_count(42, "myorg/myrepo")
        call_args = mock_run.call_args[0][0]
        assert "gh" in call_args
        assert "pr" in call_args
        assert "view" in call_args
        assert "42" in call_args
        assert "--repo" in call_args
        assert "myorg/myrepo" in call_args
        assert "latestReviews" in " ".join(call_args)


class TestMain:
    """Test main polling logic."""

    @patch("wait_for_pr_review.get_review_count")
    def test_review_already_present(self, mock_count, capsys):
        """Test review already present on first poll — returns 0 immediately."""
        mock_count.return_value = 1

        with patch.object(sys, "argv", ["wait_for_pr_review.py", "510"]):
            result = main()

        assert result == 0
        captured = capsys.readouterr()
        assert "✓" in captured.out
        assert "510" in captured.out

    @patch("wait_for_pr_review.get_review_count")
    @patch("time.sleep")
    def test_review_lands_after_polling(self, mock_sleep, mock_count, capsys):
        """Test review arrives after a few polls."""
        mock_count.side_effect = [0, 0, 1]

        with patch.object(sys, "argv", ["wait_for_pr_review.py", "510"]):
            result = main()

        assert result == 0
        assert mock_sleep.call_count == 2

    @patch("wait_for_pr_review.get_review_count")
    @patch("time.sleep")
    def test_timeout_no_review(self, mock_sleep, mock_count, capsys):
        """Test timeout reached with no review."""
        mock_count.return_value = 0

        with patch.object(
            sys,
            "argv",
            ["wait_for_pr_review.py", "510", "--timeout-secs", "10", "--interval-secs", "5"],
        ):
            result = main()

        assert result == 1
        captured = capsys.readouterr()
        assert "Timeout reached" in captured.out

    @patch("wait_for_pr_review.get_review_count")
    def test_pr_not_found_consecutive_errors(self, mock_count, capsys):
        """Test 3 consecutive fetch errors triggers exit code 2."""
        mock_count.return_value = None

        with patch.object(
            sys,
            "argv",
            ["wait_for_pr_review.py", "999", "--timeout-secs", "60", "--interval-secs", "1"],
        ):
            with patch("time.sleep"):
                result = main()

        assert result == 2
        captured = capsys.readouterr()
        assert "consecutive fetch errors" in captured.out

    @patch("wait_for_pr_review.get_review_count")
    @patch("time.sleep")
    def test_error_then_recovery(self, mock_sleep, mock_count, capsys):
        """Test transient fetch error recovers and succeeds."""
        mock_count.side_effect = [None, None, 1]

        with patch.object(
            sys,
            "argv",
            ["wait_for_pr_review.py", "510", "--timeout-secs", "60"],
        ):
            result = main()

        assert result == 0

    @patch("wait_for_pr_review.get_review_count")
    def test_min_reviews_two(self, mock_count, capsys):
        """Test --min-reviews 2 waits until 2 reviews present."""
        mock_count.side_effect = [1, 2]

        with patch.object(
            sys,
            "argv",
            ["wait_for_pr_review.py", "510", "--min-reviews", "2"],
        ):
            with patch("time.sleep"):
                result = main()

        assert result == 0

    @patch("wait_for_pr_review.get_review_count")
    def test_custom_repo(self, mock_count, capsys):
        """Test custom --repo is passed through to get_review_count."""
        mock_count.return_value = 1

        with patch.object(
            sys,
            "argv",
            ["wait_for_pr_review.py", "42", "--repo", "other/repo"],
        ):
            result = main()

        assert result == 0
        mock_count.assert_called_with(42, "other/repo")

    @pytest.mark.io
    def test_help_flag(self):
        """Test --help exits cleanly with usage info."""
        import subprocess

        result = subprocess.run(
            [sys.executable, "scripts/wait_for_pr_review.py", "--help"],
            capture_output=True,
            text=True,
            cwd=os.path.join(os.path.dirname(__file__), ".."),
        )
        assert result.returncode == 0
        assert "pr-number" in result.stdout or "pr" in result.stdout
