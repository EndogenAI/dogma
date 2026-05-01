"""Tests for check_merge_authorization.py.

Covers:
  - Happy path: all checks pass → exit 0, output contains MERGE AUTHORIZED
  - Blocked: CHANGES_REQUESTED review → exit 1, output contains MERGE BLOCKED
  - Blocked: pending reviewRequests → exit 1
  - Blocked: unresolved non-nit thread → exit 1
  - Nit exemption: unresolved nit thread with --allow-nit-unresolved (default) → exit 0
  - --no-allow-nit-unresolved: unresolved nit thread becomes blocking → exit 1
  - --dry-run: always exits 0, prints check table
  - API error (gh not found / bad PR number) → exit 2
  - get_default_repo: success and failure paths
  - PR not OPEN (merged/closed) → exit 1
"""

import json
import os
import subprocess
import sys
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# Import helpers
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from check_merge_authorization import (
    check_no_changes_requested,
    check_no_pending_requests,
    check_pr_open,
    check_threads_resolved,
    fetch_pr_data,
    format_authorized,
    format_blocked,
    format_dry_run_table,
    get_default_repo,
    main,
    run_checks,
)

# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

_OPEN_PR_DATA: dict = {
    "state": "OPEN",
    "reviews": [],
    "reviewRequests": [],
    "reviewThreads": [],
}


def _make_pr_stdout(**overrides) -> str:
    """Build gh JSON stdout string from _OPEN_PR_DATA with optional overrides."""
    data = dict(_OPEN_PR_DATA, **overrides)
    return json.dumps(data) + "\n"


def _mock_gh_success(**overrides) -> MagicMock:
    """Return a mock subprocess result that looks like a successful gh call."""
    return MagicMock(returncode=0, stdout=_make_pr_stdout(**overrides), stderr="")


# ---------------------------------------------------------------------------
# Unit tests — individual check functions
# ---------------------------------------------------------------------------


class TestCheckPrOpen:
    """Tests for check_pr_open."""

    def test_open_state_passes(self):
        """PR with state=OPEN returns True."""
        passed, reason, _ = check_pr_open({"state": "OPEN"})
        assert passed is True
        assert "OPEN" in reason

    def test_merged_state_fails(self):
        """PR with state=MERGED returns False."""
        passed, reason, next_step = check_pr_open({"state": "MERGED"})
        assert passed is False
        assert "MERGED" in reason
        assert next_step

    def test_closed_state_fails(self):
        """PR with state=CLOSED returns False."""
        passed, _, _ = check_pr_open({"state": "CLOSED"})
        assert passed is False


class TestCheckNoChangesRequested:
    """Tests for check_no_changes_requested."""

    def test_no_reviews_passes(self):
        """Empty reviews list passes."""
        passed, _, _ = check_no_changes_requested({"reviews": []})
        assert passed is True

    def test_approved_review_passes(self):
        """APPROVED review does not block."""
        data = {"reviews": [{"state": "APPROVED", "author": {"login": "alice"}}]}
        passed, _, _ = check_no_changes_requested(data)
        assert passed is True

    def test_changes_requested_blocks(self):
        """CHANGES_REQUESTED review blocks."""
        data = {"reviews": [{"state": "CHANGES_REQUESTED", "author": {"login": "bob"}}]}
        passed, reason, next_step = check_no_changes_requested(data)
        assert passed is False
        assert "bob" in reason
        assert next_step

    def test_multiple_changes_requested(self):
        """Multiple CHANGES_REQUESTED reviewers are all listed."""
        data = {
            "reviews": [
                {"state": "CHANGES_REQUESTED", "author": {"login": "alice"}},
                {"state": "CHANGES_REQUESTED", "author": {"login": "bob"}},
            ]
        }
        passed, reason, _ = check_no_changes_requested(data)
        assert passed is False
        assert "alice" in reason and "bob" in reason


class TestCheckNoPendingRequests:
    """Tests for check_no_pending_requests."""

    def test_no_pending_passes(self):
        """Empty reviewRequests list passes."""
        passed, _, _ = check_no_pending_requests({"reviewRequests": []})
        assert passed is True

    def test_pending_reviewer_blocks(self):
        """Pending reviewer blocks merge."""
        data = {"reviewRequests": [{"login": "copilot"}]}
        passed, reason, next_step = check_no_pending_requests(data)
        assert passed is False
        assert "copilot" in reason
        assert next_step

    def test_pending_team_reviewer_blocks(self):
        """Pending team reviewer (name field) blocks merge."""
        data = {"reviewRequests": [{"name": "my-team"}]}
        passed, reason, _ = check_no_pending_requests(data)
        assert passed is False
        assert "my-team" in reason


class TestCheckThreadsResolved:
    """Tests for check_threads_resolved."""

    def test_no_threads_passes(self):
        """No threads passes."""
        passed, _, _ = check_threads_resolved({"reviewThreads": []})
        assert passed is True

    def test_resolved_thread_passes(self):
        """A resolved thread does not block."""
        data = {
            "reviewThreads": [
                {
                    "isResolved": True,
                    "path": "file.py",
                    "line": 10,
                    "comments": [{"body": "Fix this"}],
                }
            ]
        }
        passed, _, _ = check_threads_resolved(data)
        assert passed is True

    def test_unresolved_non_nit_blocks(self):
        """Unresolved non-nit thread blocks."""
        data = {
            "reviewThreads": [
                {
                    "isResolved": False,
                    "path": "src/app.py",
                    "line": 42,
                    "comments": [{"body": "This needs a refactor"}],
                }
            ]
        }
        passed, reason, next_step = check_threads_resolved(data, allow_nit_unresolved=True)
        assert passed is False
        assert "src/app.py" in reason
        assert next_step

    def test_unresolved_nit_exempt_by_default(self):
        """Unresolved nit thread is exempt when allow_nit_unresolved=True."""
        data = {
            "reviewThreads": [
                {
                    "isResolved": False,
                    "path": "readme.md",
                    "line": 5,
                    "comments": [{"body": "nit: minor wording"}],
                }
            ]
        }
        passed, _, _ = check_threads_resolved(data, allow_nit_unresolved=True)
        assert passed is True

    def test_unresolved_nit_blocks_when_flag_false(self):
        """Unresolved nit thread blocks when allow_nit_unresolved=False."""
        data = {
            "reviewThreads": [
                {
                    "isResolved": False,
                    "path": "readme.md",
                    "line": 5,
                    "comments": [{"body": "Nit: minor wording"}],
                }
            ]
        }
        passed, _, _ = check_threads_resolved(data, allow_nit_unresolved=False)
        assert passed is False

    def test_nit_case_insensitive(self):
        """nit: prefix match is case-insensitive."""
        data = {
            "reviewThreads": [
                {
                    "isResolved": False,
                    "path": "x.py",
                    "line": 1,
                    "comments": [{"body": "NIT: capitalised nit"}],
                }
            ]
        }
        passed, _, _ = check_threads_resolved(data, allow_nit_unresolved=True)
        assert passed is True

    def test_multiple_unresolved_reported(self):
        """Multiple unresolved threads are all reported."""
        data = {
            "reviewThreads": [
                {
                    "isResolved": False,
                    "path": f"file{i}.py",
                    "line": i,
                    "comments": [{"body": "fix"}],
                }
                for i in range(5)
            ]
        }
        passed, reason, _ = check_threads_resolved(data, allow_nit_unresolved=True)
        assert passed is False
        # Truncation: only first 3 shown plus overflow count
        assert "+2 more" in reason

    def test_thread_with_no_comments(self):
        """Unresolved thread with empty comments list is not exempt as nit."""
        data = {
            "reviewThreads": [
                {
                    "isResolved": False,
                    "path": "x.py",
                    "line": 1,
                    "comments": [],
                }
            ]
        }
        passed, _, _ = check_threads_resolved(data, allow_nit_unresolved=True)
        assert passed is False


# ---------------------------------------------------------------------------
# Unit tests — fetch_pr_data
# ---------------------------------------------------------------------------


class TestFetchPrData:
    """Tests for fetch_pr_data."""

    @patch("subprocess.run")
    def test_happy_path(self, mock_run):
        """Valid gh response returns parsed dict."""
        mock_run.return_value = _mock_gh_success()
        data = fetch_pr_data(573, "EndogenAI/dogma")
        assert data is not None
        assert data["state"] == "OPEN"

    @patch("subprocess.run")
    def test_gh_nonzero_exit(self, mock_run):
        """Non-zero gh exit → None."""
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="not found")
        assert fetch_pr_data(999, "owner/repo") is None

    @patch("subprocess.run")
    def test_invalid_json(self, mock_run):
        """Invalid JSON response → None."""
        mock_run.return_value = MagicMock(returncode=0, stdout="not json\n", stderr="")
        assert fetch_pr_data(1, "owner/repo") is None

    @patch("subprocess.run")
    def test_missing_key(self, mock_run):
        """Response missing required key → None."""
        mock_run.return_value = MagicMock(returncode=0, stdout='{"state": "OPEN"}\n', stderr="")
        assert fetch_pr_data(1, "owner/repo") is None

    @patch("subprocess.run")
    def test_file_not_found(self, mock_run):
        """gh CLI not installed → None."""
        mock_run.side_effect = FileNotFoundError("gh: command not found")
        assert fetch_pr_data(1, "owner/repo") is None

    @patch("subprocess.run")
    def test_timeout(self, mock_run):
        """Subprocess timeout → None."""
        mock_run.side_effect = subprocess.TimeoutExpired("gh", 30)
        assert fetch_pr_data(1, "owner/repo") is None


# ---------------------------------------------------------------------------
# Unit tests — get_default_repo
# ---------------------------------------------------------------------------


class TestGetDefaultRepo:
    """Tests for get_default_repo."""

    @patch("subprocess.run")
    def test_success(self, mock_run):
        """gh repo view returns nameWithOwner correctly."""
        mock_run.return_value = MagicMock(returncode=0, stdout='{"nameWithOwner": "EndogenAI/dogma"}\n')
        assert get_default_repo() == "EndogenAI/dogma"

    @patch("subprocess.run")
    def test_gh_error(self, mock_run):
        """gh returns non-zero → None."""
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="error")
        assert get_default_repo() is None

    @patch("subprocess.run")
    def test_file_not_found(self, mock_run):
        """gh CLI not found → None."""
        mock_run.side_effect = FileNotFoundError()
        assert get_default_repo() is None


# ---------------------------------------------------------------------------
# Integration-style tests — main()
# ---------------------------------------------------------------------------


class TestMainHappyPath:
    """All checks pass → exit 0, stdout contains MERGE AUTHORIZED."""

    @patch("check_merge_authorization.fetch_pr_data")
    @patch("check_merge_authorization.get_default_repo")
    def test_all_checks_pass(self, mock_repo, mock_fetch, capsys):
        """Happy path: open PR, no reviews blocking, no pending, no unresolved threads."""
        mock_repo.return_value = "EndogenAI/dogma"
        mock_fetch.return_value = dict(_OPEN_PR_DATA)

        exit_code = main(["573"])
        assert exit_code == 0
        captured = capsys.readouterr()
        assert "MERGE AUTHORIZED" in captured.out


class TestMainBlocked:
    """Tests for blocked scenarios → exit 1."""

    @patch("check_merge_authorization.fetch_pr_data")
    @patch("check_merge_authorization.get_default_repo")
    def test_changes_requested_blocks(self, mock_repo, mock_fetch, capsys):
        """CHANGES_REQUESTED review → exit 1, output MERGE BLOCKED."""
        mock_repo.return_value = "EndogenAI/dogma"
        mock_fetch.return_value = {
            "state": "OPEN",
            "reviews": [{"state": "CHANGES_REQUESTED", "author": {"login": "alice"}}],
            "reviewRequests": [],
            "reviewThreads": [],
        }
        exit_code = main(["573"])
        assert exit_code == 1
        captured = capsys.readouterr()
        assert "MERGE BLOCKED" in captured.out

    @patch("check_merge_authorization.fetch_pr_data")
    @patch("check_merge_authorization.get_default_repo")
    def test_pending_review_request_blocks(self, mock_repo, mock_fetch, capsys):
        """Pending reviewRequest → exit 1."""
        mock_repo.return_value = "EndogenAI/dogma"
        mock_fetch.return_value = {
            "state": "OPEN",
            "reviews": [],
            "reviewRequests": [{"login": "copilot"}],
            "reviewThreads": [],
        }
        exit_code = main(["573"])
        assert exit_code == 1
        captured = capsys.readouterr()
        assert "MERGE BLOCKED" in captured.out

    @patch("check_merge_authorization.fetch_pr_data")
    @patch("check_merge_authorization.get_default_repo")
    def test_unresolved_non_nit_thread_blocks(self, mock_repo, mock_fetch, capsys):
        """Unresolved non-nit thread → exit 1."""
        mock_repo.return_value = "EndogenAI/dogma"
        mock_fetch.return_value = {
            "state": "OPEN",
            "reviews": [],
            "reviewRequests": [],
            "reviewThreads": [
                {
                    "isResolved": False,
                    "path": "src/app.py",
                    "line": 10,
                    "comments": [{"body": "This needs a refactor"}],
                }
            ],
        }
        exit_code = main(["573"])
        assert exit_code == 1
        captured = capsys.readouterr()
        assert "MERGE BLOCKED" in captured.out

    @patch("check_merge_authorization.fetch_pr_data")
    @patch("check_merge_authorization.get_default_repo")
    def test_pr_not_open_blocks(self, mock_repo, mock_fetch, capsys):
        """MERGED PR state → exit 1."""
        mock_repo.return_value = "EndogenAI/dogma"
        mock_fetch.return_value = {
            "state": "MERGED",
            "reviews": [],
            "reviewRequests": [],
            "reviewThreads": [],
        }
        exit_code = main(["573"])
        assert exit_code == 1
        captured = capsys.readouterr()
        assert "MERGE BLOCKED" in captured.out


class TestMainNitExemption:
    """Nit thread exemption behaviour."""

    @patch("check_merge_authorization.fetch_pr_data")
    @patch("check_merge_authorization.get_default_repo")
    def test_unresolved_nit_default_exempt(self, mock_repo, mock_fetch, capsys):
        """Default behaviour: unresolved nit thread does not block → exit 0."""
        mock_repo.return_value = "EndogenAI/dogma"
        mock_fetch.return_value = {
            "state": "OPEN",
            "reviews": [],
            "reviewRequests": [],
            "reviewThreads": [
                {
                    "isResolved": False,
                    "path": "readme.md",
                    "line": 3,
                    "comments": [{"body": "nit: minor wording tweak"}],
                }
            ],
        }
        exit_code = main(["573"])
        assert exit_code == 0
        assert "MERGE AUTHORIZED" in capsys.readouterr().out

    @patch("check_merge_authorization.fetch_pr_data")
    @patch("check_merge_authorization.get_default_repo")
    def test_unresolved_nit_blocking_when_flag_set(self, mock_repo, mock_fetch, capsys):
        """--no-allow-nit-unresolved makes nit threads blocking → exit 1."""
        mock_repo.return_value = "EndogenAI/dogma"
        mock_fetch.return_value = {
            "state": "OPEN",
            "reviews": [],
            "reviewRequests": [],
            "reviewThreads": [
                {
                    "isResolved": False,
                    "path": "readme.md",
                    "line": 3,
                    "comments": [{"body": "nit: minor wording tweak"}],
                }
            ],
        }
        exit_code = main(["573", "--no-allow-nit-unresolved"])
        assert exit_code == 1
        assert "MERGE BLOCKED" in capsys.readouterr().out


class TestMainDryRun:
    """--dry-run always exits 0 and prints a check table."""

    @patch("check_merge_authorization.fetch_pr_data")
    @patch("check_merge_authorization.get_default_repo")
    def test_dry_run_all_pass_exits_0(self, mock_repo, mock_fetch, capsys):
        """dry-run with passing PR exits 0."""
        mock_repo.return_value = "EndogenAI/dogma"
        mock_fetch.return_value = dict(_OPEN_PR_DATA)

        exit_code = main(["573", "--dry-run"])
        assert exit_code == 0
        out = capsys.readouterr().out
        assert "dry-run" in out.lower()
        assert "✅" in out

    @patch("check_merge_authorization.fetch_pr_data")
    @patch("check_merge_authorization.get_default_repo")
    def test_dry_run_blocked_still_exits_0(self, mock_repo, mock_fetch, capsys):
        """dry-run with a failing check still exits 0."""
        mock_repo.return_value = "EndogenAI/dogma"
        mock_fetch.return_value = {
            "state": "OPEN",
            "reviews": [{"state": "CHANGES_REQUESTED", "author": {"login": "alice"}}],
            "reviewRequests": [],
            "reviewThreads": [],
        }
        exit_code = main(["573", "--dry-run"])
        assert exit_code == 0
        out = capsys.readouterr().out
        assert "❌" in out


class TestMainApiErrors:
    """API errors → exit 2."""

    @patch("check_merge_authorization.fetch_pr_data")
    @patch("check_merge_authorization.get_default_repo")
    def test_fetch_returns_none_exits_2(self, mock_repo, mock_fetch, capsys):
        """fetch_pr_data returning None → exit 2."""
        mock_repo.return_value = "EndogenAI/dogma"
        mock_fetch.return_value = None

        exit_code = main(["999"])
        assert exit_code == 2

    @patch("check_merge_authorization.get_default_repo")
    def test_no_repo_resolved_exits_2(self, mock_repo, capsys):
        """get_default_repo returning None and no --repo → exit 2."""
        mock_repo.return_value = None

        exit_code = main(["573"])
        assert exit_code == 2

    @patch("check_merge_authorization.fetch_pr_data")
    def test_explicit_repo_skips_default_repo(self, mock_fetch, capsys):
        """--repo flag means get_default_repo is never called."""
        mock_fetch.return_value = dict(_OPEN_PR_DATA)

        exit_code = main(["573", "--repo", "owner/repo"])
        assert exit_code == 0
        assert "MERGE AUTHORIZED" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# Output formatter tests
# ---------------------------------------------------------------------------


class TestFormatters:
    """Tests for output formatter functions."""

    def test_format_authorized_contains_all_labels(self):
        """All passed check labels appear in MERGE AUTHORIZED output."""
        results = run_checks(_OPEN_PR_DATA)
        output = format_authorized(results)
        assert output.startswith("MERGE AUTHORIZED")
        assert "OPEN" in output

    def test_format_blocked_shows_first_failure(self):
        """MERGE BLOCKED line shows the first failing check."""
        data = {
            "state": "CLOSED",
            "reviews": [{"state": "CHANGES_REQUESTED", "author": {"login": "x"}}],
            "reviewRequests": [],
            "reviewThreads": [],
        }
        results = run_checks(data)
        output = format_blocked(results)
        assert output.startswith("MERGE BLOCKED")
        # First failure is the state check (a), not the reviews check (b)
        assert "OPEN" in output

    def test_format_dry_run_table_has_icons(self):
        """Dry-run table contains ✅ icons for passing checks."""
        results = run_checks(_OPEN_PR_DATA)
        table = format_dry_run_table(results)
        assert "✅" in table
        assert "dry-run" in table.lower()
