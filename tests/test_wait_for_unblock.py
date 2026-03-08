"""Tests for scripts/wait_for_unblock.py

Uses direct import (sys.path.insert) for real line coverage, following the
pattern established in tests/test_seed_labels.py.

Covers:
- parse_repo_from_remote_url: HTTPS, SSH, non-GitHub URLs
- parse_labels / parse_issue_meta: JSON parsing
- trigger_filename / format_trigger_content: pure helpers
- fetch_labels: subprocess mock — success, gh failure
- fetch_issue_meta: subprocess mock — success, failure fallback
- write_trigger: filesystem write + content validation
- poll: immediate-unblock, blocked-then-unblocked, timeout, gh error
- main: --dry-run, missing repo, exit codes
"""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import wait_for_unblock as sut  # noqa: E402, I001 — after sys.path manipulation


# ---------------------------------------------------------------------------
# parse_repo_from_remote_url
# ---------------------------------------------------------------------------


def test_parse_repo_https():
    assert sut.parse_repo_from_remote_url("https://github.com/EndogenAI/Workflows.git") == "EndogenAI/Workflows"


def test_parse_repo_https_no_git_suffix():
    assert sut.parse_repo_from_remote_url("https://github.com/EndogenAI/Workflows") == "EndogenAI/Workflows"


def test_parse_repo_ssh():
    assert sut.parse_repo_from_remote_url("git@github.com:EndogenAI/Workflows.git") == "EndogenAI/Workflows"


def test_parse_repo_non_github_returns_none():
    assert sut.parse_repo_from_remote_url("https://gitlab.com/org/repo.git") is None


def test_parse_repo_empty_returns_none():
    assert sut.parse_repo_from_remote_url("") is None


# ---------------------------------------------------------------------------
# parse_labels
# ---------------------------------------------------------------------------


def test_parse_labels_with_blocked():
    payload = json.dumps({"labels": [{"name": "status:blocked"}, {"name": "type:research"}]})
    assert sut.parse_labels(payload) == ["status:blocked", "type:research"]


def test_parse_labels_empty():
    assert sut.parse_labels(json.dumps({"labels": []})) == []


def test_parse_labels_no_key():
    assert sut.parse_labels(json.dumps({})) == []


# ---------------------------------------------------------------------------
# parse_issue_meta
# ---------------------------------------------------------------------------


def test_parse_issue_meta():
    payload = json.dumps({"title": "Agent Skills Research", "url": "https://github.com/org/repo/issues/60"})
    assert sut.parse_issue_meta(payload) == {
        "title": "Agent Skills Research",
        "url": "https://github.com/org/repo/issues/60",
    }


# ---------------------------------------------------------------------------
# trigger_filename
# ---------------------------------------------------------------------------


def test_trigger_filename_slashes_replaced():
    assert sut.trigger_filename("EndogenAI/Workflows", 60) == "EndogenAI-Workflows-issue-60.unblocked"


# ---------------------------------------------------------------------------
# format_trigger_content
# ---------------------------------------------------------------------------


def test_format_trigger_content_keys():
    content = sut.format_trigger_content("EndogenAI/Workflows", 60, {"title": "My Issue", "url": "https://example.com"})
    assert "issue: 60" in content
    assert "repo: EndogenAI/Workflows" in content
    assert "title: My Issue" in content
    assert "url: https://example.com" in content
    assert "unblocked_at:" in content
    assert content.endswith("\n")


def test_format_trigger_content_missing_meta_keys():
    content = sut.format_trigger_content("org/repo", 1, {})
    assert "title: \n" in content or "title: " in content
    assert "url: \n" in content or "url: " in content


# ---------------------------------------------------------------------------
# fetch_labels (subprocess mocked)
# ---------------------------------------------------------------------------


def _mock_run_success(labels_names):
    mock = MagicMock()
    mock.returncode = 0
    mock.stdout = json.dumps({"labels": [{"name": n} for n in labels_names]})
    mock.stderr = ""
    return mock


def _mock_run_failure(stderr="gh: issue not found"):
    mock = MagicMock()
    mock.returncode = 1
    mock.stdout = ""
    mock.stderr = stderr
    return mock


@pytest.mark.io
def test_fetch_labels_blocked_true():
    with patch("subprocess.run", return_value=_mock_run_success(["status:blocked", "type:research"])):
        is_blocked, labels = sut.fetch_labels("org/repo", 60, "status:blocked")
    assert is_blocked is True
    assert "status:blocked" in labels


@pytest.mark.io
def test_fetch_labels_not_blocked():
    with patch("subprocess.run", return_value=_mock_run_success(["type:research", "priority:high"])):
        is_blocked, labels = sut.fetch_labels("org/repo", 60, "status:blocked")
    assert is_blocked is False


@pytest.mark.io
def test_fetch_labels_gh_failure_raises():
    with patch("subprocess.run", return_value=_mock_run_failure("no such issue")):
        with pytest.raises(RuntimeError, match="no such issue"):
            sut.fetch_labels("org/repo", 9999, "status:blocked")


# ---------------------------------------------------------------------------
# fetch_issue_meta (subprocess mocked)
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_fetch_issue_meta_success():
    mock = MagicMock()
    mock.returncode = 0
    mock.stdout = json.dumps({"title": "Research Issue", "url": "https://github.com/org/repo/issues/60"})
    with patch("subprocess.run", return_value=mock):
        meta = sut.fetch_issue_meta("org/repo", 60)
    assert meta["title"] == "Research Issue"


@pytest.mark.io
def test_fetch_issue_meta_failure_returns_fallback():
    mock = MagicMock()
    mock.returncode = 1
    mock.stderr = "not found"
    with patch("subprocess.run", return_value=mock):
        meta = sut.fetch_issue_meta("org/repo", 60)
    assert "issue #60" in meta["title"]
    assert meta["url"] == ""


# ---------------------------------------------------------------------------
# write_trigger (filesystem)
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_write_trigger_creates_file(tmp_path):
    meta = {"title": "Skills Research", "url": "https://github.com/org/repo/issues/60"}
    path = sut.write_trigger(tmp_path, "org/repo", 60, meta)
    assert path.exists()
    content = path.read_text()
    assert "issue: 60" in content
    assert "repo: org/repo" in content


@pytest.mark.io
def test_write_trigger_creates_parent_dir(tmp_path):
    trigger_dir = tmp_path / "nested" / "triggers"
    meta = {"title": "T", "url": ""}
    path = sut.write_trigger(trigger_dir, "org/repo", 1, meta)
    assert path.exists()


@pytest.mark.io
def test_write_trigger_filename_matches_helper(tmp_path):
    meta = {"title": "T", "url": ""}
    path = sut.write_trigger(tmp_path, "EndogenAI/Workflows", 60, meta)
    assert path.name == sut.trigger_filename("EndogenAI/Workflows", 60)


# ---------------------------------------------------------------------------
# poll (full loop logic)
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_poll_immediate_unblock(tmp_path):
    """Issue has no blocked label on first poll — exits 0 immediately."""
    with patch("wait_for_unblock.fetch_labels", return_value=(False, ["type:research"])):
        with patch("wait_for_unblock.fetch_issue_meta", return_value={"title": "T", "url": ""}):
            code = sut.poll("org/repo", 60, interval=1, timeout=0, trigger_dir=tmp_path, blocked_label="status:blocked")
    assert code == 0
    assert (tmp_path / sut.trigger_filename("org/repo", 60)).exists()


@pytest.mark.io
def test_poll_blocked_then_unblocked(tmp_path):
    """First poll is blocked, second is not — exits 0 after two polls."""
    responses = [(True, ["status:blocked"]), (False, ["type:research"])]
    call_count = 0

    def fake_fetch_labels(*args, **kwargs):
        nonlocal call_count
        resp = responses[call_count]
        call_count += 1
        return resp

    with patch("wait_for_unblock.fetch_labels", side_effect=fake_fetch_labels):
        with patch("wait_for_unblock.fetch_issue_meta", return_value={"title": "T", "url": ""}):
            with patch("time.sleep"):
                code = sut.poll(
                    "org/repo", 60, interval=1, timeout=0, trigger_dir=tmp_path, blocked_label="status:blocked"
                )
    assert code == 0
    assert call_count == 2


@pytest.mark.io
def test_poll_timeout(tmp_path):
    """All polls return blocked; timeout exceeded — exits 1."""
    with patch("wait_for_unblock.fetch_labels", return_value=(True, ["status:blocked"])):
        with patch("time.sleep"):
            with patch("time.monotonic", side_effect=[0, 0, 5, 5, 5]):
                code = sut.poll(
                    "org/repo", 60, interval=10, timeout=3, trigger_dir=tmp_path, blocked_label="status:blocked"
                )
    assert code == 1


@pytest.mark.io
def test_poll_gh_error_returns_2(tmp_path):
    """fetch_labels raises RuntimeError — exits 2."""
    with patch("wait_for_unblock.fetch_labels", side_effect=RuntimeError("gh: not found")):
        code = sut.poll("org/repo", 60, interval=1, timeout=0, trigger_dir=tmp_path, blocked_label="status:blocked")
    assert code == 2


# ---------------------------------------------------------------------------
# main CLI
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_main_dry_run_exits_0(capsys):
    with patch("wait_for_unblock.get_repo_from_git", return_value="EndogenAI/Workflows"):
        with pytest.raises(SystemExit) as exc_info:
            sut.main(["--issue", "60", "--dry-run"])
    assert exc_info.value.code == 0
    out = capsys.readouterr().out
    assert "DRY RUN" in out
    assert "#60" in out
    assert "EndogenAI/Workflows" in out


@pytest.mark.io
def test_main_missing_repo_exits_2(capsys):
    with patch("wait_for_unblock.get_repo_from_git", return_value=None):
        with pytest.raises(SystemExit) as exc_info:
            sut.main(["--issue", "60"])
    assert exc_info.value.code == 2


@pytest.mark.io
def test_main_repo_override_used(capsys, tmp_path):
    """--repo flag takes precedence over auto-detect."""
    with patch("wait_for_unblock.get_repo_from_git", return_value=None):
        with patch("wait_for_unblock.poll", return_value=0) as mock_poll:
            with pytest.raises(SystemExit) as exc_info:
                sut.main(["--issue", "60", "--repo", "other/repo", "--interval", "1"])
    mock_poll.assert_called_once()
    assert mock_poll.call_args.kwargs["repo"] == "other/repo"
    assert exc_info.value.code == 0


@pytest.mark.io
def test_main_dry_run_infinite_timeout_label(capsys):
    with patch("wait_for_unblock.get_repo_from_git", return_value="org/repo"):
        with pytest.raises(SystemExit):
            sut.main(["--issue", "1", "--dry-run"])
    assert "infinite" in capsys.readouterr().out


@pytest.mark.io
def test_main_dry_run_fixed_timeout_label(capsys):
    with patch("wait_for_unblock.get_repo_from_git", return_value="org/repo"):
        with pytest.raises(SystemExit):
            sut.main(["--issue", "1", "--dry-run", "--timeout", "3600"])
    assert "3600s" in capsys.readouterr().out
