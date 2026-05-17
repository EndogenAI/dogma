#!/usr/bin/env python3
"""Tests for scripts/generate_coverage_badge.py

Tests cover all code paths:
- Success: coverage.xml exists → badge generated and staged
- Pytest failure → graceful exit 0
- Missing coverage.xml → graceful exit 0
- Badge generation failure → graceful exit 0
- Git staging failure → graceful exit 0
"""

import subprocess
from unittest.mock import patch

# Import the module to test
import scripts.generate_coverage_badge as generate_coverage_badge


class TestRunCommand:
    """Tests for run_command helper."""

    def test_run_command_success(self):
        """Test run_command with successful execution."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=["echo", "test"], returncode=0, stdout="test\n", stderr=""
            )

            result = generate_coverage_badge.run_command(["echo", "test"])

            assert result.returncode == 0
            assert result.stdout == "test\n"
            mock_run.assert_called_once()

    def test_run_command_failure_no_check(self):
        """Test run_command with failure when check=False."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(args=["false"], returncode=1, stdout="", stderr="error")

            result = generate_coverage_badge.run_command(["false"], check=False)

            assert result.returncode == 1
            assert result.stderr == "error"

    def test_run_command_captures_output(self):
        """Test run_command captures stdout and stderr."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=["cmd"], returncode=0, stdout="output", stderr="errors"
            )

            result = generate_coverage_badge.run_command(["cmd"])

            assert result.stdout == "output"
            assert result.stderr == "errors"
            # Verify capture_output=True, text=True passed
            mock_run.assert_called_once()
            call_kwargs = mock_run.call_args[1]
            assert call_kwargs["capture_output"] is True
            assert call_kwargs["text"] is True


class TestMain:
    """Tests for main() function."""

    @patch("scripts.generate_coverage_badge.run_command")
    def test_success_full_flow(self, mock_run_cmd, tmp_path, capsys):
        """Test full success: pytest → coverage.xml → badge → git add."""
        # Create repo structure
        docs = tmp_path / "docs"
        docs.mkdir()
        coverage_xml = tmp_path / "coverage.xml"
        coverage_xml.write_text("<coverage></coverage>")
        badge_path = docs / "coverage_badge.svg"
        badge_path.write_text("<svg></svg>")

        # Mock __file__ to point to our tmp_path
        with patch(
            "scripts.generate_coverage_badge.__file__", str(tmp_path / "scripts" / "generate_coverage_badge.py")
        ):
            # Mock all subprocess calls succeed
            mock_run_cmd.return_value = subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")

            exit_code = generate_coverage_badge.main()

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "Coverage badge generated and staged" in captured.out
        # Verify pytest, coverage-badge, and git add were called
        assert mock_run_cmd.call_count == 3

    @patch("scripts.generate_coverage_badge.run_command")
    def test_pytest_fails_graceful_exit(self, mock_run_cmd, tmp_path, capsys):
        """Test pytest failure → graceful exit 0."""
        # Mock __file__ to point to our tmp_path
        with patch(
            "scripts.generate_coverage_badge.__file__", str(tmp_path / "scripts" / "generate_coverage_badge.py")
        ):
            # Mock pytest failure
            mock_run_cmd.return_value = subprocess.CompletedProcess(
                args=["pytest"], returncode=1, stdout="", stderr="test failures"
            )

            exit_code = generate_coverage_badge.main()

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "Tests failed, skipping badge generation" in captured.err
        # Only pytest called, no badge generation
        assert mock_run_cmd.call_count == 1

    @patch("scripts.generate_coverage_badge.run_command")
    def test_missing_coverage_xml_graceful_exit(self, mock_run_cmd, tmp_path, capsys):
        """Test missing coverage.xml → graceful exit 0."""
        # Create repo structure WITHOUT coverage.xml
        docs = tmp_path / "docs"
        docs.mkdir()

        # Mock __file__ to point to our tmp_path
        with patch(
            "scripts.generate_coverage_badge.__file__", str(tmp_path / "scripts" / "generate_coverage_badge.py")
        ):
            # Mock pytest success
            mock_run_cmd.return_value = subprocess.CompletedProcess(args=["pytest"], returncode=0, stdout="", stderr="")

            exit_code = generate_coverage_badge.main()

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "coverage.xml not found" in captured.err
        # Only pytest called
        assert mock_run_cmd.call_count == 1

    @patch("scripts.generate_coverage_badge.run_command")
    def test_badge_generation_fails_graceful_exit(self, mock_run_cmd, tmp_path, capsys):
        """Test coverage-badge failure → graceful exit 0."""
        # Create repo structure with coverage.xml
        docs = tmp_path / "docs"
        docs.mkdir()
        coverage_xml = tmp_path / "coverage.xml"
        coverage_xml.write_text("<coverage></coverage>")

        # Mock __file__ to point to our tmp_path
        with patch(
            "scripts.generate_coverage_badge.__file__", str(tmp_path / "scripts" / "generate_coverage_badge.py")
        ):
            # Mock pytest success, badge generation failure
            def run_side_effect(cmd, **kwargs):
                if "pytest" in cmd:
                    return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")
                elif "coverage-badge" in cmd:
                    return subprocess.CompletedProcess(args=cmd, returncode=1, stdout="", stderr="badge error")
                return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

            mock_run_cmd.side_effect = run_side_effect

            exit_code = generate_coverage_badge.main()

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "Badge generation failed" in captured.err
        # pytest + coverage-badge called (no git add)
        assert mock_run_cmd.call_count == 2

    @patch("scripts.generate_coverage_badge.run_command")
    def test_git_add_fails_graceful_exit(self, mock_run_cmd, tmp_path, capsys):
        """Test git add failure → graceful exit 0."""
        # Create repo structure with coverage.xml and badge
        docs = tmp_path / "docs"
        docs.mkdir()
        coverage_xml = tmp_path / "coverage.xml"
        coverage_xml.write_text("<coverage></coverage>")
        badge_path = docs / "coverage_badge.svg"
        badge_path.write_text("<svg></svg>")

        # Mock __file__ to point to our tmp_path
        with patch(
            "scripts.generate_coverage_badge.__file__", str(tmp_path / "scripts" / "generate_coverage_badge.py")
        ):
            # Mock pytest and badge success, git failure
            def run_side_effect(cmd, **kwargs):
                if "pytest" in cmd:
                    return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")
                elif "coverage-badge" in cmd:
                    return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")
                elif "git" in cmd:
                    return subprocess.CompletedProcess(args=cmd, returncode=1, stdout="", stderr="git error")
                return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

            mock_run_cmd.side_effect = run_side_effect

            exit_code = generate_coverage_badge.main()

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "Failed to stage badge" in captured.err
        # All three commands called
        assert mock_run_cmd.call_count == 3

    @patch("scripts.generate_coverage_badge.run_command")
    def test_pytest_command_structure(self, mock_run_cmd, tmp_path):
        """Test pytest command has correct arguments."""
        # Mock __file__ to point to our tmp_path
        with patch(
            "scripts.generate_coverage_badge.__file__", str(tmp_path / "scripts" / "generate_coverage_badge.py")
        ):
            # Mock pytest failure to stop early
            mock_run_cmd.return_value = subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr="")

            generate_coverage_badge.main()

        # Check pytest command structure
        pytest_call = mock_run_cmd.call_args_list[0][0][0]
        assert pytest_call[0:3] == ["uv", "run", "pytest"]
        assert "tests/" in pytest_call
        assert "--cov=scripts" in pytest_call
        assert "--cov=mcp_server" in pytest_call
        assert "--cov-report=xml" in pytest_call
        assert "-q" in pytest_call

    @patch("scripts.generate_coverage_badge.run_command")
    def test_badge_command_structure(self, mock_run_cmd, tmp_path):
        """Test coverage-badge command has correct arguments."""
        # Create repo structure with coverage.xml
        docs = tmp_path / "docs"
        docs.mkdir()
        coverage_xml = tmp_path / "coverage.xml"
        coverage_xml.write_text("<coverage></coverage>")

        # Mock __file__ to point to our tmp_path
        with patch(
            "scripts.generate_coverage_badge.__file__", str(tmp_path / "scripts" / "generate_coverage_badge.py")
        ):
            # Mock pytest success, badge failure to stop early
            def run_side_effect(cmd, **kwargs):
                if "pytest" in cmd:
                    return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")
                return subprocess.CompletedProcess(args=cmd, returncode=1, stdout="", stderr="")

            mock_run_cmd.side_effect = run_side_effect

            generate_coverage_badge.main()

        # Check coverage-badge command structure
        badge_call = mock_run_cmd.call_args_list[1][0][0]
        assert badge_call[0:3] == ["uv", "run", "coverage-badge"]
        assert "-o" in badge_call
        assert "-f" in badge_call
        # Badge path should be in command
        assert any("docs" in str(arg) and "coverage_badge.svg" in str(arg) for arg in badge_call)


class TestEdgeCases:
    """Test edge cases and error conditions."""

    @patch("scripts.generate_coverage_badge.run_command")
    def test_main_returns_zero_on_exception(self, mock_run_cmd, tmp_path, capsys):
        """Test main() handles unexpected exceptions gracefully."""
        # Mock __file__ to point to our tmp_path
        with patch(
            "scripts.generate_coverage_badge.__file__", str(tmp_path / "scripts" / "generate_coverage_badge.py")
        ):
            # Mock command that raises exception
            mock_run_cmd.side_effect = RuntimeError("Unexpected error")

            # Design is graceful: exceptions are caught and exit 0
            result = generate_coverage_badge.main()
            assert result == 0

            # Verify error was logged to stderr
            captured = capsys.readouterr()
            assert "Unexpected error" in captured.err or "failed" in captured.err.lower()

    @patch("scripts.generate_coverage_badge.run_command")
    def test_empty_coverage_xml(self, mock_run_cmd, tmp_path, capsys):
        """Test with empty coverage.xml file."""
        # Create repo structure with empty coverage.xml
        docs = tmp_path / "docs"
        docs.mkdir()
        coverage_xml = tmp_path / "coverage.xml"
        coverage_xml.write_text("")

        # Mock __file__ to point to our tmp_path
        with patch(
            "scripts.generate_coverage_badge.__file__", str(tmp_path / "scripts" / "generate_coverage_badge.py")
        ):
            # Mock pytest success, badge failure (empty XML invalid)
            def run_side_effect(cmd, **kwargs):
                if "pytest" in cmd:
                    return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")
                elif "coverage-badge" in cmd:
                    return subprocess.CompletedProcess(args=cmd, returncode=1, stdout="", stderr="invalid XML")
                return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

            mock_run_cmd.side_effect = run_side_effect

            exit_code = generate_coverage_badge.main()

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "Badge generation failed" in captured.err
