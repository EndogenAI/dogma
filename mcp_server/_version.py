"""mcp_server/_version.py — Tool version metadata for live trace records.

BRANCH_COUNTER must be 0 before merging to main. Increment locally when
debugging branch-specific behaviour you want to distinguish in traces.
Reset to 0 before opening a PR (pre-push hook warns if non-zero).

Usage:
    from mcp_server._version import TOOL_VERSION
"""

from importlib.metadata import PackageNotFoundError, version

try:
    _PKG_VERSION = version("dogma-governance")
except PackageNotFoundError:
    _PKG_VERSION = "0.0.0"

BRANCH_COUNTER: int = 0
TOOL_VERSION: str = f"{_PKG_VERSION}.{BRANCH_COUNTER}"
