"""
tests/test_bulk_github_read.py

Unit tests for scripts/bulk_github_read.py.

Coverage targets
----------------
- --issues parsing: comma-separated, int conversion, invalid number
- --prs parsing: comma-separated, normalisation of 'assignees' → 'assignee'
- --query mode: gh issue list --search called with correct args
- --format table/json/csv output shapes
- --fields: only requested fields appear in output
- Exit code 1 on fetch error (gh non-zero exit)
- Exit code 0 on full success
- No real gh calls in any test (subprocess.run patched throughout)
- _simplify_record: nested labels/milestone/assignee are flattened

Markers
-------
@pytest.mark.io — tests that perform file I/O (none here — all in-memory)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import bulk_github_read as bgr  # noqa: E402

# ---------------------------------------------------------------------------
# Sample gh CLI responses
# ---------------------------------------------------------------------------

ISSUE_1 = {
    "number": 1,
    "title": "Fix the bug",
    "state": "open",
    "labels": [{"name": "type:bug", "color": "d73a4a", "description": ""}],
    "milestone": {"title": "v1.0", "number": 1},
    "assignee": {"login": "alice", "id": 42},
}

ISSUE_2 = {
    "number": 2,
    "title": "Add feature",
    "state": "closed",
    "labels": [],
    "milestone": None,
    "assignee": None,
}

PR_5 = {
    "number": 5,
    "title": "My PR",
    "state": "open",
    "labels": [{"name": "area:ci"}],
    "milestone": None,
    "assignees": [{"login": "bob", "id": 7}],
}

SEARCH_RESULTS = [ISSUE_1, ISSUE_2]


def _mock_run_for_issue(data: dict) -> MagicMock:
    m = MagicMock()
    m.returncode = 0
    m.stdout = json.dumps(data)
    m.stderr = ""
    return m


def _mock_run_for_search(data: list) -> MagicMock:
    m = MagicMock()
    m.returncode = 0
    m.stdout = json.dumps(data)
    m.stderr = ""
    return m


def _mock_run_failure() -> MagicMock:
    m = MagicMock()
    m.returncode = 1
    m.stdout = ""
    m.stderr = "gh: repository not found"
    return m


# ---------------------------------------------------------------------------
# _simplify_record
# ---------------------------------------------------------------------------


class TestSimplifyRecord:
    """_simplify_record flattens nested gh JSON structures."""

    def test_flattens_labels_list(self):
        rec = {"labels": [{"name": "type:bug"}, {"name": "priority:high"}]}
        simplified = bgr._simplify_record(rec)
        assert simplified["labels"] == "type:bug, priority:high"

    def test_empty_labels_returns_empty_string(self):
        rec = {"labels": []}
        simplified = bgr._simplify_record(rec)
        assert simplified["labels"] == ""

    def test_flattens_milestone_dict(self):
        rec = {"milestone": {"title": "v2.0", "number": 3}}
        simplified = bgr._simplify_record(rec)
        assert simplified["milestone"] == "v2.0"

    def test_none_milestone_returns_empty_string(self):
        rec = {"milestone": None}
        simplified = bgr._simplify_record(rec)
        assert simplified["milestone"] == ""

    def test_flattens_assignee_dict(self):
        rec = {"assignee": {"login": "charlie", "id": 99}}
        simplified = bgr._simplify_record(rec)
        assert simplified["assignee"] == "charlie"

    def test_none_assignee_returns_empty_string(self):
        rec = {"assignee": None}
        simplified = bgr._simplify_record(rec)
        assert simplified["assignee"] == ""

    def test_flattens_assignees_list(self):
        rec = {"assignees": [{"login": "dave"}, {"login": "eve"}]}
        simplified = bgr._simplify_record(rec)
        assert simplified["assignees"] == "dave, eve"


# ---------------------------------------------------------------------------
# _fetch_issue
# ---------------------------------------------------------------------------


class TestFetchIssue:
    """_fetch_issue calls gh correctly and returns filtered data."""

    def test_fetch_calls_gh_issue_view(self):
        with patch("subprocess.run", return_value=_mock_run_for_issue(ISSUE_1)) as mock_run:
            bgr._fetch_issue(1, bgr.DEFAULT_FIELDS)
        cmd = mock_run.call_args[0][0]
        assert cmd[0] == "gh"
        assert "issue" in cmd
        assert "view" in cmd
        assert "1" in cmd
        assert "--json" in cmd

    def test_fetch_returns_requested_fields(self):
        with patch("subprocess.run", return_value=_mock_run_for_issue(ISSUE_1)):
            result = bgr._fetch_issue(1, ["number", "title"])
        assert set(result.keys()) == {"number", "title"}
        assert result["number"] == 1
        assert result["title"] == "Fix the bug"

    def test_fetch_raises_on_gh_failure(self):
        with patch("subprocess.run", return_value=_mock_run_failure()):
            with pytest.raises(bgr.FetchError, match="Issue #1"):
                bgr._fetch_issue(1, bgr.DEFAULT_FIELDS)


# ---------------------------------------------------------------------------
# _fetch_pr
# ---------------------------------------------------------------------------


class TestFetchPr:
    """_fetch_pr normalises 'assignees' → 'assignee'."""

    def test_fetch_pr_normalises_assignees(self):
        with patch("subprocess.run", return_value=_mock_run_for_issue(PR_5)):
            result = bgr._fetch_pr(5, bgr.DEFAULT_FIELDS)
        # 'assignee' should be present, 'assignees' should not be in the output
        assert "assignee" in result
        # The value should be the first assignee dict
        assert result["assignee"] == {"login": "bob", "id": 7}

    def test_fetch_pr_raises_on_failure(self):
        with patch("subprocess.run", return_value=_mock_run_failure()):
            with pytest.raises(bgr.FetchError, match="PR #5"):
                bgr._fetch_pr(5, bgr.DEFAULT_FIELDS)


# ---------------------------------------------------------------------------
# _search_issues
# ---------------------------------------------------------------------------


class TestSearchIssues:
    """_search_issues passes the query to gh issue list --search."""

    def test_search_calls_gh_with_query(self):
        with patch("subprocess.run", return_value=_mock_run_for_search(SEARCH_RESULTS)) as mock_run:
            bgr._search_issues("is:open label:type:bug", bgr.DEFAULT_FIELDS)
        cmd = mock_run.call_args[0][0]
        assert "--search" in cmd
        assert "is:open label:type:bug" in cmd

    def test_search_returns_filtered_records(self):
        with patch("subprocess.run", return_value=_mock_run_for_search(SEARCH_RESULTS)):
            results = bgr._search_issues("q", ["number", "title"])
        assert len(results) == 2
        for rec in results:
            assert set(rec.keys()) == {"number", "title"}

    def test_search_raises_on_gh_failure(self):
        with patch("subprocess.run", return_value=_mock_run_failure()):
            with pytest.raises(bgr.FetchError, match="Search query"):
                bgr._search_issues("broken query", bgr.DEFAULT_FIELDS)


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------


class TestFormatJson:
    def test_json_output_is_valid_array(self):
        records = [bgr._filter_record(ISSUE_1, bgr.DEFAULT_FIELDS)]
        output = bgr._format_json(records)
        data = json.loads(output)
        assert isinstance(data, list)
        assert len(data) == 1

    def test_json_output_flattens_nested_fields(self):
        records = [bgr._filter_record(ISSUE_1, bgr.DEFAULT_FIELDS)]
        output = bgr._format_json(records)
        data = json.loads(output)
        assert data[0]["labels"] == "type:bug"
        assert data[0]["milestone"] == "v1.0"
        assert data[0]["assignee"] == "alice"


class TestFormatCsv:
    def test_csv_has_header_row(self):
        records = [bgr._filter_record(ISSUE_1, ["number", "title"])]
        output = bgr._format_csv(records, ["number", "title"])
        lines = output.strip().split("\n")
        assert lines[0] == "number,title"

    def test_csv_has_data_row(self):
        records = [bgr._filter_record(ISSUE_1, ["number", "title"])]
        output = bgr._format_csv(records, ["number", "title"])
        lines = output.strip().split("\n")
        assert len(lines) == 2
        assert "Fix the bug" in lines[1]

    def test_csv_empty_records(self):
        output = bgr._format_csv([], ["number", "title"])
        lines = output.strip().split("\n")
        assert lines[0] == "number,title"


class TestFormatTable:
    def test_table_has_header_and_divider(self):
        records = [bgr._filter_record(ISSUE_1, ["number", "title"])]
        output = bgr._format_table(records, ["number", "title"])
        lines = output.split("\n")
        assert "NUMBER" in lines[0]
        assert "TITLE" in lines[0]
        assert "---" in lines[1]

    def test_table_contains_data(self):
        records = [bgr._filter_record(ISSUE_1, ["number", "title"])]
        output = bgr._format_table(records, ["number", "title"])
        assert "Fix the bug" in output

    def test_table_empty_returns_no_results(self):
        output = bgr._format_table([], ["number", "title"])
        assert "(no results)" in output

    def test_table_truncates_long_values(self):
        long_title = "A" * 80
        record = {"number": 1, "title": long_title}
        output = bgr._format_table([record], ["number", "title"])
        assert "..." in output


# ---------------------------------------------------------------------------
# main() — argument validation
# ---------------------------------------------------------------------------


class TestMainArgValidation:
    """main() exits with an error if no data source is supplied."""

    def test_no_args_exits_nonzero(self):
        with pytest.raises(SystemExit) as exc_info:
            bgr.main([])
        assert exc_info.value.code != 0

    def test_invalid_issue_number_exits_1(self, capsys):
        with patch("subprocess.run"):
            rc = bgr.main(["--issues", "abc"])
        assert rc == 1
        err = capsys.readouterr().err
        assert "Invalid issue number" in err

    def test_invalid_pr_number_exits_1(self, capsys):
        with patch("subprocess.run"):
            rc = bgr.main(["--prs", "xyz"])
        assert rc == 1


# ---------------------------------------------------------------------------
# main() — --issues flag
# ---------------------------------------------------------------------------


class TestMainIssues:
    """--issues fetches each issue and outputs results."""

    def test_issues_exit_0_on_success(self, capsys):
        with patch("subprocess.run", return_value=_mock_run_for_issue(ISSUE_1)):
            rc = bgr.main(["--issues", "1", "--format", "json"])
        assert rc == 0

    def test_issues_json_output(self, capsys):
        with patch("subprocess.run", return_value=_mock_run_for_issue(ISSUE_1)):
            bgr.main(["--issues", "1", "--format", "json"])
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data[0]["number"] == 1

    def test_issues_exit_1_on_gh_error(self, capsys):
        with patch("subprocess.run", return_value=_mock_run_failure()):
            rc = bgr.main(["--issues", "1"])
        assert rc == 1

    def test_issues_table_format(self, capsys):
        with patch("subprocess.run", return_value=_mock_run_for_issue(ISSUE_1)):
            bgr.main(["--issues", "1", "--format", "table"])
        out = capsys.readouterr().out
        assert "NUMBER" in out
        assert "Fix the bug" in out

    def test_issues_csv_format(self, capsys):
        with patch("subprocess.run", return_value=_mock_run_for_issue(ISSUE_1)):
            bgr.main(["--issues", "1", "--format", "csv"])
        out = capsys.readouterr().out
        assert "number" in out.lower()
        assert "Fix the bug" in out

    def test_issues_custom_fields(self, capsys):
        with patch("subprocess.run", return_value=_mock_run_for_issue(ISSUE_1)):
            bgr.main(["--issues", "1", "--format", "json", "--fields", "number,title"])
        out = capsys.readouterr().out
        data = json.loads(out)
        assert set(data[0].keys()) == {"number", "title"}


# ---------------------------------------------------------------------------
# main() — --prs flag
# ---------------------------------------------------------------------------


class TestMainPrs:
    def test_prs_exit_0_on_success(self):
        with patch("subprocess.run", return_value=_mock_run_for_issue(PR_5)):
            rc = bgr.main(["--prs", "5", "--format", "json"])
        assert rc == 0

    def test_prs_exit_1_on_gh_error(self):
        with patch("subprocess.run", return_value=_mock_run_failure()):
            rc = bgr.main(["--prs", "5"])
        assert rc == 1


# ---------------------------------------------------------------------------
# main() — --query flag
# ---------------------------------------------------------------------------


class TestMainQuery:
    def test_query_exit_0_on_success(self):
        with patch("subprocess.run", return_value=_mock_run_for_search(SEARCH_RESULTS)):
            rc = bgr.main(["--query", "is:open", "--format", "json"])
        assert rc == 0

    def test_query_exit_1_on_gh_error(self):
        with patch("subprocess.run", return_value=_mock_run_failure()):
            rc = bgr.main(["--query", "is:open"])
        assert rc == 1

    def test_query_returns_multiple_results(self, capsys):
        with patch("subprocess.run", return_value=_mock_run_for_search(SEARCH_RESULTS)):
            bgr.main(["--query", "is:open", "--format", "json"])
        out = capsys.readouterr().out
        data = json.loads(out)
        assert len(data) == 2


# ---------------------------------------------------------------------------
# main() — mixed --issues and --prs
# ---------------------------------------------------------------------------


class TestMainMixed:
    def test_issues_and_prs_combined(self, capsys):
        def _side_effect(cmd, **kwargs):
            if "issue" in cmd and "view" in cmd:
                return _mock_run_for_issue(ISSUE_1)
            return _mock_run_for_issue(PR_5)

        with patch("subprocess.run", side_effect=_side_effect):
            rc = bgr.main(["--issues", "1", "--prs", "5", "--format", "json"])
        assert rc == 0
        out = capsys.readouterr().out
        data = json.loads(out)
        assert len(data) == 2
