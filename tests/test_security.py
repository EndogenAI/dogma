"""
tests/test_security.py — Unit tests for SSRF protection in MCP security module and fetch_source.py.

Tests the validate_url_safety() function from mcp_server._security and integration
with scripts/fetch_source.py to ensure URL scheme/host validation prevents SSRF attacks.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

# Add repo root to path for imports
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from mcp_server._security import validate_url_safety  # noqa: E402

# ---------------------------------------------------------------------------
# Unit tests for validate_url_safety()
# ---------------------------------------------------------------------------


class TestValidateURLSafety:
    """Test suite for SSRF protection via validate_url_safety()."""

    def test_valid_https_url_passes(self):
        """Valid HTTPS URLs should pass validation."""
        is_safe, reason = validate_url_safety("https://example.com/page")
        assert is_safe is True
        assert reason == ""

    def test_valid_https_with_path_passes(self):
        """HTTPS URLs with paths and query strings should pass."""
        is_safe, reason = validate_url_safety("https://arxiv.org/abs/2512.05470?v=1")
        assert is_safe is True
        assert reason == ""

    def test_http_scheme_rejected(self):
        """HTTP scheme should be rejected (not in allowlist)."""
        is_safe, reason = validate_url_safety("http://example.com")
        assert is_safe is False
        assert "http" in reason.lower()
        assert "https" in reason

    def test_file_scheme_rejected(self):
        """file:// scheme should be rejected (SSRF prevention)."""
        is_safe, reason = validate_url_safety("file:///etc/passwd")
        assert is_safe is False
        assert "file" in reason.lower()

    def test_ftp_scheme_rejected(self):
        """ftp:// scheme should be rejected."""
        is_safe, reason = validate_url_safety("ftp://example.com/file")
        assert is_safe is False
        assert "ftp" in reason.lower()

    def test_localhost_rejected(self):
        """localhost hostname should be rejected (private IP)."""
        is_safe, reason = validate_url_safety("https://localhost:8080/api")
        assert is_safe is False
        assert "private" in reason.lower() or "internal" in reason.lower()

    def test_loopback_127_rejected(self):
        """127.0.0.1 loopback address should be rejected."""
        is_safe, reason = validate_url_safety("https://127.0.0.1/admin")
        assert is_safe is False
        assert "127.0.0.1" in reason or "private" in reason.lower()

    def test_private_10_network_rejected(self):
        """10.0.0.0/8 private network should be rejected."""
        is_safe, reason = validate_url_safety("https://10.0.0.1/internal")
        assert is_safe is False
        assert "10.0.0.1" in reason or "private" in reason.lower()

    def test_private_192_network_rejected(self):
        """192.168.0.0/16 private network should be rejected."""
        is_safe, reason = validate_url_safety("https://192.168.1.1/router")
        assert is_safe is False
        assert "192.168.1.1" in reason or "private" in reason.lower()

    def test_private_172_network_rejected(self):
        """172.16.0.0/12 private network should be rejected."""
        is_safe, reason = validate_url_safety("https://172.16.0.1/service")
        assert is_safe is False
        assert "172.16.0.1" in reason or "private" in reason.lower()

    def test_metadata_endpoint_rejected(self):
        """AWS/GCP metadata endpoint 169.254.169.254 should be rejected."""
        is_safe, reason = validate_url_safety("https://169.254.169.254/latest/meta-data/")
        assert is_safe is False
        assert "169.254.169.254" in reason or "link-local" in reason.lower()

    def test_ipv6_link_local_rejected(self):
        """IPv6 link-local address (fe80::/10) should be rejected."""
        is_safe, reason = validate_url_safety("https://[fe80::1]/service")
        assert is_safe is False
        assert "fe80" in reason.lower()
        assert "link-local" in reason.lower()

    def test_invalid_url_syntax_rejected(self):
        """Malformed URLs should be rejected with syntax error."""
        is_safe, reason = validate_url_safety("not-a-url")
        assert is_safe is False
        # Should either fail scheme check or syntax parsing
        assert "scheme" in reason.lower() or "invalid" in reason.lower()

    def test_empty_hostname_rejected(self):
        """URLs without hostname should be rejected."""
        is_safe, reason = validate_url_safety("https://")
        assert is_safe is False
        assert "hostname" in reason.lower()


# ---------------------------------------------------------------------------
# Integration tests for fetch_source.py CLI
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestFetchSourceIntegration:
    """Integration tests for fetch_source.py SSRF validation."""

    def test_fetch_source_rejects_http_scheme(self):
        """fetch_source.py should exit 2 when given http:// URL."""
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "fetch_source.py"), "http://example.com", "--dry-run"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 2
        assert "http" in result.stderr.lower()

    def test_fetch_source_rejects_localhost(self):
        """fetch_source.py should exit 2 when given localhost URL."""
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "fetch_source.py"), "https://localhost/api", "--dry-run"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 2
        assert "private" in result.stderr.lower() or "internal" in result.stderr.lower()

    def test_fetch_source_rejects_metadata_endpoint(self):
        """fetch_source.py should exit 2 when given metadata endpoint URL."""
        result = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "fetch_source.py"),
                "https://169.254.169.254/latest/meta-data/",
                "--dry-run",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 2
        assert "169.254.169.254" in result.stderr or "link-local" in result.stderr.lower()

    def test_fetch_source_rejects_file_scheme(self):
        """fetch_source.py should exit 2 when given file:// URL."""
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "fetch_source.py"), "file:///etc/passwd", "--dry-run"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 2
        assert "file" in result.stderr.lower()

    def test_fetch_source_accepts_valid_https_dryrun(self):
        """fetch_source.py should accept valid HTTPS URL in dry-run mode (exit 0)."""
        result = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "fetch_source.py"),
                "https://example.com/test",
                "--dry-run",
            ],
            capture_output=True,
            text=True,
        )
        # Dry-run with valid URL should exit 0 (validation passes, no actual fetch)
        assert result.returncode == 0
