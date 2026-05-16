#!/usr/bin/env python3
"""Tests for scripts/subscribe_cve_feeds.py (stub script).

Tests verify stub behavior:
1. Main function raises NotImplementedError
2. Script exits with code 0 (stub doesn't fail CI)
3. Help text is available
4. --dry-run flag is accepted
"""

import subprocess
import sys
from unittest.mock import patch

import pytest

import scripts.subscribe_cve_feeds as subscribe_cve_feeds


class TestStubBehavior:
    """Test subscribe_cve_feeds.py stub behavior."""

    @patch("sys.argv", ["subscribe_cve_feeds.py"])
    def test_main_raises_not_implemented(self):
        """Test that main() raises NotImplementedError as documented."""
        with pytest.raises(NotImplementedError) as exc_info:
            subscribe_cve_feeds.main()

        assert "CVE subscription not yet automated" in str(exc_info.value)
        assert "#361" in str(exc_info.value)

    def test_script_exits_zero_despite_not_implemented(self):
        """Test that script exits 0 (stub doesn't fail CI)."""
        result = subprocess.run(
            [sys.executable, "scripts/subscribe_cve_feeds.py"],
            capture_output=True,
            text=True,
        )

        # Stub should exit 0, not fail
        assert result.returncode == 0
        assert "NotImplementedError" in result.stderr
        assert "manual audit required" in result.stderr.lower()

    def test_help_available(self):
        """Test that --help works and shows stub status."""
        result = subprocess.run(
            [sys.executable, "scripts/subscribe_cve_feeds.py", "--help"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "STUB" in result.stdout
        assert "not yet implemented" in result.stdout.lower()
        assert "audit_dependencies.py" in result.stdout

    def test_dry_run_flag_accepted(self):
        """Test that --dry-run flag is parsed (even if unused in stub)."""
        result = subprocess.run(
            [sys.executable, "scripts/subscribe_cve_feeds.py", "--dry-run"],
            capture_output=True,
            text=True,
        )

        # Should still exit 0 (stub behavior)
        assert result.returncode == 0
        assert "CVE subscription stub invoked" in result.stdout or "NotImplementedError" in result.stderr

    @patch("scripts.subscribe_cve_feeds.argparse.ArgumentParser.parse_args")
    def test_argparse_called(self, mock_parse_args):
        """Test that argument parsing happens even though args are unused."""
        from argparse import Namespace

        mock_parse_args.return_value = Namespace(dry_run=False)

        with pytest.raises(NotImplementedError):
            subscribe_cve_feeds.main()

        mock_parse_args.assert_called_once()
