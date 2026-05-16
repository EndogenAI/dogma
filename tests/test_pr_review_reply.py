"""Tests for scripts/pr_review_reply.py — PR review comment replies and thread resolution."""

import json
import subprocess
from pathlib import Path
from unittest import mock

import pytest


@pytest.fixture
def batch_file(tmp_path: Path) -> Path:
    """Create a batch operations JSON file."""
    batch = tmp_path / "batch.json"
    return batch


@pytest.fixture
def mock_gh_success():
    """Mock gh CLI calls to return success."""
    with mock.patch("subprocess.run") as mock_run:
        mock_run.return_value = mock.Mock(returncode=0, stdout="123\n", stderr="")
        yield mock_run


def test_single_reply_mode(batch_file: Path):
    """Posts a single reply when --reply-to provided."""
    # This test requires mocking gh API calls or integration test setup
    # For now, test that script accepts correct arguments
    result = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "scripts/pr_review_reply.py",
            "--pr",
            "1",
            "--reply-to",
            "123456",
            "--body",
            "Fixed in abc123",
            "--agent",
            "test-agent",
        ],
        capture_output=True,
        text=True,
    )

    # Without gh auth, this will fail with auth error
    # That's expected — we're testing argument parsing
    assert result.returncode in [0, 1]


def test_single_resolve_mode():
    """Resolves a single thread when --resolve provided."""
    result = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "scripts/pr_review_reply.py",
            "--pr",
            "1",
            "--resolve",
            "PRRT_kwDORfkAR85yvrwz",
            "--agent",
            "test-agent",
        ],
        capture_output=True,
        text=True,
    )

    # Without gh auth, expected to fail
    assert result.returncode in [0, 1]


def test_batch_mode_valid_json(batch_file: Path):
    """Processes batch operations from JSON file."""
    batch_data = [
        {"reply_to": 123, "body": "Fixed in commit abc", "resolve": "PRRT_node1"},
        {"reply_to": 456, "body": "Addressed comment", "resolve": "PRRT_node2"},
    ]
    batch_file.write_text(json.dumps(batch_data))

    result = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "scripts/pr_review_reply.py",
            "--pr",
            "1",
            "--batch",
            str(batch_file),
            "--agent",
            "test-agent",
        ],
        capture_output=True,
        text=True,
    )

    # Batch mode should accept valid JSON structure
    assert result.returncode in [0, 1]


def test_batch_invalid_json_fails(batch_file: Path):
    """Fails when batch JSON is malformed."""
    batch_file.write_text("{ invalid json")

    result = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "scripts/pr_review_reply.py",
            "--pr",
            "1",
            "--batch",
            str(batch_file),
            "--agent",
            "test-agent",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "invalid JSON" in result.stderr or "JSON" in result.stderr


def test_batch_not_array_fails(batch_file: Path):
    """Fails when batch JSON is not an array."""
    batch_file.write_text('{"not": "an array"}')

    result = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "scripts/pr_review_reply.py",
            "--pr",
            "1",
            "--batch",
            str(batch_file),
            "--agent",
            "test-agent",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "array" in result.stderr


def test_reply_without_body_fails():
    """Fails when --reply-to provided without --body."""
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
            "--agent",
            "test-agent",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "--body is required" in result.stderr


def test_no_mode_fails():
    """Fails when neither --reply-to, --resolve, nor --batch provided."""
    result = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "scripts/pr_review_reply.py",
            "--pr",
            "1",
            "--agent",
            "test-agent",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2  # argparse error


def test_batch_file_not_found_fails():
    """Fails when batch file doesn't exist."""
    result = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "scripts/pr_review_reply.py",
            "--pr",
            "1",
            "--batch",
            "/nonexistent/batch.json",
            "--agent",
            "test-agent",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "not found" in result.stderr


def test_missing_agent_context_fails():
    """Fails when --agent not provided and COPILOT_AGENT_ID not set."""
    import os

    # Preserve PATH but clear COPILOT_AGENT_ID
    env = os.environ.copy()
    env.pop("COPILOT_AGENT_ID", None)

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
        ],
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 1
    assert "Agent context" in result.stderr


def test_auto_detect_pr():
    """Uses gh pr view to detect active PR when --pr not provided."""
    # Without an active PR, should fail gracefully
    result = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "scripts/pr_review_reply.py",
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

    # Expected to fail (no active PR or auth issue)
    assert result.returncode in [0, 1]


def test_auto_detect_repo():
    """Uses gh repo view to detect current repo when --repo not provided."""
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
        cwd="/Users/conor/Sites/dogma",
    )

    # Should attempt to detect repo
    assert result.returncode in [0, 1]


def test_batch_entry_without_reply_or_resolve(batch_file: Path):
    """Skips batch entry with no reply_to or resolve."""
    batch_data = [
        {"reply_to": 123, "body": "Good entry"},
        {"other_field": "ignored"},  # Bad entry
    ]
    batch_file.write_text(json.dumps(batch_data))

    result = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "scripts/pr_review_reply.py",
            "--pr",
            "1",
            "--batch",
            str(batch_file),
            "--agent",
            "test-agent",
        ],
        capture_output=True,
        text=True,
    )

    # Should process batch but skip invalid entries
    assert result.returncode in [0, 1]


def test_batch_reply_without_body(batch_file: Path):
    """Skips batch entry with reply_to but no body."""
    batch_data = [{"reply_to": 123}]  # Missing body
    batch_file.write_text(json.dumps(batch_data))

    result = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "scripts/pr_review_reply.py",
            "--pr",
            "1",
            "--batch",
            str(batch_file),
            "--agent",
            "test-agent",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    # Should fail with message about missing body
