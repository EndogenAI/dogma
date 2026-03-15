"""
tests/test_bulk_github_operations.py

Unit tests for scripts/bulk_github_operations.py.

Coverage targets
----------------
- Dry-run: produces result output without calling gh
- Operation list parsing: JSON file, YAML file, stdin
- rate-limit-delay: time.sleep is called between operations (mocked)
- Exit code 2 on invalid input (parse error, missing required param, unknown op)
- Exit code 1 on gh failure (mocked subprocess returning non-zero)
- Exit code 0 on full success
- All four op types build correct gh commands
- _validate_operations catches every error class
- _simplify: --dry-run includes 'cmd' in result; real run does not

Markers
-------
@pytest.mark.io — tests that write temp files
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import bulk_github_operations as bgo  # noqa: E402

# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

SAMPLE_OPS_JSON = json.dumps(
    [
        {"op": "issue-close", "target": 42, "params": {}},
        {"op": "issue-edit", "target": 10, "params": {"labels": ["type:bug"], "milestone": "v1.0"}},
    ]
)

SAMPLE_OPS = [
    {"op": "issue-close", "target": 42, "params": {}},
    {"op": "issue-edit", "target": 10, "params": {"labels": ["type:bug"]}},
]


def _make_success_run():
    """Return a mock subprocess.run that always succeeds."""
    mock = MagicMock()
    mock.returncode = 0
    mock.stdout = ""
    mock.stderr = ""
    return mock


def _make_failure_run():
    """Return a mock subprocess.run that always fails."""
    mock = MagicMock()
    mock.returncode = 1
    mock.stdout = ""
    mock.stderr = "gh: not found"
    return mock


# ---------------------------------------------------------------------------
# _validate_operations
# ---------------------------------------------------------------------------


class TestValidateOperations:
    """Unit tests for _validate_operations."""

    def test_valid_ops_returns_no_errors(self):
        errors = bgo._validate_operations(SAMPLE_OPS)
        assert errors == []

    def test_non_dict_op_flagged(self):
        errors = bgo._validate_operations(["not-a-dict"])
        assert len(errors) == 1
        assert "must be a dict" in errors[0]

    def test_missing_op_key_flagged(self):
        errors = bgo._validate_operations([{"target": 1, "params": {}}])
        assert any("missing required key 'op'" in e for e in errors)

    def test_unknown_op_flagged(self):
        errors = bgo._validate_operations([{"op": "nuke-repo", "target": 1, "params": {}}])
        assert any("unknown op" in e for e in errors)

    def test_missing_target_for_non_create_op_flagged(self):
        errors = bgo._validate_operations([{"op": "issue-close", "params": {}}])
        assert any("'target'" in e for e in errors)

    def test_missing_title_for_create_flagged(self):
        errors = bgo._validate_operations([{"op": "issue-create", "target": None, "params": {}}])
        assert any("title" in e for e in errors)

    def test_create_with_title_is_valid(self):
        errors = bgo._validate_operations([{"op": "issue-create", "target": None, "params": {"title": "Hello"}}])
        assert errors == []


# ---------------------------------------------------------------------------
# _build_gh_cmd
# ---------------------------------------------------------------------------


class TestBuildGhCmd:
    """Unit tests for _build_gh_cmd."""

    def test_issue_create_basic(self):
        cmd = bgo._build_gh_cmd(
            {
                "op": "issue-create",
                "target": None,
                "params": {"title": "Test issue"},
            }
        )
        assert cmd == ["gh", "issue", "create", "--title", "Test issue"]

    def test_issue_create_full(self):
        cmd = bgo._build_gh_cmd(
            {
                "op": "issue-create",
                "target": None,
                "params": {
                    "title": "Bug",
                    "body": "Oops",
                    "labels": ["type:bug", "priority:high"],
                    "milestone": "v1",
                    "assignee": "alice",
                },
            }
        )
        assert "--body" in cmd
        assert "--label" in cmd
        assert "--milestone" in cmd
        assert "--assignee" in cmd
        assert cmd.count("--label") == 2

    def test_issue_edit_with_add_labels_and_milestone(self):
        cmd = bgo._build_gh_cmd(
            {
                "op": "issue-edit",
                "target": 7,
                "params": {"add-labels": ["type:bug"], "milestone": "sprint-1"},
            }
        )
        assert cmd[:4] == ["gh", "issue", "edit", "7"]
        assert "--add-label" in cmd
        assert "--milestone" in cmd

    def test_issue_edit_labels_alias(self):
        """'labels' key is an alias for 'add-labels' in issue-edit."""
        cmd = bgo._build_gh_cmd(
            {
                "op": "issue-edit",
                "target": 7,
                "params": {"labels": ["type:bug"]},
            }
        )
        assert "--add-label" in cmd

    def test_issue_edit_remove_labels(self):
        cmd = bgo._build_gh_cmd(
            {
                "op": "issue-edit",
                "target": 7,
                "params": {"remove-labels": ["stale"]},
            }
        )
        assert "--remove-label" in cmd

    def test_issue_close_cmd(self):
        cmd = bgo._build_gh_cmd({"op": "issue-close", "target": 99, "params": {}})
        assert cmd == ["gh", "issue", "close", "99"]

    def test_pr_edit_cmd(self):
        cmd = bgo._build_gh_cmd(
            {
                "op": "pr-edit",
                "target": 55,
                "params": {"labels": ["area:ci"], "assignee": "bob"},
            }
        )
        assert cmd[:4] == ["gh", "pr", "edit", "55"]
        assert "--add-label" in cmd
        assert "--assignee" in cmd


# ---------------------------------------------------------------------------
# _run_operation — dry-run
# ---------------------------------------------------------------------------


class TestRunOperationDryRun:
    """_run_operation dry-run mode should not call subprocess.run."""

    def test_dry_run_returns_dry_run_status(self):
        op_spec = {"op": "issue-close", "target": 1, "params": {}}
        with patch("subprocess.run") as mock_run:
            result = bgo._run_operation(op_spec, dry_run=True)
        mock_run.assert_not_called()
        assert result["status"] == "dry-run"
        assert result["error"] is None
        assert "cmd" in result

    def test_dry_run_cmd_contains_gh(self):
        op_spec = {"op": "issue-close", "target": 5, "params": {}}
        with patch("subprocess.run"):
            result = bgo._run_operation(op_spec, dry_run=True)
        assert result["cmd"][0] == "gh"


# ---------------------------------------------------------------------------
# _run_operation — real execution
# ---------------------------------------------------------------------------


class TestRunOperationReal:
    """_run_operation real execution path."""

    def test_success_returns_ok_status(self):
        op_spec = {"op": "issue-close", "target": 1, "params": {}}
        with patch("subprocess.run", return_value=_make_success_run()):
            result = bgo._run_operation(op_spec, dry_run=False)
        assert result["status"] == "ok"
        assert result["error"] is None

    def test_gh_failure_returns_failed_status(self):
        op_spec = {"op": "issue-close", "target": 1, "params": {}}
        with patch("subprocess.run", return_value=_make_failure_run()):
            result = bgo._run_operation(op_spec, dry_run=False)
        assert result["status"] == "failed"
        assert result["error"] is not None

    def test_subprocess_called_with_list_not_string(self):
        """Verifies subprocess.run is always called with a list, never shell=True."""
        op_spec = {"op": "issue-close", "target": 2, "params": {}}
        with patch("subprocess.run", return_value=_make_success_run()) as mock_run:
            bgo._run_operation(op_spec, dry_run=False)
        called_args = mock_run.call_args
        cmd_arg = called_args[0][0]
        assert isinstance(cmd_arg, list), "subprocess.run must be called with a list of args"
        # confirm no shell=True
        kwargs = called_args[1]
        assert not kwargs.get("shell", False)


# ---------------------------------------------------------------------------
# main() — dry-run via argv
# ---------------------------------------------------------------------------


class TestMainDryRun:
    """main() dry-run: no gh calls, exit 0, JSON output on stdout."""

    @pytest.mark.io
    def test_dry_run_exit_0(self, tmp_path, capsys):
        ops_file = tmp_path / "ops.json"
        ops_file.write_text(json.dumps([{"op": "issue-close", "target": 1, "params": {}}]))
        with patch("subprocess.run") as mock_run:
            rc = bgo.main(["--input", str(ops_file), "--dry-run"])
        mock_run.assert_not_called()
        assert rc == 0

    @pytest.mark.io
    def test_dry_run_stdout_is_json(self, tmp_path, capsys):
        ops_file = tmp_path / "ops.json"
        ops_file.write_text(json.dumps([{"op": "issue-close", "target": 1, "params": {}}]))
        with patch("subprocess.run"):
            bgo.main(["--input", str(ops_file), "--dry-run"])
        out = capsys.readouterr().out
        data = json.loads(out)
        assert isinstance(data, list)
        assert data[0]["status"] == "dry-run"


# ---------------------------------------------------------------------------
# main() — exit codes
# ---------------------------------------------------------------------------


class TestMainExitCodes:
    """Verify all documented exit codes are correct."""

    @pytest.mark.io
    def test_exit_2_on_invalid_json_input(self, tmp_path):
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("{not: valid json")
        rc = bgo.main(["--input", str(bad_file)])
        assert rc == 2

    @pytest.mark.io
    def test_exit_2_on_missing_file(self, tmp_path):
        rc = bgo.main(["--input", str(tmp_path / "nonexistent.json")])
        assert rc == 2

    @pytest.mark.io
    def test_exit_2_on_unknown_op(self, tmp_path):
        ops_file = tmp_path / "ops.json"
        ops_file.write_text(json.dumps([{"op": "delete-repo", "target": 1, "params": {}}]))
        rc = bgo.main(["--input", str(ops_file)])
        assert rc == 2

    @pytest.mark.io
    def test_exit_2_on_non_list_input(self, tmp_path):
        ops_file = tmp_path / "ops.json"
        ops_file.write_text(json.dumps({"op": "issue-close"}))
        rc = bgo.main(["--input", str(ops_file)])
        assert rc == 2

    @pytest.mark.io
    def test_exit_1_on_gh_failure(self, tmp_path):
        ops_file = tmp_path / "ops.json"
        ops_file.write_text(json.dumps([{"op": "issue-close", "target": 1, "params": {}}]))
        with patch("subprocess.run", return_value=_make_failure_run()):
            rc = bgo.main(["--input", str(ops_file)])
        assert rc == 1

    @pytest.mark.io
    def test_exit_0_on_full_success(self, tmp_path):
        ops_file = tmp_path / "ops.json"
        ops_file.write_text(
            json.dumps(
                [
                    {"op": "issue-close", "target": 1, "params": {}},
                    {"op": "issue-close", "target": 2, "params": {}},
                ]
            )
        )
        with patch("subprocess.run", return_value=_make_success_run()):
            with patch("time.sleep"):
                rc = bgo.main(["--input", str(ops_file)])
        assert rc == 0


# ---------------------------------------------------------------------------
# rate-limit-delay
# ---------------------------------------------------------------------------


class TestRateLimitDelay:
    """time.sleep is called between operations (but not after the last one)."""

    @pytest.mark.io
    def test_sleep_called_between_ops(self, tmp_path):
        ops_file = tmp_path / "ops.json"
        ops_file.write_text(
            json.dumps(
                [
                    {"op": "issue-close", "target": 1, "params": {}},
                    {"op": "issue-close", "target": 2, "params": {}},
                    {"op": "issue-close", "target": 3, "params": {}},
                ]
            )
        )
        with patch("subprocess.run", return_value=_make_success_run()):
            with patch("time.sleep") as mock_sleep:
                rc = bgo.main(["--input", str(ops_file), "--rate-limit-delay", "0.3"])
        assert rc == 0
        # 3 ops → sleep called exactly twice (between ops, not after last)
        assert mock_sleep.call_count == 2
        mock_sleep.assert_called_with(0.3)

    @pytest.mark.io
    def test_sleep_not_called_in_dry_run(self, tmp_path):
        ops_file = tmp_path / "ops.json"
        ops_file.write_text(
            json.dumps(
                [
                    {"op": "issue-close", "target": 1, "params": {}},
                    {"op": "issue-close", "target": 2, "params": {}},
                ]
            )
        )
        with patch("subprocess.run"):
            with patch("time.sleep") as mock_sleep:
                bgo.main(["--input", str(ops_file), "--dry-run"])
        mock_sleep.assert_not_called()


# ---------------------------------------------------------------------------
# YAML input
# ---------------------------------------------------------------------------


class TestYamlInput:
    """Verify YAML spec files are parsed correctly."""

    @pytest.mark.io
    def test_yaml_input_parsed(self, tmp_path):
        yaml_content = "- op: issue-close\n  target: 7\n  params: {}\n"
        ops_file = tmp_path / "ops.yaml"
        ops_file.write_text(yaml_content)
        with patch("subprocess.run", return_value=_make_success_run()):
            rc = bgo.main(["--input", str(ops_file)])
        assert rc == 0


# ---------------------------------------------------------------------------
# stdin input
# ---------------------------------------------------------------------------


class TestStdinInput:
    """JSON operations can be piped to stdin."""

    def test_stdin_json_parsed(self, monkeypatch, capsys):
        stdin_data = json.dumps([{"op": "issue-close", "target": 3, "params": {}}])
        monkeypatch.setattr("sys.stdin", __import__("io").StringIO(stdin_data))
        with patch("subprocess.run", return_value=_make_success_run()):
            rc = bgo.main([])
        assert rc == 0
