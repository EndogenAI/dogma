"""mcp_server/_security.py — Path allowlist and SSRF helpers for the dogma MCP server.

All tool implementations must call these helpers before processing any
user-supplied file path or URL. Failing to do so allows path traversal or
SSRF attacks from MCP clients.

Usage:
    from mcp_server._security import validate_repo_path, validate_url

    # For file paths:
    safe_path = validate_repo_path("/abs/path/to/file")  # raises ValueError on traversal

    # For URLs (run_research_scout):
    safe_url = validate_url("https://example.com/page")  # raises ValueError on unsafe URL
"""

from __future__ import annotations

import ipaddress
import os
import re
import socket
import urllib.parse
from pathlib import Path

# Use os.path.abspath for cross-platform repo root calculation
# (cross_platform_tools imports this module, so we can't import from there)
REPO_ROOT = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Allowlist of URL schemes accepted by run_research_scout
_ALLOWED_SCHEMES: frozenset[str] = frozenset({"https"})

# IPv4 private ranges (RFC 1918 + loopback + link-local + CGNAT)
_BLOCKED_IPV4_NETWORKS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("100.64.0.0/10"),
]


def validate_repo_path(file_path: str) -> Path:
    """Validate that *file_path* resolves within REPO_ROOT.

    Raises:
        ValueError: if the resolved path escapes REPO_ROOT (path traversal).
    """
    resolved = Path(file_path).resolve()
    try:
        resolved.relative_to(REPO_ROOT)
    except ValueError:
        raise ValueError(
            f"Path '{file_path}' resolves outside the repository root. Only paths within the repo are permitted."
        )
    return resolved


def validate_url_safety(url: str) -> tuple[bool, str]:
    """Validate URL safety for SSRF prevention (non-raising variant).

    Enforces allowlist/blocklist rules:
    - Allowlist: https:// scheme only (blocks http://, file://, ftp://, etc.)
    - Blocklist: private IP ranges, localhost, metadata endpoints

    Returns:
        (True, "") if safe
        (False, reason) if blocked

    This is the non-raising variant used by scripts that need structured error handling.
    For MCP tools that prefer exceptions, use validate_url() instead.
    """
    try:
        parsed = urllib.parse.urlparse(url)
    except Exception as exc:
        return (False, f"Invalid URL syntax: {exc}")

    # Rule 1: Scheme allowlist (https only)
    if parsed.scheme not in _ALLOWED_SCHEMES:
        return (
            False,
            f"Rejected scheme '{parsed.scheme}': only 'https' is allowed (prevents SSRF via local file access)",
        )

    hostname = parsed.hostname
    if not hostname:
        return (False, "URL must have a valid hostname")

    # Rule 2: IPv6 link-local blocklist (fe80::/10)
    if re.match(r"^\[?fe80:", hostname, re.IGNORECASE):
        return (
            False,
            f"Rejected hostname '{hostname}': IPv6 link-local addresses are not allowed "
            f"(prevents SSRF to link-local services)",
        )

    # Rule 3: DNS-resolved IP blocklist (private ranges + metadata endpoints)
    try:
        addr_info = socket.getaddrinfo(hostname, None)
        for _family, _type, _proto, _canonname, sockaddr in addr_info:
            ip_str = sockaddr[0]
            # Strip IPv6 zone ID (e.g., fe81::1%eth0) before parsing
            if "%" in ip_str:
                ip_str = ip_str.split("%")[0]
            try:
                ip_addr = ipaddress.ip_address(ip_str)
                if isinstance(ip_addr, ipaddress.IPv4Address):
                    # Block private ranges, loopback, link-local, and unspecified (0.0.0.0)
                    if ip_addr.is_unspecified:
                        return (
                            False,
                            f"Rejected: URL resolves to unspecified IPv4 {ip_addr} (prevents SSRF)",
                        )
                    for blocked in _BLOCKED_IPV4_NETWORKS:
                        if ip_addr in blocked:
                            return (
                                False,
                                f"Rejected: URL resolves to private/internal IP {ip_addr} "
                                f"(prevents SSRF to internal services)",
                            )
                elif isinstance(ip_addr, ipaddress.IPv6Address):
                    # Block link-local, loopback, private, and unspecified (::)
                    if ip_addr.is_unspecified or ip_addr.is_link_local or ip_addr.is_loopback or ip_addr.is_private:
                        return (
                            False,
                            f"Rejected: URL resolves to private/internal IPv6 {ip_addr} (prevents SSRF)",
                        )
            except ValueError:
                pass  # IP parsing failed, continue checking other results
    except OSError:
        # DNS resolution failed — allow it through (downstream fetch will surface a cleaner error)
        pass

    return (True, "")


def validate_url(url: str) -> str:
    """Validate a URL for the run_research_scout tool (raising variant).

    Enforces:
    - https:// scheme only
    - No private / loopback IPv4 or IPv6 link-local destinations (SSRF)
    - Hostname must not be a bare IP in a private range

    Raises:
        ValueError: on scheme mismatch, invalid URL, or SSRF risk.

    This is the exception-raising variant used by MCP tools.
    For scripts that need structured error handling, use validate_url_safety() instead.
    """
    is_safe, reason = validate_url_safety(url)
    if not is_safe:
        raise ValueError(reason)
    return url
