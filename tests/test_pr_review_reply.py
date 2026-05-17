"""Tests for scripts/pr_review_reply.py — PR review comment replies and thread resolution."""

import json
import subprocess
import sys
from pathlib import Path
from unittest import mock

import pytest

# Mock the capability gate decorator before importing pr_review_reply functions
with mock.patch("scripts.capability_gate.requires_capability", lambda cap: lambda f: f):
    from scripts.pr_review_reply import detect_repo, gh, main, post_reply, resolve_thread, run_batch, set_agent_context


# Set agent context for all tests using protected operations
set_agent_context("test-agent")


# ---------------------------------------------------------------------------
# Unit Tests — Business Logic
# ---------------------------------------------------------------------------


def test_gh_success():
    """gh() helper returns (returncode, stdout, stderr) tuple."""
    with mock.patch("subprocess.run") as mock_run:
        mock_run.return_value = mock.Mock(
            returncode=0,
            stdout="owner/repo\n",
            stderr="",
        )
        code, out, err = gh("repo", "view", "--json", "nameWithOwner")

        assert code == 0
        assert out == "owner/repo"
        assert err == ""
        mock_run.assert_called_once()


def test_gh_failure():
    """gh() helper captures errors correctly."""
    with mock.patch("subprocess.run") as mock_run:
        mock_run.return_value = mock.Mock(
            returncode=1,
            stdout="",
            stderr="auth failed\n",
        )
        code, out, err = gh("api", "repos/owner/repo")

        assert code == 1
        assert out == ""
        assert err == "auth failed"


def test_detect_repo_success():
    """detect_repo() returns owner/repo from gh CLI."""
    with mock.patch("scripts.pr_review_reply.gh") as mock_gh:
        mock_gh.return_value = (0, "EndogenAI/dogma", "")
        repo = detect_repo()

        assert repo == "EndogenAI/dogma"
        mock_gh.assert_called_once_with("repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner")


def test_detect_repo_failure():
    """detect_repo() exits on gh CLI error."""
    with mock.patch("scripts.pr_review_reply.gh") as mock_gh:
        mock_gh.return_value = (1, "", "not in a git repository")

        with pytest.raises(SystemExit) as exc_info:
            detect_repo()

        assert exc_info.value.code == 1


def test_post_reply_success():
    """post_reply() posts a reply to a comment and returns True on success."""
    with mock.patch("scripts.pr_review_reply.gh") as mock_gh:
        mock_gh.return_value = (0, "987654321", "")

        result = post_reply("owner/repo", 15, 123456, "Fixed in abc123")

        assert result is True
        mock_gh.assert_called_once()
        args = mock_gh.call_args[0]
        assert args == ("api", "repos/owner/repo/pulls/15/comments", "--input", "-", "--jq", ".id")


def test_post_reply_failure():
    """post_reply() returns False on gh CLI error."""
    with mock.patch("scripts.pr_review_reply.gh") as mock_gh:
        mock_gh.return_value = (1, "", "API rate limit exceeded")

        result = post_reply("owner/repo", 15, 123456, "Fixed in abc123")

        assert result is False


def test_resolve_thread_success():
    """resolve_thread() resolves a thread and returns True on success."""
    with mock.patch("scripts.pr_review_reply.gh") as mock_gh:
        mock_gh.return_value = (0, "true", "")

        result = resolve_thread("PRRT_kwDORfkAR85yvrwz")

        assert result is True
        mock_gh.assert_called_once()
        args = mock_gh.call_args[0]
        assert args[0] == "api"
        assert args[1] == "graphql"


def test_resolve_thread_failure():
    """resolve_thread() returns False on gh CLI error."""
    with mock.patch("scripts.pr_review_reply.gh") as mock_gh:
        mock_gh.return_value = (1, "", "invalid node ID")

        result = resolve_thread("INVALID_NODE")

        assert result is False


def test_run_batch_all_success():
    """run_batch() processes all operations successfully."""
    ops = [
        {"reply_to": 111, "body": "Fixed 1", "resolve": "NODE_1"},
        {"reply_to": 222, "body": "Fixed 2", "resolve": "NODE_2"},
    ]

    with (
        mock.patch("scripts.pr_review_reply.post_reply") as mock_reply,
        mock.patch("scripts.pr_review_reply.resolve_thread") as mock_resolve,
    ):
        mock_reply.return_value = True
        mock_resolve.return_value = True

        failures = run_batch(ops, "owner/repo", 15)

        assert failures == 0
        assert mock_reply.call_count == 2
        assert mock_resolve.call_count == 2


def test_run_batch_reply_only():
    """run_batch() handles reply-only operations (no resolve key)."""
    ops = [{"reply_to": 111, "body": "Fixed"}]

    with (
        mock.patch("scripts.pr_review_reply.post_reply") as mock_reply,
        mock.patch("scripts.pr_review_reply.resolve_thread") as mock_resolve,
    ):
        mock_reply.return_value = True

        failures = run_batch(ops, "owner/repo", 15)

        assert failures == 0
        assert mock_reply.call_count == 1
        assert mock_resolve.call_count == 0


def test_run_batch_resolve_only():
    """run_batch() handles resolve-only operations (no reply_to key)."""
    ops = [{"resolve": "NODE_1"}]

    with (
        mock.patch("scripts.pr_review_reply.post_reply") as mock_reply,
        mock.patch("scripts.pr_review_reply.resolve_thread") as mock_resolve,
    ):
        mock_resolve.return_value = True

        failures = run_batch(ops, "owner/repo", 15)

        assert failures == 0
        assert mock_reply.call_count == 0
        assert mock_resolve.call_count == 1


def test_run_batch_missing_body():
    """run_batch() skips reply_to entries without body."""
    ops = [{"reply_to": 111}]  # No body field

    with mock.patch("scripts.pr_review_reply.post_reply") as mock_reply:
        failures = run_batch(ops, "owner/repo", 15)

        assert failures == 1
        assert mock_reply.call_count == 0


def test_run_batch_empty_entry():
    """run_batch() skips entries with neither reply_to nor resolve."""
    ops = [{"body": "Orphaned body"}]  # No reply_to or resolve

    with (
        mock.patch("scripts.pr_review_reply.post_reply") as mock_reply,
        mock.patch("scripts.pr_review_reply.resolve_thread") as mock_resolve,
    ):
        failures = run_batch(ops, "owner/repo", 15)

        assert failures == 0  # Skipped, not a failure
        assert mock_reply.call_count == 0
        assert mock_resolve.call_count == 0


def test_run_batch_partial_failure():
    """run_batch() counts failures correctly when some operations fail."""
    ops = [
        {"reply_to": 111, "body": "Fixed 1"},
        {"reply_to": 222, "body": "Fixed 2"},
    ]

    with mock.patch("scripts.pr_review_reply.post_reply") as mock_reply:
        mock_reply.side_effect = [True, False]  # First succeeds, second fails

        failures = run_batch(ops, "owner/repo", 15)

        assert failures == 1


def test_main_reply_mode():
    """main() executes single reply mode successfully."""
    test_args = [
        "pr_review_reply.py",
        "--pr",
        "15",
        "--repo",
        "owner/repo",
        "--reply-to",
        "123",
        "--body",
        "Fixed",
        "--agent",
        "test-agent",
    ]

    with (
        mock.patch.object(sys, "argv", test_args),
        mock.patch("scripts.pr_review_reply.post_reply") as mock_reply,
        mock.patch("scripts.pr_review_reply.set_agent_context"),
    ):
        mock_reply.return_value = True

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0
        mock_reply.assert_called_once_with("owner/repo", 15, 123, "Fixed")


def test_main_resolve_mode():
    """main() executes single resolve mode successfully."""
    test_args = [
        "pr_review_reply.py",
        "--pr",
        "15",
        "--repo",
        "owner/repo",
        "--resolve",
        "NODE_123",
        "--agent",
        "test-agent",
    ]

    with (
        mock.patch.object(sys, "argv", test_args),
        mock.patch("scripts.pr_review_reply.resolve_thread") as mock_resolve,
        mock.patch("scripts.pr_review_reply.set_agent_context"),
    ):
        mock_resolve.return_value = True

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0
        mock_resolve.assert_called_once_with("NODE_123")


def test_main_batch_mode(tmp_path: Path):
    """main() executes batch mode successfully."""
    batch_file = tmp_path / "batch.json"
    batch_file.write_text(
        json.dumps(
            [
                {"reply_to": 111, "body": "Fix 1"},
                {"resolve": "NODE_222"},
            ]
        )
    )

    test_args = [
        "pr_review_reply.py",
        "--pr",
        "15",
        "--repo",
        "owner/repo",
        "--batch",
        str(batch_file),
        "--agent",
        "test-agent",
    ]

    with (
        mock.patch.object(sys, "argv", test_args),
        mock.patch("scripts.pr_review_reply.run_batch") as mock_batch,
        mock.patch("scripts.pr_review_reply.set_agent_context"),
    ):
        mock_batch.return_value = 0

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0
        mock_batch.assert_called_once()


def test_main_batch_invalid_json(tmp_path: Path):
    """main() exits with error on invalid batch JSON."""
    batch_file = tmp_path / "batch.json"
    batch_file.write_text("{ invalid json")

    test_args = [
        "pr_review_reply.py",
        "--pr",
        "15",
        "--batch",
        str(batch_file),
        "--agent",
        "test-agent",
    ]

    with mock.patch.object(sys, "argv", test_args), mock.patch("scripts.pr_review_reply.set_agent_context"):
        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1


def test_main_batch_not_array(tmp_path: Path):
    """main() exits with error when batch JSON is not an array."""
    batch_file = tmp_path / "batch.json"
    batch_file.write_text('{"not": "an array"}')

    test_args = [
        "pr_review_reply.py",
        "--pr",
        "15",
        "--batch",
        str(batch_file),
        "--agent",
        "test-agent",
    ]

    with mock.patch.object(sys, "argv", test_args), mock.patch("scripts.pr_review_reply.set_agent_context"):
        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1


def test_main_missing_agent_context():
    """main() exits with error when agent context not provided."""
    test_args = [
        "pr_review_reply.py",
        "--pr",
        "15",
        "--reply-to",
        "123",
        "--body",
        "Fixed",
    ]

    with mock.patch.object(sys, "argv", test_args), mock.patch.dict("os.environ", {}, clear=True):
        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1


def test_main_auto_detect_pr():
    """main() auto-detects PR number when --pr not provided."""
    test_args = [
        "pr_review_reply.py",
        "--repo",
        "owner/repo",
        "--reply-to",
        "123",
        "--body",
        "Fixed",
        "--agent",
        "test-agent",
    ]

    with (
        mock.patch.object(sys, "argv", test_args),
        mock.patch("scripts.pr_review_reply.gh") as mock_gh,
        mock.patch("scripts.pr_review_reply.post_reply") as mock_reply,
        mock.patch("scripts.pr_review_reply.set_agent_context"),
    ):
        mock_gh.return_value = (0, "42", "")
        mock_reply.return_value = True

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0
        mock_reply.assert_called_once_with("owner/repo", 42, 123, "Fixed")


def test_main_auto_detect_repo():
    """main() auto-detects repo when --repo not provided."""
    test_args = [
        "pr_review_reply.py",
        "--pr",
        "15",
        "--reply-to",
        "123",
        "--body",
        "Fixed",
        "--agent",
        "test-agent",
    ]

    with (
        mock.patch.object(sys, "argv", test_args),
        mock.patch("scripts.pr_review_reply.detect_repo") as mock_detect,
        mock.patch("scripts.pr_review_reply.post_reply") as mock_reply,
        mock.patch("scripts.pr_review_reply.set_agent_context"),
    ):
        mock_detect.return_value = "detected/repo"
        mock_reply.return_value = True

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0
        mock_reply.assert_called_once_with("detected/repo", 15, 123, "Fixed")


def test_main_reply_without_body():
    """main() exits with error when --reply-to provided without --body."""
    test_args = [
        "pr_review_reply.py",
        "--pr",
        "15",
        "--reply-to",
        "123",
        "--agent",
        "test-agent",
    ]

    with mock.patch.object(sys, "argv", test_args), mock.patch("scripts.pr_review_reply.set_agent_context"):
        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1


def test_main_batch_file_not_found():
    """main() exits with error when batch file doesn't exist."""
    test_args = [
        "pr_review_reply.py",
        "--pr",
        "15",
        "--batch",
        "/nonexistent/batch.json",
        "--agent",
        "test-agent",
    ]

    with mock.patch.object(sys, "argv", test_args), mock.patch("scripts.pr_review_reply.set_agent_context"):
        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# Integration Tests — CLI Smoke Tests
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_cli_help():
    """CLI displays help message."""
    result = subprocess.run(
        ["uv", "run", "python", "scripts/pr_review_reply.py", "--help"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Post replies to PR inline review comments" in result.stdout


@pytest.mark.integration
def test_cli_missing_mode_arg():
    """CLI exits with error when no mode argument provided."""
    result = subprocess.run(
        ["uv", "run", "python", "scripts/pr_review_reply.py", "--pr", "1"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2  # argparse error
    assert "required" in result.stderr or "one of the arguments" in result.stderr


@pytest.mark.integration
def test_cli_integration_smoke():
    """CLI integration smoke test with mocked environment."""
    result = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "scripts/pr_review_reply.py",
            "--pr",
            "1",
            "--reply-to",
            "123",
            "--body",
            "Test",
            "--agent",
            "test-agent",
        ],
        capture_output=True,
        text=True,
    )

    # Expected to fail (auth or no active PR), but should parse args correctly
    assert result.returncode in [0, 1]
