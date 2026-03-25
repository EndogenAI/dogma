"""
test_enrich_research_issues.py — Tests for scripts/enrich_research_issues.py.

Scope: unit tests covering bare-bones detection, dry-run output, apply mode comment
posting, GitHub API error handling, and the empty-result path. All subprocess.run calls
are mocked — no real gh CLI calls, no network access, no file system writes outside
tmp_path provided by pytest fixtures.
"""

import json
import subprocess
from unittest.mock import MagicMock, patch

import pytest

import scripts.enrich_research_issues as script

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_issue(number: int, title: str, body: str) -> dict:
    return {"number": number, "title": title, "body": body, "labels": []}


LONG_BODY = "x" * 301
SHORT_BODY = "Short body."
BODY_WITH_AC = "Some intro.\n\n## Acceptance Criteria\n- [ ] item"
BARE_BONES_BODY = "A bare-bones research note."


# ---------------------------------------------------------------------------
# 1. filter_bare_bones
# ---------------------------------------------------------------------------


def test_filter_bare_bones_issues():
    issues = [
        _make_issue(1, "Has AC", BODY_WITH_AC),
        _make_issue(2, "Long body", LONG_BODY),
        _make_issue(3, "Bare bones", BARE_BONES_BODY),
        _make_issue(4, "Short no AC", SHORT_BODY),
        _make_issue(5, "Exactly 300 chars", "y" * 300),
    ]
    result = script.filter_bare_bones(issues)
    numbers = [i["number"] for i in result]
    assert 1 not in numbers, "Issue with ## Acceptance Criteria should be excluded"
    assert 2 not in numbers, "Issue with body > 300 chars should be excluded"
    assert 3 in numbers
    assert 4 in numbers
    assert 5 in numbers  # boundary: exactly 300 chars is bare-bones


# ---------------------------------------------------------------------------
# 2. dry_run_prints_table
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_dry_run_prints_table(capsys):
    issues_json = json.dumps(
        [
            _make_issue(10, "Research topic A", BARE_BONES_BODY),
            _make_issue(11, "Research topic B with long body", LONG_BODY),
        ]
    )

    mock_result = MagicMock()
    mock_result.stdout = issues_json

    with patch("subprocess.run", return_value=mock_result) as mock_run:
        exit_code = script.main([])

    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Research topic A" in captured.out
    # Long-body issue should NOT appear
    assert "#11" not in captured.out

    # gh issue comment must NOT be called
    for c in mock_run.call_args_list:
        args = c[0][0] if c[0] else c[1].get("args", [])
        assert "comment" not in args, "dry-run must not call gh issue comment"


# ---------------------------------------------------------------------------
# 3. apply_posts_comment
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_apply_posts_comment(tmp_path):
    issues_json = json.dumps(
        [
            _make_issue(20, "Bare topic", BARE_BONES_BODY),
            _make_issue(21, "Another bare", "tiny"),
        ]
    )

    fetch_result = MagicMock()
    fetch_result.stdout = issues_json

    comment_result = MagicMock(returncode=0)

    call_results = [fetch_result, comment_result, comment_result]

    with patch("subprocess.run", side_effect=call_results) as mock_run:
        exit_code = script.main(["--apply"])

    assert exit_code == 0

    # Verify gh issue comment was called twice (once per bare-bones issue)
    comment_calls = [c for c in mock_run.call_args_list if c[0] and "comment" in c[0][0]]
    assert len(comment_calls) == 2

    # Each comment call must use --body-file (not --body)
    for c in comment_calls:
        cmd = c[0][0]
        assert "--body-file" in cmd, "comment must use --body-file"
        assert "--body" not in [a for a in cmd if a == "--body"], "must not use inline --body"


# ---------------------------------------------------------------------------
# 4. gh_api_error_exits_1
# ---------------------------------------------------------------------------


def test_gh_api_error_exits_1():
    with patch(
        "subprocess.run",
        side_effect=subprocess.CalledProcessError(1, "gh", stderr="auth error"),
    ):
        exit_code = script.main([])
    assert exit_code == 1


# ---------------------------------------------------------------------------
# 5. no_bare_bones_issues_exits_0
# ---------------------------------------------------------------------------


def test_no_bare_bones_issues_exits_0(capsys):
    issues_json = json.dumps(
        [
            _make_issue(30, "Full issue", BODY_WITH_AC),
            _make_issue(31, "Long body issue", LONG_BODY),
        ]
    )

    mock_result = MagicMock()
    mock_result.stdout = issues_json

    with patch("subprocess.run", return_value=mock_result):
        exit_code = script.main([])

    assert exit_code == 0
    captured = capsys.readouterr()
    assert "No bare-bones" in captured.out
